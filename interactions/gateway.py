# Normal libraries
import websockets
from asyncio import sleep
from json import dumps, loads
from logging import Logger, getLogger
from threading import _start_new_thread
from time import sleep
from typing import Any, Coroutine, Optional

# 3rd-party libraries
from .base import Data, Route
from .types.enums import WebSocketOPCodes

log: Logger = getLogger(Data.LOGGER)

class Gateway(websockets.client.WebSocketClientProtocol):
    """
    Object representing a connection to the gateway.

    Discord's standard process for establishing a WebSocket
    connection to their Gateway is actually relatively straightforward
    once you can wrap your head around the interesting way that they
    chose to document it all. The process acts like a tree:

    CONNECT TO WEBSOCKET SERVER
    |- OPCODE 10/HELLO
       |- IDENTIFY
          |- RESUME
             |- HEARTBEAT
             |- OPCODE 11 / HEARTBEAT_ACK

    :ivar path:
    :ivar websocket:
    :ivar data:
    :ivar token:
    :ivar session_id:
    """
    __slots__ = (
        "path",
        "websocket",
        "data",
        "token",
        "session_id"
    )
    path: str
    websocket: Any
    data: Optional[dict]
    token: str
    session_id: Optional[int]

    async def __init__(
        self,
        token: str
    ) -> None:
        """
        Instantiates the WebSocket class.
        
        :param token: The token to use to connect to the gateway.
        :type token: str
        :return: None
        """
        self.path = (Route.GATEWAY, "&encoding=json")
        self.websocket = None
        self.data = None
        self.token = token
        self.session_id = None

        await self.connect()

    async def send(
        self,
        json: dict
    ) -> Optional[dict]:
        """
        Sends information to the WebSocket connection.
        
        :param json: A dictionary/serialized JSON table to send.
        :type json: dict
        :return: typing.Optional[dict]
        """
        await super().send(dumps(json))
        return await self.recv()

    async def recv(self) -> Optional[dict]:
        """
        Receives information from the WebSocket connection.
        
        :return: typing.Optional[dict]
        """
        response = await super().recv()
        self.data = loads(response) if response else None
        return self.data

    async def heartbeat(
        self,
        interval: Optional[int]=0
    ) -> None:
        """
        Sends a HEARTBEAT packet to keep the connection validated.

        :param interval: An offset for how periodic the heartbeat should be sent. Defaults to ``0``.
        :type interval: typing.Optional[int]
        :return: None
        """
        payload: dict = {
            "op": WebSocketOPCodes.HEARTBEAT,
            "d": "null"
        }
        log.info("Beginning to send a heartbeat.")
        while True:
            try:
                sleep(interval)
                await self.send(payload)

                if self.data["op"] is WebSocketOPCodes.HEARTBEAT_ACK:
                    log.info("Heartbeat sent.")
                    continue
                else:
                    log.debug("The heartbeat was not acknowledged by the gateway.")
                    await self.resume()
            except TimeoutError:
                log.error("Heartbeat could not be sent, closing the gateway connection.")
                break

    async def identify(self) -> Coroutine:
        """
        Sends an IDENTIFY packet for acknowledging the connection.

        :return: typing.Coroutine
        """
        payload: dict = {
            "op": WebSocketOPCodes.IDENTIFY,
            "d": {
                "token": self.token,
                "properties": {
                    "$os": "windows",
                    "$browser": "chrome",
                    "$device": "pc"
                }
            }
        }
        return await self.send(payload)

    async def resume(self) -> Coroutine:
        """
        Sends a RESUME packet to keep listening for socket events.
        
        :return: typing.Coroutine
        """
        payload: dict = {
            "op": WebSocketOPCodes.RESUME,
            "d": {
                "token": self.token,
                "session_id": self.session_id
            }
        }
        return self.send(payload)

    async def connect(self) -> None:
        """
        Makes a connection to the Discord Gateway.
        
        :return: None
        """
        async with websockets.client.Connect(self.path) as self.websocket:
            if self.data["op"] is WebSocketOPCodes.HELLO:
                try:
                    identify: Coroutine = await self.identify()
                    if identify:
                        interval: int = self.data["d"]["heartbeat_interval"] / 1000
                        heartbeat = await self.heartbeat(interval)
                        _start_new_thread(heartbeat, (interval, self.websocket))

                        await self.resume()
                except:
                    log.error("Could not identify the connection to the gateway.")
            else:
                log.error("The gateway did not say hello back to us.")