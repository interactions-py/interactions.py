from asyncio import AbstractEventLoop, get_event_loop
from typing import Any, Callable, Coroutine, List, Optional, Union

from .api.cache import Cache
from .api.dispatch import Listener
from .api.error import JSONException
from .api.gateway import WebSocket
from .api.http import HTTPClient
from .api.models.guild import Guild
from .api.models.intents import Intents
from .api.models.user import User
from .enums import ApplicationCommandType
from .models.command import Option


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
        """
        Makes a login with the Discord API.

        :param token: The application token needed for authorization.
        :type token: str
        :return: None
        """

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
        self.websocket.dispatch.register(
            coro, name=coro.__name__ if coro.__name__.startswith("on") else "on_interaction_create"
        )
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
        # permissions: Optional[List[Permission]] = None,
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

        def decorator(coro: Coroutine) -> Any:
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

            for interaction in self.cache.interactions:
                if interaction.value.name == name:
                    raise Exception("We cannot overwrite this, but we should be syncing.")
                    # make a call to our internal sync method instead of an exception.

            for guild in _scope:
                payload: dict = {
                    "type": type.value if isinstance(type, ApplicationCommandType) else type,
                    "name": name,
                    "description": _description,
                    "options": _options,
                    "default_permission": _default_permission,
                }

                if self.me is None:
                    data = self.loop.run_until_complete(self.http.get_self())
                    self.me = User(**data)

                request = self.loop.run_until_complete(
                    self.http.create_application_command(self.me.id, data=payload, guild_id=guild)
                )

                if request.get("code"):
                    raise JSONException(request["code"])  # todo: work on this pls

                # self.cache.add_interaction(
                #    id=_att["application_id"], interaction=ApplicationCommand(**_payload)
                # )

                return self.event(coro)

        return decorator
