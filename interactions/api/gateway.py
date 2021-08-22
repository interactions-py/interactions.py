# Normal libraries
import traceback
from asyncio.events import AbstractEventLoop, get_event_loop
from aiohttp import ClientSession, ClientWebSocketResponse
from asyncio import (
    get_event_loop,
    run_coroutine_threadsafe,
    set_event_loop
)
from concurrent.futures import _base
from orjson import dumps, loads
from logging import DEBUG, basicConfig, Logger, getLogger
from random import random
from threading import Event, Thread
from typing import Any, Optional, Union
import sys

# 3rd-party libraries
from .base import Data, Route
from .error import GatewayException
from .types.enums import OPCodes

basicConfig(level=DEBUG)
log: Logger = getLogger(Data.LOGGER.value)
event_loop: AbstractEventLoop = get_event_loop()


class Heartbeat(Thread):
    """
    The heartbeat class for the gateway.

    :ivar websocket: The WebSocket connection.
    :ivar interval: The heartbeat interval.
    :ivar event: The threading event.
    """
    __slots__ = "websocket", "interval", "event"
    websocket: Any
    interval: Union[int, float]
    event: Event

    def __init__(
            self,
            websocket: Any,
            interval: Union[int, float]
    ) -> None:
        """
        Object representing keeping a consistent connection to the gateway.

        :param websocket: The WebSocket connection to use to send heartbeats.
        :type websocket: typing.Any
        :param interval: The interval/rate heartbeats are sent at.
        :type interval: typing.Union[int, float]
        :return: None
        """
        super().__init__()
        self.websocket = websocket
        self.interval = (interval / 1000)
        self.event = Event()

    def run(self) -> None:
        """Automatically begin sending heartbeats to the gateway."""
        while not self.event.wait(self.interval - random()):
            coro = run_coroutine_threadsafe(
                coro=self.websocket.heartbeat(),
                loop=self.websocket.loop
            )
            while True:
                try:
                    coro.result(timeout=10)
                    break
                except _base.TimeoutError:
                    log.debug("The heartbeat took too long to send.")
                    log.error("The client was unable to send a heartbeat, closing the connection.")
                    self.stop()

    def stop(self) -> None:
        """Stops sending heartbeats to the gateway."""
        return self.event.set()


class WebSocket:
    """
    The websocket class for the gateway.

    :ivar session: The current asynchronous client connection.
    :ivar websock: The current websocket connection.
    :ivar token: The token used for identifying.
    :ivar intents: The intents used for identifying.
    :ivar session_id: The current session ID.
    :ivar sequence: The current sequence.
    :ivar closed: The current connection state.
    """
    __slots__ = (
        "session",
        "websock",
        "loop",
        "token",
        "intents",
        "session_id",
        "sequence",
        "keep_alive",
        "closed"
    )
    session: ClientSession
    websock: ClientWebSocketResponse
    loop: Optional[AbstractEventLoop]
    token: str
    intents: Optional[int]
    session_id: Optional[int]
    sequence: Optional[int]
    keep_alive: Optional[Heartbeat]
    closed: bool

    def __init__(
            self,
            token: str,
            intents: Optional[int] = 513,
            loop: Optional[AbstractEventLoop] = event_loop
    ) -> None:
        """
        Object representing how/the connection to the gateway.

        :param token: The token to use for identifying.
        :type token: str
        :param intents: The intents you're accessing. Required as of v8
        :type intents: typing.Optional[int]
        :return: None
        """
        self.loop = loop
        self.token = token
        self.intents = intents
        self.session_id = None
        self.sequence = None
        self.keep_alive = None
        self.closed = False

        set_event_loop(self.loop)

    async def recv(self) -> None:
        """Receives packets sent from the gateway."""
        packet = await self.websock.receive()
        return loads(packet.data) if packet and isinstance(packet.data, (bytearray, bytes, memoryview, str)) else None


    async def connect(
            self,
            session_id: Optional[int] = None,
            sequence: Optional[int] = None
    ) -> None:
        """
        Establishes a connection to the gateway.

        :param session_id: The session ID if you're trying to resume a connection. Defaults to ``None``.
        :type session_id: typing.Optional[int]
        :param sequence: The sequence if you're trying to resume a connection. Defaults to ``None``.
        :type sequence: typing.Optional[int]
        :return: None
        """

        async with ClientSession() as self.session:
            async with self.session.ws_connect(Route.GATEWAY.value + "&encoding=json") as self.websock:
                while not self.closed:
                    stream = await self.recv()

                    if self.websock.close_code:
                        code = self.websock.close_code  # Gateway close code.
                        # Since it is an error code...
                        raise GatewayException(code)

                    if stream is None:  # If its not a string, "Interrupt" like system
                        continue
                    op: Optional[int] = stream.get("op")
                    data: Optional[dict] = stream.get("d")
                    event: Optional[str] = stream.get("t")
                    self.sequence = stream.get("s")

                    if op != OPCodes.DISPATCH:
                        if op == OPCodes.HELLO:
                            if not self.session_id:
                                await self.identify()
                            else:
                                await self.resume()
                            interval: int = data["heartbeat_interval"]
                            self.keep_alive = Heartbeat(self, interval)
                            await self.heartbeat()
                            self.keep_alive.start()
                            continue
                        if op == OPCodes.HEARTBEAT:
                            if self.keep_alive:
                                await self.heartbeat()
                            continue
                        if op == OPCodes.HEARTBEAT_ACK:
                            if self.keep_alive:
                                log.debug("The gateway has validated the client's heartbeat.")
                            continue
                        if op in (
                                OPCodes.INVALIDATE_SESSION,
                                OPCodes.RECONNECT
                        ):
                            self.session_id = None
                            self.sequence = None
                            self.closed = True
                            if data or op == OPCodes.RECONNECT:
                                try:
                                    log.warning(
                                        "The websocket connection has disconnected, attempting to reconnect.")
                                    await self.resume()
                                except:
                                    log.error(
                                        "The websocket connection was disconnected, we're closing instead of reconnecting.")
                                    await self.websock.close()
                    else:
                        if event == "READY":
                            log.info("The client has successfully connected to the gateway.")
                        else:
                            _dispatch = await self.dispatch(event, data)  # which dispatches based off the "stream.get(t)"
                        continue


    @staticmethod
    async def dispatch(
            name: str,
            data: dict
    ) -> dict:
        """
        Returns the last dispatched event.

        :param name: The name of the gateway event.
        :type name: str
        :param data: The packet data from the event.
        :type data: dict
        :return: dict
        """
        return {"name": name, "data": data}

    async def send(
            self,
            data: Union[str, dict]
    ) -> None:
        """
        Sends a data packet to the gateway.

        :param data: The data to send in the form of a packet.
        :type data: typing.Union[str, dict]
        :return: None
        """
        packet: str = dumps(data).decode("utf-8") if isinstance(data, dict) else data
        await self.websock.send_str(packet)

    async def identify(self) -> None:
        """Sends an IDENTIFY packet to the gateway."""
        payload: dict = {
            "op": OPCodes.IDENTIFY,
            "d": {
                "token": self.token,
                "intents": self.intents,
                "properties": {
                    "$os": sys.platform,
                    "$browser": "discord-interactions",
                    "$device": "discord-interactions"
                }
            }
        }
        await self.send(payload)
        log.debug("The client has sent an IDENTIFY packet to the gateway.")

    async def resume(self) -> None:
        """Sends a RESUME packet to the gateway."""
        payload: dict = {
            "op": OPCodes.RESUME,
            "d": {
                "token": self.token,
                "seq": self.sequence,
                "session_id": self.session_id
            }
        }
        await self.send(payload)
        log.debug("The client has sent a RESUME packet to the gateway.")

    async def heartbeat(self) -> None:
        """Sends a HEARTBEAT packet to the gateway."""
        payload: dict = {
            "op": OPCodes.HEARTBEAT,
            "d": self.session_id
        }
        await self.send(payload)
        log.debug("The client has sent a HEARTBEAT packet to the gateway.")
