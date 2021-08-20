# Normal libraries
import sys, websockets
from asyncio import (
    AbstractEventLoop,
    Future,
    get_event_loop,
    new_event_loop,
    set_event_loop
)
from json import dumps, loads
import logging
from logging import basicConfig, getLogger, Logger
from threading import Event, _start_new_thread, Thread
from time import sleep
from typing import Any, Optional

# 3rd-party libraries
from .base import Data, Route
from .types.enums import OPCodes

basicConfig(level=logging.DEBUG)
log: Logger = getLogger("interactions.log")
token: str = "Mzc5MzQzMzIyNTQ1NzgyNzg0.WgiY_w.YSF9oEUMvDAOmycTkZBz3WE6c40"

class Heartbeat(Thread):
    """
    Object representing keeping a consistent gateway connection.
    
    :ivar websocket:
    :ivar interval:
    """
    __slots__ = "websocket", "interval"
    websocket: Any
    interval: float
    payload: dict

    def __init__(
        self,
        websocket: Any,
        interval: float
    ) -> None:
        """
        Instantiates the Heartbeat class.
        
        :param websocket: The WebSocket connection.
        :type websocket: WebSocket
        :param interval: The interval to periodically send heartbeats.
        :type interval: float
        :return: None
        """
        super().__init__()
        self.websocket = websocket
        self.interval = interval
        self.event = Event()

    async def run(
        self,
        interval: float,
        websocket: Any
    ) -> None:
        """
        Automatically send heartbeats to the gateway.

        .. note::

            Inherits the arguments from the class constructor.

        :return: None
        """
        while True:
            sleep(interval)
            await self.websocket.heartbeat()

    def stop(self) -> None:
        """
        Stop sending heartbeats to the gateway.

        :return: None
        """
        return self.event.set()

class WebSocket:
    """
    Object representing logic for connecting to the gateway.

    :ivar websocket:
    :ivar data:
    """
    __slots__ = (
        "session",
        "session_id",
        "heart",
        "sequence",
        "interval",
        "intents",
        "closed"
    )
    session: Any
    session_id: Optional[int]
    heart: Optional[Heartbeat]
    sequence: Optional[int]
    interval: Optional[int]
    intents: Optional[int]
    closed: bool

    def __init__(self) -> None:
        """
        Instantiates the WebSocket class.

        :return: None
        """
        self.closed = False

    async def connect(
        self,
        intents: Optional[int]=513,
        session_id: Optional[int]=None
    ) -> None:
        """
        Validates a connection to the WebSocket server.
        
        :param intents: The intents to pass for the application connection.
        :type intents: typing.Optional[int]
        :return: None
        """
        self.intents = intents
        self.session_id = session_id
        path: str = Route.GATEWAY.value + "&encoding=json"
        async with websockets.connect(path) as self.session:
            stream = await self.recv()
            fields: dict = {
                "op": stream.get("op"),
                "data": stream.get("d"),
                "seq": stream.get("s")
            }
            self.sequence: int = fields["seq"] if fields["seq"] is not None else "null"

            while not self.closed:
                if fields["op"] != OPCodes.DISPATCH:
                    if fields["op"] == OPCodes.HELLO:
                        if not self.session_id:
                            await self.identify()
                        else:
                            await self.resume()
                        self.interval: float = fields["data"]["heartbeat_interval"] / 1000
                        await self.heartbeat()
                        self.heart = Heartbeat(self, self.interval)
                        await _start_new_thread(self.heart.run, (self.interval, self.session))
                        self.heart.start()
                        return

                    if fields["op"] == OPCodes.HEARTBEAT:
                        if self.heart:
                            await self.heartbeat()
                        return

                    if fields["op"] == OPCodes.HEARTBEAT_ACK:
                        if self.heart:
                            log.info("The gateway has validated the client's heartbeat.")
                        return

                    if fields["op"] in (
                        OPCodes.INVALIDATE_SESSION,
                        OPCodes.RECONNECT
                    ):
                        self.session_id, self.sequence = None
                        if fields["data"] or fields["op"] == OPCodes.RECONNECT:
                            await self.session.close(code=1000)
                else:
                    log.debug("We've received a dispatch event.")
                    if stream.get("t") == "READY":
                        self.sequence = stream.get("s") or "null"
                        self.session_id = fields["data"]["session_id"]
                        log.info("The client has successfully connected to the gateway.")
                        return

    async def send(
        self,
        data: dict
    ) -> None:
        """
        Sends packets to the WebSocket server.

        :param data: The packet you want to send.
        :type data: dict
        :return: None
        """
        await self.session.send(dumps(data))
        return await self.recv()

    async def recv(self) -> None:
        """
        Receives packets returned back by the WebSocket server.
        
        :return: None
        """
        packet = await self.session.recv()
        response = loads(packet) if packet else None
        return response

    async def heartbeat(self) -> None:
        """
        Sends a HEARTBEAT packet to the gateway.

        :return: None
        """
        payload: dict = {
            "op": OPCodes.HEARTBEAT,
            "d": self.sequence
        }
        await self.send(payload)
        log.debug("Client is sending a heartbeat...")

    async def identify(self) -> None:
        """
        Sends an IDENTIFY packet to the gateway.

        :return: None
        """
        payload: dict = {
            "op": OPCodes.IDENTIFY,
            "d": {
                "token": token,
                "intents": self.intents,
                "properties": {
                    "$os": sys.platform,
                    "$browser": "discord-interactions",
                    "$device": "discord-interactions"
                }
            }
        }
        await self.send(payload)
        log.debug("The client has identified itself to the gateway.")

    async def resume(self) -> None:
        """
        Sends a RESUME packet to the gateway.

        :return: None
        """
        payload: dict = {
            "op": OPCodes.RESUME,
            "d": {
                "token": token,
                "seq": self.sequence,
                "session_id": self.session_id
            }
        }
        await self.send(payload)
        log.debug("The client has resumed their connection with the gateway.")

async def main():
    gateway = WebSocket()
    await gateway.connect()

get_event_loop().run_until_complete(main())