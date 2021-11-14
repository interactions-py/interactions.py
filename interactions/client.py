from asyncio import get_event_loop
from logging import Logger, basicConfig, getLogger
from typing import Any, Callable, Coroutine, Dict, List, Optional, Union

from .api.cache import Cache, Item
from .api.error import InteractionException, JSONException
from .api.gateway import WebSocket
from .api.http import HTTPClient
from .api.models.guild import Guild
from .api.models.intents import Intents
from .api.models.team import Application
from .base import Data
from .enums import ApplicationCommandType
from .models.command import ApplicationCommand, Option
from .models.component import Button, Component, SelectMenu

cache: Cache = Cache()

basicConfig(level=Data.LOGGER)
log: Logger = getLogger("client")


class Client:
    """
    A class representing the client connection to Discord's gateway and API via. WebSocket and HTTP.

    :ivar asyncio.AbstractEventLoop loop: The main overall asynchronous coroutine loop in effect.
    :ivar interactions.api.dispatch.Listener listener: An instance of :class:`interactions.api.dispatch.Listener`.
    :ivar typing.Optional[typing.Union[interactions.api.models.intents.Intents, typing.List[interactions.api.models.intentsIntents]]] intents: The application's intents as :class:`interactions.api.models.Intents`.
    :ivar interactions.api.http.Request http: An instance of :class:`interactions.api.http.Request`.
    :ivar interactions.api.gateway.WebSocket websocket: An instance of :class:`interactions.api.gateway.WebSocket`.
    :ivar str token: The application token.
    """

    def __init__(
        self, token: str, intents: Optional[Union[Intents, List[Intents]]] = Intents.DEFAULT
    ) -> None:
        """
        :param token: The token of the application for authentication and connection.
        :type token: str
        :param intents: The intents you wish to pass through the client. Defaults to :meth:`interactions.api.models.intents.Intents.DEFAULT` or ``513``.
        :type intents: typing.Optional[typing.Union[interactions.api.models.Intents, typing.List[Intents]]]
        :return: None
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
        self.token = token
        cache.token = token

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
        :return: None
        """
        while not self.websocket.closed:
            await self.websocket.connect(token)

    def start(self) -> None:
        """Starts the client session."""
        self.synchronize_commands()
        self.loop.run_until_complete(self.login(self.token))

    def synchronize_commands(self) -> None:
        """
        Synchronizes all of the commands that are currently existing,
        and updates those that are currently not being used.

        .. warning::
            This internal call does not need to be manually triggered,
            as it will automatically be done for you. Additionally,
            this will not delete unused commands for you.

        :return: None
        """
        commands = self.loop.run_until_complete(self.http.get_application_command(self.me.id))
        change: list = []

        for command in commands:
            _command: Optional[Item] = cache.interactions.get(command["id"])
            if _command:
                if ApplicationCommand(**command) == _command:
                    log.warning(f"Detected change to command ID {command.id}.")
                    change.append(command)
            else:
                cache.interactions.add(Item(command["id"], ApplicationCommand(**command)))

        for command in change:
            log.debug(f"Updated command {command.id}.")
            self.http.edit_application_command(
                application_id=self.me.id,
                data=command["data"],
                command_id=command["id"],
                guild_id=command.get("guild_id"),
            )
            cache.interactions.add(Item(command["id"], ApplicationCommand(**command)))

    def event(self, coro: Coroutine, name: Optional[str] = None) -> Callable[..., Any]:
        """
        A decorator for listening to dispatched events from the
        gateway.

        :param coro: The coroutine of the event.
        :type coro: typing.Coroutine
        :return: typing.Callable[..., typing.Any]
        """
        self.websocket.dispatch.register(coro, name=name)
        return coro

    def command(
        self,
        *,
        type: Optional[Union[str, int, ApplicationCommandType]] = ApplicationCommandType.CHAT_INPUT,
        name: Optional[str] = None,
        description: Optional[str] = None,
        scope: Optional[Union[int, Guild, List[int], List[Guild]]] = None,
        options: Optional[List[Option]] = None,
        default_permission: Optional[bool] = None
        # permissions: Optional[List[Permission]] = None
    ) -> Callable[..., Any]:
        """
        A decorator for registering an application command to the Discord API,
        as well as being able to listen for ``INTERACTION_CREATE`` dispatched
        gateway events.

        :param type: The type of application command. Defaults to :meth:`interactions.enums.ApplicationCommandType.CHAT_INPUT` or ``1``.
        :type type: typing.Optional[typing.Union[str, int, interactions.enums.ApplicationCommandType]]
        :param name: The name of the application command. This *is* required but kept optional to follow kwarg rules.
        :type name: typing.Optional[str]
        :param description: The description of the application command. This should be left blank if you are not using ``CHAT_INPUT``.
        :type description: typing.Optional[str]
        :param scope: The "scope"/applicable guilds the application command applies to.
        :type scope: typing.Optional[typing.Union[int, interactions.api.models.guild.Guild, typing.List[int], typing.List[interactions.api.models.guild.Guild]]]
        :param options: The "arguments"/options of an application command. This should bel eft blank if you are not using ``CHAT_INPUT``.
        :type options: typing.Optional[typing.List[interactions.models.command.Option]]
        :param default_permission: The default permission of accessibility for the application command. Defaults to ``True``.
        :type default_permission: typing.Optional[bool]
        :return: typing.Callable[..., typing.Any]
        """
        if not name:
            raise Exception("Command must have a name!")

        if type == ApplicationCommandType.CHAT_INPUT and not description:
            raise Exception("Chat-input commands must have a description!")

        def decorator(coro: Coroutine) -> Any:
            if "ctx" not in coro.__code__.co_varnames:
                raise InteractionException(11)
            if isinstance(type, ApplicationCommandType):
                _type: int = type.value
            if isinstance(type, str):
                _type: int = ApplicationCommandType.type.value
            else:
                _type = type

            _description: str = "" if description is None else description
            _options: list = [] if options is None else options
            _default_permission: bool = True if default_permission is None else default_permission
            # _permissions: list = [] if permissions is None else permissions
            _scope: list = []

            if isinstance(scope, list):
                if all(isinstance(x, Guild) for x in scope):
                    _scope.append(guild.id for guild in scope)
                elif all(isinstance(x, int) for x in scope):
                    _scope.append(guild for guild in scope)
            else:
                _scope.append(scope)

            for guild in _scope:
                payload: ApplicationCommand = ApplicationCommand(
                    type=_type,
                    name=name,
                    description=_description,
                    options=_options,
                    default_permission=_default_permission,
                )

                request = self.loop.run_until_complete(
                    self.http.create_application_command(
                        self.me.id, data=payload._json, guild_id=guild
                    )
                )

                if request.get("code"):
                    raise JSONException(request["code"])  # TODO: work on this pls

            for interaction in cache.interactions.values:
                if interaction.values[interaction].value.name == name:
                    self.synchronize_commands(name)
                    # TODO: make a call to our internal sync method instead of an exception.
                else:
                    cache.interactions.add(Item(id=request["application_id"], value=payload))

            return self.event(coro, name=name)

        return decorator

    def component(self, component: Union[Button, SelectMenu]) -> Callable[..., Any]:
        def decorator(coro: Coroutine) -> Any:
            payload: Component = Component(
                type=component.type,
                custom_id=component._json.get("custom_id"),
                disabled=component._json.get("disabled"),
                style=component._json.get("style"),
                label=component._json.get("label"),
                emoji=component._json.get("emoji"),
                url=component._json.get("url"),
                options=component._json.get("options"),
                placeholder=component._json.get("placeholder"),
                min_values=component._json.get("min_values"),
                max_values=component._json.get("max_values"),
                components=component._json.get("components"),
            )

            return self.event(coro, name=payload.custom_id if payload.custom_id else coro.__name__)

        return decorator

    async def raw_socket_create(self, data: Dict[Any, Any]) -> None:
        """
        This is an internal function that takes any gateway socket event
        and then returns the data purely basedd off of what it does in
        the client instantiation class.

        :param data: The data that is returned
        :type data: typing.Dict[typing.Any, typing.Any]
        :return: None
        """
        return data

    async def raw_guild_create(self, guild) -> None:
        """
        This is an internal function that caches the guild creates on ready.

        :param guild: The guild object data in question.
        :type guild: interactions.api.model.guild.Guild
        :return: None.
        """
        cache.guilds.add(Item(id=guild.id, value=guild))
