try:
    from orjson import dumps, loads
except ImportError:
    from json import dumps, loads

from asyncio import (
    FIRST_COMPLETED,
    Event,
    Lock,
    Task,
    TimeoutError,
    create_task,
    get_event_loop,
    get_running_loop,
    new_event_loop,
    wait,
    wait_for,
)
from sys import platform, version_info
from time import perf_counter
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Type, Union
from zlib import decompressobj

from aiohttp import ClientWebSocketResponse, WSMessage, WSMsgType

from ...base import __version__, get_logger
from ...client.enums import InteractionType, OptionType
from ...client.models import Option
from ...utils.missing import MISSING
from ..dispatch import Listener
from ..enums import OpCodeType
from ..error import LibraryException
from ..http.client import HTTPClient
from ..models.flags import Intents
from ..models.guild import Guild
from ..models.gw import GuildMember, GuildRole
from ..models.member import Member
from ..models.message import Message
from ..models.misc import Snowflake
from ..models.presence import ClientPresence
from ..models.role import Role
from .heartbeat import _Heartbeat
from .ratelimit import WSRateLimit

if TYPE_CHECKING:
    from ...client.context import _Context
    from ..cache import Storage
    from ..models.gw import GuildMembers

log = get_logger("gateway")

__all__ = ("WebSocketClient",)


class WebSocketClient:
    """
    A class representing the client's connection to the Gateway via. WebSocket.

    .. note ::
        The ``__heartbeat_event`` Event object is different from the one built in to the Heartbeater object.
        The latter is used to trace heartbeat acknowledgement.

    :ivar AbstractEventLoop _loop: The asynchronous event loop.
    :ivar Listener _dispatch: The built-in event dispatcher.
    :ivar WSRateLimit _ratelimiter: The websocket ratelimiter object.
    :ivar HTTPClient _http: The user-facing HTTP client.
    :ivar ClientWebSocketResponse _client: The WebSocket data of the connection.
    :ivar Event __closed: Whether the connection has been closed or not.
    :ivar dict _options: The connection options made during connection.
    :ivar Intents _intents: The gateway intents used for connection.
    :ivar dict _ready: The contents of the application returned when ready.
    :ivar _Heartbeat __heartbeater: The context state of a "heartbeat" made to the Gateway.
    :ivar Event __heartbeat_event: The state of the overall heartbeat process.
    :ivar Optional[List[Tuple[int]]] __shard: The shards used during connection.
    :ivar Optional[ClientPresence] __presence: The presence used in connection.
    :ivar Event ready: The ready state of the client as an ``asyncio.Event``.
    :ivar Task _task: The task containing the heartbeat manager process.
    :ivar bool __started: Whether the client has started.
    :ivar Optional[str] session_id: The ID of the ongoing session.
    :ivar Optional[int] sequence: The sequence identifier of the ongoing session.
    :ivar float _last_send: The latest time of the last send_packet function call since connection creation, in seconds.
    :ivar float _last_ack: The latest time of the last ``HEARTBEAT_ACK`` event since connection creation, in seconds.
    :ivar Optional[str] resume_url: The Websocket ratelimit URL for resuming connections, if any.
    :ivar Optional[str] ws_url: The Websocket URL for instantiating connections without resuming.
    :ivar Lock reconnect_lock: The lock used for reconnecting the client.
    :ivar Lock _closing_lock: The lock used for closing the client.
    :ivar Optional[Task] __stopping: The task containing stopping the client, if any.
    """

    __slots__ = (
        "_loop",
        "_dispatch",
        "_ratelimiter",
        "_http",
        "_client",
        "__closed",  # placeholder to work with variables atm. its event variant of "_closed"
        "_options",
        "_intents",
        "_ready",
        "__heartbeater",
        "__shard",
        "__presence",
        "_zlib",
        "_task",
        "__heartbeat_event",
        "__started",
        "session_id",
        "sequence",
        "ready",
        "_last_send",
        "_last_ack",
        "resume_url",
        "ws_url",
        "reconnect_lock",
        "_closing_lock",
        "__stopping",
    )

    def __init__(
        self,
        token: str,
        intents: Intents,
        session_id: Optional[str] = MISSING,
        sequence: Optional[int] = MISSING,
        shards: Optional[List[Tuple[int]]] = MISSING,
        presence: Optional[ClientPresence] = MISSING,
    ) -> None:
        """
        :param token: The token of the application for connecting to the Gateway.
        :type token: str
        :param intents: The Gateway intents of the application for event dispatch.
        :type intents: Intents
        :param session_id?: The ID of the session if trying to reconnect. Defaults to ``None``.
        :type session_id?: Optional[str]
        :param sequence?: The identifier sequence if trying to reconnect. Defaults to ``None``.
        :type sequence?: Optional[int]
        :param shards?: The list of shards for the application's initial connection, if provided. Defaults to ``None``.
        :type shards?: Optional[List[Tuple[int]]]
        :param presence?: The presence shown on an application once first connected. Defaults to ``None``.
        :type presence?: Optional[ClientPresence]
        """
        try:
            self._loop = get_event_loop() if version_info < (3, 10) else get_running_loop()
        except RuntimeError:
            self._loop = new_event_loop()
        self._dispatch: Listener = Listener()

        self._ratelimiter = (
            WSRateLimit(loop=self._loop) if version_info < (3, 10) else WSRateLimit()
        )
        self.__heartbeater: _Heartbeat = _Heartbeat(
            loop=self._loop if version_info < (3, 10) else None
        )
        self._http: HTTPClient = token

        self._client: Optional["ClientWebSocketResponse"] = None

        self.__closed: Event = Event(loop=self._loop) if version_info < (3, 10) else Event()
        self._options: dict = {
            "max_msg_size": 0,
            "timeout": 60,
            "autoclose": False,
            "compress": 0,
            "headers": {
                "User-Agent": f"DiscordBot (https://github.com/interactions-py/library {__version__}) "
            },
        }

        self._intents: Intents = intents
        self.__shard: Optional[List[Tuple[int]]] = None if shards is MISSING else shards
        self.__presence: Optional[ClientPresence] = None if presence is MISSING else presence

        self._task: Optional[Task] = None
        self.__heartbeat_event = Event(loop=self._loop) if version_info < (3, 10) else Event()
        self.__started: bool = False

        self.session_id: Optional[str] = None if session_id is MISSING else session_id
        self.sequence: Optional[str] = None if sequence is MISSING else sequence
        self.ready: Event = Event(loop=self._loop) if version_info < (3, 10) else Event()

        self._last_send: float = perf_counter()
        self._last_ack: float = perf_counter()

        self.resume_url: Optional[str] = None
        self.ws_url: Optional[str] = None
        self.reconnect_lock = Lock(loop=self._loop) if version_info < (3, 10) else Lock()

        self._closing_lock = Event(loop=self._loop) if version_info < (3, 10) else Event()

        self.__stopping: Optional[Task] = None

        self._zlib = decompressobj()

    @property
    def latency(self) -> float:
        """
        The latency of the connection, in seconds.
        """
        return self._last_ack - self._last_send

    async def run_heartbeat(self) -> None:
        """Controls the heartbeat manager. Do note that this shouldn't be executed by outside processes."""

        if self.__heartbeat_event.is_set():  # resets task of heartbeat event mgr loop
            # Because we're hardresetting the process every instance its called, also helps with recursion
            self.__heartbeat_event.clear()

        if not self.__heartbeater.event.is_set():  # resets task of heartbeat ack event
            self.__heartbeater.event.set()

        try:
            await self._manage_heartbeat()
        except Exception:
            self._closing_lock.set()
            log.exception("Heartbeater exception.")

    async def _manage_heartbeat(self) -> None:
        """Manages the heartbeat loop."""
        log.debug(f"Sending heartbeat every {self.__heartbeater.delay / 1000} seconds...")
        while not self.__heartbeat_event.is_set():

            log.debug("Sending heartbeat...")
            if not self.__heartbeater.event.is_set():
                log.debug("HEARTBEAT_ACK missing, reconnecting...")
                await self._reconnect(True)  # resume here.

            self.__heartbeater.event.clear()
            await self.__heartbeat()

            try:
                # wait for next iteration, accounting for latency
                await wait_for(
                    self.__heartbeat_event.wait(), timeout=self.__heartbeater.delay / 1000
                )
            except TimeoutError:
                continue  # Then we can check heartbeat ack this way and then like it autorestarts.
            else:
                return  # break loop because something went wrong.

    async def run(self) -> None:
        """
        Handles the client's connection with the Gateway.
        """

        if isinstance(self._http, str):
            self._http = HTTPClient(self._http)

        url = await self._http.get_gateway()
        self.ws_url = url
        self._client = await self._http._req._session.ws_connect(url, **self._options)

        data = await self.__receive_packet(True)  # First data is the hello packet.

        self.__heartbeater.delay = data["d"]["heartbeat_interval"]

        self._task = create_task(self.run_heartbeat())

        await self.__identify(self.__shard, self.__presence)

        self.__closed.set()
        self.__heartbeater.event.set()

        while True:
            if self.__stopping is None:
                self.__stopping = create_task(self._closing_lock.wait())
            _receive = create_task(self.__receive_packet())

            done, _ = await wait({self.__stopping, _receive}, return_when=FIRST_COMPLETED)
            # Using asyncio.wait to find which one reaches first, when its *closed* or when a message is
            # *received*

            if _receive in done:
                msg = await _receive
            else:
                await self.__stopping
                _receive.cancel()
                return

            if msg is not None:  # this can happen
                await self._handle_stream(msg)

    async def _handle_stream(self, stream: Dict[str, Any]):
        """
        Parses raw stream data recieved from the Gateway, including Gateway opcodes and events.

        .. note ::
            This should never be called directly.

        :param stream: The packet stream to handle.
        :type stream: Dict[str, Any]
        """
        op: Optional[int] = stream.get("op")
        event: Optional[str] = stream.get("t")
        data: Optional[Dict[str, Any]] = stream.get("d")

        seq: Optional[str] = stream.get("s")
        if seq:
            self.sequence = seq

        if op != OpCodeType.DISPATCH:
            log.debug(data)

            if op == OpCodeType.HEARTBEAT:
                await self.__heartbeat()
            if op == OpCodeType.HEARTBEAT_ACK:
                self._last_ack = perf_counter()
                log.debug("HEARTBEAT_ACK")
                self.__heartbeater.event.set()

            if op == OpCodeType.INVALIDATE_SESSION:
                log.debug("INVALID_SESSION")
                self.ready.clear()
                await self._reconnect(bool(data))

            if op == OpCodeType.RECONNECT:
                log.debug("RECONNECT")
                await self._reconnect(True)

        elif event == "RESUMED":
            log.debug(f"RESUMED (session_id: {self.session_id}, seq: {self.sequence})")
        elif event == "READY":
            self.ready.set()
            self._dispatch.dispatch("on_ready")
            self._ready = data
            self.session_id = data["session_id"]
            self.resume_url = data["resume_gateway_url"]
            if not self.__started:
                self.__started = True
                self._dispatch.dispatch("on_start")
            log.debug(f"READY (session_id: {self.session_id}, seq: {self.sequence})")
        else:
            log.debug(f"{event}: {str(data).encode('utf-8')}")
            self._dispatch_event(event, data)

    async def wait_until_ready(self) -> None:
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
        self._dispatch.dispatch("raw_socket_create", event, data)
        path: str = "interactions"
        path += ".models" if event == "INTERACTION_CREATE" else ".api.models"
        if event == "INTERACTION_CREATE":
            if data.get("type"):
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
                                (option["type"] if isinstance(option, dict) else option.type.value),
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
                    _name = f"autocomplete_{_context.data.name}"

                    if _context.data._json.get("options"):
                        for option in _context.data.options:
                            if isinstance(option, dict):
                                option = Option(**option)
                            if option.type not in (
                                OptionType.SUB_COMMAND,
                                OptionType.SUB_COMMAND_GROUP,
                            ):
                                if option.focused:
                                    __name, _value = self.__sub_command_context(option, _context)
                                    _name += f"_{__name}" if __name else ""
                                    if _value:
                                        __args.append(_value)
                                        break

                            elif option.type == OptionType.SUB_COMMAND:
                                for _option in option.options:
                                    if isinstance(_option, dict):
                                        _option = Option(**_option)
                                    if _option.focused:
                                        __name, _value = self.__sub_command_context(
                                            _option, _context
                                        )
                                        _name += f"_{__name}" if __name else ""
                                        if _value:
                                            __args.append(_value)
                                        break

                            elif option.type == OptionType.SUB_COMMAND_GROUP:
                                for _option in option.options:
                                    if isinstance(_option, dict):
                                        _option = Option(**_option)
                                    for __option in _option.options:
                                        if isinstance(__option, dict):
                                            __option = Option(**__option)
                                        if __option.focused:
                                            __name, _value = self.__sub_command_context(
                                                __option, _context
                                            )
                                            _name += f"_{__name}" if __name else ""
                                            if _value:
                                                __args.append(_value)
                                            break
                                    break

                    self._dispatch.dispatch("on_autocomplete", _context)
                elif data["type"] == InteractionType.MODAL_SUBMIT:
                    _name = f"modal_{_context.data.custom_id}"

                    if _context.data.components:
                        for component in _context.data.components:
                            if component.components:
                                __args.append([_value.value for _value in component.components][0])

                    self._dispatch.dispatch("on_modal", _context)

                self._dispatch.dispatch(_name, *__args, **__kwargs)
                self._dispatch.dispatch("on_interaction", _context)
                self._dispatch.dispatch("on_interaction_create", _context)
            else:
                log.warning(
                    "Context is being created for the interaction, but no type is specified. Skipping..."
                )
        elif event not in {"TYPING_START", "VOICE_STATE_UPDATE", "VOICE_SERVER_UPDATE"}:
            name: str = event.lower()
            try:
                data["_client"] = self._http

                _event_path: list = [section.capitalize() for section in name.split("_")]
                _name: str = _event_path[0] if len(_event_path) < 3 else "".join(_event_path[:-1])
                model = getattr(__import__(path), _name)
                obj = model(**data)

                guild_obj = guild_model = None
                if model is GuildRole:
                    guild_obj = Role(**role_data) if (role_data := data.get("role")) else None
                    guild_model = Role
                elif model is GuildMember:
                    guild_obj = Member(**data)
                    guild_model = Member

                _cache: "Storage" = self._http.cache[model]
                _guild_cache: "Storage" = self._http.cache[guild_model]

                ids = None
                id = self.__get_object_id(data, obj, model)
                if id is None:
                    ids = self.__get_object_ids(obj, model)

                if "_create" in name or "_add" in name:
                    self._dispatch.dispatch(f"on_{name}", obj)

                    if id:
                        _cache.merge(obj, id)
                        if guild_obj:
                            _guild_cache.add(guild_obj, id)

                    self.__modify_guild_cache(
                        name, data, guild_model or model, guild_obj or obj, id, ids
                    )

                elif "_update" in name:
                    self._dispatch.dispatch(f"on_raw_{name}", obj)

                    if not id and ids is None:
                        return self._dispatch.dispatch(f"on_{name}", obj)

                    self.__modify_guild_cache(
                        name, data, guild_model or model, guild_obj or obj, id, ids
                    )
                    if ids is not None:
                        # Not cached but it needed for guild_emojis_update and guild_stickers_update events
                        return self._dispatch.dispatch(f"on_{name}", obj)
                    if id is None:
                        return

                    if guild_obj:
                        old_guild_obj = _guild_cache.get(id)
                        if old_guild_obj:
                            old_guild_obj.update(**guild_obj._json)
                        else:
                            _guild_cache.add(guild_obj, id)

                    old_obj = _cache.get(id)
                    if old_obj:
                        before = model(**old_obj._json)
                        old_obj.update(**obj._json)
                    else:
                        before = None
                        old_obj = obj

                    _cache.add(old_obj, id)
                    self._dispatch.dispatch(
                        f"on_{name}", before, old_obj
                    )  # give previously stored and new one

                elif "_remove" in name or "_delete" in name:
                    self._dispatch.dispatch(
                        f"on_raw_{name}", obj
                    )  # Deprecated. Remove this in the future.

                    old_obj = None
                    if id:
                        _guild_cache.pop(id)
                        self.__modify_guild_cache(
                            name, data, guild_model or model, guild_obj or obj, id, ids
                        )
                        old_obj = _cache.pop(id)

                    elif ids is not None and "message" in name:
                        # currently only message has '_delete_bulk' event but ig better keep this condition for future.
                        _message_cache: "Storage" = self._http.cache[Message]
                        for message_id in ids:
                            _message_cache.pop(message_id)

                    self._dispatch.dispatch(f"on_{name}", old_obj or obj)

                elif "guild_members_chunk" in name:
                    self.__modify_guild_cache(name, data, model, obj, ids=ids)

                    _member_cache: "Storage" = self._http.cache[Member]
                    obj: GuildMembers
                    for member in obj.members:
                        member._guild_id = obj.guild_id
                        _member_cache.add(member, (obj.guild_id, member.id))

                    self._dispatch.dispatch(f"on_{name}", obj)

                else:
                    self._dispatch.dispatch(f"on_{name}", obj)

            except AttributeError as error:
                log.warning(f"An error occurred dispatching {name}: {error}")

    def __get_object_id(
        self, data: dict, obj: Any, model: type
    ) -> Optional[Union[Snowflake, Tuple[Snowflake, Snowflake]]]:
        """
        Gets an ID from object.

        :param data: The data for the event.
        :type data: dict
        :param obj: The object of the event.
        :type obj: Any
        :param model: The model of the event.
        :type model: type
        :return: Object ID
        :rtype: Optional[Union[Snowflake, Tuple[Snowflake, Snowflake]]]
        """
        if isinstance(obj, (Member, GuildMember)):
            id = (Snowflake(data["guild_id"]), obj.id)
        else:
            id = getattr(obj, "id", None)
        if id is not None:
            return id

        if model.__name__ == "GuildScheduledEventUser":
            id = obj.guild_scheduled_event_id
        elif model.__name__ == "Presence":
            id = obj.user.id
        elif model.__name__ in [
            "GuildBan",
            # Extend this for everything that starts with 'Guild' and should not be cached
        ]:
            id = None
        elif model.__name__.startswith("Guild"):
            model_name = model.__name__[5:].lower()
            if (_data := getattr(obj, model_name, None)) and not isinstance(_data, list):
                id = getattr(_data, "id") if not isinstance(_data, dict) else Snowflake(_data["id"])
            elif hasattr(obj, f"{model_name}_id"):
                id = getattr(obj, f"{model_name}_id", None)

        return id

    def __get_object_ids(self, obj: Any, model: type) -> Optional[List[Snowflake]]:
        """
        Gets a list of ids of object.

        :param obj: The object of the event.
        :type obj: Any
        :param model: The model of the event.
        :type model: type
        :return: Object IDs
        :rtype: Optional[Union[Snowflake, Tuple[Snowflake, Snowflake]]]
        """
        ids = getattr(obj, "ids", None)
        if ids is not None:
            return ids

        if model.__name__.startswith("Guild"):
            model_name = model.__name__[5:].lower()
            if (_data := getattr(obj, model_name, None)) is not None:
                ids = [
                    getattr(_obj, "id") if not isinstance(_obj, dict) else Snowflake(_obj["id"])
                    for _obj in _data
                ]

        return ids

    def __modify_guild_cache(
        self,
        name: str,
        data: dict,
        model: Any,
        obj: Any,
        id: Optional[Snowflake] = None,
        ids: Optional[List[Snowflake]] = None,
    ):
        """
        Modifies guild cache.

        :param event: The name of the event.
        :type event: str
        :param data: The data for the event.
        :type data: dict
        :param obj: The object of the event.
        :type obj: Any
        :param model: The model of the event.
        :type model: Any
        """
        if not (
            (guild_id := data.get("guild_id"))
            and not isinstance(obj, Guild)
            and "message" not in name
            and (id is not None or ids is not None)
            and (guild := self._http.cache[Guild].get(Snowflake(guild_id)))
        ):
            return

        attr: str = model.__name__.lower()

        if attr.startswith("guild"):
            attr = attr[5:]
        if attr == "threadmembers":  # TODO: Figure out why this here
            return
        if not attr.endswith("s"):
            attr = f"{attr}s"
        iterable = getattr(guild, attr, None)
        if iterable is not None and isinstance(iterable, list):
            if "_create" in name or "_add" in name:
                iterable.append(obj)
            elif id:
                _id = id[1] if isinstance(id, tuple) else id
                for index, __obj in enumerate(iterable):
                    if __obj.id == _id:
                        if "_remove" in name or "_delete" in name:
                            iterable.remove(__obj)

                        elif "_update" in name and hasattr(obj, "id"):
                            iterable[index] = obj
                        break
            elif ids is not None and (objs := getattr(obj, attr, None)) is not None:
                if "_update" in name:
                    iterable.clear()
                    iterable.extend(objs)
                elif "_chunk" in name:
                    for _obj in objs:
                        for index, __obj in enumerate(iterable):
                            if __obj.id == _obj.id:
                                iterable[index] = _obj
                                break
                        else:
                            iterable.append(_obj)

            setattr(guild, attr, iterable)

        self._http.cache[Guild].add(guild)

    def __contextualize(self, data: dict) -> "_Context":
        """
        Takes raw data given back from the Gateway
        and gives "context" based off of what it is.

        :param data: The data from the Gateway.
        :type data: dict
        :return: The context object.
        :rtype: Any
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

            data["_client"] = self._http
            context: Type["_Context"] = getattr(__import__("interactions.client.context"), _context)

            return context(**data)

    def __sub_command_context(
        self, data: Union[dict, Option], context: "_Context"
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

        elif _data.get("type") and _data["type"] == OptionType.SUB_COMMAND:
            # sub_command_groups must have options so there is no extra check needed for those
            __kwargs["sub_command"] = _data["name"]

        elif _data.get("value") is not None and _data.get("name") is not None:
            __kwargs[_data["name"]] = _data["value"]

        return __kwargs

    def __option_type_context(self, context: "_Context", type: int) -> dict:
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
            _roles = context.data.resolved.roles if context.data.resolved.roles is not None else {}
            _members = (
                context.data.resolved.members if context.guild_id else context.data.resolved.users
            )
            _resolved = {
                **(_members if _members is not None else {}),
                **_roles,
            }
        return _resolved

    async def _reconnect(self, to_resume: bool, code: Optional[int] = 1012) -> None:
        """
        Restarts the client's connection and heartbeat with the Gateway.
        """

        self.ready.clear()

        async with self.reconnect_lock:
            self.__closed.clear()

            if self._client is not None:
                await self._client.close(code=code)

            self._client = None

            self._zlib = decompressobj()

            # We need to check about existing heartbeater tasks for edge cases.

            if self._task:
                self._task.cancel()
                if self.__heartbeat_event.is_set():
                    self.__heartbeat_event.clear()  # Because we're hardresetting the process

            if not to_resume:
                url = self.ws_url if self.ws_url else await self._http.get_gateway()
            else:
                url = f"{self.resume_url}?v=10&encoding=json&compress=zlib-stream"

            self._client = await self._http._req._session.ws_connect(url, **self._options)

            data = await self.__receive_packet(True)  # First data is the hello packet.

            self.__heartbeater.delay = data["d"]["heartbeat_interval"]

            self._task = create_task(self.run_heartbeat())

            if not to_resume:
                await self.__identify(self.__shard, self.__presence)
            else:
                await self.__resume()

            self.__closed.set()
            self.__heartbeat_event.set()

    async def __receive_packet(self, ignore_lock: bool = False) -> Optional[Dict[str, Any]]:
        """
        Receives a stream of packets sent from the Gateway in an async process.

        :return: The packet stream.
        :rtype: Optional[Dict[str, Any]]
        """

        buffer = bytearray()

        while True:

            if not ignore_lock:
                # meaning if we're reconnecting or something because of tasks
                await self.__closed.wait()

            packet: WSMessage = await self._client.receive()

            if packet.type == WSMsgType.CLOSE:
                log.debug(f"Disconnecting from gateway = {packet.data}::{packet.extra}")

                if packet.data >= 4000:
                    # This means that the error code is 4000+, which may signify Discord-provided error codes.

                    raise LibraryException(packet.data)

                if ignore_lock:
                    raise LibraryException(
                        message="Discord unexpectedly wants to close the WS on receiving by force.",
                        severity=50,
                    )

                await self._reconnect(packet.data != 1000, packet.data)
                continue

            elif packet.type == WSMsgType.CLOSED:
                # We need to wait/reconnect depending about other event holders.

                if ignore_lock:
                    raise LibraryException(
                        message="Discord unexpectedly closed on receiving by force.", severity=50
                    )

                if not self.__closed.is_set():
                    await self.__closed.wait()

                    # Edge case on force reconnecting if we dont
                else:
                    await self._reconnect(True)

            elif packet.type == WSMsgType.CLOSING:

                if ignore_lock:
                    raise LibraryException(
                        message="Discord unexpectedly closing on receiving by force.", severity=50
                    )

                await self.__closed.wait()
                continue

            if packet.data is None:
                continue  # We just loop it over because it could just be processing something.

            if isinstance(packet.data, bytes):
                buffer.extend(packet.data)

                if len(packet.data) < 4 or packet.data[-4:] != b"\x00\x00\xff\xff":
                    # buffer isn't done we need to wait
                    continue

                msg = self._zlib.decompress(buffer)
                msg = msg.decode("utf-8")
            else:
                msg = packet.data

            try:
                _msg = loads(msg)
            except Exception as e:
                import traceback

                log.debug(
                    f'Error serialising message: {"".join(traceback.format_exception(type(e), e, e.__traceback__))}.'
                )
                # There's an edge case when the packet's None... or some other deserialisation error.
                # Instead of raising an exception, we just log it to debug, so it doesn't annoy end user's console logs.
                _msg = None

            return _msg

    async def _send_packet(self, data: Dict[str, Any]) -> None:
        """
        Sends a packet to the Gateway.

        :param data: The data to send to the Gateway.
        :type data: Dict[str, Any]
        """
        _data = dumps(data) if isinstance(data, dict) else data
        packet: str = _data.decode("utf-8") if isinstance(_data, bytes) else _data
        log.debug(packet)

        if data["op"] in {OpCodeType.IDENTIFY.value, OpCodeType.RESUME.value}:
            # This can't use the reconnect lock *because* its already referenced in
            # self._reconnect(), hence an infinite hang.

            if self._client is not None:
                self._last_send = perf_counter()

                await self._client.send_str(packet)
        else:
            async with self.reconnect_lock:  # needs to lock while it reconnects.

                if data["op"] != OpCodeType.HEARTBEAT.value:
                    # This is because the ratelimiter limits already accounts for this.
                    await self._ratelimiter.block()

                if self._client is not None:  # this mitigates against another edge case.
                    self._last_send = perf_counter()

                    await self._client.send_str(packet)

    async def __identify(
        self, shard: Optional[List[Tuple[int]]] = None, presence: Optional[ClientPresence] = None
    ) -> None:
        """
        Sends an ``IDENTIFY`` packet to the gateway.

        :param shard?: The shard ID to identify under.
        :type shard?: Optional[List[Tuple[int]]]
        :param presence?: The presence to change the bot to on identify.
        :type presence?: Optional[ClientPresence]
        """
        self.__shard = shard
        self.__presence = presence
        payload: dict = {
            "op": OpCodeType.IDENTIFY.value,
            "d": {
                "token": self._http.token,
                "intents": self._intents.value,
                "properties": {
                    "os": platform,
                    "browser": "interactions.py",
                    "device": "interactions.py",
                },
                "compress": True,
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
            "op": OpCodeType.RESUME.value,
            "d": {"token": self._http.token, "seq": self.sequence, "session_id": self.session_id},
        }
        log.debug(f"RESUMING: {payload}")
        await self._send_packet(payload)
        log.debug("RESUME")

    async def __heartbeat(self) -> None:
        """Sends a ``HEARTBEAT`` packet to the gateway."""
        payload: dict = {"op": OpCodeType.HEARTBEAT.value, "d": self.sequence}
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

    async def _update_presence(self, presence: ClientPresence) -> None:
        """
        Sends an ``UPDATE_PRESENCE`` packet to the gateway.

        .. note::
            There is a ratelimit to using this method (5 per minute).
            As there's no gateway ratelimiter yet, breaking this ratelimit
            will force your bot to disconnect.

        :param presence: The presence to change the bot to on identify.
        :type presence: ClientPresence
        """
        payload: dict = {"op": OpCodeType.PRESENCE.value, "d": presence._json}
        await self._send_packet(payload)
        log.debug(f"UPDATE_PRESENCE: {presence._json}")
        self.__presence = presence

    async def request_guild_members(
        self,
        guild_id: int,
        limit: int,
        query: Optional[str] = None,
        presences: Optional[bool] = None,
        user_ids: Optional[Union[int, List[int]]] = None,
        nonce: Optional[str] = None,
    ) -> None:
        """Sends an ``REQUEST_MEMBERS`` packet to the gateway.

        :param guild_id: ID of the guild to get members for.
        :type guild_id: int
        :param limit: Maximum number of members to send matching the 'query' parameter. Required when specifying 'query'.
        :type limit: int
        :param query: String that username starts with.
        :type query: Optional[str]
        :param presences: Used to specify if we want the presences of the matched members.
        :type presences: Optional[bool]
        :param user_ids: Used to specify which users you wish to fetch.
        :type user_ids: Optional[Union[int, List[int]]]
        :param nonce: Nonce to identify the Guild Members Chunk response.
        :type nonce: Optional[str]
        """
        _data: dict = {"guild_id": guild_id, "query": query or "", "limit": limit}
        if presences is not None:
            _data["presences"] = presences
        if user_ids is not None:
            _data["user_ids"] = user_ids
        if nonce is not None:
            _data["nonce"] = nonce
        payload: dict = {"op": OpCodeType.REQUEST_MEMBERS.value, "d": _data}

        await self._send_packet(payload)
        log.debug(f"REQUEST_MEMBERS: {payload}")

    async def close(self) -> None:
        """
        Closes the current connection.
        """
        if self._client:
            await self._client.close()
        self.__closed.set()
