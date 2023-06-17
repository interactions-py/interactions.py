import asyncio
import random
import socket
import struct
import threading
import time
from enum import IntEnum
from threading import Event

import select
from aiohttp import WSMsgType

from interactions.api.gateway.websocket import WebsocketClient
from interactions.api.voice.encryption import Encryption
from interactions.client.const import MISSING
from interactions.client.errors import VoiceWebSocketClosed
from interactions.client.utils.input_utils import FastJson

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

        self.sock_sequence = 0
        self.timestamp = 0
        self.ready = Event()
        self.user_ssrc_map = {}
        self.cond = None

        self._udp_ka = threading.Thread(target=self._udp_keep_alive, daemon=True)

    async def wait_until_ready(self) -> None:
        await asyncio.to_thread(self.ready.wait)

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

    async def receive(self, force=False) -> str:  # noqa: C901
        buffer = bytearray()

        while True:
            if not force:
                await self._closed.wait()

            resp = await self.ws.receive()

            if resp.type == WSMsgType.CLOSE:
                self.logger.debug(f"Disconnecting from voice gateway! Reason: {resp.data}::{resp.extra}")
                if resp.data in (4006, 4009, 4014, 4015):
                    # these are all recoverable close codes, anything else means we're foobared
                    # codes: session expired, session timeout, disconnected, server crash
                    self.ready.clear()
                    # docs state only resume on 4015
                    await self.reconnect(resume=resp.data == 4015)
                    continue
                raise VoiceWebSocketClosed(resp.data)

            if resp.type is WSMsgType.CLOSED:
                if force:
                    raise RuntimeError("Discord unexpectedly closed the underlying socket during force receive!")

                if not self._closed.is_set():
                    # Because we are waiting for the even before we receive, this shouldn't be
                    # possible - the CLOSING message should be returned instead. Either way, if this
                    # is possible after all we can just wait for the event to be set.
                    await self._closed.wait()
                else:
                    # This is an odd corner-case where the underlying socket connection was closed
                    # unexpectedly without communicating the WebSocket closing handshake. We'll have
                    # to reconnect ourselves.
                    await self.reconnect(resume=True)

            elif resp.type is WSMsgType.CLOSING:
                if force:
                    raise RuntimeError("WebSocket is unexpectedly closing during force receive!")

                # This happens when the keep-alive handler is reconnecting the connection even
                # though we waited for the event before hand, because it got to run while we waited
                # for data to come in. We can just wait for the event again.
                await self._closed.wait()
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
            case OP.SPEAKING:
                self.user_ssrc_map[data["ssrc"]] = {"user_id": int(data["user_id"]), "speaking": data["speaking"]}
            case OP.CLIENT_DISCONNECT:
                self.logger.debug(
                    f"User {data['user_id']} has disconnected from voice, ssrc ({self.user_ssrc_map.pop(data['user_id'], MISSING)}) invalidated"
                )

            case _:
                return self.logger.debug(f"Unhandled OPCODE: {op} = {data = }")

    async def reconnect(self, *, resume: bool = False, code: int = 1012) -> None:
        async with self._race_lock:
            self._closed.clear()

            if self.ws is not None:
                await self.ws.close(code=code)

            self.ws = None

            if not resume:
                self.logger.debug("Waiting for updated server information...")
                try:
                    await asyncio.wait_for(self._voice_server_update.wait(), timeout=5)
                except asyncio.TimeoutError:
                    self._kill_bee_gees.set()
                    self.close()
                    self.logger.debug("Terminating VoiceGateway due to disconnection")
                    return None

                self._voice_server_update.clear()

            self.ws = await self.state.client.http.websocket_connect(self.ws_url)

            try:
                hello = await self.receive(force=True)
                self.heartbeat_interval = hello["d"]["heartbeat_interval"] / 1000
            except RuntimeError:
                # sometimes the initial connection fails with voice gateways, handle that
                return await self.reconnect(resume=resume, code=code)

            if not resume:
                await self._identify()
            else:
                await self._resume_connection()

            self._closed.set()
            self._acknowledged.set()

    async def _resume_connection(self) -> None:
        if self.ws is None:
            raise RuntimeError

        payload = {
            "op": OP.RESUME,
            "d": {"server_id": self.guild_id, "session_id": self.session_id, "token": self.token},
        }
        await self.ws.send_json(payload)

        if not self._udp_ka.is_alive():
            self._udp_ka = threading.Thread(target=self._udp_keep_alive, daemon=True)
            self._udp_ka.start()

    def _udp_keep_alive(self) -> None:
        keep_alive = b"\xc9\x00\x00\x00\x00\x00\x00\x00\x00"

        self.logger.debug("Starting UDP Keep Alive")
        while not self.socket._closed and self.ws and not self.ws.closed:
            try:
                _, writable, _ = select.select([], [self.socket], [], 0)
                while not writable:
                    _, writable, _ = select.select([], [self.socket], [], 0)

                # discord will never respond to this, but it helps maintain the hole punch
                self.socket.sendto(keep_alive, (self.voice_ip, self.voice_port))
                time.sleep(5)
            except socket.error as e:
                self.logger.warning(f"Ending Keep Alive due to {e}")
                return
            except AttributeError:
                return
            except Exception as e:
                self.logger.debug("Keep Alive Error: ", exc_info=e)
        self.logger.debug("Ending UDP Keep Alive")

    async def establish_voice_socket(self) -> None:
        """Establish the socket connection to discord"""
        self.logger.debug("IP Discovery in progress...")

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setblocking(False)

        packet = bytearray(74)
        struct.pack_into(">H", packet, 0, 1)  # 1 = Send
        struct.pack_into(">H", packet, 2, 70)  # 70 = Length
        struct.pack_into(">I", packet, 4, self.ssrc)

        self.socket.sendto(packet, (self.voice_ip, self.voice_port))
        resp = await self.loop.sock_recv(self.socket, 74)
        self.logger.debug(f"Voice Initial Response Received: {resp}")

        ip_start = 8
        ip_end = resp.index(0, ip_start)
        self.me_ip = resp[ip_start:ip_end].decode("ascii")

        self.me_port = struct.unpack_from(">H", resp, len(resp) - 2)[0]
        self.logger.debug(f"IP Discovered: {self.me_ip} #{self.me_port}")

        await self._select_protocol()

        if not self._udp_ka.is_alive():
            self._udp_ka = threading.Thread(target=self._udp_keep_alive, daemon=True)
            self._udp_ka.start()

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
        """Send a packet to the voice socket"""
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
        self.socket.sendto(packet, (self.voice_ip, self.voice_port))
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

    def set_new_voice_server(self, payload: dict) -> None:
        """
        Set a new voice server to connect to.

        Args:
            payload: New voice server connection data

        """
        self.ws_url = f"wss://{payload['endpoint']}?v=4"
        self.token = payload["token"]
        self.guild_id = payload["guild_id"]
        self._voice_server_update.set()
