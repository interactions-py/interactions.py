from asyncio import AbstractEventLoop, Event, Lock, get_running_loop, sleep
from logging import Logger, basicConfig, getLogger
from sys import version_info
from typing import Any, ClassVar, Optional
from urllib.parse import quote

from aiohttp import ClientSession
from aiohttp import __version__ as http_version

from ..api.error import HTTPException
from ..base import Data, __version__

basicConfig(level=Data.LOGGER)
log: Logger = getLogger("http")

__all__ = ("Route", "Padlock", "Request", "HTTPClient")


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

    :ivar loop: The current coroutine event loop.
    :ivar session: The current session for making requests.
    :ivar ratelimits: The current ratelimits from the Discord API.
    :ivar headers: The current headers used for the Discord API.
    :ivar lock: The ratelimit lock event.
    """

    __slots__ = ("token", "loop", "ratelimits", "headers", "session", "lock")
    token: str
    loop: AbstractEventLoop
    ratelimits: dict
    headers: dict
    session: ClientSession
    lock: Event

    def __init__(self, token: str) -> None:
        """
        :param token: The application token used for authorizing.
        :type token: str
        :return: None
        """
        self.token = token
        self.loop = get_running_loop()
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

    async def request(self, route: Route, **kwargs) -> Optional[Any]:
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

        for _ in range(3):  # we're not using this variable, flow why
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
                        raise HTTPException(response.status)
                    elif response.status == 429:
                        retry_after = data["retry_after"]

                        if "X-Ratelimit-Global" in response.headers.keys():
                            self.lock.set()
                            log.warning("The HTTP request has encountered a global API ratelimit.")
                            await sleep(retry_after)
                            self.lock.clear()
                        else:
                            log.warning("A local ratelimit with the bucket has been encountered.")
                            await sleep(retry_after)
                        continue
                    return data

    async def close(self) -> None:
        """Closes the current session."""
        await self.session.close()


class HTTPClient:
    """
    A WIP class that represents the http Client that handles all major endpoints to Discord API.
    """

    token: str
    headers: dict
    _req: Optional[Request]

    def __init__(self, token: str):
        self.token = token
        self._req = Request(self.token)  # Only one session, in theory

        # An ideology is that this client does every single HTTP call, which reduces multiple ClientSessions in theory
        # because of how they are constructed/closed. This includes Gateway

    async def get_gateway(self) -> str:
        """This calls the Gateway endpoint."""

        url: Any = await self._req.request(Route("GET", "/gateway"))  # typehinting Any because pycharm yells
        return url["url"] + "?v=9&encoding=json"

    async def login(self) -> Optional[dict]:
        """
        This 'logins' to the gateway, which makes it available to use any other endpoint.
        """

        return await self._req.request(Route("GET", "/users/@me"))  # Internally raises any Exception.

    async def logout(self) -> None:
        """This 'log outs' the session."""

        await self._req.request(Route("POST", "/auth/logout"))

    @property
    def req(self):
        return self._req

    # ---- Oauth2 endpoint

    async def get_current_bot_information(self) -> dict:
        """
        Returns the bot user application object without flags.
        """
        return await self._req.request(Route("GET", f"/oauth2/applications/@me"))

    async def get_current_authorisation_information(self) -> dict:
        """
        Returns info about the current authorization of the bot user
        """
        return await self._req.request(Route("GET", f"/oauth2/@me"))

    # ---- User endpoint

    async def get_self(self) -> dict:
        """An alias to `get_user`, but only gets the current bot user."""
        return await self.get_user()

    async def get_user(self, user_id: Optional[int] = "@me") -> dict:
        # absolutely no idea if python typing lets me do this ^
        """
        Gets a user object for a given user ID.

        :param user_id: A user ID, represented by an integer snowflake ID. If omitted, this defaults
        to the current bot user.
        :return A partial User object in the form of a dictionary.
        """

        return await self._req.request(Route("GET", f"/users/{user_id}"))

    async def get_self_guilds(self) -> list:
        """
        Gets all guild objects associated with the current bot user.

        :return a list of partial guild objects the current bot user is a part of.
        """
        return await self._req.request(Route("GET", f"/users/@me/guilds"))

    async def leave_guild(self, guild_id: int) -> dict:
        """
        Leaves a guild.

        :param guild_id: The guild snowflake ID associated.
        :return: (Unconfirmed)
        """
        return await self._req.request(Route("DELETE", f"/users/@me/guilds/{guild_id}"))

    async def modify_self(self, payload: dict) -> dict:
        """
        Modify the bot user account settings.
        :param payload: The data to send.
        """
        return await self._req.request(Route("PATCH", f"/users/@me"), data=payload)

    async def modify_self_nick_in_guild(self, guild_id: int, nickname: Optional[str]):
        """
        Changes a nickname of the current bot user in a guild.

        :param guild_id: Guild snowflake ID.
        :param nickname: The new nickname, if any.
        :return: Nothing needed to be yielded.
        """
        return await self._req.request(Route("PATCH", f"/guilds/{guild_id}/members/@me/nick"), data={"nick": nickname})

    async def create_dm(self, recipient_id: int) -> dict:
        """
        Creates a new DM channel with a user.
        :param recipient_id: User snowflake ID.
        :return: Returns a dictionary representing a DM Channel object.
        """
        # only named recipient_id because of api mirroring

        return await self._req.request(Route("POST", f"/users/@me/channels"), data=dict(recipient_id=recipient_id))

    # Message endpoint

    async def create_message(self, payload: dict, channel_id: int) -> dict:
        """
        Send a message to the specified channel.

        :param payload: Dictionary contents of a message. (i.e. message payload)
        :param channel_id: Channel snowflake ID.
        :return dict: Dictionary representing a message (?)
        """
        return await self._req.request(Route("POST", f"/channels/{channel_id}/messages"), data=payload)

    # Thread endpoint

    async def join_thread(self, thread_id: int) -> None:
        """
        Have the bot user join a thread.
        :param thread_id: The thread to join.
        """
        return await self._req.request(Route("PUT", f"/channels/{thread_id}/thread-members/@me"))

    async def leave_thread(self, thread_id: int) -> None:
        """
        Have the bot user leave a thread.
        :param thread_id: The thread to leave.
        """
        return await self._req.request(Route("DELETE", f"/channels/{thread_id}/thread-members/@me"))

    # Reaction endpoint

    async def create_reaction(self, channel_id: int, message_id: int, emoji: str) -> None:
        """
        Create a reaction for a message.
        :param channel_id: Channel snowflake ID.
        :param message_id: Message snowflake ID.
        :param emoji: The emoji to use (format: `name:id`)
        """
        return await self._req.request(
            Route(
                "PUT",
                f"/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me"
            )
        )

    async def remove_self_reaction(
        self, channel_id: int, message_id: int, emoji: str
    ) -> None:
        """
        Remove bot user's reaction from a message.
        :param channel_id: Channel snowflake ID.
        :param message_id: Message snowflake ID.
        :param emoji: The emoji to remove (format: `name:id`)
        """
        return await self._req.request(
            Route(
                "DELETE",
                f"/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me"
            )
        )
