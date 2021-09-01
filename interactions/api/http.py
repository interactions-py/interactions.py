from asyncio import AbstractEventLoop, Event, Lock, get_event_loop, sleep
from logging import Logger, basicConfig, getLogger
from sys import version_info
from typing import Any, ClassVar, Optional
from urllib.parse import quote

from aiohttp import ClientSession
from aiohttp import __version__ as http_version

from ..base import Data, __version__

basicConfig(level=Data.LOGGER)
log: Logger = getLogger("http")

__all__ = ("Route", "Padlock", "Request")


class Route:
    """
    A class representing how an HTTP route is structured.

    :ivar method: The HTTP method.
    :ivar path: The URL path.
    :ivar channel_id: The channel ID from the bucket if given.
    :ivar guild_id: The guild ID from the bucket if given.
    """

    __slots__ = ("__api__", "method", "path", "channel_id", "guild_id")
    __api__: ClassVar[str]
    method: str
    path: str
    channel_id: Optional[str]
    guild_id: Optional[str]

    def __init__(self, method: str, path: str, **kwargs) -> None:
        r"""
        :param method: The HTTP request method.
        :type method: str
        :param path: The path of the HTTP/URL.
        :type path: str
        :param \**kwargs: Optional keyword-only arguments to pass as information in the route.
        :type \**kwargs: dict
        :return: None
        """
        self.__api__ = "https://discord.com/api/v9"
        self.method = method
        self.path = path.format(**kwargs)
        self.channel_id = kwargs.get("channel_id")
        self.guild_id = kwargs.get("guild_id")

    @property
    def bucket(self) -> str:
        """
        Returns the route's bucket.

        :return: str
        """
        return f"{self.channel_id}:{self.guild_id}:{self.path}"


class Padlock:
    """
    A class representing ratelimited sessions as a "locked" event.

    :ivar lock: The lock coroutine event.
    :ivar keep_open: Whether the lock should stay open or not.
    """

    __slots__ = ("lock", "keep_open")
    lock: Lock
    keep_open: bool

    def __init__(self, lock: Lock) -> None:
        """
        :param lock: The lock coroutine event.
        :type lock: asyncio.Lock
        :return: None
        """
        self.lock = lock
        self.keep_open = True

    def click(self) -> None:
        """Re-closes the lock after the instiantiation and invocation ends."""
        self.keep_open = False

    def __enter__(self) -> Any:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.keep_open:
            self.lock.release()


class Request:
    """
    A class representing how HTTP requests are sent/read.

    :ivar url: The current Discord API URL.
    :ivar loop: The current coroutine event loop.
    :ivar session: The current session for making requests.
    :ivar ratelimits: The current ratelimits from the Discord API.
    :ivar lock: The ratelimit lock event.
    """

    __slots__ = ("token", "loop", "ratelimits", "headers", "session", "lock")
    token: str
    loop: Optional[AbstractEventLoop]
    ratelimts: dict
    headers: dict
    session: ClientSession
    lock: Event

    def __init__(self, token: str, loop: Optional[AbstractEventLoop] = None) -> None:
        """
        :param token: The application token used for authorizing.
        :type token: str
        :param loop: The event loop used to make requests on. Defaults to ``None`` and creates one for you.
        :type loop: typing.Optional[asyncio.AbstractEventLoop]
        :return: None
        """
        self.token = token
        self.loop = get_event_loop() if loop is None else loop
        self.session = ClientSession()
        self.ratelimits = {}
        self.headers = {
            "X-Ratelimit-Precision": "millisecond",
            "Authorization": f"Bot {self.token}",
            "User-Agent": f"DiscordBot (https://github.com/goverfl0w/discord-interactions {__version__} "
            f"Python/{version_info[0]}.{version_info[1]} "
            f"aiohttp/{http_version}",
        }
        self.lock = Event(loop=self.loop)

        self.lock.set()

    def check_session(self) -> None:
        """Ensures that we have a valid connection session."""
        if self.session.closed:
            self.session = ClientSession()

    async def request(self, route: Route, **kwargs) -> None:
        r"""
        Sends a request to the Discord API.

        :param route: The HTTP route to request.
        :type route: interactions.api.http.Route
        :param \**kwargs: Optional keyword-only arguments to pass as information in the request.
        :type \**kwargs: dict
        :return: None
        """
        self.check_session()

        bucket: Optional[str] = route.bucket

        for attempt in range(3):
            ratelimit: Lock = self.ratelimits.get(bucket)

            if not self.lock.is_set():
                log.warning("Global lock is still locked, waiting for it to clear...")
                await self.lock.wait()

            if ratelimit is None:
                self.ratelimits[bucket] = Lock()
                continue

            await ratelimit.acquire()

            with Padlock(ratelimit) as lock:  # noqa: F841
                kwargs["headers"] = {**self.headers, **kwargs.get("headers", {})}

                try:
                    reason = kwargs.pop("reason")
                except:  # noqa
                    pass
                else:
                    if reason:
                        kwargs["headers"]["X-Audit-Log-Reason"] = quote(reason, safe="/ ")

                async with self.session.request(
                    route.method, route.__api__ + route.path, **kwargs
                ) as response:
                    data = await response.json()
                    log.debug(data)

                    if response.status in (300, 401, 403, 404):
                        raise Exception("api is being poopy with us.")
                    elif response.status == 429:
                        retry_after = data["retry_after"]

                        if "X-Ratelimit-Global" in response.headers.keys():
                            self.lock.set()
                            log.warning("The HTTP request has encountered a global API ratelimit.")
                            await sleep(retry_after)
                            self.lock.clear()
                            continue
                        else:
                            log.warning("A local ratelimit with the bucket has been encountered.")
                            await sleep(retry_after)
                            continue

                    return data

    async def close(self) -> None:
        """Closes the current session."""
        await self.session.close()
