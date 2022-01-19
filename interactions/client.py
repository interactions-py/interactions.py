import sys
from asyncio import get_event_loop
from importlib import import_module
from importlib.util import resolve_name
from logging import Logger, getLogger
from typing import Any, Callable, Coroutine, Dict, List, Optional, Union

from interactions.api.dispatch import Listener
from interactions.api.models.misc import Snowflake

from .api.cache import Cache
from .api.cache import Item as Build
from .api.error import InteractionException
from .api.gateway import WebSocket
from .api.http import HTTPClient
from .api.models.flags import Intents
from .api.models.guild import Guild
from .api.models.gw import Presence
from .api.models.team import Application
from .decor import command
from .decor import component as _component
from .enums import ApplicationCommandType
from .models.command import ApplicationCommand, Option
from .models.component import Button, Modal, SelectMenu

log: Logger = getLogger("client")
_token: str = ""  # noqa
_cache: Optional[Cache] = None


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
        self.extensions = {}
        _token = token  # noqa: F841
        _cache = self.http.cache  # noqa: F841

        if disable_sync:
            self.automate_sync = False
            log.warning(
                "Automatic synchronization has been disabled. Interactions may need to be manually synchronized."
            )
        else:
            self.automate_sync = True

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
            self.websocket.dispatch.register(self.raw_message_create, "on_message_update")
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

    async def compare_sync(self, payload: dict, result: dict) -> bool:
        """
        This compares the payloads between the Client and the API such that
        it can mitigate synchronisation API calls.
        """

        # This needs to be redone after discord updates their docs.

        _res = True

        for attrs in ["type", "guild_id", "name", "description", "options", "default_permission"]:
            if attrs == "options" and payload["type"] != 1:
                continue

            if attrs == "guild_id":
                if str(payload.get(attrs, None)) == result.get(attrs, None):
                    continue

            if payload.get(attrs, None) != result.get(attrs, (None if attrs != "options" else [])):
                _res = False
                return _res

        return _res

    async def synchronize(self, payload: Optional[ApplicationCommand] = None) -> None:
        """
        Synchronizes the command specified by checking through the
        currently registered application commands on the API and
        modifying if there is a detected change in structure.

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

        async def create(data: ApplicationCommand) -> None:
            """
            Creates a new application command in the API if one does not exist for it.
            :param data: The data of the command to create.
            :type data: ApplicationCommand
            """
            log.debug(
                f"Command {data.name} was not found in the API, creating and adding to the cache."
            )

            _created_command = ApplicationCommand(
                **(
                    await self.http.create_application_command(
                        application_id=self.me.id, data=data._json, guild_id=data.guild_id
                    )
                )
            )

            self.http.cache.interactions.add(
                Build(id=_created_command.name, value=_created_command)
            )

        if commands:
            log.debug("Commands were found, checking for sync.")
            for command in commands:
                result: ApplicationCommand = ApplicationCommand(
                    application_id=command.get("application_id"),
                    id=command.get("id"),
                    type=command.get("type"),
                    guild_id=str(command["guild_id"]) if command.get("guild_id") else None,
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

                            _cmp = await self.compare_sync(payload._json, result._json)

                            if not _cmp:
                                log.debug(
                                    f"Command {result.name} found unsynced, editing in the API and updating the cache."
                                )
                                payload._json["name"] = payload_name
                                _updated = ApplicationCommand(
                                    **await self.http.edit_application_command(
                                        application_id=self.me.id,
                                        data=payload._json,
                                        command_id=result.id,
                                        guild_id=result._json.get("guild_id"),
                                    )
                                )
                                self.http.cache.interactions.add(
                                    Build(id=_updated.name, value=_updated)
                                )
                                break
                    else:
                        await create(payload)
                else:
                    log.debug(f"Adding command {result.name} to cache.")
                    self.http.cache.interactions.add(Build(id=result.name, value=result))
        else:
            if payload:
                await create(payload)

        cached_commands: List[dict] = [command for command in self.http.cache.interactions.view]
        cached_command_names = [
            command.get("name") for command in cached_commands if command.get("name")
        ]

        log.debug(f"Cached commands: {cached_commands}")
        log.debug(f"Cached command names: {cached_command_names}")

        if cached_commands:
            for command in commands:
                if command["name"] not in cached_command_names:
                    log.debug(
                        f"Command {command['name']} was found in the API but never cached, deleting from the API and cache."
                    )
                    await self.http.delete_application_command(
                        application_id=self.me.id,
                        command_id=command["id"],
                        guild_id=command.get("guild_id"),
                    )

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
        self.websocket.dispatch.register(coro, name)
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
        :return: A callable response.
        :rtype: Callable[..., Any]
        """

        def decorator(coro: Coroutine) -> Callable[..., Any]:
            if not name:
                raise InteractionException(11, message="Your command must have a name.")

            if type == ApplicationCommandType.CHAT_INPUT and not description:
                raise InteractionException(
                    11, message="Chat-input commands must have a description."
                )

            if not len(coro.__code__.co_varnames):
                raise InteractionException(
                    11, message="Your command needs at least one argument to return context."
                )
            if options and (len(coro.__code__.co_varnames) + 1) < len(options):
                raise InteractionException(
                    11,
                    message="You must have the same amount of arguments as the options of the command.",
                )

            commands: List[ApplicationCommand] = command(
                type=type,
                name=name,
                description=description,
                scope=scope,
                options=options,
                default_permission=default_permission,
            )

            if self.automate_sync:
                [self.loop.run_until_complete(self.synchronize(command)) for command in commands]

            return self.event(coro, name=f"command_{name}")

        return decorator

    def message_command(
        self,
        *,
        name: Optional[str] = None,
        scope: Optional[Union[int, Guild, List[int], List[Guild]]] = None,
        default_permission: Optional[bool] = None,
    ) -> Callable[..., Any]:
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

        :param name: The name of the application command. This *is* required but kept optional to follow kwarg rules.
        :type name: Optional[str]
        :param scope?: The "scope"/applicable guilds the application command applies to. Defaults to ``None``.
        :type scope: Optional[Union[int, Guild, List[int], List[Guild]]]
        :param default_permission?: The default permission of accessibility for the application command. Defaults to ``True``.
        :type default_permission: Optional[bool]
        :return: A callable response.
        :rtype: Callable[..., Any]
        """

        def decorator(coro: Coroutine) -> Callable[..., Any]:
            if not name:
                raise InteractionException(11, message="Your command must have a name.")

            if not len(coro.__code__.co_varnames):
                raise InteractionException(
                    11,
                    message="Your command needs at least one argument to return context.",
                )

            commands: List[ApplicationCommand] = command(
                type=ApplicationCommandType.MESSAGE,
                name=name,
                scope=scope,
                default_permission=default_permission,
            )

            if self.automate_sync:
                [self.loop.run_until_complete(self.synchronize(command)) for command in commands]

            return self.event(coro, name=f"command_{name}")

        return decorator

    def user_command(
        self,
        *,
        name: Optional[str] = None,
        scope: Optional[Union[int, Guild, List[int], List[Guild]]] = None,
        default_permission: Optional[bool] = None,
    ) -> Callable[..., Any]:
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

        :param name: The name of the application command. This *is* required but kept optional to follow kwarg rules.
        :type name: Optional[str]
        :param scope?: The "scope"/applicable guilds the application command applies to. Defaults to ``None``.
        :type scope: Optional[Union[int, Guild, List[int], List[Guild]]]
        :param default_permission?: The default permission of accessibility for the application command. Defaults to ``True``.
        :type default_permission: Optional[bool]
        :return: A callable response.
        :rtype: Callable[..., Any]
        """

        def decorator(coro: Coroutine) -> Callable[..., Any]:
            if not name:
                raise InteractionException(11, message="Your command must have a name.")

            if not len(coro.__code__.co_varnames):
                raise InteractionException(
                    11,
                    message="Your command needs at least one argument to return context.",
                )

            commands: List[ApplicationCommand] = command(
                type=ApplicationCommandType.USER,
                name=name,
                scope=scope,
                default_permission=default_permission,
            )

            if self.automate_sync:
                [self.loop.run_until_complete(self.synchronize(command)) for command in commands]

            return self.event(coro, name=f"command_{name}")

        return decorator

    def component(self, component: Union[str, Button, SelectMenu]) -> Callable[..., Any]:
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
        :rtype: Callable[..., Any]
        """

        def decorator(coro: Coroutine) -> Any:
            payload: str = (
                _component(component).custom_id
                if isinstance(component, (Button, SelectMenu))
                else component
            )
            return self.event(coro, name=f"component_{payload}")

        return decorator

    def autocomplete(
        self, name: str, command: Union[ApplicationCommand, int]
    ) -> Callable[..., Any]:
        """
        A decorator for listening to ``INTERACTION_CREATE`` dispatched gateway
        events involving autocompletion fields.

        The structure for an autocomplete callback:

        .. code-block:: python

            @autocomplete("option_name")
            async def autocomplete_choice_list(ctx, user_input: str = ""):
                await ctx.populate([...])

        :param name: The name of the option to autocomplete.
        :type name: str
        :param command: The command or commnd ID with the option.
        :type command: Union[ApplicationCommand, int]
        :return: A callable response.
        :rtype: Callable[..., Any]
        """
        _command: Union[Snowflake, int] = (
            command.id if isinstance(command, ApplicationCommand) else command
        )

        def decorator(coro: Coroutine) -> Any:
            return self.event(coro, name=f"autocomplete_{_command}_{name}")

        return decorator

    def modal(self, modal: Modal) -> Callable[..., Any]:
        """
        A decorator for listening to ``INTERACTION_CREATE`` dispatched gateway
        events involving modals.

        .. error::
            This feature is currently under experimental/**beta access**
            to those whitelisted for testing. Currently using this will
            present you with an error with the modal not working.

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

    def load(self, name: str, package: Optional[str] = None) -> None:
        """
        "Loads" an extension off of the current client by adding a new class
        which is imported from the library.

        :param name: The name of the extension.
        :type name: str
        :param package?: The package of the extension.
        :type package: Optional[str]
        """
        _name: str = resolve_name(name, package)

        if _name in self.extensions:
            log.error(f"Extension {name} has already been loaded. Skipping.")

        module = import_module(name, package)

        try:
            setup = getattr(module, "setup")
            setup(self)
        except Exception as error:
            del sys.modules[name]
            log.error(f"Could not load {name}: {error}. Skipping.")
        else:
            log.debug(f"Loaded extension {name}.")
            self.extensions[_name] = module

    def remove(self, name: str, package: Optional[str] = None) -> None:
        """
        Removes an extension out of the current client from an import resolve.

        :param name: The name of the extension.
        :type name: str
        :param package?: The package of the extension.
        :type package: Optional[str]
        """
        _name: str = resolve_name(name, package)
        module = self.extensions.get(_name)

        if module not in self.extensions:
            log.error(f"Extension {name} has not been loaded before. Skipping.")

        log.debug(f"Removed extension {name}.")
        del sys.modules[_name]
        del self.extensions[_name]

    def reload(self, name: str, package: Optional[str] = None) -> None:
        """
        "Reloads" an extension off of current client from an import resolve.

        :param name: The name of the extension.
        :type name: str
        :param package?: The package of the extension.
        :type package: Optional[str]
        """
        _name: str = resolve_name(name, package)
        module = self.extensions.get(_name)

        if module is None:
            log.warning(f"Extension {name} could not be reloaded because it was never loaded.")
            self.extend(name, package)

        self.remove(name, package)
        self.load(name, package)

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
        self.http.cache.self_guilds.add(Build(id=str(guild.id), value=guild))

        return guild._json


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

        def setup(bot):
            CoolCode(bot)
    """

    client: Client
    commands: Optional[List[ApplicationCommand]]
    listeners: Optional[List[Listener]]

    def __new__(cls, bot: Client) -> None:
        cls.client = bot
        cls.commands = []
        cls.listeners = []

        for _, content in cls.__dict__.items():
            if not content.startswith("__") or content.startswith("_"):
                if "on_" in content:
                    cls.listeners.append(content)
                else:
                    cls.commands.append(content)

        for _command in cls.commands:
            cls.client.command(**_command)
