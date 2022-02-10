try:
    from orjson import dumps, loads
except ImportError:
    from json import dumps, loads

from asyncio import (
    AbstractEventLoop,
    Event,
    Task,
    ensure_future,
    get_event_loop,
    get_running_loop,
    new_event_loop,
    sleep,
)
from logging import Logger
from sys import platform, version_info
from typing import Any, Dict, List, Optional, Tuple

from aiohttp import WSMessage

from ..api.models.gw import Presence
from ..base import get_logger
from .dispatch import Listener
from .enums import OpCodeType
from .error import GatewayException
from .http import HTTPClient
from .models.flags import Intents
from .models.misc import MISSING

log: Logger = get_logger("gateway")


__all__ = ("_Heartbeat", "WebSocketClient")


class _Heartbeat:
    """An internal class representing the heartbeat in a WebSocket connection."""

    event: Event
    delay: float

    def __init__(self, loop: AbstractEventLoop) -> None:
        """
        :param loop: The event loop to base the asynchronous manager.
        :type loop: AbstractEventLoop
        """
        self.event = Event(loop=loop) if version_info < (3, 10) else Event()
        self.delay = 0.0


class WebSocketClient:
    """
    A class representing the client's connection to the Gateway via. WebSocket.

    :ivar AbstractEventLoop _loop: The asynchronous event loop.
    :ivar Listener _dispatch: The built-in event dispatcher.
    :ivar HTTPClient _http: The user-facing HTTP client.
    :ivar ClientWebSocketResponse _client: The WebSocket data of the connection.
    :ivar bool _closed: Whether the connection has been closed or not.
    :ivar dict _options: The connection options made during connection.
    :ivar Intents _intents: The gateway intents used for connection.
    :ivar dict _ready: The contents of the application returned when ready.
    :ivar _Heartbeat __heartbeater: The context state of a "heartbeat" made to the Gateway.
    :ivar Optional[List[Tuple[int]]] __shard: The shards used during connection.
    :ivar Optional[Presence] __presence: The presence used in connection.
    :ivar Task __task: The closing task for ending connections.
    :ivar int session_id: The ID of the ongoing session.
    :ivar str sequence: The sequence identifier of the ongoing session.
    """

    __slots__ = (
        "_loop",
        "_dispatch",
        "_http",
        "_client",
        "_closed",
        "_options",
        "_intents",
        "_ready",
        "__heartbeater",
        "__shard",
        "__presence",
        "__task",
        "session_id",
        "sequence",
        "ready",
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
        self.__heartbeater: _Heartbeat = _Heartbeat(
            loop=self._loop if version_info < (3, 10) else None
        )
        self.__shard = None
        self.__presence = None
        self.__task = None
        self.session_id = None if session_id is MISSING else session_id
        self.sequence = None if sequence is MISSING else sequence
        self.ready = None

    @property
    async def __heartbeat_manager(self) -> None:
        """Manages the heartbeat loop."""
        while True:
            if self.__heartbeater.event.is_set():
                await self.__heartbeat_packet
                self.__heartbeater.event.clear()
                await sleep(self.__heartbeater.delay / 1000)
            else:
                log.debug("Heartbeat ACK not recieved, reconnecting to Gateway...")
                await self._client.close()
                await self._establish_connection()
                break

    async def _establish_connection(
        self, shard: Optional[List[Tuple[int]]] = MISSING, presence: Optional[Presence] = MISSING
    ) -> None:
        """
        Establishes a client connection with the Gateway.

        :param shard?: The shards to establish a connection with. Defaults to ``None``.
        :type shard: Optional[List[Tuple[int]]]
        :param presence: The presence to carry with. Defaults to ``None``.
        :type presence: Optional[Presence]
        """
        self._client = None
        self._closed = False
        self.__heartbeater.delay = 0.0
        self._options["headers"] = {"User-Agent": self._http._req._headers["User-Agent"]}
        url = await self._http.get_gateway()

        async with self._http._req._session.ws_connect(url, **self._options) as self._client:
            while not self._closed:
                stream = await self.__receive_packet_stream

                if stream is None:
                    continue
                if self._client.close_code in range(4010, 4014) or self._client.close_code == 4004:
                    raise GatewayException(self._client.close_code)
                else:
                    self._establish_connection()

                await self._handle_connection(stream, shard, presence)

    async def __close(self):
        """Closes the client's connection and heartbeat with the Gateway."""
        if self.__task:
            self.__task: Task()
            self.__task.cancel()
        await self._client.close()
        await self._establish_connection()

    async def _handle_connection(
        self,
        stream: Dict[str, Any],
        shard: Optional[List[Tuple[int]]] = MISSING,
        presence: Optional[Presence] = MISSING,
    ) -> None:
        """
        Handles the client's connection with the Gateway.

        :param stream: The packet stream to handle.
        :type stream: Dict[str, Any]
        :param shard?: The shards to establish a connection with. Defaults to ``None``.
        :type shard: Optional[List[Tuple[int]]]
        :param presence: The presence to carry with. Defaults to ``None``.
        :type presence: Optional[Presence]
        """
        op: Optional[int] = stream.get("op")
        event: Optional[str] = stream.get("t")
        data: Optional[Dict[str, Any]] = stream.get("d")

        if op != OpCodeType.DISPATCH:
            log.debug(data)

            if op == OpCodeType.HELLO:
                self.__heartbeater.delay = data["heartbeat_interval"]
                self.__heartbeater.event.set()
                self.__task = ensure_future(self.__heartbeat_manager)

                if not self.session_id:
                    await self.__identify_packet(shard, presence)
                else:
                    await self.__resume_packet
            if op == OpCodeType.HEARTBEAT:
                await self.__heartbeat_packet
            if op == OpCodeType.HEARTBEAT_ACK:
                log.debug("HEARTBEAT_ACK")
                self.__heartbeater.event.set()
            if op in (OpCodeType.INVALIDATE_SESSION, OpCodeType.RECONNECT):
                log.debug("INVALID_SESSION/RECONNECT")
                if data and op != OpCodeType.RECONNECT:
                    self.session_id = None
                    self.sequence = None
                    self._closed = True
                await self.__close()
        elif event == "READY":
            self._ready = data
            self.session_id = data["session_id"]
            self.sequence = stream["s"]
            self._dispatch.dispatch("on_ready")
            log.debug(f"READY (session_id: {self.session_id}, seq: {self.sequence})")
        else:
            log.debug(f"{event}: {data}")
            # self.handle_dispatch(event, data)

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
        self, shard: Optional[List[Tuple[int]]] = None, presence: Optional[Presence] = None
    ) -> None:
        """
        Sends an ``IDENTIFY`` packet to the gateway.

        :param shard?: The shard ID to identify under.
        :type shard: Optional[List[Tuple[int]]]
        :param presence?: The presence to change the bot to on identify.
        :type presence: Optional[Presence]
        """
        self.__shard = shard
        self.__presence = presence
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

        if isinstance(shard, List) and len(shard) >= 1:
            payload["d"]["shard"] = shard
        if isinstance(presence, Presence):
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
        payload: dict = {"op": OpCodeType.HEARTBEAT, "d": self.sequence}
        await self._send_packet(payload)
        log.debug("HEARTBEAT")

    @property
    def shard(self) -> Optional[List[Tuple[int]]]:
        """Returns the current shard"""
        return self.__shard

    @property
    def presence(self) -> Optional[Presence]:
        """Returns the current presence."""
        return self.__presence
