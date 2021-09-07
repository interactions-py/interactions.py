from asyncio import AbstractEventLoop, get_running_loop
from typing import Any, Callable, Coroutine, Dict, List, Optional, Union

from interactions.enums import ApplicationCommandType
from interactions.models.command import ApplicationCommand, Option, Permission

from .api.dispatch import Listener
from .api.gateway import WebSocket
from .api.http import Request
from .api.models.guild import Guild
from .api.models.intents import Intents


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

    loop: AbstractEventLoop
    intents: Optional[Union[Intents, List[Intents]]]
    http: Request
    websocket: WebSocket
    token: str

    def __init__(
        self, token: str, intents: Optional[Union[Intents, List[Intents]]] = Intents.DEFAULT
    ) -> None:
        """
        :param token: The token of the application for authentication and connection.
        :type token: str
        :param intents: The intents you wish to pass through the client. Defaults to :meth:`interactions.api.models.Intents.DEFAULT` or ``513``.
        :type intents: typing.Optional[typing.Union[interactions.api.models.Intents, typing.List[Intents]]]
        :return: None
        """
        if isinstance(intents, list):
            for intent in intents:
                self.intents |= intent
        else:
            self.intents = intents

        self.loop = get_running_loop()
        self.listener = Listener()
        self.http = Request(token)
        self.websocket = WebSocket(intents=self.intents)
        self.token = token

    async def login(self, token: str) -> None:
        """Makes a login with the Discord API."""
        while not self.websocket.closed:
            await self.websocket.connect(token)

    def start(self) -> None:
        """Starts the client session."""
        self.loop.run_until_complete(self.login(self.token))

    def event(self, coro: Coroutine) -> Callable[..., Any]:
        self.websocket.dispatch.register(coro)
        return coro

    def command(
        self,
        *,
        type: Optional[Union[str, int, ApplicationCommandType]] = ApplicationCommandType.CHAT_INPUT,
        name: str,
        description: Optional[str] = None,
        guild: Optional[Union[int, Guild]] = None,
        guilds: Optional[List[Union[int, Guild]]] = None,
        options: Optional[List[Option]] = None,
        default_permission: Optional[bool] = None,
        permissions: Optional[List[Permission]] = None,
        connector: Optional[Dict[str, str]] = None
    ) -> Callable[..., Any]:
        """
        A decorator for registering an application command to the Discord API,
        as well as being able to listen for ``INTERACTION_CREATE`` dispatched
        gateway events.

        .. note::
            If you don't pass in ``options`` in the decorator but add them to the
            coroutine method underneath the decorator, the options will be
            automatically generated for you. It will also attempt to read a docstring
            if one is present in the coroutine method to register the description
            of the option for you.

        :param type: The type of application command to register.
        :type type: typing.Optional[typing.Union[str, int, interactions.enums.ApplicationCommandType]]
        :param name: The name of the application command.
        :type name: str
        :param description: The description of the application command. **This only applies for "slash"/chat-input commands.**
        :type description: typing.Optional[str]
        :param guild: The guild you wish to register the application command under. Leaving this empty defaults to a **global** command.
        :type guild: typing.Optional[typing.Union[int, interactions.api.models.guild.Guild]]
        :param guilds: An alias of the ``guild`` keyword-argument if you wish to enter in a list instead.
        :type guilds: typing.Optional[typing.List[typing.Union[int, interactions.api.models.guild.Guild]]]
        :param options: The "arguments"/options of the application command. **This only applies for "slash"/chat-input commands.**
        :type options: typing.Optional[typing.List[interactions.models.command.Option]]
        :param default_permission: The default permission of the application command. Leave this empty if you don't want to touch permissions.
        :type default_permission: typing.Optional[bool]
        :param permissions: Given criterion/permissions for the application command's user to meet in order to use.
        :type permissions: typing.Optional[typing.List[interactions.models.command.Permission]]
        :param connector: A connector to have non-English native option names but register currently in the coroutine method.
        :type connector: typing.Optional[typing.Dict[str, str]]
        :return: typing.Callable[..., typing.Any]
        """
        _guilds = []

        if guild is None and guilds is not None:
            for _guild in guilds:
                if isinstance(_guild, Guild):
                    _guilds.append(_guild.id)
                else:
                    _guilds.append(_guild)
        else:
            _guilds[0] = guild.id if isinstance(guild, Guild) else guild

        command = ApplicationCommand(
            type=type,
            name=str,
            description=description,
            options=options,
            default_permission=default_permission,
            permissions=permissions
        )
        # we need to make a "me" class instance of the bot's information as some class.
        # route = f"/applications/{self.me.id}"

        if len(_guilds) >= 2:
            for _guild in _guilds:
                command.guild_id = _guild
                # route += "/guilds/{_guild}/commands"
                # Add in the HTTP request call here for adding application commands based on a guild.
                # something like: self.http.request(Route("POST", f"{route}"), json=command) ?
                ...
        else:
            # route += "/commands"
            ...