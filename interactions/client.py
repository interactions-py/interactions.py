from asyncio import AbstractEventLoop, get_event_loop
from typing import Any, Callable, Coroutine, List, Optional, Union

from .api.dispatch import Listener
from .api.gateway import WebSocket
from .api.http import Request
from .api.models import Intents


class Client:
    """
    A class representing a client connection to the Discord API.

    :ivar loop: The main overall asynchronous coroutine loop in effect.
    :ivar listener: An instance of :class:`interactions.api.dispatch.Listener`.
    :ivar intents: The application's intents as :class:`interactions.api.models.Intents`.
    :ivar http: An instance of :class:`interactions.api.http.Request`.
    :ivar websocket: An instance of :class:`interactions.api.gateway.WebSocket`.
    :ivar token: The application token.
    """

    loop: Optional[AbstractEventLoop]
    intents: Optional[Union[Intents, List[Intents]]]
    http: Request
    websocket: WebSocket
    token: str

    def __init__(
        self,
        token: str,
        intents: Optional[Union[Intents, List[Intents]]] = Intents.DEFAULT,
        loop: Optional[AbstractEventLoop] = None,
    ) -> None:
        """
        An object representing the client connection to Discord's Gateway
        and API via. WebSocket and HTTP.

        :param token: The token of the application for authentication and connection.
        :type token: str
        :param intents: The intents you wish to pass through the client. Defaults to :meth:`interactions.api.models.Intents.DEFAULT` or ``513``.
        :type intents: typing.Optional[typing.Union[interactions.api.models.Intents, typing.List[Intents]]]
        :param loop: The asynchronous coroutine loop you wish to use. Defaults to ``None`` and creates a global loop instead.
        :type loop: typing.Optional[asyncio.AbstractEventLoop]
        :return: None
        """
        if isinstance(intents, list):
            for intent in intents:
                self.intents |= intent
        else:
            self.intents = intents

        self.loop = get_event_loop() if loop is None else loop
        self.listener = Listener(loop=self.loop)
        self.http = Request(token=token, loop=self.loop)
        self.websocket = WebSocket(intents=self.intents, loop=self.loop)
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