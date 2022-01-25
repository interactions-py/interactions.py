try:
    from orjson import dumps, loads
except ImportError:
    from json import dumps, loads

from asyncio import Event, create_task, get_event_loop, get_running_loop, new_event_loop, wait_for
from logging import Logger
from sys import platform, version_info
from typing import Any, Dict, List, Optional, Tuple

from aiohttp import WSMessage

from ..api.models.gw import Presence
from ..base import get_logger
from ..models.misc import MISSING
from .dispatch import Listener
from .enums import OpCodeType
from .error import GatewayException
from .http import HTTPClient
from .models.flags import Intents

log: Logger = get_logger("gateway")

__all__ = "WebSocketClient"


class WebSocketClient:
    """A class representing the client's connection to the Gateway via. WebSocket."""

    __slots__ = (
        "_loop",
        "_dispatch",
        "_http",
        "_client",
        "_closed",
        "_options",
        "_intents",
        "__trace",
        "__heartbeater",
        "__morgued",
        "session_id",
        "sequence",
    )

    def __init__(
        self,
        token: str,
        intents: Intents,
        session_id: Optional[int] = MISSING,
        sequence: Optional[int] = MISSING,
    ) -> None:
        """
        :param token: The token of the application for connecting to the Gateway.
        :type token: str
        :param intents: The Gateway intents of the application for event dispatch.
        :type intents: Intents
        :param session_id?: The ID of the session if trying to reconnect. Defaults to ``None``.
        :type session_id: Optional[int]
        :param sequence?: The identifier sequence if trying to reconnect. Defaults to ``None``.
        :type sequence: Optional[int]
        """
        try:
            self._loop = get_event_loop() if version_info < (3, 10) else get_running_loop()
        except RuntimeError:
            self._loop = new_event_loop()
        self._dispatch = Listener()
        self._http = HTTPClient(token)
        self._client = None
        self._closed = False
        self._options = {
            "max_msg_size": 1024 ** 2,
            "timeout": 60,
            "autoclose": False,
            "compress": 0,
        }
        self._intents = intents
        self.__heartbeater = Event(loop=self._loop if version_info < (3, 10) else None)
        self.__morgued = Event(loop=self._loop if version_info < (3, 10) else None)
        self.session_id = None if session_id is MISSING else session_id
        self.sequence = None if sequence is MISSING else sequence
        self.ready = None

    async def _establish_connection(
        self, shard: Optional[List[Tuple[int]]] = MISSING, presence: Optional[Presence] = MISSING
    ) -> None:
        """Establishes a client connection with the Gateway."""
        self._options["headers"] = {"User-Agent": self._http._req._headers["User-Agent"]}
        url: str = await self._http.get_bot_gateway()

        async with self._http._req._session.ws_connect(url, **self._options) as self._client:
            while not self._closed:
                stream = await self.__receive_packet_stream

                if stream is None:
                    continue
                if self._client.close_code:
                    raise GatewayException(self._client.close_code)

                await self._handle_connection(stream, shard, presence)

    async def _handle_connection(
        self,
        stream: Dict[str, Any],
        shard: Optional[List[Tuple[int]]] = MISSING,
        presence: Optional[Presence] = MISSING,
    ) -> None:
        """Handles the client's connection with the Gateway."""
        op: Optional[int] = stream.get("op")
        event: Optional[str] = stream.get("t")
        data: Optional[Dict[str, Any]] = stream.get("d")

        if op != OpCodeType.DISPATCH:
            log.debug(data)

            if op == OpCodeType.HELLO:
                if not self.session_id:
                    await self.__identify_packet(shard, presence)
                else:
                    await self.__resume_packet
                await self.__heartbeat_packet
                self.__heartbeater.set()
                create_task(self.__heartbeater)
                wait_for(self.__morgued, timeout=data["heartbeat_interval"], loop=self._loop)
            if op == OpCodeType.HEARTBEAT and self.__heartbeater.is_set():
                await self.__heartbeat_packet
            if op == OpCodeType.HEARTBEAT_ACK and self.__heartbeater.is_set():
                log.debug("HEARTBEAT_ACK")
            if op in (OpCodeType.INVALID_SESSION, OpCodeType.RECONNECT):
                log.debug("INVALID_SESSION/RECONNECT")
                if not data or op == OpCodeType.RECONNECT:
                    try:
                        await self.__resume_packet
                        await self.__identify_packet(shard, presence)
                    except Exception as exc:
                        log.error("Server declined to reconnect, closing.")
                        log.error(f"{type(exc)}: {exc}")
                        await self._client.close()
                else:
                    self.session_id = None
                    self.sequence = None
                    self._closed = True
        elif event == "READY":
            self.session_id = data["session_id"]
            self.sequence = stream["s"]
            self.dispatch.dispatch("on_ready")
            log.debug(f"READY (session_id: {self.session_id}, seq: {self.sequence})")
        else:
            log.debug(f"{event}: {dumps(data, indent=4, sort_keys=True)}")
            self.handle_dispatch(event, data)

    @property
    async def __receive_packet_stream(self) -> Optional[Dict[str, Any]]:
        """
        Receives a stream of packets sent from the Gateway.

        :return: The packet stream.
        :rtype: Optional[Dict[str, Any]]
        """
        packet: WSMessage = await self._client.receive()
        return loads(packet.data) if packet and isinstance(packet.data, str) else None

    async def _send_packet(self, data: Dict[str, Any]) -> None:
        """
        Sends a packet to the Gateway.

        :param data: The data to send to the Gateway.
        :type data: Dict[str, Any]
        """
        packet: str = dumps(data).decode("utf-8") if isinstance(data, dict) else data
        await self._client.send_str(packet)
        log.debug(packet)

    async def __identify_packet(
        self, shard: Optional[List[int]] = MISSING, presence: Optional[Presence] = MISSING
    ) -> None:
        """
        Sends an ``IDENTIFY`` packet to the gateway.

        :param shard?: The shard ID to identify under.
        :type shard: Optional[int]
        :param presence?: The presence to change the bot to on identify.
        :type presence: Optional[Presence]
        """
        payload: dict = {
            "op": OpCodeType.IDENTIFY,
            "d": {
                "token": self._http.token,
                "intents": self._intents.value,
                "properties": {
                    "$os": platform,
                    "$browser": "interactions.py",
                    "$device": "interactions.py",
                },
            },
        }

        if shard is not MISSING:
            payload["d"]["shard"] = shard
        if presence is not MISSING:
            payload["d"]["presence"] = presence._json

        log.debug(f"IDENTIFYING: {payload}")
        await self._send_packet(payload)
        log.debug("IDENTIFY")

    @property
    async def __resume_packet(self) -> None:
        """Sends a ``RESUME`` packet to the gateway."""
        payload: dict = {
            "op": OpCodeType.RESUME,
            "d": {"token": self._http.token, "seq": self.sequence, "session_id": self.session_id},
        }
        log.debug(f"RESUMING: {payload}")
        await self._send_packet(payload)
        log.debug("RESUME")

    @property
    async def __heartbeat_packet(self) -> None:
        """Sends a ``HEARTBEAT`` packet to the gateway."""
        payload: dict = {"op": OpCodeType.HEARTBEAT, "d": self.session_id}
        await self._send_packet(payload)
        log.debug("HEARTBEAT")
