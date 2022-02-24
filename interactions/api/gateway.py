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
from sys import platform, version_info
from time import perf_counter
from typing import Any, Dict, List, Optional, Tuple, Union

from aiohttp import WSMessage

from ..base import get_logger
from ..enums import InteractionType, OptionType
from ..models.command import Option
from .dispatch import Listener
from .enums import OpCodeType
from .error import GatewayException
from .http import HTTPClient
from .models.flags import Intents
from .models.misc import MISSING
from .models.presence import ClientPresence

log = get_logger("gateway")


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
        try:
            self.event = Event(loop=loop) if version_info < (3, 10) else Event()
        except TypeError:
            pass
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
    :ivar Optional[ClientPresence] __presence: The presence used in connection.
    :ivar Event ready: The ready state of the client as an ``asyncio.Event``.
    :ivar Task __task: The closing task for ending connections.
    :ivar Optional[str] session_id: The ID of the ongoing session.
    :ivar Optional[int] sequence: The sequence identifier of the ongoing session.
    :ivar float _last_send: The latest time of the last send_packet function call since connection creation, in seconds.
    :ivar float _last_ack: The latest time of the last ``HEARTBEAT_ACK`` event since connection creation, in seconds.
    :ivar float latency: The latency of the connection, in seconds.
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
        "_last_send",
        "_last_ack",
        "latency",
    )

    def __init__(
        self,
        token: str,
        intents: Intents,
        session_id: Optional[str] = MISSING,
        sequence: Optional[int] = MISSING,
    ) -> None:
        """
        :param token: The token of the application for connecting to the Gateway.
        :type token: str
        :param intents: The Gateway intents of the application for event dispatch.
        :type intents: Intents
        :param session_id?: The ID of the session if trying to reconnect. Defaults to ``None``.
        :type session_id: Optional[str]
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
            "max_msg_size": 1024**2,
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
        self.ready = Event(loop=self._loop) if version_info < (3, 10) else Event()

        self._last_send = perf_counter()
        self._last_ack = perf_counter()
        self.latency: float("nan")  # noqa: F821
        # self.latency has to be noqa, this is valid in python but not in Flake8.

    async def _manage_heartbeat(self) -> None:
        """Manages the heartbeat loop."""
        while True:
            if self._closed:
                await self.__restart()
            if self.__heartbeater.event.is_set():
                await self.__heartbeat()
                self.__heartbeater.event.clear()
                await sleep(self.__heartbeater.delay / 1000)
            else:
                log.debug("HEARTBEAT_ACK missing, reconnecting...")
                await self.__restart()
                break

    async def __restart(self):
        """Restart the client's connection and heartbeat with the Gateway."""
        if self.__task:
            self.__task: Task
            self.__task.cancel()
        self._client = None  # clear pending waits
        self.__heartbeater.event.clear()
        await self._establish_connection()

    async def _establish_connection(
        self,
        shard: Optional[List[Tuple[int]]] = MISSING,
        presence: Optional[ClientPresence] = MISSING,
    ) -> None:
        """
        Establishes a client connection with the Gateway.

        :param shard?: The shards to establish a connection with. Defaults to ``None``.
        :type shard: Optional[List[Tuple[int]]]
        :param presence: The presence to carry with. Defaults to ``None``.
        :type presence: Optional[ClientPresence]
        """
        self._client = None
        self.__heartbeater.delay = 0.0
        self._closed = False
        self._options["headers"] = {"User-Agent": self._http._req._headers["User-Agent"]}
        url = await self._http.get_gateway()

        async with self._http._req._session.ws_connect(url, **self._options) as self._client:
            self._closed = self._client.closed

            if self._closed:
                await self._establish_connection()

            while not self._closed:
                stream = await self.__receive_packet_stream

                if stream is None:
                    continue
                if self._client is None:
                    await self._establish_connection()
                    break

                if self._client.close_code in range(4010, 4014) or self._client.close_code == 4004:
                    raise GatewayException(self._client.close_code)

                await self._handle_connection(stream, shard, presence)

    async def _handle_connection(
        self,
        stream: Dict[str, Any],
        shard: Optional[List[Tuple[int]]] = MISSING,
        presence: Optional[ClientPresence] = MISSING,
    ) -> None:
        """
        Handles the client's connection with the Gateway.

        :param stream: The packet stream to handle.
        :type stream: Dict[str, Any]
        :param shard?: The shards to establish a connection with. Defaults to ``None``.
        :type shard: Optional[List[Tuple[int]]]
        :param presence: The presence to carry with. Defaults to ``None``.
        :type presence: Optional[ClientPresence]
        """
        op: Optional[int] = stream.get("op")
        event: Optional[str] = stream.get("t")
        data: Optional[Dict[str, Any]] = stream.get("d")

        if op != OpCodeType.DISPATCH:
            log.debug(data)

            if op == OpCodeType.HELLO:
                self.__heartbeater.delay = data["heartbeat_interval"]
                self.__heartbeater.event.set()

                if self.__task:
                    self.__task.cancel()  # so we can reduce redundant heartbeat bg tasks.

                self.__task = ensure_future(self._manage_heartbeat())

                if not self.session_id:
                    await self.__identify(shard, presence)
                else:
                    await self.__resume()
            if op == OpCodeType.HEARTBEAT:
                await self.__heartbeat()
            if op == OpCodeType.HEARTBEAT_ACK:
                self._last_ack = perf_counter()
                log.debug("HEARTBEAT_ACK")
                self.__heartbeater.event.set()
                self.latency = self._last_ack - self._last_send
            if op in (OpCodeType.INVALIDATE_SESSION, OpCodeType.RECONNECT):
                log.debug("INVALID_SESSION/RECONNECT")

                # if data and op != OpCodeType.RECONNECT:
                #    self.session_id = None
                #    self.sequence = None
                # self._closed = True

                if bool(data) is False and op == OpCodeType.INVALIDATE_SESSION:
                    self.session_id = None

                await self.__restart()
        elif event == "RESUMED":
            log.debug(f"RESUMED (session_id: {self.session_id}, seq: {self.sequence})")
        elif event == "READY":
            self._ready = data
            self.session_id = data["session_id"]
            self.sequence = stream["s"]
            self._dispatch.dispatch("on_ready")
            log.debug(f"READY (session_id: {self.session_id}, seq: {self.sequence})")
            self.ready.set()
        else:
            log.debug(f"{event}: {data}")
            self._dispatch_event(event, data)

    async def wait_until_ready(self):
        """Waits for the client to become ready according to the Gateway."""
        await self.ready.wait()

    def _dispatch_event(self, event: str, data: dict) -> None:
        """
        Dispatches an event from the Gateway.

        :param event: The name of the event.
        :type event: str
        :param data: The data for the event.
        :type data: dict
        """
        path: str = "interactions"
        path += ".models" if event == "INTERACTION_CREATE" else ".api.models"

        if event != "TYPING_START":
            if event != "INTERACTION_CREATE":
                name: str = event.lower()
                try:
                    _event_path: list = [section.capitalize() for section in name.split("_")]
                    _name: str = (
                        _event_path[0] if len(_event_path) < 3 else "".join(_event_path[:-1])
                    )
                    __obj: object = getattr(__import__(path), _name)

                    if name in {"_create", "_add"}:
                        data["_client"] = self._http

                    self._dispatch.dispatch(f"on_{name}", __obj(**data))  # noqa
                except AttributeError as error:
                    log.fatal(f"An error occured dispatching {name}: {error}")
            else:
                if not data.get("type"):
                    log.warning(
                        "Context is being created for the interaction, but no type is specified. Skipping..."
                    )
                else:
                    _context = self.__contextualize(data)
                    _name: str = ""
                    __args: list = [_context]
                    __kwargs: dict = {}

                    if data["type"] == InteractionType.APPLICATION_COMMAND:
                        _name = f"command_{_context.data.name}"

                        if _context.data._json.get("options"):
                            for option in _context.data.options:
                                _type = self.__option_type_context(
                                    _context,
                                    (
                                        option["type"]
                                        if isinstance(option, dict)
                                        else option.type.value
                                    ),
                                )
                                if _type:
                                    if isinstance(option, dict):
                                        _type[option["value"]]._client = self._http
                                        option.update({"value": _type[option["value"]]})
                                    else:
                                        _type[option.value]._client = self._http
                                        option._json.update({"value": _type[option.value]})
                                _option = self.__sub_command_context(option, _context)
                                __kwargs.update(_option)

                        self._dispatch.dispatch("on_command", _context)
                    elif data["type"] == InteractionType.MESSAGE_COMPONENT:
                        _name = f"component_{_context.data.custom_id}"

                        if _context.data._json.get("values"):
                            __args.append(_context.data.values)

                        self._dispatch.dispatch("on_component", _context)
                    elif data["type"] == InteractionType.APPLICATION_COMMAND_AUTOCOMPLETE:
                        _name = f"autocomplete_{_context.data.id}"

                        if _context.data._json.get("options"):
                            for option in _context.data.options:
                                __name, _value = self.__sub_command_context(option, _context)
                                _name += f"_{__name}" if __name else ""

                                if _value:
                                    __args.append(_value)

                        self._dispatch.dispatch("on_autocomplete", _context)
                    elif data["type"] == InteractionType.MODAL_SUBMIT:
                        _name = f"modal_{_context.data.custom_id}"

                        if _context.data._json.get("components"):
                            for component in _context.data.components:
                                if component.get("components"):
                                    __args.append(
                                        [_value["value"] for _value in component["components"]][0]
                                    )
                                else:
                                    __args.append(
                                        [_value.value for _value in component.components][0]
                                    )

                        self._dispatch.dispatch("on_modal", _context)

                    self._dispatch.dispatch(_name, *__args, **__kwargs)
                    self._dispatch.dispatch("on_interaction", _context)
                    self._dispatch.dispatch("on_interaction_create", _context)

        self._dispatch.dispatch("raw_socket_create", data)

    def __contextualize(self, data: dict) -> object:
        """
        Takes raw data given back from the Gateway
        and gives "context" based off of what it is.

        :param data: The data from the Gateway.
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

            data["client"] = self._http
            context: object = getattr(__import__("interactions.context"), _context)

            return context(**data)

    def __sub_command_context(
        self, data: Union[dict, Option], context: object
    ) -> Union[Tuple[str], dict]:
        """
        Checks if an application command schema has sub commands
        needed for argument collection.

        :param data: The data structure of the option.
        :type data: Union[dict, Option]
        :param context: The context to refer subcommands from.
        :type context: object
        :return: A dictionary of the collected options, if any.
        :rtype: Union[Tuple[str], dict]
        """
        __kwargs: dict = {}
        _data: dict = data._json if isinstance(data, Option) else data

        def _check_auto(option: dict) -> Optional[Tuple[str]]:
            return (option["name"], option["value"]) if option.get("focused") else None

        check = _check_auto(_data)

        if check:
            return check
        if _data.get("options"):
            if _data["type"] == OptionType.SUB_COMMAND:
                __kwargs["sub_command"] = _data["name"]

                for sub_option in _data["options"]:
                    _check = _check_auto(sub_option)
                    _type = self.__option_type_context(
                        context,
                        (
                            sub_option["type"]
                            if isinstance(sub_option, dict)
                            else sub_option.type.value
                        ),
                    )

                    if _type:
                        if isinstance(sub_option, dict):
                            _type[sub_option["value"]]._client = self._http
                            sub_option.update({"value": _type[sub_option["value"]]})
                        else:
                            _type[sub_option.value]._client = self._http
                            sub_option._json.update({"value": _type[sub_option.value]})
                    if _check:
                        return _check

                    __kwargs[sub_option["name"]] = sub_option["value"]
            elif _data["type"] == OptionType.SUB_COMMAND_GROUP:
                __kwargs["sub_command_group"] = _data["name"]
                for _group_option in _data["options"]:
                    _check_auto(_group_option)
                    __kwargs["sub_command"] = _group_option["name"]

                    for sub_option in _group_option["options"]:
                        _check = _check_auto(sub_option)
                        _type = self.__option_type_context(
                            context,
                            (
                                sub_option["type"]
                                if isinstance(sub_option, dict)
                                else sub_option.type.value
                            ),
                        )

                        if _type:
                            if isinstance(sub_option, dict):
                                _type[sub_option["value"]]._client = self._http
                                sub_option.update({"value": _type[sub_option["value"]]})
                            else:
                                _type[sub_option.value]._client = self._http
                                sub_option._json.update({"value": _type[sub_option.value]})
                        if _check:
                            return _check

                        __kwargs[sub_option["name"]] = sub_option["value"]
        elif _data.get("value") and _data.get("name"):
            __kwargs[_data["name"]] = _data["value"]

        return __kwargs

    def __option_type_context(self, context: object, type: int) -> dict:
        """
        Looks up the type of option respective to the existing
        option types.

        :param context: The context to refer types from.
        :type context: object
        :param type: The option type.
        :type type: int
        :return: The option type context.
        :rtype: dict
        """
        _resolved = {}
        if type == OptionType.USER.value:
            _resolved = (
                context.data.resolved.members if context.guild_id else context.data.resolved.users
            )
        elif type == OptionType.CHANNEL.value:
            _resolved = context.data.resolved.channels
        elif type == OptionType.ROLE.value:
            _resolved = context.data.resolved.roles
        elif type == OptionType.ATTACHMENT.value:
            _resolved = context.data.resolved.attachments
        elif type == OptionType.MENTIONABLE.value:
            _resolved = {
                **(
                    context.data.resolved.members
                    if context.guild_id
                    else context.data.resolved.users
                ),
                **context.data.resolved.roles,
            }
        return _resolved

    async def restart(self):
        await self.__restart()

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
        self._last_send = perf_counter()
        packet: str = dumps(data).decode("utf-8") if isinstance(data, dict) else data
        await self._client.send_str(packet)
        log.debug(packet)

    async def __identify(
        self, shard: Optional[List[Tuple[int]]] = None, presence: Optional[ClientPresence] = None
    ) -> None:
        """
        Sends an ``IDENTIFY`` packet to the gateway.

        :param shard?: The shard ID to identify under.
        :type shard: Optional[List[Tuple[int]]]
        :param presence?: The presence to change the bot to on identify.
        :type presence: Optional[ClientPresence]
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
        if isinstance(presence, ClientPresence):
            payload["d"]["presence"] = presence._json

        log.debug(f"IDENTIFYING: {payload}")
        await self._send_packet(payload)
        log.debug("IDENTIFY")

    async def __resume(self) -> None:
        """Sends a ``RESUME`` packet to the gateway."""
        payload: dict = {
            "op": OpCodeType.RESUME,
            "d": {"token": self._http.token, "seq": self.sequence, "session_id": self.session_id},
        }
        log.debug(f"RESUMING: {payload}")
        await self._send_packet(payload)
        log.debug("RESUME")

    async def __heartbeat(self) -> None:
        """Sends a ``HEARTBEAT`` packet to the gateway."""
        payload: dict = {"op": OpCodeType.HEARTBEAT, "d": self.sequence}
        await self._send_packet(payload)
        log.debug("HEARTBEAT")

    @property
    def shard(self) -> Optional[List[Tuple[int]]]:
        """Returns the current shard"""
        return self.__shard

    @property
    def presence(self) -> Optional[ClientPresence]:
        """Returns the current presence."""
        return self.__presence
