from asyncio import AbstractEventLoop, Event, Lock, get_running_loop, sleep
from logging import Logger, basicConfig, getLogger
from sys import version_info
from typing import Any, ClassVar, Optional, List, Dict
from urllib.parse import quote

from aiohttp import ClientSession, FormData
from aiohttp import __version__ as http_version

from .. import Channel, Member
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

        if response is not None:  # after _ -> 3
            # This is reached if every retry failed.
            if response.status >= 500:
                raise HTTPException(response.status, message="The server had an error processing your request.")

            raise HTTPException(response.status)  # Unknown, unparsed

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
        return await self._req.request(Route("PATCH", "/guilds/{guild_id}/members/@me/nick", guild_id=guild_id),
                                       data={"nick": nickname})

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
        return await self._req.request(Route("POST", "/channels/{channel_id}/messages", channel_id=channel_id),
                                       data=payload)

    # Guild endpoint

    async def get_self_guilds(self) -> list:
        """
        Gets all guild objects associated with the current bot user.

        :return a list of partial guild objects the current bot user is a part of.
        """
        return await self._req.request(Route("GET", f"/users/@me/guilds"))

    async def get_guild(self, guild_id: int):
        """
        Requests an individual guild from the API.
        :param guild_id: The guild snowflake ID associated.
        :return: The guild object associated, if any.
        """
        return await self._req.request(Route('GET', '/guilds/{guild_id}', guild_id=guild_id))

    async def leave_guild(self, guild_id: int) -> None:
        """
        Leaves a guild.

        :param guild_id: The guild snowflake ID associated.
        :return: None
        """
        return await self._req.request(Route("DELETE", "/users/@me/guilds/{guild_id}", guild_id=guild_id))

    async def get_vanity_code(self, guild_id: int) -> dict:
        return await self._req.request(Route('GET', '/guilds/{guild_id}/vanity-url', guild_id=guild_id))

    async def modify_vanity_code(self, guild_id: int, code: str, reason: Optional[str] = None) -> None:
        payload: Dict[str, Any] = {'code': code}
        return await self._req.request(Route('PATCH', '/guilds/{guild_id}/vanity-url', guild_id=guild_id), json=payload,
                                 reason=reason)

    async def get_all_channels(self, guild_id: int) -> List[dict]:
        """
        Requests from the API to get all channels in the guild.

        :param guild_id: Guild Snowflake ID
        :return: A list of channels.
        """
        return await self._req.request(Route('GET', '/guilds/{guild_id}/channels', guild_id=guild_id))

    async def get_member(self, guild_id: int, member_id: int) -> Optional[Member]:
        """
        Uses the API to fetch a member from a guild.
        :param guild_id: Guild ID snowflake.
        :param member_id: Member ID snowflake.
        :return: A member object, if any.
        """
        return await self._req.request(Route('GET', '/guilds/{guild_id}/members/{member_id}', guild_id=guild_id, member_id=member_id))

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

    async def add_member_to_thread(self, thread_id: int, user_id: int) -> None:
        """
        Add another user to a thread.
        :param thread_id: The ID of the thread
        :param user_id: The ID of the user to add
        """
        return await self._req.request(Route("PUT", f"/channels/{thread_id}/thread-members/@{user_id}"))

    async def remove_member_from_thread(self, thread_id: int, user_id: int) -> None:
        """
        Remove another user from a thread.
        :param thread_id: The ID of the thread
        :param user_id: The ID of the user to remove
        """
        return await self._req.request(Route("DELETE", f"/channels/{thread_id}/thread-members/@{user_id}"))

    async def list_thread_members(self, thread_id: int) -> List[dict]:
        """
        Get a list of members in the thread.
        :param thread_id: the id of the thread
        :return: a list of member objects
        """
        return await self._req.request(Route("GET", f"/channels/{thread_id}/thread-members"))

    async def list_public_archived_threads(self, channel_id: int, limit: int = None,
                                           before: Optional[int] = None) -> List[dict]:
        """
        Get a list of archived public threads in a given channel.

        :param channel_id: The channel to get threads from
        :param limit: Optional limit of threads to
        :param before: Get threads before this Thread snowflake ID
        :return: a list of threads
        """
        payload = {}
        if limit:
            payload["limit"] = limit
        if before:
            payload["before"] = before
        return await self._req.request(Route("GET", f"/channels/{channel_id}/threads/archived/public"), data=payload)

    async def list_private_archived_threads(self, channel_id: int, limit: int = None,
                                            before: Optional[int] = None) -> List[dict]:
        """
        Get a list of archived private threads in a channel.
        :param channel_id: The channel to get threads from
        :param limit: Optional limit of threads to
        :param before: Get threads before this Thread snowflake ID
        :return: a list of threads
        """
        payload = {}
        if limit:
            payload["limit"] = limit
        if before:
            payload["before"] = before
        return await self._req.request(Route("GET", f"/channels/{channel_id}/threads/archived/private"), data=payload)

    async def list_joined_private_archived_threads(self, channel_id: int, limit: int = None,
                                                   before: Optional[int] = None) -> List[dict]:
        """
        Get a list of archived private threads in a channel that the bot has joined.
        :param channel_id: The channel to get threads from
        :param limit: Optional limit of threads to
        :param before: Get threads before this snowflake ID
        :return: a list of threads
        """
        payload = {}
        if limit:
            payload["limit"] = limit
        if before:
            payload["before"] = before
        return await self._req.request(
            Route("GET", f"/channels/{channel_id}/users/@me/threads/archived/private"), data=payload
        )

    async def list_active_threads(self, guild_id: int) -> List[dict]:
        """
        List active threads within a guild.
        :param guild_id: the guild id to get threads from
        :return: A list of active threads
        """
        return await self._req.request(Route("GET", f"/guilds/{guild_id}/threads/active"))

    async def create_thread(self, channel_id: int, name: str, auto_archive_duration: int, thread_type: int = None,
                            invitable: Optional[bool] = None, message_id: Optional[int] = None,
                            reason: Optional[str] = None) -> dict:
        """
        From a given channel, create a Thread with an optional message to start with..

        :param channel_id: The ID of the channel to create this thread in
        :param name: The name of the thread
        :param auto_archive_duration: duration in minutes to automatically archive the thread after recent activity,
            can be set to: 60, 1440, 4320, 10080
        :param thread_type: The type of thread, defaults to public. ignored if creating thread from a message
        :param invitable: Boolean to display if the Thread is open to join or private.
        :param message_id: An optional message to create a thread from.
        :param reason: An optional reason for the audit log
        :return: The created thread
        """
        payload = dict(name=name, auto_archive_duration=auto_archive_duration)
        if message_id:
            return await self._req.request(
                Route("POST", f"/channels/{channel_id}/messages/{message_id}/threads"), data=payload, reason=reason
            )
        payload["type"] = thread_type
        payload["invitable"] = invitable
        return await self._req.request(Route("POST", f"/channels/{channel_id}/threads"), data=payload, reason=reason)

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
                "/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me",
                channel_id=channel_id,
                message_id=message_id,
                emoji=emoji,
            )
        )

    async def remove_self_reaction(self, channel_id: int, message_id: int, emoji: str) -> None:
        """
        Remove bot user's reaction from a message.
        :param channel_id: Channel snowflake ID.
        :param message_id: Message snowflake ID.
        :param emoji: The emoji to remove (format: `name:id`)
        """
        return await self._req.request(
            Route(
                "DELETE",
                "/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me",
                channel_id=channel_id,
                message_id=message_id,
                emoji=emoji,
            )
        )

    async def remove_user_reaction(self, channel_id: int, message_id: int, emoji: str, user_id: int) -> None:
        """
        Remove user's reaction from a message

        :param channel_id: The channel this is taking place in
        :param message_id: The message to remove the reaction on.
        :param emoji: The emoji to remove. (format: `name:id`)
        :param user_id: The user to remove reaction of.
        """
        return await self._req.request(
            Route(
                "DELETE",
                "/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/{user_id}",
                channel_id=channel_id,
                message_id=message_id,
                emoji=emoji,
                user_id=user_id,
            )
        )

    async def remove_all_reactions(self, channel_id: int, message_id: int) -> None:
        """
        Remove reactions from a message.

        :param channel_id: The channel this is taking place in.
        :param message_id: The message to clear reactions from.
        """
        return await self._req.request(
            Route("DELETE", "/channels/{channel_id}/messages/{message_id}/reactions", channel_id=channel_id,
                  message_id=message_id))

    async def get_reactions_of_emoji(self, channel_id: int, message_id: int, emoji: str) -> List:
        """
        Gets specific reaction from a message
        :param channel_id: The channel this is taking place in.
        :param message_id: The message to get the reaction.
        :param emoji: The emoji to get. (format: `name:id`)
        """
        return await self._req.request(
            Route(
                "GET",
                "/channels/{channel_id}/messages/{message_id}/reactions/{emoji}",
                channel_id=channel_id,
                message_id=message_id,
                emoji=emoji,
            )
        )

    # Sticker endpoint

    async def get_sticker(self, sticker_id: int) -> dict:
        """
        Get a specific sticker.
        :param sticker_id: The id of the sticker
        :return: Sticker or None
        """
        return await self._req.request(Route("GET", f"/stickers/{sticker_id}"))

    async def list_nitro_sticker_packs(self) -> list:
        """
        Gets the list of sticker packs available to Nitro subscribers.
        :return: List of sticker packs
        """
        return await self._req.request(Route("GET", "/sticker-packs"))

    async def list_guild_stickers(self, guild_id: int) -> List[dict]:
        """
        Get the stickers for a guild.
        :param guild_id: The guild to get stickers from
        :return: List of Stickers or None
        """
        return await self._req.request(Route("GET", f"/guild/{guild_id}/stickers"))

    async def get_guild_sticker(self, guild_id: int, sticker_id: int) -> dict:
        """
        Get a sticker from a guild.
        :param guild_id: The guild to get stickers from
        :param sticker_id: The sticker to get from the guild
        :return: Sticker or None
        """
        return await self._req.request(Route("GET", f"/guild/{guild_id}/stickers/{sticker_id}"))

    async def create_guild_sticker(self, payload: FormData, guild_id: int, reason: Optional[str] = None):
        """
        Create a new sticker for the guild. Requires the MANAGE_EMOJIS_AND_STICKERS permission.
        :param payload: the payload to send.
        :param guild_id: The guild to create sticker at.
        :param reason: The reason for this action.
        :return: The new sticker data on success.
        """
        return await self._req.request(Route("POST", f"/guild/{guild_id}/stickers"), data=payload, reason=reason)

    async def modify_guild_sticker(self, payload: dict, guild_id: int, sticker_id: int, reason: Optional[str] = None):
        """
        Modify the given sticker. Requires the MANAGE_EMOJIS_AND_STICKERS permission.
        :param payload: the payload to send.
        :param guild_id: The guild of the target sticker.
        :param sticker_id:  The sticker to modify.
        :param reason: The reason for this action.
        :return: The updated sticker data on success.
        """
        return await self._req.request(
            Route("PATCH", f"/guild/{guild_id}/stickers/{sticker_id}"), data=payload, reason=reason
        )

    async def delete_guild_sticker(self, guild_id: int, sticker_id: int, reason: Optional[str] = None) -> None:
        """
        Delete the given sticker. Requires the MANAGE_EMOJIS_AND_STICKERS permission.
        :param guild_id: The guild of the target sticker.
        :param sticker_id:  The sticker to delete.
        :param reason: The reason for this action.
        :return: Returns 204 No Content on success.
        """
        return await self._req.request(Route("DELETE", f"/guild/{guild_id}/stickers/{sticker_id}"), reason=reason)
