from asyncio import get_event_loop
from logging import Logger, StreamHandler, basicConfig, getLogger
from typing import Any, Callable, Coroutine, Dict, List, Optional, Union

from interactions.api.models.gw import Presence

from .api.cache import Cache
from .api.cache import Item as Build
from .api.error import InteractionException, JSONException
from .api.gateway import WebSocket
from .api.http import HTTPClient
from .api.models.guild import Guild
from .api.models.intents import Intents
from .api.models.team import Application
from .base import CustomFormatter, Data
from .enums import ApplicationCommandType
from .models.command import ApplicationCommand, Option
from .models.component import Button, Component, Modal, SelectMenu

basicConfig(level=Data.LOGGER)
log: Logger = getLogger("client")
stream: StreamHandler = StreamHandler()
stream.setLevel(Data.LOGGER)
stream.setFormatter(CustomFormatter())
log.addHandler(stream)
_token: str = ""  # noqa
_cache: Cache = Cache()


class Client:
    """
    A class representing the client connection to Discord's gateway and API via. WebSocket and HTTP.

    :ivar AbstractEventLoop loop: The main overall asynchronous coroutine loop in effect.
    :ivar Listener listener: An instance of :class:`interactions.api.dispatch.Listener`.
    :ivar Optional[Union[Intents, List[Intents]]] intents: The application's intents as :class:`interactions.api.models.Intents`.
    :ivar HTTPClient http: An instance of :class:`interactions.api.http.Request`.
    :ivar WebSocket websocket: An instance of :class:`interactions.api.gateway.WebSocket`.
    :ivar str token: The application token.
    """

    def __init__(
        self,
        token: str,
        intents: Optional[Union[Intents, List[Intents]]] = Intents.DEFAULT,
        disable_sync: Optional[bool] = False,
        log_level: Optional[int] = Data.LOGGER,
        shard: Optional[List[int]] = None,
        presence: Optional[Presence] = None,
    ) -> None:
        """
        :param token: The token of the application for authentication and connection.
        :type token: str
        :param intents?: The intents you wish to pass through the client. Defaults to :meth:`interactions.api.models.intents.Intents.DEFAULT` or ``513``.
        :type intents: Optional[Union[Intents, List[Intents]]]
        :param disable_sync?: Whether you want to disable automate synchronization or not.
        :type disable_sync: Optional[bool]
        :param log_level?: The logging level to set for the terminal. Defaults to what is set internally.
        :type log_level: Optional[int]
        :param presence?: The presence of the application when connecting.
        :type presence: Optional[Presence]
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
        self.http.token = token
        self.shard = shard
        self.presence = presence
        _token = token  # noqa: F841
        _cache = self.http.cache  # noqa: F841

        if disable_sync:  # you don't need to change this. this is already correct.
            self.automate_sync = False
            log.warning(
                "Automatic synchronization has been disabled. Interactions may need to be manually synchronized."
            )
        else:
            self.automate_sync = True

        Data.LOGGER = log_level

        if not self.me:
            data = self.loop.run_until_complete(self.http.get_current_bot_information())
            self.me = Application(**data)

    async def login(self, token: str) -> None:
        """
        Makes a login with the Discord API.

        :param token: The application token needed for authorization.
        :type token: str
        :return: None
        """
        while not self.websocket.closed:
            await self.websocket.connect(token, self.shard, self.presence)

    def start(self) -> None:
        """Starts the client session."""
        self.loop.run_until_complete(self.ready())

    async def ready(self) -> None:
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

        def register_events() -> None:
            self.websocket.dispatch.register(self.raw_socket_create)
            self.websocket.dispatch.register(self.raw_channel_create, "on_channel_create")
            self.websocket.dispatch.register(self.raw_message_create, "on_message_create")
            self.websocket.dispatch.register(self.raw_guild_create, "on_guild_create")

        try:
            register_events()
            await self.synchronize()
            ready = True
        except Exception as error:
            log.critical(f"Could not prepare the client: {error}")
        finally:
            if ready:
                log.debug("Client is now ready.")
                await self.login(self.token)

    async def synchronize(self, payload: Optional[ApplicationCommand] = None) -> None:
        """
        Synchronizes the command specified by checking through the
        currently registered application commands on the API and
        modifying if there is a detected chagne in structure.

        .. warning::
            This internal call does not need to be manually triggered,
            as it will automatically be done for you. Additionally,
            this will not delete unused commands for you.

        :param payload?: The payload/object of the command.
        :type payload: Optional[ApplicationCommand]
        """
        _guild = None
        if payload:
            _guild = str(payload.guild_id)

        commands: List[dict] = await self.http.get_application_command(
            application_id=self.me.id, guild_id=_guild
        )
        command_names: List[str] = [command["name"] for command in commands]

        async def create() -> None:
            """
            Creates a new application command in the API if one does not exist for it.
            """
            log.debug(
                f"Command {payload.name} was not found in the API, creating and adding to the cache."
            )
            request = await self.http.create_application_command(
                application_id=self.me.id, data=payload._json, guild_id=payload.guild_id
            )

            if request.get("code"):
                raise JSONException(request["code"])
            else:
                self.http.cache.interactions.add(Build(id=payload.name, value=payload))

        if commands:
            log.debug("Commands were found, checking for sync.")
            for command in commands:
                result: ApplicationCommand = ApplicationCommand(
                    application_id=command.get("application_id"),
                    id=command.get("id"),
                    type=command.get("type"),
                    guild_id=str(command.get("guild_id")),
                    name=command.get("name"),
                    description=command.get("description", ""),
                    default_permission=command.get("default_permission", False),
                    default_member_permissions=command.get("default_member_permissions", None),
                    version=command.get("version"),
                    name_localizations=command.get("name_localizations"),
                    description_localizations=command.get("description_localizations"),
                )

                if payload:
                    if payload.name in command_names:
                        log.debug(f"Checking command {payload.name} for syncing.")

                        if payload.name == result.name:
                            payload_name: str = payload.name

                            del result._json["name"]
                            del payload._json["name"]

                            if result._json != payload._json:
                                log.debug(
                                    f"Command {result.name} found unsynced, editing in the API and updating the cache."
                                )
                                payload._json["name"] = payload_name
                                request = await self.http.edit_application_command(
                                    application_id=self.me.id,
                                    data=payload._json,
                                    command_id=result.id,
                                    guild_id=result.guild_id,
                                )
                                self.http.cache.interactions.add(
                                    Build(id=payload.name, value=payload)
                                )

                                if request.get("code"):
                                    raise JSONException(request["code"])
                                break
                    else:
                        await create()
                else:
                    log.debug(f"Adding command {result.name} to cache.")
                    self.http.cache.interactions.add(Build(id=result.name, value=result))
        else:
            await create()

        cached_commands: List[dict] = [command for command in self.http.cache.interactions.view()]
        cached_command_names = [command["name"] for command in cached_commands]

        if cached_commands:
            for command in commands:
                if command["name"] not in cached_command_names:
                    log.debug(
                        f"Command {command['name']} was found in the API but never cached, deleting from the API and cache."
                    )
                    request = await self.http.delete_application_command(
                        application_id=self.me.id,
                        command_id=command["id"],
                        guild_id=command["guild_id"],
                    )

                    if request:
                        if request.get("code"):
                            raise JSONException(request["code"])

    def event(self, coro: Coroutine, name: Optional[str] = None) -> Callable[..., Any]:
        """
        A decorator for listening to dispatched events from the
        gateway.

        :param coro: The coroutine of the event.
        :type coro: Coroutine
        :param name?: The name of the event.
        :type name: Optional[str]
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
        # permissions: Optional[
        #     Union[Dict[str, Any], List[Dict[str, Any]], Permission, List[Permission]]
        # ] = None,
    ) -> Callable[..., Any]:
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
            if options:
                if (len(coro.__code__.co_varnames) + 1) < len(options):
                    raise InteractionException(
                        11,
                        message="You must have the same amount of arguments as the options of the command.",
                    )

            _type: int = 0
            if isinstance(type, ApplicationCommandType):
                _type: int = type.value
            else:
                _type: int = ApplicationCommandType(type).value

            _description: str = "" if description is None else description
            _options: list = []

            if options:
                if all(isinstance(option, Option) for option in options):
                    _options = [option._json for option in options]
                elif all(
                    isinstance(option, dict) and all(isinstance(value, str) for value in option)
                    for option in options
                ):
                    _options = [option for option in options]
                elif isinstance(options, Option):
                    _options = [options._json]
                else:
                    _options = [options]

            _default_permission: bool = True if default_permission is None else default_permission

            # TODO: Implement permission building and syncing.
            # _permissions: list = []

            # if permissions:
            #     if all(isinstance(permission, Permission) for permission in permissions):
            #         _permissions = [permission._json for permission in permissions]
            #     elif all(
            #         isinstance(permission, dict)
            #         and all(isinstance(value, str) for value in permission)
            #         for permission in permissions
            #     ):
            #         _permissions = [permission for permission in permissions]
            #     elif isinstance(permissions, Permission):
            #         _permissions = [permissions._json]
            #     else:
            #         _permissions = [permissions]

            _scope: list = []

            if scope:
                if isinstance(scope, list):
                    if all(isinstance(guild, Guild) for guild in scope):
                        [_scope.append(guild.id) for guild in scope]
                    elif all(isinstance(guild, int) for guild in scope):
                        [_scope.append(guild) for guild in scope]
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
                    self.loop.run_until_complete(self.synchronize(payload))

            return self.event(coro, name=name)

        return decorator

    def component(self, component: Union[Button, SelectMenu]) -> Callable[..., Any]:
        """
        A decorator for listening to ``INTERACTION_CREATE`` dispatched gateway
        events involving components.

        The structure for a component callback:

        .. code-block:: python

            @component(interactions.Button(
                style=interactions.ButtonStyle.PRIMARY,
                label="click me!",
                custom_id="click_me_button",
            ))
            async def button_response(ctx):
                ...

        The context of the component callback decorator inherits the same
        as of the command decorator.

        :param component: The component you wish to callback for.
        :type component: Union[Button, SelectMenu]
        :return: A callable response.
        :rtype: Callable[..., Any]
        """

        def decorator(coro: Coroutine) -> Any:
            payload: Component = Component(**component._json)
            return self.event(coro, name=payload.custom_id)

        return decorator

    def autocomplete(self, name: str) -> Callable[..., Any]:
        """
        A decorator for listening to ``INTERACTION_CREATE`` dispatched gateway
        events involving autocompletion fields.

        The structure for an autocomplete callback:

        .. code-block:: python

            @autocomplete("option_name")
            async def autocomplete_choice_list(ctx):
                await ctx.populate([...])

        :param name: The name of the option to autocomplete.
        :type name: str
        :return: A callable response.
        :rtype: Callable[..., Any]
        """

        def decorator(coro: Coroutine) -> Any:
            return self.event(coro, name=f"autocomplete_{name}")

        return decorator

    def modal(self, modal: Modal) -> Callable[..., Any]:
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

        :param modal: The modal you wish to callback for.
        :type modal: Modal
        :return: A callable response.
        :rtype: Callable[..., Any]
        """

        def decorator(coro: Coroutine) -> Any:
            return self.event(coro, name=f"modal_{modal.custom_id}")

        return decorator

    async def raw_socket_create(self, data: Dict[Any, Any]) -> Dict[Any, Any]:
        """
        This is an internal function that takes any gateway socket event
        and then returns the data purely based off of what it does in
        the client instantiation class.

        :param data: The data that is returned
        :type data: Dict[Any, Any]
        :return: A dictionary of raw data.
        :rtype: Dict[Any, Any]
        """

        return data

    async def raw_channel_create(self, channel) -> dict:
        """
        This is an internal function that caches the channel creates when dispatched.

        :param channel: The channel object data in question.
        :type channel: Channel
        :return: The channel as a dictionary of raw data.
        :rtype: dict
        """
        self.http.cache.channels.add(Build(id=channel.id, value=channel))

        return channel._json

    async def raw_message_create(self, message) -> dict:
        """
        This is an internal function that caches the message creates when dispatched.

        :param message: The message object data in question.
        :type message: Message
        :return: The message as a dictionary of raw data.
        :rtype: dict
        """
        self.http.cache.messages.add(Build(id=message.id, value=message))

        return message._json

    async def raw_guild_create(self, guild) -> dict:
        """
        This is an internal function that caches the guild creates on ready.

        :param guild: The guild object data in question.
        :type guild: Guild
        :return: The guild as a dictionary of raw data.
        :rtype: dict
        """
        self.http.cache.guilds.add(Build(id=str(guild.id), value=guild))

        return guild._json
