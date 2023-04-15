import asyncio
import random
import socket
import struct
import threading
import time
from enum import IntEnum
from threading import Event
from typing import TYPE_CHECKING

import select
from aiohttp import WSMsgType

import interactions.api.events.internal as events
from interactions.api.gateway.websocket import WebsocketClient
from interactions.api.voice.encryption import Encryption
from interactions.client.const import MISSING
from interactions.client.errors import VoiceWebSocketClosed
from interactions.client.utils.input_utils import FastJson
from interactions.models.internal.listener import Listener

if TYPE_CHECKING:
    from interactions.api.gateway.gateway import GatewayClient

__all__ = ("VoiceGateway",)


class OP(IntEnum):
    IDENTIFY = 0
    SELECT_PROTOCOL = 1
    READY = 2
    HEARTBEAT = 3
    SESSION_DESCRIPTION = 4
    SPEAKING = 5
    HEARTBEAT_ACK = 6
    RESUME = 7
    HELLO = 8
    RESUMED = 9
    CLIENT_DISCONNECT = 13


class HandshakeTracker:
    def __init__(self, voice_gateway: "VoiceGateway"):
        self.active = False
        self.voice_gateway: "VoiceGateway" = voice_gateway

    def __enter__(self):
        if self.active:
            raise RuntimeError("Cannot enter a handshake context while another handshake is in progress")
        self.active = True
        self.voice_gateway._received_server_update.clear()
        self.voice_gateway._received_state_update.clear()
        self.voice_gateway.ready.clear()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.active = False
        self.voice_gateway._received_server_update.clear()
        self.voice_gateway._received_state_update.clear()

    @property
    def handshaking(self) -> bool:
        return self.active


class VoiceGateway(WebsocketClient):
    guild_id: str
    heartbeat_interval: int
    session_id: str
    token: str
    encryptor: Encryption

    ssrc: int
    me_ip: str
    me_port: int
    voice_ip: str
    voice_port: int
    voice_modes: list[str]
    selected_mode: str
    socket: socket.socket
    ready: Event

    def __init__(self, state, voice_state: dict, voice_server: dict) -> None:
        super().__init__(state)

        self._voice_server_update = asyncio.Event()
        self.ws_url = f"wss://{voice_server['endpoint']}?v=4"
        self.session_id = voice_state["session_id"]
        self.token = voice_server["token"]
        self.secret: str | None = None
        self.guild_id = voice_server["guild_id"]
        self.channel_id = voice_state["channel_id"]

        self.sock_sequence = 0
        self.timestamp = 0
        self.ready = Event()
        self.user_ssrc_map = {}
        self.cond = None

        self._udp_ka = threading.Thread(target=self._udp_keep_alive, daemon=True)

        self.client_gateway: "GatewayClient" = self.state.client.get_guild_websocket(self.guild_id)

        self.on_voice_state_update = Listener.create("on_raw_voice_state_update")(self._on_voice_state_update)
        self.on_voice_server_update = Listener.create("on_raw_voice_server_update")(self._on_voice_server_update)
        self.state.client.add_listener(self.on_voice_server_update)
        self.state.client.add_listener(self.on_voice_state_update)

        self._received_server_update = asyncio.Event()
        self._received_state_update = asyncio.Event()
        self._handshake = HandshakeTracker(self)

    async def cleanup(self) -> None:
        if self._udp_ka.is_alive():
            self._udp_ka.join()
        self._udp_ka = None
        self.state.client.listeners["raw_voice_server_update"].remove(self.on_voice_server_update)
        self.state.client.listeners["raw_voice_state_update"].remove(self.on_voice_state_update)
        self.logger.debug(f"{self.guild_id}:: Successfully removed listeners")

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await super().__aexit__(exc_type, exc_val, exc_tb)
        await self.cleanup()

    @property
    def connected(self) -> bool:
        return self.ready.is_set()

    async def wait_until_ready(self) -> None:
        await asyncio.to_thread(self.ready.wait)

    async def _on_voice_server_update(self, event: events.RawGatewayEvent) -> None:
        data = event.data

        if data["guild_id"] != self.guild_id:
            return
        if self._received_server_update.is_set():
            return

        self.ws_url = f"wss://{data['endpoint']}?v=4"
        self.token = data["token"]
        self.guild_id = data["guild_id"]

        if not self._handshake.handshaking:
            self.logger.debug(f"{self.guild_id}:: Received voice server update, but not handshaking")
            await self.ws.close()

        self._received_server_update.set()

    async def _on_voice_state_update(
        self,
        event: events.RawGatewayEvent,
    ) -> None:
        data = event.data

        if data["guild_id"] != self.guild_id:
            return

        self.session_id = data["session_id"]

        if channel_id := data["channel_id"]:
            if int(channel_id) == self.channel_id:
                return
            await self.state.client.fetch_channel(channel_id)
            self.logger.debug(f"{self.guild_id}:: Client forcefully moved from {self.channel_id} to {channel_id}")
            self.channel_id = int(channel_id)
        else:
            self.logger.debug(f"{self.guild_id}:: Disconnected from voice {self.channel_id}")
            self.close()

    async def run(self) -> None:
        """Start receiving events from the websocket."""
        while True:
            if self._stopping is None:
                self._stopping = asyncio.create_task(self._close_gateway.wait())
            receiving = asyncio.create_task(self.receive())
            done, _ = await asyncio.wait({self._stopping, receiving}, return_when=asyncio.FIRST_COMPLETED)

            if receiving in done:
                # Note that we check for a received message first, because if both completed at
                # the same time, we don't want to discard that message.
                msg = await receiving
            else:
                # This has to be the stopping task, which we join into the current task (even
                # though that doesn't give any meaningful value in the return).
                await self._stopping
                receiving.cancel()
                return

            op = msg.get("op")
            data = msg.get("d")
            if seq := msg.get("s"):
                self.sequence = seq

            # This may try to reconnect the connection so it is best to wait
            # for it to complete before receiving more - that way there's less
            # possible race conditions to consider.
            await self.dispatch_opcode(data, op)

    async def receive(self, force=False) -> dict:
        buffer = bytearray()

        while True:
            if not force:
                await self._closed.wait()

            resp = await self.ws.receive()

            if resp.type in (WSMsgType.CLOSED, WSMsgType.CLOSING, WSMsgType.CLOSE, WSMsgType.ERROR):
                close_info_log = f"{self.guild_id}:: Voice websocket closed with code {resp.data}"
                if resp.data in (1000, 4015):
                    self.logger.info(close_info_log)
                    raise VoiceWebSocketClosed(resp.data)
                if resp.data == 4014:
                    self.logger.info(f"{self.guild_id}:: Forcefully disconnected from voice")
                    await self.wait_for_reconnect()
                    continue
                self.logger.info(close_info_log)
                await self.client_gateway.voice_state_update(self.guild_id, None)
                try:
                    await self.reconnect()
                except Exception:
                    self.logger.exception(f"{self.guild_id}:: Failed to reconnect to voice")
                    continue

            if resp.data is None:
                continue

            if isinstance(resp.data, bytes):
                buffer.extend(resp.data)

                if len(resp.data) < 4 or resp.data[-4:] != b"\x00\x00\xff\xff":
                    # message isn't complete yet, wait
                    continue

                msg = self._zlib.decompress(buffer)
                msg = msg.decode("utf-8")
            else:
                msg = resp.data

            try:
                msg = FastJson.loads(msg)
            except Exception as e:
                self.logger.error(e)

            return msg

    async def dispatch_opcode(self, data, op) -> None:
        match op:
            case OP.HEARTBEAT_ACK:
                self._latency.append(time.perf_counter() - self._last_heartbeat)

                if self._last_heartbeat != 0 and self._latency[-1] >= 15:
                    self.logger.warning(
                        f"High Latency! Voice heartbeat took {self._latency[-1]:.1f}s to be acknowledged!"
                    )
                else:
                    self.logger.debug(f"❤ Heartbeat acknowledged after {self._latency[-1]:.5f} seconds")

                return self._acknowledged.set()

            case OP.READY:
                self.logger.debug("Discord send VC Ready! Establishing a socket connection...")
                self.voice_ip = data["ip"]
                self.voice_port = data["port"]
                self.ssrc = data["ssrc"]
                self.voice_modes = [mode for mode in data["modes"] if mode in Encryption.SUPPORTED]

                if not self.voice_modes:
                    self.logger.critical("NO VOICE ENCRYPTION MODES SHARED WITH GATEWAY!")

                await self.establish_voice_socket()

            case OP.SESSION_DESCRIPTION:
                self.logger.info(f"Voice connection established; using {data['mode']}")
                self.selected_mode = data["mode"]
                self.secret = data["secret_key"]
                self.encryptor = Encryption(self.secret)
                self.ready.set()
                if self.cond:
                    with self.cond:
                        self.cond.notify()
                if self._udp_ka is None or not self._udp_ka.is_alive():
                    self._udp_ka = threading.Thread(target=self._udp_keep_alive, daemon=True)
                    self._udp_ka.start()
            case OP.SPEAKING:
                self.user_ssrc_map[data["ssrc"]] = {"user_id": int(data["user_id"]), "speaking": data["speaking"]}
            case OP.CLIENT_DISCONNECT:
                self.logger.debug(
                    f"User {data['user_id']} has disconnected from voice, ssrc ({self.user_ssrc_map.pop(data['user_id'], MISSING)}) invalidated"
                )

            case _:
                return self.logger.debug(f"Unhandled OPCODE: {op} = {data = }")

    async def reconnect(self, *args, **kwargs) -> None:
        async with self._race_lock:
            self.ready.clear()

            for i in range(5):
                with self._handshake:
                    tasks = [
                        self._received_state_update.wait(),
                        self._received_state_update.wait(),
                    ]
                    await self.client_gateway.voice_state_update(self.guild_id, self.channel_id)

                    try:
                        await asyncio.wait(tasks, timeout=5, return_when=asyncio.ALL_COMPLETED)
                    except asyncio.TimeoutError:
                        await self.client_gateway.voice_state_update(self.guild_id, None)
                        raise

                try:
                    await self._connect_websocket()
                    break
                except Exception:
                    self.logger.exception("Failed to reconnect to voice gateway")
                    await asyncio.sleep(2**i)
                    await self.client_gateway.voice_state_update(self.guild_id, None)
                    continue

            self.logger.debug("Reconnected to voice gateway")

    async def wait_for_reconnect(self) -> bool:
        with self._handshake:
            try:
                await asyncio.wait_for(self._received_server_update.wait(), timeout=5)
            except asyncio.TimeoutError:
                await self.disconnect(force=True)
                return False

        try:
            await self._connect_websocket()
        except Exception:
            return False
        return True

    async def _resume_connection(self) -> None:
        if self.ws is None:
            raise RuntimeError

        payload = {
            "op": OP.RESUME,
            "d": {"server_id": self.guild_id, "session_id": self.session_id, "token": self.token},
        }
        await self.ws.send_json(payload)

    async def disconnect(self, *, force: bool = False):
        if not force and not self.connected:
            return

        self._close_gateway.set()
        self._kill_bee_gees.set()

        try:
            if self.ws:
                await self.ws.close(code=1000)

            await self.client_gateway.voice_state_update(self.guild_id, None)
        finally:
            if self.socket:
                self.socket.close()

    def _udp_keep_alive(self) -> None:
        keep_alive = b"\xc9\x00\x00\x00\x00\x00\x00\x00\x00"

        self.logger.debug("Starting UDP Keep Alive")
        try:
            while not self._kill_bee_gees.is_set() and self.ready.is_set() and not self._close_gateway.is_set():
                if not self.socket._closed and not self.ws.closed:
                    try:
                        _, writable, _ = select.select([], [self.socket], [], 0)
                        while not writable:
                            _, writable, _ = select.select([], [self.socket], [], 0)

                        # discord will never respond to this, but it helps maintain the hole punch
                        self.send_to_socket(keep_alive)

                        time.sleep(5)
                    except socket.error as e:
                        self.logger.warning(f"Ending Keep Alive due to {e}")
                        return
                    except Exception as e:
                        self.logger.debug("Keep Alive Error: ", exc_info=e)
        except AttributeError as e:
            self.logger.error("UDP Keep Alive has been closed", exc_info=e)
        self.logger.debug("Ending UDP Keep Alive")

    def send_to_socket(self, data: bytes, *, log=True) -> None:
        self.socket.sendto(data, (self.voice_ip, self.voice_port))
        if log:
            self.logger.debug(f"{self.guild_id}:: Sent {len(data)} bytes to voice socket :: {data!r}")

    async def establish_voice_socket(self) -> None:
        """Establish the socket connection to discord"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setblocking(False)

        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 8192)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 8192)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        tries = 0
        packet = bytearray(74)
        packet[:2] = (1).to_bytes(2, byteorder="big")
        packet[2:4] = (0x46).to_bytes(2, byteorder="big")
        packet[4:8] = self.ssrc.to_bytes(4, byteorder="big")

        while tries < 5:
            self.logger.debug("IP Discovery in progress..." + (f" (Attempt {tries + 1}/5)" if tries > 0 else ""))
            self.socket.settimeout(10)
            self.send_to_socket(packet)

            resp = await self.loop.sock_recv(self.socket, 74)

            if len(resp) != 74:
                tries += 1
                if tries == 5:
                    self.logger.critical("IP Discovery failed, terminating voice connection")
                    self.close()
                    return
                continue

            self.me_ip = resp[8:].split(b"\x00", 1)[0].decode()
            self.me_port = int.from_bytes(resp[72:74], byteorder="big")
            self.logger.debug(f"IP Discovered: {self.me_ip} #{self.me_port}")
            self.socket.settimeout(0)
            break

        await self._select_protocol()

    def generate_packet(self, data: bytes) -> bytes:
        """Generate a packet to be sent to the voice socket."""
        header = bytearray(12)
        header[0] = 0x80
        header[1] = 0x78

        struct.pack_into(">H", header, 2, self.sock_sequence)
        struct.pack_into(">I", header, 4, self.timestamp)
        struct.pack_into(">I", header, 8, self.ssrc)

        return self.encryptor.encrypt(self.voice_modes[0], header, data)

    def send_packet(self, data: bytes, encoder, needs_encode=True) -> None:
        """Send a packet to the voice socket - called from a thread."""
        self.sock_sequence += 1
        if self.sock_sequence > 0xFFFF:
            self.sock_sequence = 0

        if self.timestamp > 0xFFFFFFFF:
            self.timestamp = 0

        if needs_encode:
            data = encoder.encode(data)
        packet = self.generate_packet(data)

        _, writable, _ = select.select([], [self.socket], [], 0)
        while not writable:
            _, writable, errored = select.select([], [self.socket], [], 0)
            if errored:
                self.logger.error(f"Socket errored: {errored}")
            continue
        self.send_to_socket(packet, log=False)
        self.timestamp += encoder.samples_per_frame

    async def send_heartbeat(self) -> None:
        await self.send_json({"op": OP.HEARTBEAT, "d": random.uniform(0.0, 1.0)})
        self.logger.debug("❤ Voice Connection is sending Heartbeat")

    async def _identify(self) -> None:
        """Send an identify payload to the voice gateway."""
        payload = {
            "op": OP.IDENTIFY,
            "d": {
                "server_id": self.guild_id,
                "user_id": self.state.client.user.id,
                "session_id": self.session_id,
                "token": self.token,
            },
        }
        serialized = FastJson.dumps(payload)
        await self.ws.send_str(serialized)

        self.logger.debug("Voice Connection has identified itself to Voice Gateway")

    async def _select_protocol(self) -> None:
        """Inform Discord of our chosen protocol."""
        payload = {
            "op": OP.SELECT_PROTOCOL,
            "d": {
                "protocol": "udp",
                "data": {"address": self.me_ip, "port": self.me_port, "mode": self.voice_modes[0]},
            },
        }
        await self.send_json(payload)

    async def speaking(self, is_speaking: bool = True) -> None:
        """
        Tell the gateway if we're sending audio or not.

        Args:
            is_speaking: If we're sending audio or not

        """
        payload = {
            "op": OP.SPEAKING,
            "d": {
                "speaking": 1 << 0 if is_speaking else 0,
                "delay": 0,
                "ssrc": self.ssrc,
            },
        }
        await self.ws.send_json(payload)
