import contextlib
import logging
import re
import sys
from asyncio import AbstractEventLoop, CancelledError, get_event_loop, iscoroutinefunction
from functools import wraps
from importlib import import_module
from importlib.util import resolve_name
from inspect import getmembers
from types import ModuleType
from typing import Any, Callable, Coroutine, Dict, List, Optional, Tuple, Union

from ..api import WebSocketClient as WSClient
from ..api.error import LibraryException
from ..api.http.client import HTTPClient
from ..api.models.flags import Intents, Permissions
from ..api.models.guild import Guild
from ..api.models.misc import Image, Snowflake
from ..api.models.presence import ClientPresence
from ..api.models.team import Application
from ..api.models.user import User
from ..base import get_logger
from ..utils.attrs_utils import convert_list
from ..utils.missing import MISSING
from .decor import component as _component
from .enums import ApplicationCommandType, Locale, OptionType
from .models.command import ApplicationCommand, Choice, Command, Option
from .models.component import Button, Modal, SelectMenu

log: logging.Logger = get_logger("client")

__all__ = (
    "Client",
    "Extension",
    "extension_listener",
    "extension_command",
    "extension_component",
    "extension_modal",
    "extension_autocomplete",
    "extension_user_command",
    "extension_message_command",
)


class Client:
    """
    A class representing the client connection to Discord's gateway and API via. WebSocket and HTTP.

    :param token: The token of the application for authentication and connection.
    :type token: str
    :param intents?: Allows specific control of permissions the application has when connected. In order to use multiple intents, the | operator is recommended. Defaults to ``Intents.DEFAULT``.
    :type intents?: Optional[Intents]
    :param shards?: Dictates and controls the shards that the application connects under.
    :type shards?: Optional[List[Tuple[int]]]
    :param presence?: Sets an RPC-like presence on the application when connected to the Gateway.
    :type presence?: Optional[ClientPresence]
    :param default_scope?: Sets the default scope of all commands.
    :type default_scope?: Optional[Union[int, Guild, List[int], List[Guild]]]
    :param disable_sync?: Controls whether synchronization in the user-facing API should be automatic or not.
    :type disable_sync?: Optional[bool]
    :param logging?: Set to ``True`` to enable debug logging or set to a log level to use a specific level
    :type logging?: Optional[Union[bool, logging.DEBUG, logging.INFO, logging.NOTSET, logging.WARNING, logging.ERROR, logging.CRITICAL]]

    :ivar AbstractEventLoop _loop: The asynchronous event loop of the client.
    :ivar HTTPClient _http: The user-facing HTTP connection to the Web API, as its own separate client.
    :ivar WebSocketClient _websocket: An object-orientation of a websocket server connection to the Gateway.
    :ivar Intents _intents: The Gateway intents of the application. Defaults to ``Intents.DEFAULT``.
    :ivar Optional[List[Tuple[int]]] _shard: The list of bucketed shards for the application's connection.
    :ivar Optional[ClientPresence] _presence: The RPC-like presence shown on an application once connected.
    :ivar str _token: The token of the application used for authentication when connecting.
    :ivar Optional[Dict[str, ModuleType]] _extensions: The "extensions" or cog equivalence registered to the main client.
    :ivar Application me?: The application representation of the client.
    """

    def __init__(
        self,
        token: str,
        **kwargs,
    ) -> None:
        self._loop: AbstractEventLoop = get_event_loop()
        self._http: HTTPClient = token
        self._intents: Intents = kwargs.get("intents", Intents.DEFAULT)
        self._shards: List[Tuple[int]] = kwargs.get("shards", [])
        self._commands: List[Command] = []
        self._default_scope = kwargs.get("default_scope")
        self._presence = kwargs.get("presence")
        self._websocket: WSClient = WSClient(
            token=token, intents=self._intents, shards=self._shards, presence=self._presence
        )
        self._token = token
        self._extensions = {}
        self._scopes = set([])
        self.__command_coroutines = []
        self.__global_commands = {}
        self.__guild_commands = {}

        self.me: Optional[Application] = None
        self.__id_autocomplete = {}
        if self._default_scope:
            if not isinstance(self._default_scope, list):
                self._default_scope = [self._default_scope]
            if any(isinstance(scope, Guild) for scope in self._default_scope):
                self._default_scope = [
                    (scope.id if isinstance(scope, Guild) else scope)
                    for scope in self._default_scope
                ]
        self._default_scope = convert_list(int)(self._default_scope)

        if _logging := kwargs.get("logging"):

            # thx i0 for posting this on the retux Discord

            if _logging is True:
                _logging = logging.DEBUG

            _format = (
                "%(asctime)s [%(levelname)s] - .%(funcName)s(): %(message)s"
                if _logging == logging.DEBUG
                else "%(asctime)s [%(levelname)s] - %(message)s"
            )

            logging.basicConfig(format=_format, level=_logging)

        if kwargs.get("disable_sync"):
            self._automate_sync = False
            log.warning(
                "Automatic synchronization has been disabled. Interactions may need to be manually synchronized."
            )
        else:
            self._automate_sync = True

    @property
    def guilds(self) -> List[Guild]:
        """Returns a list of guilds the bot is in."""

        return list(self._http.cache[Guild].values.values())

    @property
    def latency(self) -> float:
        """Returns the connection latency in milliseconds."""

        return self._websocket.latency * 1000

    def start(self) -> None:
        """Starts the client session."""

        try:
            self._loop.run_until_complete(self._ready())
        except (CancelledError, Exception) as e:
            self._loop.run_until_complete(self._logout())
            raise e from e
        except KeyboardInterrupt:
            log.error("KeyboardInterrupt detected, shutting down the bot.")
        finally:
            self._loop.run_until_complete(self._logout())

    async def __register_id_autocomplete(self) -> None:  # TODO: make this use ID and not name
        for key in self.__id_autocomplete.keys():
            if isinstance(key, str):  # compatibility with the decorator from the Command obj
                for _ in self.__id_autocomplete[key]:
                    # _ contains {"coro" : coro, "name": <name_as_string>}
                    self.event(
                        _["coro"],
                        name=f"autocomplete_{key}_{_['name']}",
                    )
            else:
                _command_obj = self._find_command(key)
                _command: str = _command_obj.name
                for _ in self.__id_autocomplete[key]:
                    # _ contains {"coro" : coro, "name": <name_as_string>}
                    self.event(
                        _["coro"],
                        name=f"autocomplete_{_command}_{_['name']}",
                    )

    @staticmethod
    async def __compare_sync(
        data: dict, pool: List[dict]
    ) -> Tuple[bool, dict]:  # sourcery no-metrics
        """
        Compares an application command during the synchronization process.

        :param data: The application command to compare.
        :type data: dict
        :param pool: The "pool" or list of commands to compare from.
        :type pool: List[dict]
        :return: Whether the command has changed or not.
        :rtype: bool
        """

        # sourcery skip: none-compare

        attrs: List[str] = [
            name
            for name in ApplicationCommand.__slots__
            if not name.startswith("_")
            and not name.endswith("id")
            and name not in {"version", "default_permission"}
        ]

        option_attrs: List[str] = [name for name in Option.__slots__ if not name.startswith("_")]
        choice_attrs: List[str] = [name for name in Choice.__slots__ if not name.startswith("_")]
        log.info(f"Current attributes to compare: {', '.join(attrs)}.")
        clean: bool = True

        _command: dict = {}

        def __check_options(command, data):
            # sourcery skip: low-code-quality, none-compare
            # sourcery no-metrics
            _command_option_names = [option["name"] for option in command.get("options")]
            _data_option_names = [option["name"] for option in data.get("options")]

            if any(option not in _command_option_names for option in _data_option_names) or len(
                _data_option_names
            ) != len(_command_option_names):
                return False

            for option in command.get("options"):
                for _option in data.get("options"):
                    if _option["name"] == option["name"]:
                        for option_attr in option_attrs:
                            if (
                                option.get(option_attr)
                                and not _option.get(option_attr)
                                or not option.get(option_attr)
                                and _option.get(option_attr)
                            ):
                                return False
                            elif option_attr == "choices":
                                if not option.get("choices") or not _option.get("choices"):
                                    continue

                                _option_choice_names = [
                                    choice["name"] for choice in option.get("choices")
                                ]
                                _data_choice_names = [
                                    choice["name"] for choice in _option.get("choices")
                                ]

                                if any(
                                    _ not in _option_choice_names for _ in _data_choice_names
                                ) or len(_data_choice_names) != len(_option_choice_names):
                                    return False

                                for choice in option.get("choices"):
                                    for _choice in _option.get("choices"):
                                        if choice["name"] == _choice["name"]:
                                            for choice_attr in choice_attrs:
                                                if (
                                                    choice.get(choice_attr)
                                                    and not _choice.get(choice_attr)
                                                    or not choice.get(choice_attr)
                                                    and _choice.get(choice_attr)
                                                ):
                                                    return False
                                                elif choice.get(choice_attr) != _choice.get(
                                                    choice_attr
                                                ):
                                                    return False
                                                else:
                                                    continue

                                for i, __name in enumerate(_option_choice_names):
                                    if _data_choice_names[i] != __name:
                                        return False

                            elif option_attr == "required":
                                if (
                                    option.get(option_attr) == None  # noqa: E711
                                    and _option.get(option_attr) == False  # noqa: E712
                                ):
                                    # API not including if False
                                    continue

                            elif option_attr == "options":
                                if not option.get(option_attr) and not _option.get("options"):
                                    continue
                                _clean = __check_options(option, _option)
                                if not _clean:
                                    return _clean

                            elif option.get(option_attr) != _option.get(option_attr):
                                return False
                            else:
                                continue
            return next(
                (
                    False
                    for i, __name in enumerate(_command_option_names)
                    if _data_option_names[i] != __name
                ),
                True,
            )

        for command in pool:
            if command["name"] == data["name"]:
                _command = command
                # in case it continues looping
                if not command.get("options"):
                    command["options"] = []
                    # this will ensure that the option will be an emtpy list, since discord returns `None`
                    # when no options are present, but they're in the data as `[]`
                if command.get("guild_id") and not isinstance(command.get("guild_id"), int):
                    if isinstance(command.get("guild_id"), list):
                        command["guild_id"] = [int(_) for _ in command["guild_id"]]
                    else:
                        command["guild_id"] = int(command["guild_id"])
                    # ensure that IDs are present as integers since discord returns strings.
                for attr in attrs:
                    if attr == "options":
                        if (
                            not command.get("options")
                            and data.get("options")
                            or command.get("options")
                            and not data.get("options")
                        ):
                            clean = False
                            return clean, _command

                        elif command.get("options") and data.get("options"):

                            clean = __check_options(command, data)

                        if not clean:
                            return clean, _command

                        else:
                            continue

                    elif attr.endswith("localizations"):
                        if command.get(attr, None) is None and data.get(attr) == {}:
                            # This is an API/Version difference.
                            continue

                    elif (
                        attr == "dm_permission"
                        and data.get(attr) == True  # noqa: E712
                        and command.get(attr) == None  # noqa: E711
                    ):
                        # idk, it encountered me and synced unintentionally
                        continue

                    # elif data.get(attr, None) and command.get(attr) == data.get(attr):
                    elif command.get(attr, None) == data.get(attr, None):
                        # hasattr checks `dict.attr` not `dict[attr]`
                        continue
                    clean = False
                    break

        return clean, _command

    async def _ready(self) -> None:
        """
        Prepares the client with an internal "ready" check to ensure
        that all conditions have been met in a chronological order:

        .. code-block::

            CLIENT START
            |___ GATEWAY
            |   |___ READY
            |   |___ DISPATCH
            |___ SYNCHRONIZE
            |   |___ CACHE
            |___ DETECT DECORATOR
            |   |___ BUILD MODEL
            |   |___ SYNCHRONIZE
            |   |___ CALLBACK
            LOOP
        """
        ready: bool = False

        if isinstance(self._http, str):
            self._http = HTTPClient(self._http)

        data = await self._http.get_current_bot_information()
        self.me = Application(**data, _client=self._http)

        try:
            if self.me.flags is not None:
                # This can be None.
                if self._intents.GUILD_PRESENCES in self._intents and not (
                    self.me.flags.GATEWAY_PRESENCE in self.me.flags
                    or self.me.flags.GATEWAY_PRESENCE_LIMITED in self.me.flags
                ):
                    raise RuntimeError("Client not authorised for the GUILD_PRESENCES intent.")
                if self._intents.GUILD_MEMBERS in self._intents and not (
                    self.me.flags.GATEWAY_GUILD_MEMBERS in self.me.flags
                    or self.me.flags.GATEWAY_GUILD_MEMBERS_LIMITED in self.me.flags
                ):
                    raise RuntimeError("Client not authorised for the GUILD_MEMBERS intent.")
                if self._intents.GUILD_MESSAGES in self._intents and not (
                    self.me.flags.GATEWAY_MESSAGE_CONTENT in self.me.flags
                    or self.me.flags.GATEWAY_MESSAGE_CONTENT_LIMITED in self.me.flags
                ):
                    log.critical("Client not authorised for the MESSAGE_CONTENT intent.")
            elif self._intents.value != Intents.DEFAULT.value:
                raise RuntimeError("Client not authorised for any privileged intents.")

            self.__resolve_commands()

            if self._automate_sync:
                await self.__sync()
            else:
                await self.__get_all_commands()
            await self.__register_id_autocomplete()

            ready = True
        except Exception:
            log.exception("Could not prepare the client:")
        finally:
            if ready:
                log.debug("Client is now ready.")
                await self._login()

    async def _stop(self) -> None:
        """Stops the websocket connection gracefully."""

        log.debug("Shutting down the client....")
        self._websocket.ready.clear()  # Clears ready state.
        self._websocket._closing_lock.set()  # Toggles the "ready-to-shutdown" state for the bot.
        # And subsequently, the processes will close itself.

        await self._http._req._session.close()  # Closes the HTTP session associated with the client.

    async def _login(self) -> None:
        """Makes a login with the Discord API."""

        try:
            await self._websocket.run()
        except Exception:
            log.exception("Websocket have raised an exception, closing.")

            if self._websocket._closing_lock.is_set():
                # signal for closing.

                try:
                    if self._websocket._task is not None:
                        self._websocket.__heartbeat_event.set()
                        try:
                            # Wait for the keep-alive handler to finish so we can discard it gracefully
                            await self._websocket._task
                        finally:
                            self._websocket._task = None
                finally:  # then the overall WS client
                    if self._websocket._client is not None:
                        # This needs to be properly closed
                        try:
                            await self._websocket._client.close(code=1000)
                        finally:
                            self._websocket._client = None

    async def wait_until_ready(self) -> None:
        """Helper method that waits until the websocket is ready."""
        await self._websocket.wait_until_ready()

    async def __get_all_commands(self) -> None:
        # this method is just copied from the sync method
        # I expect this to be changed in the sync rework
        # until then this will deliver a cache if sync is off to make autocomplete work bug-free
        # but even with sync off, we should cache all commands here always

        _guilds = await self._http.get_self_guilds()
        _guild_ids = [int(_["id"]) for _ in _guilds]
        self._scopes.update(_guild_ids)
        _cmds = await self._http.get_application_commands(
            application_id=self.me.id, with_localizations=True
        )

        for command in _cmds:
            if command.get("code"):
                # Error exists.
                raise LibraryException(command["code"], message=f'{command["message"]} |')

        self.__global_commands = {"commands": _cmds, "clean": True}
        # TODO: add to cache (later)

        # responsible for checking if a command is in the cache but not a coro -> allowing removal

        for _id in _guild_ids:
            try:
                _cmds = await self._http.get_application_commands(
                    application_id=self.me.id, guild_id=_id, with_localizations=True
                )
            except LibraryException as e:
                if int(e.code) != 50001:
                    raise LibraryException(code=e.code, message=e.message)

                log.warning(
                    f"Your bot is missing access to guild with corresponding id {_id}! "
                    "Syncing commands will not be possible until it is invited with "
                    "`application.commands` scope!"
                )
                continue

            for command in _cmds:
                if command.get("code"):
                    # Error exists.
                    raise LibraryException(command["code"], message=f'{command["message"]} |')

            self.__guild_commands[_id] = {"commands": _cmds, "clean": True}

    def __resolve_commands(self) -> None:
        """
        Resolves all commands to the command coroutines.

        .. warning::
            This is an internal method. Do not call it unless you know what you are doing!
        """
        for cmd in self._commands:
            if cmd.resolved:
                continue

            cmd.listener = self._websocket._dispatch

            if cmd.default_scope and self._default_scope:
                cmd.scope = (
                    cmd.scope.extend(self._default_scope)
                    if isinstance(cmd.scope, list)
                    else self._default_scope
                )

            data: Union[dict, List[dict]] = cmd.full_data
            coro = cmd.dispatcher

            self.__check_command(
                command=ApplicationCommand(**(data[0] if isinstance(data, list) else data)),
                coro=coro,
            )

            if cmd.autocompletions:
                self.__id_autocomplete.update(cmd.autocompletions)

            coro = coro.__func__ if hasattr(coro, "__func__") else coro

            coro._command_data = data
            coro._name = cmd.name
            coro._converters = cmd.converters

            if (data["name"] if isinstance(data, dict) else data[0]["name"]) not in (
                (
                    c._command_data["name"]
                    if isinstance(c._command_data, dict)
                    else c._command_data[0]["name"]
                )
                for c in self.__command_coroutines
            ):
                self.__command_coroutines.append(coro)

            if cmd.scope not in (MISSING, None):
                if isinstance(cmd.scope, List):
                    [self._scopes.add(_ if isinstance(_, int) else _.id) for _ in cmd.scope]
                else:
                    self._scopes.add(cmd.scope if isinstance(cmd.scope, int) else cmd.scope.id)

            self.event(coro, name=f"command_{cmd.name}")
            cmd.resolved = True

    async def __sync(self) -> None:  # sourcery no-metrics
        """
        Synchronizes all commands to the API.

        .. warning::
            This is an internal method. Do not call it unless you know what you are doing!
        """
        # sourcery skip: low-code-quality

        log.debug("starting command sync")
        _guilds = await self._http.get_self_guilds()
        _guild_ids = [int(_["id"]) for _ in _guilds]
        self._scopes.update(_guild_ids)
        _cmds = await self._http.get_application_commands(
            application_id=self.me.id, with_localizations=True
        )

        for command in _cmds:
            if command.get("code"):
                # Error exists.
                raise LibraryException(command["code"], message=f'{command["message"]} |')

        self.__global_commands = {"commands": _cmds, "clean": True}
        # TODO: add to cache (later)

        __check_global_commands: List[str] = [cmd["name"] for cmd in _cmds]
        __check_guild_commands: Dict[int, List[str]] = {}
        __blocked_guilds: set = set()

        # responsible for checking if a command is in the cache but not a coro -> allowing removal

        for _id in _guild_ids.copy():
            try:
                _cmds = await self._http.get_application_commands(
                    application_id=self.me.id, guild_id=_id, with_localizations=True
                )
            except LibraryException as e:
                if int(e.code) != 50001:
                    raise LibraryException(code=e.code, message=e.message) from e

                log.warning(
                    f"Your bot is missing access to guild with corresponding id {_id}! "
                    "Adding commands will not be possible until it is invited with "
                    "`application.commands` scope!"
                )
                __blocked_guilds.add(_id)
                _guild_ids.remove(_id)
                continue

            self.__guild_commands[_id] = {"commands": _cmds, "clean": True}
            __check_guild_commands[_id] = [cmd["name"] for cmd in _cmds] if _cmds else []

        for coro in self.__command_coroutines:
            if hasattr(coro, "_command_data"):  # just so IDE knows it exists
                if isinstance(coro._command_data, list):
                    _guild_command: dict
                    for _guild_command in coro._command_data:
                        _guild_id = _guild_command.get("guild_id")
                        if _guild_id in __blocked_guilds:
                            log.fatal(f"Cannot sync commands on guild with id {_guild_id}!")
                            raise LibraryException(50001, message="Missing Access |")
                        if _guild_command["name"] not in __check_guild_commands[_guild_id]:
                            self.__guild_commands[_guild_id]["clean"] = False
                            self.__guild_commands[_guild_id]["commands"].append(_guild_command)

                        else:
                            clean, _command = await self.__compare_sync(
                                _guild_command, self.__guild_commands[_guild_id]["commands"]
                            )
                            if not clean:
                                self.__guild_commands[_guild_id]["clean"] = False
                                # _pos = self.__guild_commands[_guild_id]["commands"].index(_command)
                                # self.__guild_commands[_guild_id]["commands"][_pos] = _guild_command

                                for _pos, _dict in enumerate(
                                    self.__guild_commands[_guild_id]["commands"]
                                ):
                                    if _dict["name"] == _command["name"]:
                                        self.__guild_commands[_guild_id]["commands"][
                                            _pos
                                        ] = _guild_command
                                        break

                            if __check_guild_commands[_guild_id]:
                                del __check_guild_commands[_guild_id][
                                    __check_guild_commands[_guild_id].index(_guild_command["name"])
                                ]

                elif coro._command_data["name"] in __check_global_commands:  # noqa
                    clean, _command = await self.__compare_sync(
                        coro._command_data, self.__global_commands["commands"]
                    )

                    if not clean:
                        self.__global_commands["clean"] = False
                        # _pos = self.__global_commands["commands"].index(_command)
                        # self.__global_commands["commands"][_pos] = coro._command_data

                        for _pos, _dict in enumerate(self.__global_commands["commands"]):
                            if _dict["name"] == _command["name"]:
                                self.__global_commands["commands"][_pos] = coro._command_data
                                break

                    if __check_global_commands:
                        del __check_global_commands[
                            __check_global_commands.index(coro._command_data["name"])  # noqa
                        ]

                else:
                    self.__global_commands["clean"] = False
                    self.__global_commands["commands"].append(coro._command_data)

        if not self.__command_coroutines:
            if self.__global_commands["commands"]:
                self.__global_commands["clean"] = False
                self.__global_commands["commands"] = []
                __check_global_commands = []
            for _id in _guild_ids:
                if self.__guild_commands[_id]["commands"]:
                    __check_guild_commands[_id] = []
                    self.__guild_commands[_id]["clean"] = False
                    self.__guild_commands[_id]["commands"] = []

        if __check_global_commands:
            # names are present but not found in registered global command coroutines. Deleting.
            self.__global_commands["clean"] = False
            for name in __check_global_commands:
                _pos = self.__global_commands["commands"].index(
                    [_ for _ in self.__global_commands["commands"] if _["name"] == name][0]
                )
                del self.__global_commands["commands"][_pos]

        for _id in _guild_ids:
            if __check_guild_commands[_id]:
                self.__guild_commands[_id]["clean"] = False
                for name in __check_guild_commands[_id]:
                    _pos = self.__guild_commands[_id]["commands"].index(
                        [_ for _ in self.__guild_commands[_id]["commands"] if _["name"] == name][0]
                    )
                    del self.__guild_commands[_id]["commands"][_pos]

        if not self.__global_commands["clean"] or any(
            not self.__guild_commands[_id]["clean"] for _id in _guild_ids
        ):
            if not self.__global_commands["clean"]:
                res = await self._http.overwrite_application_command(
                    application_id=int(self.me.id), data=self.__global_commands["commands"]
                )
                self.__global_commands["clean"] = True
                self.__global_commands["commands"] = res

            for _id in _guild_ids:
                if not self.__guild_commands[_id]["clean"]:
                    res = await self._http.overwrite_application_command(
                        application_id=int(self.me.id),
                        data=self.__guild_commands[_id]["commands"],
                        guild_id=_id,
                    )
                    self.__guild_commands[_id]["clean"] = True
                    self.__guild_commands[_id]["commands"] = res

    def event(
        self, coro: Optional[Callable[..., Coroutine]] = MISSING, *, name: Optional[str] = MISSING
    ) -> Callable[..., Any]:
        """
        A decorator for listening to events dispatched from the
        Gateway.

        :param coro: The coroutine of the event.
        :type coro: Optional[Callable[..., Coroutine]]
        :param name(?): The name of the event. If not given, this defaults to the coroutine's name.
        :type name: Optional[str]
        :return: A callable response.
        :rtype: Callable[..., Any]
        """

        def decorator(coro: Optional[Callable[..., Coroutine]]):
            self._websocket._dispatch.register(
                coro, name=name if name is not MISSING else coro.__name__
            )
            return coro

        if coro is not MISSING:
            self._websocket._dispatch.register(
                coro, name=name if name is not MISSING else coro.__name__
            )
            return coro

        return decorator

    async def change_presence(self, presence: ClientPresence) -> None:
        """
        A method that changes the current client's presence on runtime.

         .. note::
            There is a ratelimit to using this method (5 per minute).
            As there's no gateway ratelimiter yet, breaking this ratelimit
            will force your bot to disconnect.

        :param presence: The presence to change the bot to on identify.
        :type presence: ClientPresence
        """
        await self._websocket._update_presence(presence)

    def __check_command(
        self,
        command: ApplicationCommand,
        coro: Callable[..., Coroutine],
        regex: str = r"^[a-z0-9_-]{1,32}$",
    ) -> None:  # sourcery no-metrics
        """
        Checks if a command is valid.
        """
        reg = re.compile(regex)
        _options_names: List[str] = []
        _sub_groups_present: bool = False
        _sub_cmds_present: bool = False

        def __check_sub_group(_sub_group: Option):
            nonlocal _sub_groups_present
            _sub_groups_present = True
            if _sub_group.name is MISSING:
                raise LibraryException(11, message="Sub command groups must have a name.")
            __indent = 4
            log.debug(
                f"{' ' * __indent}checking sub command group '{_sub_group.name}' of command '{command.name}'"
            )
            if not re.fullmatch(reg, _sub_group.name):
                raise LibraryException(
                    11,
                    message=f"The sub command group name does not match the regex for valid names ('{regex}')",
                )
            elif _sub_group.description is MISSING and not _sub_group.description:
                raise LibraryException(11, message="A description is required.")
            elif len(_sub_group.description) > 100:
                raise LibraryException(11, message="Descriptions must be less than 100 characters.")

            if not _sub_group.options:
                raise LibraryException(11, message="sub command groups must have subcommands!")
            if len(_sub_group.options) > 25:
                raise LibraryException(
                    11, message="A sub command group cannot contain more than 25 sub commands!"
                )
            for _sub_command in _sub_group.options:
                __check_sub_command(_sub_command, _sub_group)

        def __check_sub_command(_sub_command: Option, _sub_group: Option = MISSING):
            nonlocal _sub_cmds_present
            _sub_cmds_present = True
            if _sub_command.name is MISSING:
                raise LibraryException(11, message="sub commands must have a name!")
            if _sub_group is not MISSING:
                __indent = 8
                log.debug(
                    f"{' ' * __indent}checking sub command '{_sub_command.name}' of group '{_sub_group.name}'"
                )
            else:
                __indent = 4
                log.debug(
                    f"{' ' * __indent}checking sub command '{_sub_command.name}' of command '{command.name}'"
                )
            if not re.fullmatch(reg, _sub_command.name):
                raise LibraryException(
                    11,
                    message=f"The sub command name does not match the regex for valid names ('{reg}')",
                )
            elif _sub_command.description is MISSING or not _sub_command.description:
                raise LibraryException(11, message="A description is required.")
            elif len(_sub_command.description) > 100:
                raise LibraryException(11, message="Descriptions must be less than 100 characters.")

            if _sub_command.options is not MISSING and _sub_command.options:
                if len(_sub_command.options) > 25:
                    raise LibraryException(
                        11, message="Your sub command must have less than 25 options."
                    )
                _sub_opt_names = []
                for _opt in _sub_command.options:
                    __check_options(_opt, _sub_opt_names, _sub_command)
                del _sub_opt_names

        def __check_options(_option: Option, _names: list, _sub_command: Option = MISSING):
            nonlocal _options_names
            if getattr(_option, "autocomplete", False) and getattr(_option, "choices", False):
                log.warning("Autocomplete may not be set to true if choices are present.")
            if _option.name is MISSING:
                raise LibraryException(11, message="Options must have a name.")
            if _sub_command is not MISSING:
                __indent = 12 if _sub_groups_present else 8
                log.debug(
                    f"{' ' * __indent}checking option '{_option.name}' of sub command '{_sub_command.name}'"
                )
            else:
                __indent = 4
                log.debug(
                    f"{' ' * __indent}checking option '{_option.name}' of command '{command.name}'"
                )
            _options_names.append(_option.name)
            if not re.fullmatch(reg, _option.name):
                raise LibraryException(
                    11,
                    message=f"The option name ('{_option.name}') does not match the regex for valid names ('{regex}').",
                )
            if _option.description is MISSING or not _option.description:
                raise LibraryException(
                    11,
                    message="A description is required.",
                )
            elif len(_option.description) > 100:
                raise LibraryException(
                    11,
                    message="Descriptions must be less than 100 characters.",
                )
            if _option.name in _names:
                raise LibraryException(
                    11, message="You must not have two options with the same name in a command!"
                )
            _names.append(_option.name)

        def __check_coro():
            __indent = 4
            log.debug(f"{' ' * __indent}Checking coroutine: '{coro.__name__}'")
            _ismethod = hasattr(coro, "__func__")
            if not len(coro.__code__.co_varnames) ^ (
                _ismethod and len(coro.__code__.co_varnames) == 1
            ):
                raise LibraryException(
                    11, message="Your command needs at least one argument to return context."
                )
            elif "kwargs" in coro.__code__.co_varnames:
                return
            elif _sub_cmds_present and len(coro.__code__.co_varnames) < (3 if _ismethod else 2):
                raise LibraryException(
                    11, message="Your command needs one argument for the sub_command."
                )
            elif _sub_groups_present and len(coro.__code__.co_varnames) < (4 if _ismethod else 3):
                raise LibraryException(
                    11,
                    message="Your command needs one argument for the sub_command and one for the sub_command_group.",
                )
            add: int = (
                1 + abs(_sub_cmds_present) + abs(_sub_groups_present) + 1 if _ismethod else +0
            )

            if len(coro.__code__.co_varnames) - add < len(set(_options_names)):
                log.debug(
                    "Coroutine is missing arguments for options:"
                    f" {[_arg for _arg in _options_names if _arg not in coro.__code__.co_varnames]}"
                )
                raise LibraryException(
                    11, message="You need one argument for every option name in your command!"
                )

        if command.name is MISSING:
            raise LibraryException(11, message="Your command must have a name.")

        else:
            log.debug(f"checking command '{command.name}':")
        if (
            not re.fullmatch(reg, command.name)
            and command.type == ApplicationCommandType.CHAT_INPUT
        ):
            raise LibraryException(
                11,
                message=f"Your command name ('{command.name}') does not match the regex for valid names ('{regex}').",
            )
        elif command.type == ApplicationCommandType.CHAT_INPUT and (
            command.description is MISSING or not command.description
        ):
            raise LibraryException(11, message="A description is required.")
        elif command.type != ApplicationCommandType.CHAT_INPUT and (
            command.description is not MISSING and command.description
        ):
            raise LibraryException(11, message="Only chat-input commands can have a description.")

        elif command.description is not MISSING and len(command.description) > 100:
            raise LibraryException(11, message="Descriptions must be less than 100 characters.")

        if command.options and command.options is not MISSING:
            if len(command.options) > 25:
                raise LibraryException(11, message="Your command must have less than 25 options.")

            if command.type != ApplicationCommandType.CHAT_INPUT:
                raise LibraryException(
                    11, message="Only CHAT_INPUT commands can have options/sub-commands!"
                )

            _opt_names = []
            for _option in command.options:
                if _option.type == OptionType.SUB_COMMAND_GROUP:
                    __check_sub_group(_option)

                elif _option.type == OptionType.SUB_COMMAND:
                    __check_sub_command(_option)

                else:
                    __check_options(_option, _opt_names)
            del _opt_names

        __check_coro()

    def command(
        self,
        *,
        type: Optional[Union[int, ApplicationCommandType]] = ApplicationCommandType.CHAT_INPUT,
        name: Optional[str] = MISSING,
        description: Optional[str] = MISSING,
        scope: Optional[Union[int, Guild, List[int], List[Guild]]] = MISSING,
        options: Optional[
            Union[Dict[str, Any], List[Dict[str, Any]], Option, List[Option]]
        ] = MISSING,
        name_localizations: Optional[Dict[Union[str, Locale], str]] = MISSING,
        description_localizations: Optional[Dict[Union[str, Locale], str]] = MISSING,
        default_member_permissions: Optional[Union[int, Permissions]] = MISSING,
        dm_permission: Optional[bool] = MISSING,
        default_scope: bool = True,
    ) -> Callable[[Callable[..., Coroutine]], Command]:
        """
        A decorator for registering an application command to the Discord API,
        as well as being able to listen for ``INTERACTION_CREATE`` dispatched
        gateway events.

        The structure of a chat-input command:

        .. code-block:: python

            @command(name="command-name", description="this is a command.")
            async def command_name(ctx):
                ...

        You are also able to establish it as a message or user command by simply passing
        the ``type`` kwarg field into the decorator:

        .. code-block:: python

            @command(type=interactions.ApplicationCommandType.MESSAGE, name="Message Command")
            async def message_command(ctx):
                ...

        The ``scope`` kwarg field may also be used to designate the command in question
        applicable to a guild or set of guilds.

        To properly utilise the ``default_member_permissions`` kwarg, it requires OR'ing the permission values, similar to instantiating the client with Intents.
        For example:

        .. code-block:: python

            @command(name="kick", description="Kick a user.", default_member_permissions=interactions.Permissions.BAN_MEMBERS | interactions.Permissions.KICK_MEMBERS)
            async def kick(ctx, user: interactions.Member):
                ...

        Another example below for instance is an admin-only command:

        .. code-block:: python

            @command(name="sudo", description="this is an admin-only command.", default_member_permissions=interactions.Permissions.ADMINISTRATOR)
            async def sudo(ctx):
                ...

        .. note::
            If ``default_member_permissions`` is not given, this will default to anyone that is able to use the command.

        :param type?: The type of application command. Defaults to :meth:`interactions.enums.ApplicationCommandType.CHAT_INPUT` or ``1``.
        :type type?: Optional[Union[str, int, ApplicationCommandType]]
        :param name: The name of the application command. This *is* required but kept optional to follow kwarg rules.
        :type name: Optional[str]
        :param description?: The description of the application command. This should be left blank if you are not using ``CHAT_INPUT``.
        :type description?: Optional[str]
        :param scope?: The "scope"/applicable guilds the application command applies to.
        :type scope?: Optional[Union[int, Guild, List[int], List[Guild]]]
        :param options?: The "arguments"/options of an application command. This should be left blank if you are not using ``CHAT_INPUT``.
        :type options?: Optional[Union[Dict[str, Any], List[Dict[str, Any]], Option, List[Option]]]
        :param name_localizations?: The dictionary of localization for the ``name`` field. This enforces the same restrictions as the ``name`` field.
        :type name_localizations?: Optional[Dict[Union[str, Locale], str]]
        :param description_localizations?: The dictionary of localization for the ``description`` field. This enforces the same restrictions as the ``description`` field.
        :type description_localizations?: Optional[Dict[Union[str, Locale], str]]
        :param default_member_permissions?: The permissions bit value of ``interactions.api.model.flags.Permissions``. If not given, defaults to :meth:`interactions.api.model.flags.Permissions.USE_APPLICATION_COMMANDS` or ``2147483648``
        :type default_member_permissions?: Optional[Union[int, Permissions]]
        :param dm_permission?: The application permissions if executed in a Direct Message. Defaults to ``True``.
        :type dm_permission?: Optional[bool]
        :param default_scope?: Whether the scope of the command is the default scope set in the client. Defaults to ``True``.
        :type default_scope?: bool
        :return: A callable response.
        :rtype: Callable[[Callable[..., Coroutine]], Command]
        """

        def decorator(coro: Callable[..., Coroutine]) -> Command:
            cmd = Command(
                coro=coro,
                type=type,
                name=name,
                description=description,
                options=options,
                scope=scope,
                default_member_permissions=default_member_permissions,
                dm_permission=dm_permission,
                name_localizations=name_localizations,
                description_localizations=description_localizations,
                default_scope=default_scope,
            )
            cmd.client = self
            self._commands.append(cmd)
            return cmd

        return decorator

    def message_command(
        self,
        *,
        name: Optional[str] = MISSING,
        scope: Optional[Union[int, Guild, List[int], List[Guild]]] = MISSING,
        name_localizations: Optional[Dict[Union[str, Locale], Any]] = MISSING,
        default_member_permissions: Optional[Union[int, Permissions]] = MISSING,
        dm_permission: Optional[bool] = MISSING,
        default_scope: bool = True,
    ) -> Callable[[Callable[..., Coroutine]], Command]:
        """
        A decorator for registering a message context menu to the Discord API,
        as well as being able to listen for ``INTERACTION_CREATE`` dispatched
        gateway events.

        The structure of a message context menu:

        .. code-block:: python

            @message_command(name="Context menu name")
            async def context_menu_name(ctx):
                ...

        The ``scope`` kwarg field may also be used to designate the command in question
        applicable to a guild or set of guilds.

        :param name: The name of the application command.
        :type name: Optional[str]
        :param scope?: The "scope"/applicable guilds the application command applies to. Defaults to ``None``.
        :type scope?: Optional[Union[int, Guild, List[int], List[Guild]]]
        :param default_permission?: The default permission of accessibility for the application command. Defaults to ``True``.
        :type default_permission?: Optional[bool]
        :param name_localizations?: The dictionary of localization for the ``name`` field. This enforces the same restrictions as the ``name`` field.
        :type name_localizations?: Optional[Dict[Union[str, Locale], str]]
        :param default_member_permissions?: The permissions bit value of ``interactions.api.model.flags.Permissions``. If not given, defaults to :meth:`interactions.api.model.flags.Permissions.USE_APPLICATION_COMMANDS` or ``2147483648``
        :type default_member_permissions?: Optional[Union[int, Permissions]]
        :param dm_permission?: The application permissions if executed in a Direct Message. Defaults to ``True``.
        :type dm_permission?: Optional[bool]
        :param default_scope?: Whether the scope of the command is the default scope set in the client. Defaults to ``True``.
        :type default_scope?: bool
        :return: A callable response.
        :rtype: Callable[[Callable[..., Coroutine]], Command]
        """

        def decorator(coro: Callable[..., Coroutine]) -> Command:
            return self.command(
                type=ApplicationCommandType.MESSAGE,
                name=name,
                scope=scope,
                default_member_permissions=default_member_permissions,
                dm_permission=dm_permission,
                name_localizations=name_localizations,
                default_scope=default_scope,
            )(coro)

        return decorator

    def user_command(
        self,
        *,
        name: Optional[str] = MISSING,
        scope: Optional[Union[int, Guild, List[int], List[Guild]]] = MISSING,
        name_localizations: Optional[Dict[Union[str, Locale], Any]] = MISSING,
        default_member_permissions: Optional[Union[int, Permissions]] = MISSING,
        dm_permission: Optional[bool] = MISSING,
        default_scope: bool = True,
    ) -> Callable[[Callable[..., Coroutine]], Command]:
        """
        A decorator for registering a user context menu to the Discord API,
        as well as being able to listen for ``INTERACTION_CREATE`` dispatched
        gateway events.

        The structure of a user context menu:

        .. code-block:: python

            @user_command(name="Context menu name")
            async def context_menu_name(ctx):
                ...

        The ``scope`` kwarg field may also be used to designate the command in question
        applicable to a guild or set of guilds.

        :param name: The name of the application command.
        :type name: Optional[str]
        :param scope?: The "scope"/applicable guilds the application command applies to. Defaults to ``None``.
        :type scope?: Optional[Union[int, Guild, List[int], List[Guild]]]
        :param default_permission?: The default permission of accessibility for the application command. Defaults to ``True``.
        :type default_permission?: Optional[bool]
        :param name_localizations?: The dictionary of localization for the ``name`` field. This enforces the same restrictions as the ``name`` field.
        :type name_localizations?: Optional[Dict[Union[str, Locale], str]]
        :param default_member_permissions?: The permissions bit value of ``interactions.api.model.flags.Permissions``. If not given, defaults to :meth:`interactions.api.model.flags.Permissions.USE_APPLICATION_COMMANDS` or ``2147483648``
        :type default_member_permissions?: Optional[Union[int, Permissions]]
        :param dm_permission?: The application permissions if executed in a Direct Message. Defaults to ``True``.
        :type dm_permission?: Optional[bool]
        :param default_scope?: Whether the scope of the command is the default scope set in the client. Defaults to ``True``.
        :type default_scope?: bool
        :return: A callable response.
        :rtype: Callable[[Callable[..., Coroutine]], Command]
        """

        def decorator(coro: Callable[..., Coroutine]) -> Command:
            return self.command(
                type=ApplicationCommandType.USER,
                name=name,
                scope=scope,
                default_member_permissions=default_member_permissions,
                dm_permission=dm_permission,
                name_localizations=name_localizations,
                default_scope=default_scope,
            )(coro)

        return decorator

    def component(
        self, component: Union[str, Button, SelectMenu]
    ) -> Callable[[Callable[..., Coroutine]], Callable[..., Coroutine]]:
        """
        A decorator for listening to ``INTERACTION_CREATE`` dispatched gateway
        events involving components.

        The structure for a component callback:

        .. code-block:: python

            # Method 1
            @component(interactions.Button(
                style=interactions.ButtonStyle.PRIMARY,
                label="click me!",
                custom_id="click_me_button",
            ))
            async def button_response(ctx):
                ...

            # Method 2
            @component("custom_id")
            async def button_response(ctx):
                ...

        The context of the component callback decorator inherits the same
        as of the command decorator.

        :param component: The component you wish to callback for.
        :type component: Union[str, Button, SelectMenu]
        :return: A callable response.
        :rtype: Callable[[Callable[..., Coroutine]], Callable[..., Coroutine]]
        """

        def decorator(coro: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
            payload: str = (
                _component(component).custom_id
                if isinstance(component, (Button, SelectMenu))
                else component
            )
            return self.event(coro, name=f"component_{payload}")

        return decorator

    def _find_command(self, command: Union[str, int]) -> ApplicationCommand:
        """
        Iterates over `commands` and returns an :class:`ApplicationCommand` if it matches the name from `command`

        :param command: The name or ID of the command to match
        :type command: Union[str, int]
        :return: An ApplicationCommand model
        :rtype: ApplicationCommand
        """
        key = "name" if isinstance(command, str) else "id"
        _command: Dict
        _command_obj = next(
            (
                ApplicationCommand(**_command)
                for _command in self.__global_commands["commands"]
                if str(_command[key]) == str(command)
            ),
            None,
        )

        if not _command_obj:
            for scope in self._scopes:
                _command_obj = next(
                    (
                        ApplicationCommand(**_command)
                        for _command in self.__guild_commands[scope]["commands"]
                        if str(_command[key]) == str(command)
                    ),
                    None,
                )
                if _command_obj:
                    break

        if not _command_obj or (hasattr(_command_obj, "id") and not _command_obj.id):
            raise LibraryException(
                6,
                message="The command does not exist. Make sure to define"
                + " your autocomplete callback after your commands",
            )
        else:
            return _command_obj

    def autocomplete(
        self, command: Union[ApplicationCommand, int, str, Snowflake], name: str
    ) -> Callable[[Callable[..., Coroutine]], Callable[..., Coroutine]]:
        """
        A decorator for listening to ``INTERACTION_CREATE`` dispatched gateway
        events involving autocompletion fields.

        The structure for an autocomplete callback:

        .. code-block:: python

            @autocomplete(command="command_name", name="option_name")
            async def autocomplete_choice_list(ctx, user_input: str = ""):
                await ctx.populate([
                    interactions.Choice(...),
                    interactions.Choice(...),
                    ...
                ])

        :param command: The command, command ID, or command name with the option.
        :type command: Union[ApplicationCommand, int, str, Snowflake]
        :param name: The name of the option to autocomplete.
        :type name: str
        :return: A callable response.
        :rtype: Callable[[Callable[..., Coroutine]], Callable[..., Coroutine]]
        """

        if isinstance(command, ApplicationCommand):
            _command: str = command.name
        elif isinstance(command, str):
            _command: str = command
        elif isinstance(command, (int, Snowflake)):
            _command: Union[Snowflake, int] = int(command)
        else:
            raise LibraryException(
                message="You can only insert strings, integers and ApplicationCommands here!",
                code=12,
            )

        def decorator(coro: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
            if isinstance(_command, (int, Snowflake)):
                curr_autocomplete = self.__id_autocomplete.get(_command, [])
                curr_autocomplete.append({"coro": coro, "name": name})
                self.__id_autocomplete[_command] = curr_autocomplete
                return coro
            return self.event(coro, name=f"autocomplete_{_command}_{name}")

        return decorator

    def modal(
        self, modal: Union[Modal, str]
    ) -> Callable[[Callable[..., Coroutine]], Callable[..., Coroutine]]:
        """
        A decorator for listening to ``INTERACTION_CREATE`` dispatched gateway
        events involving modals.

        The structure for a modal callback:

        .. code-block:: python

            @modal(interactions.Modal(
                interactions.TextInput(
                    style=interactions.TextStyleType.PARAGRAPH,
                    custom_id="how_was_your_day_field",
                    label="How has your day been?",
                    placeholder="Well, so far...",
                ),
            ))
            async def modal_response(ctx):
                ...

        The context of the modal callback decorator inherits the same
        as of the component decorator.

        :param modal: The modal or custom_id of modal you wish to callback for.
        :type modal: Union[Modal, str]
        :return: A callable response.
        :rtype: Callable[[Callable[..., Coroutine]], Callable[..., Coroutine]]
        """

        def decorator(coro: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
            payload: str = modal.custom_id if isinstance(modal, Modal) else modal
            return self.event(coro, name=f"modal_{payload}")

        return decorator

    def load(
        self, name: str, package: Optional[str] = None, *args, **kwargs
    ) -> Optional["Extension"]:
        r"""
        "Loads" an extension off of the current client by adding a new class
        which is imported from the library.

        :param name: The name of the extension.
        :type name: str
        :param package?: The package of the extension.
        :type package?: Optional[str]
        :param \*args?: Optional arguments to pass to the extension
        :type \**args: tuple
        :param \**kwargs?: Optional keyword-only arguments to pass to the extension.
        :type \**kwargs?: dict
        :return: The loaded extension.
        :rtype: Optional[Extension]
        """
        _name: str = resolve_name(name, package)

        if _name in self._extensions:
            log.error(f"Extension {name} has already been loaded. Skipping.")
            return

        module = import_module(
            name, package
        )  # should be a module, because Extensions just need to be __init__-ed

        try:
            setup = getattr(module, "setup")
            extension = setup(self, *args, **kwargs)
        except Exception as error:
            del sys.modules[name]
            log.error(f"Could not load {name}: {error}. Skipping.")
            raise error from error
        else:
            log.debug(f"Loaded extension {name}.")
            self._extensions[_name] = module
            return extension

    def remove(
        self, name: str, remove_commands: bool = True, package: Optional[str] = None
    ) -> None:
        """
        Removes an extension out of the current client from an import resolve.

        :param name: The name of the extension.
        :type name: str
        :param remove_commands?: Whether to remove commands before reloading. Defaults to True.
        :type remove_commands?: bool
        :param package?: The package of the extension.
        :type package?: Optional[str]
        """
        try:
            _name: str = resolve_name(name, package)
        except AttributeError:
            _name = name

        extension = self._extensions.get(_name)

        if _name not in self._extensions:
            log.error(f"Extension {name} has not been loaded before. Skipping.")
            return

        if isinstance(extension, ModuleType):  # loaded as a module
            for ext_name, ext in getmembers(
                extension, lambda x: isinstance(x, type) and issubclass(x, Extension)
            ):

                if ext_name != "Extension":
                    _extension = self._extensions.get(ext_name)
                    with contextlib.suppress(AttributeError):
                        self._loop.create_task(
                            _extension.teardown(remove_commands=remove_commands)
                        )  # made for Extension, usable by others
            del sys.modules[_name]

        else:
            with contextlib.suppress(AttributeError):
                self._loop.create_task(
                    extension.teardown(remove_commands=remove_commands)
                )  # made for Extension, usable by others
        del self._extensions[_name]

        log.debug(f"Removed extension {name}.")

    def reload(
        self,
        name: str,
        package: Optional[str] = None,
        remove_commands: bool = True,
        *args,
        **kwargs,
    ) -> Optional["Extension"]:
        r"""
        "Reloads" an extension off of current client from an import resolve.

        .. warning::
            This will remove and re-add application commands, counting towards your daily application
            command creation limit, as long as you have the ``remove_commands`` argument set to ``True``, what it is by
            default.

        :param name: The name of the extension
        :type name: str
        :param package?: The package of the extension
        :type package?: Optional[str]
        :param remove_commands?: Whether to remove commands before reloading. Defaults to True
        :type remove_commands?: bool
        :param \*args?: Optional arguments to pass to the extension
        :type \**args: tuple
        :param \**kwargs?: Optional keyword-only arguments to pass to the extension.
        :type \**kwargs?: dict
        :return: The reloaded extension.
        :rtype: Optional[Extension]
        """
        _name: str = resolve_name(name, package)
        extension = self._extensions.get(_name)

        if extension is None:
            log.warning(f"Extension {name} could not be reloaded because it was never loaded.")
            return self.load(name, package)

        self.remove(name, package=package, remove_commands=remove_commands)
        return self.load(name, package, *args, **kwargs)

    def get_extension(self, name: str) -> Optional[Union[ModuleType, "Extension"]]:
        return self._extensions.get(name)

    async def modify(
        self,
        username: Optional[str] = MISSING,
        avatar: Optional[Image] = MISSING,
    ) -> User:
        """
        Modify the bot user account settings.

        :param username?: The new username of the bot
        :type username?: Optional[str]
        :param avatar?: The new avatar of the bot
        :type avatar?: Optional[Image]
        :return: The modified User object
        :rtype: User
        """
        payload: dict = {}
        if avatar is not MISSING:
            payload["avatar"] = avatar.data
        if username is not MISSING:
            payload["username"] = username
        data: dict = await self._http.modify_self(payload=payload)

        return User(**data)

    async def request_guild_members(
        self,
        guild_id: Union[Guild, Snowflake, int, str],
        limit: Optional[int] = MISSING,
        query: Optional[str] = MISSING,
        presences: Optional[bool] = MISSING,
        user_ids: Optional[Union[Snowflake, List[Snowflake]]] = MISSING,
        nonce: Optional[str] = MISSING,
    ) -> None:
        """
        Requests guild members via websocket.

        :param guild_id: ID of the guild to get members for.
        :type guild_id: Union[Guild, Snowflake, int, str]
        :param limit: Maximum number of members to send matching the 'query' parameter. Required when specifying 'query'.
        :type limit: Optional[int]
        :param query: String that username starts with.
        :type query: Optional[str]
        :param presences: Used to specify if we want the presences of the matched members.
        :type presences: Optional[bool]
        :param user_ids: Used to specify which users you wish to fetch.
        :type user_ids: Optional[Union[Snowflake, List[Snowflake]]]
        :param nonce: Nonce to identify the Guild Members Chunk response.
        :type nonce: Optional[str]
        """
        await self._websocket.request_guild_members(
            guild_id=int(guild_id.id) if isinstance(guild_id, Guild) else int(guild_id),
            limit=limit if limit is not MISSING else 0,
            query=query if query is not MISSING else None,
            presences=presences if presences is not MISSING else None,
            user_ids=user_ids if user_ids is not MISSING else None,
            nonce=nonce if nonce is not MISSING else None,
        )

    async def _logout(self) -> None:
        await self._websocket.close()
        await self._http._req.close()


# TODO: Implement the rest of cog behaviour when possible.
class Extension:
    """
    A class that allows you to represent "extensions" of your code, or
    essentially cogs that can be ran independent of the root file in
    an object-oriented structure.

    The structure of an extension:

    .. code-block:: python

        class CoolCode(interactions.Extension):
            def __init__(self, client):
                self.client = client

            @command(
                type=interactions.ApplicationCommandType.USER,
                name="User command in cog",
            )
            async def cog_user_cmd(self, ctx):
                ...

        def setup(client):
            CoolCode(client)
    """

    client: Client

    def __new__(cls, client: Client, *args, **kwargs) -> "Extension":
        # sourcery skip: low-code-quality

        self = super().__new__(cls)

        self.client = client
        self._commands = {}
        self._listeners = {}

        # This gets every coroutine in a way that we can easily change them
        # cls
        for name, func in getmembers(self, predicate=iscoroutinefunction):
            # TODO we can make these all share the same list, might make it easier to load/unload
            if hasattr(func, "__listener_name__"):  # set by extension_listener
                func = client.event(
                    func, name=func.__listener_name__
                )  # capture the return value for friendlier ext-ing

                listeners = self._listeners.get(func.__listener_name__, [])
                listeners.append(func)
                self._listeners[func.__listener_name__] = listeners

            if hasattr(func, "__component_data__"):
                args, kwargs = func.__component_data__
                func = client.component(*args, **kwargs)(func)

                component = kwargs.get("component") or args[0]
                comp_name = (
                    _component(component).custom_id
                    if isinstance(component, (Button, SelectMenu))
                    else component
                )
                comp_name = f"component_{comp_name}"

                listeners = self._listeners.get(comp_name, [])
                listeners.append(func)
                self._listeners[comp_name] = listeners

            if hasattr(func, "__autocomplete_data__"):
                all_args_kwargs = func.__autocomplete_data__
                for _ in all_args_kwargs:
                    args, kwargs = _[0], _[1]
                    func = client.autocomplete(*args, **kwargs)(func)

                    name = kwargs.get("name") or args[0]
                    _command = kwargs.get("command") or args[1]

                    _command: Union[Snowflake, int] = (
                        _command.id if isinstance(_command, ApplicationCommand) else _command
                    )

                    auto_name = f"autocomplete_{_command}_{name}"

                    listeners = self._listeners.get(auto_name, [])
                    listeners.append(func)
                    self._listeners[auto_name] = listeners

            if hasattr(func, "__modal_data__"):
                args, kwargs = func.__modal_data__
                func = client.modal(*args, **kwargs)(func)

                modal = kwargs.get("modal") or args[0]
                _modal_id: str = modal.custom_id if isinstance(modal, Modal) else modal
                modal_name = f"modal_{_modal_id}"

                listeners = self._listeners.get(modal_name, [])
                listeners.append(func)
                self._listeners[modal_name] = listeners

        for _, cmd in getmembers(self, predicate=lambda command: isinstance(command, Command)):
            cmd: Command

            if cmd.name in {_cmd.name for _cmd in self.client._commands}:
                continue

            cmd.extension = self
            cmd.client = self.client
            self.client._commands.append(cmd)

            commands = self._commands.get(cmd.name, [])
            coro = cmd.dispatcher
            coro = coro.__func__ if hasattr(coro, "__func__") else coro
            commands.append(coro)
            self._commands[f"command_{cmd.name}"] = commands

        client._extensions[cls.__name__] = self

        self.client._Client__resolve_commands()  # noqa

        if client._websocket.ready.is_set() and client._automate_sync:
            client._loop.create_task(client._Client__sync())  # noqa

        return self

    async def teardown(self, remove_commands: bool = True):
        for event, funcs in self._listeners.items():
            for func in funcs:
                self.client._websocket._dispatch.events[event].remove(func)

        for cmd, funcs in self._commands.items():
            _cmd: str = cmd.split("_", 1)[1]

            for _coro in self.client._Client__command_coroutines:
                if _coro._name == _cmd:
                    self.client._Client__command_coroutines.remove(_coro)  # noqa
                    break

            for _command in self.client._commands:
                if _command.name == _cmd:
                    self.client._commands.remove(_command)
                    break

            for i in range(len(funcs)):
                self.client._websocket._dispatch.events[cmd].pop(i)  # noqa

        if self.client._automate_sync and remove_commands:
            await self.client._Client__sync()  # noqa


@wraps(Client.command)
def extension_command(**kwargs) -> Callable[[Callable[..., Coroutine]], Command]:
    def decorator(coro) -> Command:
        cmd = Command(coro=coro, **kwargs)
        coro.__command_data__ = cmd
        return cmd

    return decorator


def extension_listener(func: Optional[Coroutine] = None, name: Optional[str] = None):
    def decorator(func: Coroutine):
        func.__listener_name__ = name or func.__name__

        return func

    if func:
        # allows omitting `()` on `@listener`
        func.__listener_name__ = name or func.__name__
        return func

    return decorator


@wraps(Client.component)
def extension_component(*args, **kwargs):
    def decorator(func):
        func.__component_data__ = (args, kwargs)
        return func

    return decorator


@wraps(Client.autocomplete)
def extension_autocomplete(*args, **kwargs):
    def decorator(func):
        try:
            if getattr(func, "__autocomplete_data__"):
                func.__autocomplete_data__.append((args, kwargs))
        except AttributeError:
            func.__autocomplete_data__ = [(args, kwargs)]
        finally:
            return func

    return decorator


@wraps(Client.modal)
def extension_modal(*args, **kwargs):
    def decorator(func):
        func.__modal_data__ = (args, kwargs)
        return func

    return decorator


@wraps(Client.message_command)
def extension_message_command(**kwargs) -> Callable[[Callable[..., Coroutine]], Command]:
    def decorator(func) -> Command:
        kwargs["type"] = ApplicationCommandType.MESSAGE
        return extension_command(**kwargs)(func)

    return decorator


@wraps(Client.user_command)
def extension_user_command(**kwargs) -> Callable[[Callable[..., Coroutine]], Command]:
    def decorator(func) -> Command:
        kwargs["type"] = ApplicationCommandType.USER
        return extension_command(**kwargs)(func)

    return decorator
