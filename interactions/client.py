from asyncio import AbstractEventLoop, get_event_loop
from typing import Any, Callable, Coroutine, List, NoReturn, Optional, Union

from .api.cache import Cache
from .api.dispatch import Listener
from .api.gateway import WebSocket
from .api.http import HTTPClient
from .api.models.guild import Guild
from .api.models.intents import Intents
from .api.models.user import User
from .enums import ApplicationCommandType
from .models.command import Option, Permission


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
    http: HTTPClient
    cache: Cache
    websocket: WebSocket
    me: Optional[User]
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

        self.loop = get_event_loop()
        self.listener = Listener()
        self.cache = Cache()
        self.http = HTTPClient(token)
        self.websocket = WebSocket(intents=self.intents)
        self.me = None
        self.token = token

    async def login(self, token: str) -> None:
        """Makes a login with the Discord API."""

        if self.me is None:
            data = await self.http.get_self()
            self.me = User(**data)

        while not self.websocket.closed:
            await self.websocket.connect(token)

    def start(self) -> None:
        """Starts the client session."""
        self.loop.run_until_complete(self.login(self.token))

    def event(self, coro: Coroutine) -> Callable[..., Any]:
        """
        A decorator for listening to dispatched events from the
        gateway.

        :return: typing.Callable[..., typing.Any]
        """
        self.websocket.dispatch.register(coro)
        return coro

    def command(
        self,
        name: str,
        type: Optional[Union[str, int, ApplicationCommandType]] = ApplicationCommandType.CHAT_INPUT,
        description: Optional[str] = None,
        scope: Optional[Union[int, Guild, List[int], List[Guild]]] = None,
        options: Optional[List[Option]] = None,
        default_permission: Optional[bool] = None,
        permissions: Optional[List[Permission]] = None,
    ) -> Callable[..., Any]:
        """
        A decorator for registering an application command to the Discord API,
        as well as being able to listen for ``INTERACTION_CREATE`` dispatched
        gateway events.
        """

        def decorator(coro: Coroutine) -> Any:

            guilds: List[NoReturn, int] = [None]
            _description: str = (
                "No description set." if (description is None and type == 1) else description
            )
            _options: list = [] if options is None else options
            _default_permission: bool = True if default_permission is None else default_permission
            _permissions: list = [] if permissions is None else permissions

            if scope is not None:
                print(f"Scope is {scope}")
                if isinstance(scope, list):
                    if len(scope) >= 1:
                        # if isinstance(scope, List[Guild]):

                        # TODO: Relook guild logic.
                        if isinstance(scope[0], Guild):
                            guilds.append(guild.id for guild in scope)
                        else:
                            if isinstance(scope, list):
                                guilds.append(iter(scope))
                else:
                    guilds[0] = scope

            for interaction in self.cache.interactions:
                if interaction.value.name == name:
                    raise Exception("We cannot overwrite this, but we should be syncing.")
                    # make a call to our internal sync method instead of an exception.

            # path: str = f"/applications/{self.me.id}"

            for guild in guilds:
                #  += f"/guilds/{guild}" if guild else "/commands"
                _payload = {
                    "type": type,
                    "name": name,
                    "description": _description,
                    "guild_id": guild,
                    "options": _options,
                    "default_permission": _default_permission,
                    "permissions": _permissions,
                }

                if guild is None:
                    _payload.pop("guild_id")  # why need it?

                # self.http.request(Route("POST", path), data=payload._json)

                if self.me is None:
                    data = self.loop.run_until_complete(self.http.get_self())
                    # You think it doesn't work but it does on boot.
                    self.me = User(**data)

                self.loop.create_task(
                    self.http.create_application_command(
                        self.me._json["id"], data=_payload, guild_id=guild
                    )
                )

            self.event(coro)

        return decorator
