import sys
from asyncio import AbstractEventLoop, get_running_loop, run_coroutine_threadsafe
from logging import Logger, basicConfig, getLogger
from random import random
from threading import Event, Thread
from typing import Any, Optional, Union

from orjson import dumps, loads

from ..base import Data
from .dispatch import Listener
from .enums import OpCodeType
from .error import GatewayException
from .http import Request, Route
from .models.intents import Intents

basicConfig(level=Data.LOGGER)
log: Logger = getLogger("gateway")

__all__ = ("Heartbeat", "WebSocket")


class Heartbeat(Thread):
    """
    A class representing a consistent heartbeat connection with the gateway.

    :ivar ws: The WebSocket class to infer on.
    :ivar interval: The heartbeat interval determined by the gateway.
    :ivar event: The multi-threading event.
    """

    __slots__ = ("ws", "interval", "event")
    ws: Any
    interval: Union[int, float]
    event: Event

    def __init__(self, ws: Any, interval: int) -> None:
        """
        :param ws: The WebSocket inference to run the coroutine off of.
        :type ws: typing.Any
        :param interval: The interval to periodically send events.
        :type interval: int
        :return: None
        """
        super().__init__()
        self.ws = ws
        self.interval = interval / 1000
        self.event = Event()

    def run(self) -> None:
        """Starts the heartbeat connection."""
        while not self.event.wait(self.interval - random()):
            try:
                coro = run_coroutine_threadsafe(self.ws.heartbeat(), loop=self.ws.loop)
                while True:
                    try:
                        coro.result(timeout=10)
                        break
                    except:  # noqa
                        log.debug("The heartbeat took too long to send.")
                        log.error(
                            "The client was unable to send a heartbeat, closing the connection."
                        )
                        self.stop()
            except:  # noqa
                pass

    def stop(self) -> None:
        """Stops the heartbeat connection."""
        self.event.set()


class WebSocket:
    """
    A class representing a websocket connection with the gateway.

    :ivar intents: An instance of :class:`interactions.api.models.Intents`.
    :ivar loop: The coroutine event loop established on.
    :ivar req: An instance of :class:`interactions.api.http.Request`.
    :ivar dispatch: An instance of :class:`interactions.api.dispatch.Listener`.
    :ivar session: The current client session.
    :ivar session_id: The current ID of the gateway session.
    :ivar sequence: The current sequence of the gateway connection.
    :ivar keep_alive: An instance of :class:`interactions.api.gateway.Heartbeat`.
    :ivar closed: The current connection state.
    """

    __slots__ = (
        "intents",
        "loop",
        "req",
        "dispatch",
        "session",
        "session_id",
        "sequence",
        "keep_alive",
        "closed",
    )
    intents: Intents
    loop: AbstractEventLoop
    req: Optional[Request]
    dispatch: Listener
    session: Any
    session_id: Optional[int]
    sequence: Optional[int]
    keep_alive: Optional[Heartbeat]
    closed: bool

    def __init__(
        self,
        intents: Intents,
        session_id: Optional[int] = None,
        sequence: Optional[int] = None,
    ) -> None:
        """
        :param intents: The intents used for identifying the connection.
        :type intents: interactions.api.models.Intents
        :param session_id: The session ID if you're trying to resume a connection. Defaults to ``None``.
        :type session_id: typing.Optional[int]
        :param sequence: The sequence if you're trying to resume a connection. Defaults to ``None``.
        :type sequence: typing.Optional[int]
        :return: None
        """
        self.intents = intents
        self.loop = get_running_loop()
        self.req = None
        self.dispatch = Listener(loop=self.loop)
        self.session = None
        self.session_id = session_id
        self.sequence = sequence
        self.keep_alive = None
        self.closed = False

    async def recv(self) -> None:
        """Receives packets sent from the gateway."""
        packet = await self.session.receive()
        return (
            loads(packet.data)
            if packet and isinstance(packet.data, (bytearray, bytes, memoryview, str))
            else None
        )

    async def connect(self, token: str) -> None:
        """
        Establishes a connection to the gateway.

        :param token: The token to use for identifying.
        :type token: str
        :return: None
        """
        self.req = Request(token, loop=self.loop)
        gateway_url = await self.req.request(Route("GET", "/gateway"))

        options: dict = {
            "max_msg_size": 1024 ** 2,
            "timeout": 60,
            "autoclose": False,
            "headers": {"User-Agent": self.req.headers["User-Agent"]},
            "compress": 0,
        }

        async with self.req.session.ws_connect(
            gateway_url["url"] + "?v=9&encoding=json", **options
        ) as self.session:
            while not self.closed:
                stream = await self.recv()

                if stream is None:
                    continue

                if self.session.close_code:
                    code = self.session.close_code
                    raise GatewayException(code)

                op: Optional[int] = stream.get("op")
                event: Optional[str] = stream.get("t")
                data: Optional[dict] = stream.get("d")
                self.sequence = stream.get("s")

                if op != OpCodeType.DISPATCH:
                    log.debug(data)

                    if op == OpCodeType.HELLO:
                        if not self.session_id:
                            await self.identify()
                        else:
                            await self.resume()

                        heartbeat_interval = data["heartbeat_interval"]
                        self.keep_alive = Heartbeat(self, heartbeat_interval)

                        await self.heartbeat()
                        self.keep_alive.start()

                        continue

                    if op == OpCodeType.HEARTBEAT:
                        if self.keep_alive:
                            await self.heartbeat()
                        continue

                    if op == OpCodeType.HEARTBEAT_ACK:
                        if self.keep_alive:
                            log.debug("HEARTBEAT_ACK")
                        continue

                    if op in (OpCodeType.INVALIDATE_SESSION, OpCodeType.RECONNECT):
                        self.session_id = None
                        self.sequence = None

                        log.debug("INVALID_SESSION/RECONNECT")

                        if not data or op == OpCodeType.RECONNECT:
                            try:
                                await self.resume()
                            except Exception as exc:
                                log.error("Server declined to reconnect, closing.")
                                log.error(exc)
                                await self.session.close()
                        else:
                            self.closed = True

                else:
                    if event == "READY":
                        self.session_id = data["session_id"]
                        self.sequence = stream["s"]
                        self.dispatch.dispatch("on_ready")
                        log.debug(f"READY (SES_ID: {self.session_id}, SEQ_ID: {self.sequence})")
                    else:
                        log.debug(f"{event}: {data}")
                        self.dispatch.dispatch(f"on_{event.lower()}", data)
                    continue

    async def send(self, data: Union[str, dict]) -> None:
        packet: str = dumps(data).decode("utf-8") if isinstance(data, dict) else data
        await self.session.send_str(packet)
        log.debug(packet)

    async def identify(self) -> None:
        """Sends an ``IDENTIFY`` packet to the gateway."""
        payload: dict = {
            "op": OpCodeType.IDENTIFY,
            "d": {
                "token": self.req.token,
                "intents": self.intents,
                "properties": {
                    "$os": sys.platform,
                    "$browser": "discord-interactions",
                    "$device": "discord-interactions",
                },
            },
        }
        await self.send(payload)
        log.debug("IDENTIFY")

    async def resume(self) -> None:
        """Sends a ``RESUME`` packet to the gateway."""
        payload: dict = {
            "op": OpCodeType.RESUME,
            "d": {"token": self.req.token, "seq": self.sequence, "session_id": self.session_id},
        }
        await self.send(payload)
        log.debug("RESUME")

    async def heartbeat(self) -> None:
        """Sends a ``HEARTBEAT`` packet to the gateway."""
        payload: dict = {"op": OpCodeType.HEARTBEAT, "d": self.session_id}
        await self.send(payload)
        log.debug("HEARTBEAT")
