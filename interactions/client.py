from asyncio import get_event_loop
from logging import Logger, basicConfig, getLogger
from typing import Any, Callable, Coroutine, Dict, List, Optional, Union

from .api.cache import Item
from .api.error import InteractionException, JSONException
from .api.gateway import WebSocket
from .api.http import HTTPClient
from .api.models.guild import Guild
from .api.models.intents import Intents
from .api.models.team import Application
from .base import Data
from .enums import ApplicationCommandType
from .models.command import ApplicationCommand, Option, Permission
from .models.component import Button, Component, SelectMenu

basicConfig(level=Data.LOGGER)
log: Logger = getLogger("client")
_token: str = ""  # noqa


class Client:
    """
    A class representing the client connection to Discord's gateway and API via. WebSocket and HTTP.

    :ivar AbstractEventLoop loop: The main overall asynchronous coroutine loop in effect.
    :ivar Listener listener: An instance of :class:`interactions.api.dispatch.Listener`.
    :ivar Optional[Union[Intents, List[Intents]]] intents: The application's intents as :class:`interactions.api.models.Intents`.
    :ivar Request http: An instance of :class:`interactions.api.http.Request`.
    :ivar WebSocket websocket: An instance of :class:`interactions.api.gateway.WebSocket`.
    :ivar str token: The application token.
    """

    def __init__(
        self,
        token: str,
        intents: Optional[Union[Intents, List[Intents]]] = Intents.DEFAULT,
        disable_sync: Optional[bool] = None,
    ) -> None:
        """
        :param token: The token of the application for authentication and connection.
        :type token: str
        :param intents?: The intents you wish to pass through the client. Defaults to :meth:`interactions.api.models.intents.Intents.DEFAULT` or ``513``.
        :type intents: Optional[Union[Intents, List[Intents]]]
        :param disable_sync?: Whether you want to disable automate synchronization or not.
        :type disable_sync: Optional[bool]
        """
        if isinstance(intents, list):
            for intent in intents:
                self.intents |= intent
        else:
            self.intents = intents

        self.loop = get_event_loop()
        self.http = HTTPClient(token)
        self.websocket = WebSocket(intents=self.intents)
        self.me = None
        # the token family :)
        self.token = token
        self.http.token = token
        _token = token  # noqa: F841

        if disable_sync:
            self.automate_sync = False
            log.warn(
                "Automatic synchronization has been disabled. Interactions may need to be manually synchronized."
            )
        else:
            self.automate_sync = True

        if not self.me:
            data = self.loop.run_until_complete(self.http.get_self())
            self.me = Application(**data)

        self.websocket.dispatch.register(self.raw_socket_create)
        self.websocket.dispatch.register(self.raw_guild_create, "on_guild_create")

    async def login(self, token: str) -> None:
        """
        Makes a login with the Discord API.

        :param token: The application token needed for authorization.
        :type token: str
        """
        while not self.websocket.closed:
            await self.websocket.connect(token)

    def start(self) -> None:
        """Starts the client session."""
        self.loop.run_until_complete(self.login(self.token))

    async def synchronize(
        self, payload: ApplicationCommand, permissions: Optional[Union[dict, List[dict]]]
    ) -> None:
        """
        Synchronizes the command specified by checking through the
        currently registered application commands on the API and
        modifying if there is a detected chagne in structure.

        .. warning::
            This internal call does not need to be manually triggered,
            as it will automatically be done for you. Additionally,
            this will not delete unused commands for you.

        :param payload: The payload/object of the command.
        :type payload: ApplicationCommand
        :param permissions: The permissions of the command.
        :type permissions: Optional[Union[dict, List[dict]]]
        """

        # TODO: Clean up.
        commands: List[dict] = await self.http.get_application_command(
            application_id=self.me.id, guild_id=payload.guild_id
        )

        if commands:
            log.debug("Commands were found, checking for sync.")
            for command in commands:
                log.debug(f"Checking command {command['name']}.")
                result: ApplicationCommand = ApplicationCommand(
                    id=command.get("id"),
                    type=command.get("type"),
                    guild_id=int(command.get("guild_id")),
                    name=command.get("name"),
                    description=command.get("description", ""),
                    options=command.get("options", []),
                    default_permission=command.get("default_permission", False),
                )
                self.http.cache.interactions.add(Item(result.name, result))

                if result.name == payload.name:
                    request: HTTPClient = None
                    _result_name = result._json["name"]
                    _payload_name = payload._json["name"]

                    del result._json["name"]
                    del payload._json["name"]
                    if result._json != payload._json:
                        log.info(
                            f"Detected unsynced command {payload.name}, editing and updating cache."
                        )

                        result._json["name"] = _result_name
                        payload._json["name"] = _payload_name
                        request = await self.http.edit_application_command(
                            application_id=self.me.id,
                            data=payload._json,
                            command_id=result.id,
                            guild_id=payload.guild_id,
                        )
                        self.http.cache.interactions.add(Item(payload.name, payload))

                        if request.get("code"):
                            raise JSONException(request["code"])
                else:
                    log.info(
                        "Detected command declared but not in the API, creating and updating cache."
                    )
                    request = await self.http.create_application_command(
                        application_id=self.me.id,
                        data=payload._json,
                        guild_id=payload.guild_id,
                    )
                    self.http.cache.interactions.add(Item(payload.name, payload))

                    if request.get("code"):
                        raise JSONException(request["code"])

        # TODO: Work more on this later.
        # cached_commands: list = [self.http.cache.interactions.values[command] for command in self.http.cache.interactions.values]
        # for command in commands:
        #     result: ApplicationCommand = ApplicationCommand(
        #         id=command.get("id"),
        #         type=command.get("type"),
        #         guild_id=int(command.get("guild_id")),
        #         name=command.get("name"),
        #         description=command.get("description", ""),
        #         options=command.get("options", []),
        #         default_permission=command.get("default_permission", False),
        #     )

        #     if result not in cached_commands:
        #         log.info(
        #             f"Detected unused command {result.name}, deleting from the API and cache."
        #         )
        #         request = self.loop.run_until_complete(
        #             self.http.delete_application_command(
        #                 application_id=self.me.id, command_id=result.id, guild_id=result.guild_id
        #             )
        #         )

    def event(self, coro: Coroutine, name: Optional[str] = None) -> Callable[..., Any]:
        """
        A decorator for listening to dispatched events from the
        gateway.

        :param coro: The coroutine of the event.
        :type coro: Coroutine
        :return: A callable response.
        :rtype: Callable[..., Any]
        """
        self.websocket.dispatch.register(coro, name=name)
        return coro

    def command(
        self,
        *,
        type: Optional[Union[int, ApplicationCommandType]] = ApplicationCommandType.CHAT_INPUT,
        name: Optional[str] = None,
        description: Optional[str] = None,
        scope: Optional[Union[int, Guild, List[int], List[Guild]]] = None,
        options: Optional[Union[Dict[str, Any], List[Dict[str, Any]], Option, List[Option]]] = None,
        default_permission: Optional[bool] = None,
        permissions: Optional[
            Union[Dict[str, Any], List[Dict[str, Any]], Permission, List[Permission]]
        ] = None,
    ) -> Callable[..., Any]:
        """
        A decorator for registering an application command to the Discord API,
        as well as being able to listen for ``INTERACTION_CREATE`` dispatched
        gateway events.

        :param type?: The type of application command. Defaults to :meth:`interactions.enums.ApplicationCommandType.CHAT_INPUT` or ``1``.
        :type type: Optional[Union[str, int, ApplicationCommandType]]
        :param name: The name of the application command. This *is* required but kept optional to follow kwarg rules.
        :type name: Optional[str]
        :param description?: The description of the application command. This should be left blank if you are not using ``CHAT_INPUT``.
        :type description: Optional[str]
        :param scope?: The "scope"/applicable guilds the application command applies to.
        :type scope: Optional[Union[int, Guild, List[int], List[Guild]]]
        :param options?: The "arguments"/options of an application command. This should be left blank if you are not using ``CHAT_INPUT``.
        :type options: Optional[Union[Dict[str, Any], List[Dict[str, Any]], Option, List[Option]]]
        :param default_permission?: The default permission of accessibility for the application command. Defaults to ``True``.
        :type default_permission: Optional[bool]
        :param permissions: The permissions of an application command.
        :type permissions: Optional[Union[Dict[str, Any], List[Dict[str, Any]], Permission, List[Permission]]]
        :return: A callable response.
        :rtype: Callable[..., Any]
        """
        if not name:
            raise InteractionException(11, message="Your command must have a name.")

        if type == ApplicationCommandType.CHAT_INPUT and not description:
            raise InteractionException(11, message="Chat-input commands must have a description.")

        def decorator(coro: Coroutine) -> Any:
            if not len(coro.__code__.co_varnames):
                raise InteractionException(
                    11, message="Your command needs at least one argument to return context."
                )
            elif (len(coro.__code__.co_varnames) + 1) < len(options):
                raise InteractionException(
                    11,
                    message="You must have the same amount of arguments as the options of the command.",
                )

            _type: int = 0
            if isinstance(type, ApplicationCommandType):
                _type: int = type.value
            else:
                _type: int = ApplicationCommandType(type)

            _description: str = "" if description is None else description
            _options: list = []

            if options:
                if all(isinstance(option, Option) for option in options):
                    _options = [option._json for option in options]
                elif all(isinstance(option, Dict[str, Any]) for option in options):
                    _options = [option for option in options]
                elif isinstance(options, Option):
                    _options = [options._json]
                else:
                    _options = [options]

            _default_permission: bool = True if default_permission is None else default_permission
            _permissions: list = []

            if permissions:
                if all(isinstance(permission, Permission) for permission in permissions):
                    _permissions = [permission._json for permission in permissions]
                elif all(isinstance(permission, Dict[str, Any]) for permission in permissions):
                    _permissions = [permission for permission in permissions]
                elif isinstance(permissions, Permission):
                    _permissions = [permissions._json]
                else:
                    _permissions = [permissions]

            _scope: list = []

            if scope:
                if isinstance(scope, list):
                    if all(isinstance(guild, Guild) for guild in scope):
                        _scope.append(guild.id for guild in scope)
                    elif all(isinstance(guild, int) for guild in scope):
                        _scope.append(guild for guild in scope)
                else:
                    _scope.append(scope)

            for guild in _scope:
                payload: ApplicationCommand = ApplicationCommand(
                    type=_type,
                    guild_id=guild,
                    name=name,
                    description=_description,
                    options=_options,
                    default_permission=_default_permission,
                )
                if self.automate_sync:
                    self.loop.run_until_complete(self.synchronize(payload, _permissions))

            return self.event(coro, name=f"command_{name}")

        return decorator

    def component(self, component: Union[Button, SelectMenu]) -> Callable[..., Any]:
        """
        A decorator for handling interaction responses to components.

        :param component: The component you wish to callback for.
        :type component: Union[Button, SelectMenu]
        :return: A callable response.
        :rtype: Callable[..., Any]
        """

        def decorator(coro: Coroutine) -> Any:
            payload: Component = Component(**component._json)
            return self.event(coro, name=f"autocomplete_{payload.custom_id}")

        return decorator

    def autocomplete(self, name: str) -> Callable[..., Any]:
        """
        A decorator for handling autocompletion fields with commands.

        :param name: The name of the option to autocomplete.
        :type name: str
        :return: A callable response.
        :rtype: Callable[..., Any]
        """

        def decorator(coro: Coroutine) -> Any:
            return self.event(coro, name=f"autocomplete_{name}")

        return decorator

    async def raw_socket_create(self, data: Dict[Any, Any]) -> Dict[Any, Any]:
        """
        This is an internal function that takes any gateway socket event
        and then returns the data purely basedd off of what it does in
        the client instantiation class.

        :param data: The data that is returned
        :type data: Dict[Any, Any]
        :return: A dictionary of raw data.
        :rtype: Dict[Any, Any]
        """
        return data

    async def raw_guild_create(self, guild) -> None:
        """
        This is an internal function that caches the guild creates on ready.

        :param guild: The guild object data in question.
        :type guild: Guild
        """
        self.http.cache.guilds.add(Item(id=guild.id, value=guild))
