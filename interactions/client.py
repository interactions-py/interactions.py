# Normal libraries
from asyncio import AbstractEventLoop, get_event_loop, iscoroutinefunction
from asyncio.tasks import create_task
from typing import Any, Coroutine, List, Optional, Union

from interactions.api.error import ClientException

# 3rd-party libraries
from .api.gateway import WebSocket
from .api.http import Request
from .api.models import Intents


class Client:
    """
    The client class for the API wrapper.

    :ivar loop: The main overall asynchronous coroutine loop in effect.
    :ivar intents: The application's intents as :class:`interactions.api.models.Intents`.
    :ivar http: An HTTP instance as :class:`interactions.api.http.Request`.
    :ivar websocket: A WebSocket instance as :class:`interactions.api.gateway.WebSocket`.
    :ivar connection: The current connection state of the client.
    :ivar closed: An activated/"switched" declaration of if the connection closes.
    :ivar cache: The global cache combed from all HTTP requests.
    :ivar listeners: The application's events that are currently being listened to.
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
        "listeners",
        # "me",
        "interactions",
    )
    loop: Optional[AbstractEventLoop]
    intents: Optional[Union[Intents, List[Intents]]]
    http: Request
    websocket: Optional[WebSocket]
    connection: Optional[Any]
    closed: bool
    cache: dict
    listeners: dict
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
        self.http = Request(loop=self.loop)
        self.websocket = None
        self.connection = None
        self.closed = None
        self.cache = {}
        self.listeners = {}
        # self.me = None
        self.interactions = {}

    async def login(self, token: str) -> None:
        """Makes a login with the Discord API."""
        self.websocket = WebSocket(intents=self.intents, loop=self.loop)

        while not self.closed:
            await self.websocket.connect(token)
            self.listen_for(self.websocket.last_dispatched)

    def start(self) -> None:
        """Starts the client session."""
        self.loop.run_until_complete(self.login(self.token))

    def listen_for(self, event: str, *args, **kwargs) -> None:
        r"""
        Listens for the last dispatched event, and makes the appropriate
        HTTP request needed if found.

        :param event: The name of the event to listen for.
        :type event: str
        :param \*args: Multiple arguments to pass information to.
        :param \**kwargs: Keyword-arguments to pass information to.
        :return: None
        """
        listeners: list = self.listeners.get(event, [])
        for listener in listeners:
            if event == listener:
                try:
                    self.create_event(listener, event, *args, **kwargs)
                except Exception as exc:  # noqa
                    return

    def create_event(self, coro: Coroutine, event: str, *args, **kwargs) -> Any:
        r"""
        Creates a new task to later be listened as a new event.

        :param coro: The coroutine to task.
        :type coro: typing.Coroutine
        :param event: The name of the event.
        :type event: str
        :param \*args: Multiple arguments to pass information to.
        :param \**kwargs: Keyword-arguments to pass information to.
        :return: typing.Any
        """

        async def wrapper(_coro, _event, *_args, **_kwargs) -> Coroutine:
            try:
                await _coro(*_args, **_kwargs)
            except Exception as exc:  # noqa
                return

        wrapped = wrapper(coro, event, *args, **kwargs)
        return create_task(wrapped, name=f"interaction:: {event}")

    def create_listener(self, coro: Coroutine, event: str) -> Optional[ClientException]:
        """
        Creates a new listener event to be used for listening.

        :param coro: The coroutine to establish as a listener.
        :type coro: typing.Coroutine
        :param event: The name of the event to listen to.
        :type event: str
        :return: typing.Optional[interactions.api.error.ClientException]
        """
        if not iscoroutinefunction(coro):
            raise ClientException(
                message="The function given is not a coroutine, so a listener could not created."
            )

        event = event.removeprefix("on_")

        if event not in self.listeners:
            self.listeners[event] = []
        self.listeners[event].append(coro)

    def event(self, coro: Coroutine) -> Any:
        """
        A decorator to listen to events from the Discord API.

        .. note::
            The name of the coroutine will be used to determine the event it will listen for.

            ``def on_ready`` will be a listener for ``READY`` dispatched events.

        :param coro: The coroutine to check events for.
        :type coro: typing.Coroutine
        :return: typing.Any
        """
        self.create_listener(coro, coro.__name__)
