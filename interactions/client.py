from asyncio import AbstractEventLoop, get_event_loop
from typing import Any, Callable, Coroutine, List, Optional, Union

from .api.cache import Cache
from .api.dispatch import Listener
from .api.gateway import WebSocket
from .api.http import Request
from .api.models.guild import Guild
from .api.models.intents import Intents
from .api.models.user import User
from .enums import ApplicationCommandType
from .models.command import ApplicationCommand, Option, Permission


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
        self.http = Request(token)
        self.cache = Cache()
        self.websocket = WebSocket(intents=self.intents)
        self.me = None
        self.token = token

    async def login(self, token: str) -> None:
        """Makes a login with the Discord API."""
        # data = self.loop.run_until_complete(self.http.get_self())
        # self.me = User(**data)

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
        *,
        type: Optional[Union[str, int, ApplicationCommandType]] = ApplicationCommandType.CHAT_INPUT,
        name: Optional[str] = None,
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
        if not name:
            raise Exception("Command must have a name!")

        def decorator(coro: Coroutine) -> Any:
            _description: str = "" if description is None else description
            _options: list = [] if options is None else options
            _default_permission: bool = True if default_permission is None else default_permission
            _permissions: list = [] if permissions is None else permissions
            _scope: list = []

            # past method we used was pretty stupid to comb for instance-type
            # checking on what scope we had applicable on guild application
            # commands. this should be much better
            if isinstance(scope, List[Guild]):
                _scope.append(guild.id for guild in scope)
            elif isinstance(scope, List[int]):
                _scope.append(guild for guild in scope)
            else:
                _scope.append(scope)

            for interaction in self.cache.interactions:
                if name == interaction.value.name:
                    # self.synchronize()
                    raise Exception("Cannot overwrite an existing command.")

            for guild in _scope:
                # no need to pop guild_id because we want consistency
                # with model data. That way if people try to do smth.
                # like (ctx.slash.guild_id) it gives None for those
                # trying to build systems/infrastructures integrally
                # based on the application command design into their bots
                # so that it gives back what is/isn't.

                payload: ApplicationCommand = ApplicationCommand(
                    type=type,
                    name=name,
                    description=_description,
                    guild_id=guild,
                    options=_options,
                    default_permission=_default_permission,
                    permissions=_permissions,
                )
                request = self.http.create_application_command(
                    self.me._json["id"], data=payload, guild_id=guild
                )

                # set the loop and cache, this is a WAY simpler workaround
                # to our prior given issue with determining how we'll
                # handle mass caching -- let's just do it when we have an
                # explicit call made.
                self.cache.add_interaction(id=request["application_command"], interaction=payload)
                self.loop.create_task(request)

            return self.event(coro)  # have to actually return the event call

        return decorator  # now we can return the given decoratored information
