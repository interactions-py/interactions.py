# Normal libraries
from asyncio import AbstractEventLoop, get_event_loop
from typing import Any, List, Optional, Union

# 3rd-party libraries
from .api.gateway import WebSocket
from .api.http import Request
from .api.models import Intents


class Client:
    """
    The client class for the API wrapper.

    :ivar loop: The main overall asynchronous coroutine loop in effect.
    :ivar intents: The application's intents as :class:`interactions.api.models.IntentsFlag`.
    :ivar http: An HTTP instance as :class:`interactions.api.http.Request`.
    :ivar websocket: A WebSocket instance as :class:`interactions.api.gateway.WebSocket`.
    :ivar connection: The current connection state of the client.
    :ivar closed: An activated/"switched" declaration of if the connection closes.
    :ivar cache: The global cache combed from all HTTP requests.
    :ivar me: A model of the user of the application as :class:`interactions.api.models.User`.
    :ivar interactions: The collected list of interactions waiting for creation/syncing.
    """

    __slots__ = (
        "loop",
        "intents",
        "http",
        "websocket",
        "connection",
        "closed",
        "cache",
        # "me",
        "interactions",
    )
    loop: Optional[AbstractEventLoop]
    intents: Optional[Union[Intents, List[Intents]]]
    http: Request
    websocket: WebSocket
    connection: Optional[Any]
    closed: bool
    cache: dict
    # me: Optional[User]
    interactions: dict

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
        :type intents: typing.Optional[typing.Union[Intents, typing.List[Intents]]]
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
        self.http = Request(loop=self.loop)
        self.websocket = WebSocket(token=token, intents=self.intents, loop=self.loop)
        self.connection = None
        self.closed = None
        self.cache = {}
        # self.me = None
        self.interactions = {}

    async def login(self) -> None:
        """Makes a login with the Discord API."""
        await self.websocket.connect()

    def start(self) -> None:
        """Starts the client session."""
        self.loop.run_until_complete(self.login())
