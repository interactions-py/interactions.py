import sys
from asyncio import get_event_loop, run_coroutine_threadsafe
from json import dumps
from logging import Logger, StreamHandler, basicConfig, getLogger
from random import random
from threading import Event, Thread
from typing import Any, List, Optional, Union

from orjson import dumps as ordumps
from orjson import loads

from interactions.api.models.gw import Presence
from interactions.enums import InteractionType, OptionType

from ..base import CustomFormatter, Data
from .dispatch import Listener
from .enums import OpCodeType
from .error import GatewayException
from .http import HTTPClient
from .models.intents import Intents

basicConfig(level=Data.LOGGER)
log: Logger = getLogger("gateway")
stream: StreamHandler = StreamHandler()
stream.setLevel(Data.LOGGER)
stream.setFormatter(CustomFormatter())
log.addHandler(stream)

__all__ = ("Heartbeat", "WebSocket")


class Heartbeat(Thread):
    """
    A class representing a consistent heartbeat connection with the gateway.

    :ivar WebSocket ws: The WebSocket class to infer on.
    :ivar Union[int, float] interval: The heartbeat interval determined by the gateway.
    :ivar Event event: The multi-threading event.
    """

    __slots__ = ("ws", "interval", "event")

    def __init__(self, ws: Any, interval: int) -> None:
        """
        :param ws: The WebSocket inference to run the coroutine off of.
        :type ws: Any
        :param interval: The interval to periodically send events.
        :type interval: int
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
                        break
            except:  # noqa
                break

    def stop(self) -> None:
        """Stops the heartbeat connection."""
        self.event.set()


class WebSocket:
    """
    A class representing a websocket connection with the gateway.

    :ivar Intents intents: An instance of :class:`interactions.api.models.Intents`.
    :ivar AbstractEventLoop loop: The coroutine event loop established on.
    :ivar Request req: An instance of :class:`interactions.api.http.Request`.
    :ivar Listener dispatch: An instance of :class:`interactions.api.dispatch.Listener`.
    :ivar Any session: The current client session.
    :ivar int session_id: The current ID of the gateway session.
    :ivar int sequence: The current sequence of the gateway connection.
    :ivar Heartbeat keep_alive: An instance of :class:`interactions.api.gateway.Heartbeat`.
    :ivar bool closed: The current connection state.
    :ivar HTTPClient http: The internal HTTP client used to connect to the gateway.
    :ivar dict options: The websocket connection options.
    """

    __slots__ = (
        "intents",
        "loop",
        "dispatch",
        "session",
        "session_id",
        "sequence",
        "keep_alive",
        "closed",
        "http",
        "options",
    )

    def __init__(
        self,
        intents: Intents,
        session_id: Optional[int] = None,
        sequence: Optional[int] = None,
    ) -> None:
        """
        :param intents: The intents used for identifying the connection.
        :type intents: Intents
        :param session_id?: The session ID if you're trying to resume a connection. Defaults to ``None``.
        :type session_id: Optional[int]
        :param sequence?: The sequence if you're trying to resume a connection. Defaults to ``None``.
        :type sequence: Optional[int]
        """
        self.intents = intents
        self.loop = get_event_loop()
        self.dispatch = Listener()
        self.session = None
        self.session_id = session_id
        self.sequence = sequence

        self.keep_alive = None
        self.closed = False
        self.http = None
        self.options: dict = {
            "max_msg_size": 1024 ** 2,
            "timeout": 60,
            "autoclose": False,
            "compress": 0,
        }

    async def recv(self) -> Optional[Any]:
        """Receives packets sent from the gateway."""
        packet = await self.session.receive()
        return (
            loads(packet.data)
            if packet and isinstance(packet.data, (bytearray, bytes, memoryview, str))
            else None
        )

    async def connect(self, token: str, shard: Optional[List[int]] = None) -> None:
        """
        Establishes a connection to the gateway.

        :param token: The token to use for identifying.
        :type token: str
        :param shard?: The shard ID to identify under.
        :type shard: Optional[int]
        """
        self.http = HTTPClient(token)
        self.options["headers"] = {"User-Agent": self.http.req.headers["User-Agent"]}
        url = await self.http.get_gateway()

        async with self.http._req.session.ws_connect(url, **self.options) as self.session:
            while not self.closed:
                stream = await self.recv()

                if stream is None:
                    continue

                if self.session.close_code:
                    code = self.session.close_code
                    raise GatewayException(code)

                await self.handle_connection(stream, shard)

    async def handle_connection(self, stream: dict, shard: Optional[List[int]] = None) -> None:
        """
        Handles the connection to the gateway.

        :param stream: The data stream from the gateway.
        :type stream: dict
        :param shard?: The shard ID to identify under.
        :type shard: Optional[int]
        """
        op: Optional[int] = stream.get("op")
        event: Optional[str] = stream.get("t")
        data: Optional[dict] = stream.get("d")
        self.sequence = stream.get("s")

        if op != OpCodeType.DISPATCH:
            log.debug(data)

            if op == OpCodeType.HELLO:
                if not self.session_id:
                    await self.identify(shard)
                else:
                    await self.resume()

                heartbeat_interval = data["heartbeat_interval"]
                self.keep_alive = Heartbeat(self, heartbeat_interval)

                await self.heartbeat()
                self.keep_alive.start()

            if op == OpCodeType.HEARTBEAT:
                if self.keep_alive:
                    await self.heartbeat()

            if op == OpCodeType.HEARTBEAT_ACK:
                if self.keep_alive:
                    log.debug("HEARTBEAT_ACK")

            if op in (OpCodeType.INVALIDATE_SESSION, OpCodeType.RECONNECT):
                log.debug("INVALID_SESSION/RECONNECT")
                if not data or op == OpCodeType.RECONNECT:
                    try:
                        await self.resume()
                    except Exception as exc:
                        log.error("Server declined to reconnect, closing.")
                        log.error(exc)
                        await self.session.close()
                else:
                    self.session_id = None
                    self.sequence = None
                    self.closed = True
        else:
            if event == "READY":
                self.session_id = data["session_id"]
                self.sequence = stream["s"]
                self.dispatch.dispatch("on_ready")
                log.debug(f"READY (SES_ID: {self.session_id}, SEQ_ID: {self.sequence})")
            else:
                log.debug(f"{event}: {dumps(data, indent=4, sort_keys=True)}")
                self.handle_dispatch(event, data)

    def handle_dispatch(self, event: str, data: dict) -> None:
        """
        Handles the dispatched event data from a gateway event.

        :param event: The name of the event.
        :type event: str
        :param data: The data of the event.
        :type data: dict
        """
        if event != "TYPING_START":
            name: str = event.lower()
            path: str = "interactions"
            path += ".models" if event == "INTERACTION_CREATE" else ".api.models"

            if event != "INTERACTION_CREATE" and "VOICE" not in event:
                try:
                    _name: str = [piece for piece in name.split("_")]
                    _name = (
                        _name[0].capitalize()
                        if len(_name) < 3
                        else "".join(piece.capitalize() for piece in _name[:-1])
                    )
                    log.debug(f"Dispatching object {_name} from event {name}")
                    obj: object = getattr(
                        __import__(path),
                        _name,
                    )
                    self.dispatch.dispatch(f"on_{_name}", obj(**data))  # noqa
                except AttributeError as error:  # noqa
                    log.fatal(f"You're missing a data model for the event {name}: {error}")
            else:
                context = self.contextualize(data)
                _name: str
                _args: list = [context]

                if data["type"] == InteractionType.APPLICATION_COMMAND:
                    print(context.data)
                    _name = context.data.name
                    if hasattr(context.data, "options"):
                        if (
                            context.data.options
                        ):  # because of the Mixin, the above conditional never misses. nonechecking
                            for option in context.data.options:
                                if option["type"] in (
                                    OptionType.SUB_COMMAND,
                                    OptionType.SUB_COMMAND_GROUP,
                                ):
                                    pass
                                else:
                                    _args.append(option["value"])
                elif data["type"] == InteractionType.MESSAGE_COMPONENT:
                    _name = context.data.custom_id
                elif data["type"] == InteractionType.APPLICATION_COMMAND_AUTOCOMPLETE:
                    _name = f"autocomplete_{context.data.options[0]['name']}"
                elif data["type"] == InteractionType.MODAL_SUBMIT:
                    _name = f"modal_{context.data.custom_id}"

                self.dispatch.dispatch(_name, *_args)

            self.dispatch.dispatch("raw_socket_create", data)

    def contextualize(self, data: dict) -> object:
        """
        Takes raw data given back from the gateway
        and gives "context" based off of what it is.

        :param data: The data from the gateway.
        :type data: dict
        :return: The context object.
        :rtype: object
        """
        if data["type"] != InteractionType.PING:
            _context: str = ""

            if data["type"] in (
                InteractionType.APPLICATION_COMMAND,
                InteractionType.APPLICATION_COMMAND_AUTOCOMPLETE,
                InteractionType.MODAL_SUBMIT,
            ):
                _context = "CommandContext"
            elif data["type"] == InteractionType.MESSAGE_COMPONENT:
                _context = "ComponentContext"

            context: object = getattr(__import__("interactions.context"), _context)
            return context(**data)

    async def send(self, data: Union[str, dict]) -> None:
        packet: str = ordumps(data).decode("utf-8") if isinstance(data, dict) else data
        await self.session.send_str(packet)
        log.debug(packet)

    async def identify(
        self, shard: Optional[List[int]] = None, presence: Optional[Presence] = None
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
                "token": self.http.token,
                "intents": self.intents,
                "properties": {
                    "$os": sys.platform,
                    "$browser": "discord-interactions",
                    "$device": "discord-interactions",
                },
            },
        }

        if shard:
            payload["d"]["shard"] = shard
        if presence:
            payload["d"]["presence"] = presence._json

        await self.send(payload)
        log.debug("IDENTIFY")

    async def resume(self) -> None:
        """Sends a ``RESUME`` packet to the gateway."""
        payload: dict = {
            "op": OpCodeType.RESUME,
            "d": {"token": self.http.token, "seq": self.sequence, "session_id": self.session_id},
        }
        await self.send(payload)
        log.debug("RESUME")

    async def heartbeat(self) -> None:
        """Sends a ``HEARTBEAT`` packet to the gateway."""
        payload: dict = {"op": OpCodeType.HEARTBEAT, "d": self.session_id}
        await self.send(payload)
        log.debug("HEARTBEAT")
