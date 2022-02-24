import asyncio
import traceback
from asyncio import AbstractEventLoop, Lock, get_event_loop, get_running_loop, new_event_loop
from json import dumps
from logging import Logger
from sys import version_info
from typing import Any, ClassVar, Dict, List, Optional, Tuple, Union
from urllib.parse import quote

from aiohttp import ClientSession, FormData
from aiohttp import __version__ as http_version

import interactions.api.cache
from interactions.api.models.misc import MISSING
from interactions.base import __version__, get_logger

from ..api.cache import Cache, Item
from ..api.error import HTTPException
from ..api.models import (
    Channel,
    Embed,
    Emoji,
    Guild,
    GuildPreview,
    GuildTemplate,
    Invite,
    Member,
    Message,
    Role,
    Snowflake,
    StageInstance,
    User,
    WelcomeScreen,
)

log: Logger = get_logger("http")

__all__ = ("Route", "Request", "HTTPClient")
_session: ClientSession = ClientSession()


class Route:
    """
    A class representing how an HTTP route is structured.

    :ivar ClassVar[str] __api__: The HTTP route path.
    :ivar str method: The HTTP method.
    :ivar str path: The URL path.
    :ivar Optional[str] channel_id: The channel ID from the bucket if given.
    :ivar Optional[str] guild_id: The guild ID from the bucket if given.
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
        :param \**kwargs?: Optional keyword-only arguments to pass as information in the route.
        :type \**kwargs: dict
        """
        self.__api__ = "https://discord.com/api/v10"
        self.method = method
        self.path = path.format(**kwargs)
        self.channel_id = kwargs.get("channel_id")
        self.guild_id = kwargs.get("guild_id")

    def get_bucket(self, shared_bucket: Optional[str] = None) -> str:
        """
        Returns the route's bucket. If shared_bucket is None, returns the path with major parameters.
        Otherwise, it relies on Discord's given bucket.

        :param shared_bucket: The bucket that Discord provides, if available.
        :type shared_bucket: Optional[str]

        :return: The route bucket.
        :rtype: str
        """
        return (
            f"{self.channel_id}:{self.guild_id}:{self.path}"
            if shared_bucket is None
            else f"{self.channel_id}:{self.guild_id}:{shared_bucket}"
        )

    @property
    def endpoint(self) -> str:
        """
        Returns the route's endpoint.

        :return: The route endpoint.
        :rtype: str
        """
        return f"{self.method}:{self.path}"


class Limiter:
    """
    A class representing a limitation for an HTTP request.

    :ivar Lock lock: The "lock" or controller of the request.
    :ivar float reset_after: The remaining time before the request can be ran.
    """

    lock: Lock
    reset_after: float

    def __init__(self, *, lock: Lock, reset_after: Optional[float] = MISSING) -> None:
        """
        :param lock: The asynchronous lock to control limits for.
        :type lock: Lock
        :param reset_after: The remaining time to run the limited lock on. Defaults to ``0``.
        :type reset_after: Optional[float]
        """
        self.lock = lock
        self.reset_after = 0 if reset_after is MISSING else reset_after

    async def __aenter__(self) -> "Limiter":
        await self.lock.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        return self.lock.release()

    def release_lock(self):
        # Releases the lock if its locked, overriding the traditional release() method.
        # Useful for per-route, not needed? for globals.

        # See #428.

        if self.lock.locked():
            self.lock.release()


class Request:
    """
    A class representing how HTTP requests are sent/read.

    :ivar str token: The current application token.
    :ivar AbstractEventLoop _loop: The current coroutine event loop.
    :ivar Dict[str, Limiter] ratelimits: The current per-route rate limiters from the API.
    :ivar Dict[str, str] buckets: The current endpoint to shared_bucket cache from the API.
    :ivar dict _headers: The current headers for an HTTP request.
    :ivar ClientSession _session: The current session for making requests.
    :ivar Limiter _global_lock: The global rate limiter.
    """

    __slots__ = (
        "token",
        "_loop",
        "ratelimits",
        "buckets",
        "_headers",
        "_session",
        "_global_lock",
    )
    token: str
    _loop: AbstractEventLoop
    ratelimits: Dict[str, Limiter]  # bucket: Limiter
    buckets: Dict[str, str]  # endpoint: shared_bucket
    _headers: dict
    _session: ClientSession
    _global_lock: Limiter

    def __init__(self, token: str) -> None:
        """
        :param token: The application token used for authorizing.
        :type token: str
        """
        self.token = token
        try:
            self._loop = get_event_loop() if version_info < (3, 10) else get_running_loop()
        except RuntimeError:
            self._loop = new_event_loop()
        self.ratelimits = {}
        self.buckets = {}
        self._headers = {
            "Authorization": f"Bot {self.token}",
            "User-Agent": f"DiscordBot (https://github.com/interactions-py/library {__version__}) "
            f"Python/{version_info[0]}.{version_info[1]} "
            f"aiohttp/{http_version}",
        }
        self._session = _session
        self._global_lock = (
            Limiter(lock=Lock(loop=self._loop)) if version_info < (3, 10) else Limiter(lock=Lock())
        )

    def _check_session(self) -> None:
        """Ensures that we have a valid connection session."""
        if self._session.closed:
            self._session = ClientSession()

    async def _check_lock(self) -> None:
        """Checks the global lock for its current state."""
        if self._global_lock.lock.locked():
            log.warning("The HTTP client is still globally locked, waiting for it to clear.")
            await self._global_lock.lock.acquire()
            self._global_lock.reset_after = 0

    async def request(self, route: Route, **kwargs) -> Optional[Any]:
        r"""
        Sends a request to the Discord API.

        :param route: The HTTP route to request.
        :type route: Route
        :param \**kwargs?: Optional keyword-only arguments to pass as information in the request.
        :type \**kwargs: dict
        :return: The contents of the request if any.
        :rtype: Optional[Any]
        """

        kwargs["headers"] = {**self._headers, **kwargs.get("headers", {})}
        kwargs["headers"]["Content-Type"] = "application/json"

        reason = kwargs.pop("reason", None)
        if reason:
            kwargs["headers"]["X-Audit-Log-Reason"] = quote(reason, safe="/ ")

        # Huge credit and thanks to LordOfPolls for the lock/retry logic.

        bucket = route.get_bucket(
            self.buckets.get(route.endpoint)
        )  # string returning path OR prioritised hash bucket metadata.

        # The idea is that its regulated by the priority of Discord's bucket header and not just self-computation.

        if self.ratelimits.get(bucket):
            _limiter: Limiter = self.ratelimits.get(bucket)
            if _limiter.lock.locked():
                if (
                    _limiter.reset_after != 0
                ):  # Just saying 0 seconds isn't helpful, so this is suppressed.
                    log.warning(
                        f"The current bucket is still under a rate limit. Calling later in {_limiter.reset_after} seconds."
                    )
                self._loop.call_later(_limiter.reset_after, _limiter.release_lock)
            _limiter.reset_after = 0
        else:
            self.ratelimits[bucket] = (
                Limiter(lock=Lock(loop=self._loop))
                if version_info < (3, 10)
                else Limiter(lock=Lock())
            )
            _limiter: Limiter = self.ratelimits.get(bucket)

        await _limiter.lock.acquire()  # _limiter is the per shared bucket/route endpoint

        # Implement retry logic. The common seems to be 5, so this is hardcoded, for the most part.

        for tries in range(5):  # 3, 5? 5 seems to be common
            try:
                self._check_session()
                await self._check_lock()

                async with self._session.request(
                    route.method, route.__api__ + route.path, **kwargs
                ) as response:

                    data = await response.json(content_type=None)
                    reset_after: float = float(
                        response.headers.get("X-RateLimit-Reset-After", "0.0")
                    )
                    remaining: str = response.headers.get("X-RateLimit-Remaining")
                    _bucket: str = response.headers.get("X-RateLimit-Bucket")
                    is_global: bool = response.headers.get("X-RateLimit-Global", False)

                    log.debug(f"{route.method}: {route.__api__ + route.path}: {kwargs}")

                    if _bucket is not None:
                        self.buckets[route.endpoint] = _bucket
                        # real-time replacement/update/add if needed.

                    if isinstance(data, dict) and data.get("errors"):
                        log.debug(
                            f"RETURN {response.status}: {dumps(data, indent=4, sort_keys=True)}"
                        )
                        # This "redundant" debug line is for debug use and tracing back the error codes.

                        raise HTTPException(data["code"], message=data["message"])
                    elif remaining and not int(remaining):
                        if response.status == 429:
                            log.warning(
                                f"The HTTP client has encountered a per-route ratelimit. Locking down future requests for {reset_after} seconds."
                            )
                            _limiter.reset_after = reset_after
                            await asyncio.sleep(_limiter.reset_after)
                            continue
                        elif is_global:
                            log.warning(
                                f"The HTTP client has encountered a global ratelimit. Locking down future requests for {reset_after} seconds."
                            )
                            self._global_lock.reset_after = reset_after
                            self._loop.call_later(
                                self._global_lock.reset_after, self._global_lock.lock.release
                            )

                    log.debug(f"RETURN {response.status}: {dumps(data, indent=4, sort_keys=True)}")

                    _limiter.release_lock()  # checks if its locked, then releases upon success.

                    return data

            # These account for general/specific exceptions. (Windows...)
            except OSError as e:
                if tries < 4 and e.errno in (54, 10054):
                    await asyncio.sleep(2 * tries + 1)
                    continue
                try:
                    _limiter.lock.release()
                except RuntimeError:
                    pass
                raise

            # For generic exceptions we give a traceback for debug reasons.
            except Exception as e:
                try:
                    _limiter.lock.release()
                except RuntimeError:
                    pass
                log.error("".join(traceback.format_exception(type(e), e, e.__traceback__)))
                break

    async def close(self) -> None:
        """Closes the current session."""
        await self.session.close()


class HTTPClient:
    """
    The user-facing client of the Web API for individual endpoints.

    :ivar str token: The token of the application.
    :ivar Request _req: The requesting interface for endpoints.
    :ivar Cache cache: The referenced cache.
    """

    token: str
    _req: Request
    cache: Cache

    def __init__(self, token: str):
        self.token = token
        self._req = Request(self.token)
        self.cache = interactions.api.cache.ref_cache

        # An ideology is that this client does every single HTTP call, which reduces multiple ClientSessions in theory
        # because of how they are constructed/closed. This includes Gateway

    async def get_gateway(self) -> str:
        """This calls the Gateway endpoint and returns a v9 gateway link with JSON encoding."""

        url: Any = await self._req.request(
            Route("GET", "/gateway")
        )  # typehinting Any because pycharm yells
        return f'{url["url"]}?v=10&encoding=json'

    async def get_bot_gateway(self) -> Tuple[int, str]:
        """
        This calls the BOT Gateway endpoint.

        :return: A tuple denoting (shard, gateway_url), url from API v9 and JSON encoding
        """

        data: Any = await self._req.request(Route("GET", "/gateway/bot"))
        return data["shards"], f'{data["url"]}?v=9&encoding=json'

    async def login(self) -> Optional[dict]:
        """
        This 'logins' to the gateway, which makes it available to use any other endpoint.
        """

        return await self._req.request(
            Route("GET", "/users/@me")
        )  # Internally raises any Exception.

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
        return await self._req.request(Route("GET", "/oauth2/applications/@me"))

    async def get_current_authorisation_information(self) -> dict:
        """
        Returns info about the current authorization of the bot user
        """
        return await self._req.request(Route("GET", "/oauth2/@me"))

    # ---- User endpoint

    async def get_self(self) -> dict:
        """
        An alias to `get_user`, but only gets the current bot user.

        :return: A partial User object of the current bot user in the form of a dictionary.
        """
        return await self.get_user()

    async def get_user(self, user_id: Optional[int] = None) -> dict:
        """
        Gets a user object for a given user ID.

        :param user_id: A user snowflake ID. If omitted, this defaults to the current bot user.
        :return: A partial User object in the form of a dictionary.
        """

        if user_id is None:
            user_id = "@me"

        request = await self._req.request(Route("GET", f"/users/{user_id}"))
        self.cache.users.add(Item(id=user_id, value=User(**request)))

        return request

    async def modify_self(self, payload: dict) -> dict:
        """
        Modify the bot user account settings.

        :param payload: The data to send.
        """
        return await self._req.request(Route("PATCH", "/users/@me"), json=payload)

    async def modify_self_nick_in_guild(self, guild_id: int, nickname: Optional[str]):
        """
        Changes a nickname of the current bot user in a guild.

        :param guild_id: Guild snowflake ID.
        :param nickname: The new nickname, if any.
        :return: Nothing needed to be yielded.
        """
        return await self._req.request(
            Route("PATCH", "/guilds/{guild_id}/members/@me/nick", guild_id=guild_id),
            json={"nick": nickname},
        )

    async def create_dm(self, recipient_id: int) -> dict:
        """
        Creates a new DM channel with a user.

        :param recipient_id: User snowflake ID.
        :return: Returns a dictionary representing a DM Channel object.
        """
        # only named recipient_id because of api mirroring

        request = await self._req.request(
            Route("POST", "/users/@me/channels"), json={"recipient_id": recipient_id}
        )
        self.cache.dms.add(Item(id=str(recipient_id), value=Channel(**request)))

        return request

    # Message endpoint

    async def send_message(
        self,
        channel_id: Union[int, Snowflake],
        content: str,
        tts: bool = False,
        embeds: Optional[List[Embed]] = None,
        nonce: Union[int, str] = None,
        allowed_mentions=None,  # don't know type
        message_reference: Optional[Message] = None,
    ):
        """
        A higher level implementation of :meth:`create_message()` that handles the payload dict internally.
        Does not integrate components into the function, and is a port from v3.0.0
        """
        payload = {}

        if content:
            payload["content"] = content

        if tts:
            payload["tts"] = True

        if embeds:
            payload["embeds"] = embeds

        if nonce:
            payload["nonce"] = nonce

        if allowed_mentions:
            payload["allowed_mentions"] = allowed_mentions

        if message_reference:
            payload["message_reference"] = message_reference

        # TODO: post-v4. add attachments to payload.

        if isinstance(channel_id, Snowflake):
            channel_id = int(channel_id)

        return await self.create_message(payload, channel_id)

    async def create_message(self, payload: dict, channel_id: int) -> dict:
        """
        Send a message to the specified channel.

        :param payload: Dictionary contents of a message. (i.e. message payload)
        :param channel_id: Channel snowflake ID.
        :return dict: Dictionary representing a message (?)
        """
        request = await self._req.request(
            Route("POST", "/channels/{channel_id}/messages", channel_id=channel_id), json=payload
        )
        if request.get("id"):
            self.cache.messages.add(Item(id=request["id"], value=Message(**request)))

        return request

    async def get_message(self, channel_id: int, message_id: int) -> Optional[dict]:
        """
        Get a specific message in the channel.

        :param channel_id: the channel this message belongs to
        :param message_id: the id of the message
        :return: message if it exists.
        """
        return await self._req.request(
            Route("GET", f"/channels/{channel_id}/messages/{message_id}")
        )

    async def delete_message(
        self, channel_id: int, message_id: int, reason: Optional[str] = None
    ) -> None:
        """
        Deletes a message from a specified channel.

        :param channel_id: Channel snowflake ID.
        :param message_id: Message snowflake ID.
        :param reason: Optional reason to show up in the audit log. Defaults to `None`.
        """
        r = Route(
            "DELETE",
            "/channels/{channel_id}/messages/{message_id}",
            channel_id=channel_id,
            message_id=message_id,
        )
        return await self._req.request(r, reason=reason)

    async def delete_messages(
        self, channel_id: int, message_ids: List[int], reason: Optional[str] = None
    ) -> None:
        """
        Deletes messages from a specified channel.

        :param channel_id: Channel snowflake ID.
        :param message_ids: An array of message snowflake IDs.
        :param reason: Optional reason to show up in the audit log. Defaults to `None`.
        """
        r = Route("POST", "/channels/{channel_id}/messages/bulk-delete", channel_id=channel_id)
        payload = {
            "messages": message_ids,
        }

        return await self._req.request(r, json=payload, reason=reason)

    async def edit_message(self, channel_id: int, message_id: int, payload: dict) -> dict:
        """
        Edits a message that already exists.

        :param channel_id: Channel snowflake ID.
        :param message_id: Message snowflake ID.
        :param payload: Any new data that needs to be changed.
        :type payload: dict
        :return: A message object with edited attributes.
        """
        return await self._req.request(
            Route(
                "PATCH",
                "/channels/{channel_id}/messages/{message_id}",
                channel_id=channel_id,
                message_id=message_id,
            ),
            json=payload,
        )

    async def pin_message(self, channel_id: int, message_id: int) -> None:
        """
        Pin a message to a channel.

        :param channel_id: Channel ID snowflake.
        :param message_id: Message ID snowflake.
        """
        return await self._req.request(Route("PUT", f"/channels/{channel_id}/pins/{message_id}"))

    async def unpin_message(self, channel_id: int, message_id: int) -> None:
        """
        Unpin a message to a channel.

        :param channel_id: Channel ID snowflake.
        :param message_id: Message ID snowflake.
        """
        return await self._req.request(Route("DELETE", f"/channels/{channel_id}/pins/{message_id}"))

    async def publish_message(self, channel_id: int, message_id: int) -> dict:
        """
        Publishes (API calls it crossposts) a message in a News channel to any that is followed by.

        :param channel_id: Channel the message is in
        :param message_id: The id of the message to publish
        :return: message object
        """
        return await self._req.request(
            Route("POST", f"/channels/{channel_id}/messages/{message_id}/crosspost")
        )

    # Guild endpoint

    async def get_self_guilds(self) -> list:
        """
        Gets all guild objects associated with the current bot user.

        :return a list of partial guild objects the current bot user is a part of.
        """
        request = await self._req.request(Route("GET", "/users/@me/guilds"))

        for guild in request:
            if guild.get("id"):
                self.cache.self_guilds.add(Item(id=guild["id"], value=Guild(**guild)))

        return request

    async def get_guild(self, guild_id: int):
        """
        Requests an individual guild from the API.

        :param guild_id: The guild snowflake ID associated.
        :return: The guild object associated, if any.
        """
        request = await self._req.request(Route("GET", "/guilds/{guild_id}", guild_id=guild_id))
        self.cache.guilds.add(Item(id=str(guild_id), value=Guild(**request)))

        return request

    async def get_guild_preview(self, guild_id: int) -> GuildPreview:
        """
        Get a guild's preview.

        :param guild_id: Guild ID snowflake.
        :return: Guild Preview object associated with the snowflake
        """
        return await self._req.request(Route("GET", f"/guilds/{guild_id}/preview"))

    async def modify_guild(
        self, guild_id: int, payload: dict, reason: Optional[str] = None
    ) -> dict:
        """
        Modifies a guild's attributes.

        :param guild_id: Guild ID snowflake.
        :param payload: The parameters to change.
        :param reason: Reason to send to the audit log, if given.
        :return: The modified guild object as a dictionary
        :rtype: dict
        """

        return await self._req.request(
            Route("PATCH", f"/guilds/{guild_id}"), json=payload, reason=reason
        )

    async def leave_guild(self, guild_id: int) -> None:
        """
        Leaves a guild.

        :param guild_id: The guild snowflake ID associated.
        :return: None
        """
        return await self._req.request(
            Route("DELETE", "/users/@me/guilds/{guild_id}", guild_id=guild_id)
        )

    async def delete_guild(self, guild_id: int) -> None:
        """
        Deletes a guild.

        :param guild_id: Guild ID snowflake.
        """
        return await self._req.request(Route("DELETE", f"/guilds/{guild_id}"))

    async def get_guild_widget(self, guild_id: int) -> dict:
        """
        Returns the widget for the guild.

        :param guild_id: Guild ID snowflake.
        :return: Guild Widget contents as a dict: {"enabled":bool, "channel_id": str}
        """
        return await self._req.request(Route("GET", f"/guilds/{guild_id}/widget.json"))

    async def get_guild_widget_settings(self, guild_id: int) -> dict:
        """
        Get guild widget settings.

        :param guild_id: Guild ID snowflake.
        :return: Guild Widget contents as a dict: {"enabled":bool, "channel_id": str}
        """
        return await self._req.request(Route("GET", f"/guilds/{guild_id}"))

    async def get_guild_widget_image(self, guild_id: int, style: Optional[str] = None) -> str:
        """
        Get an url representing a png image widget for the guild.

        ..note::
            See _<https://discord.com/developers/docs/resources/guild#get-guild-widget-image> for list of styles.

        :param guild_id: Guild ID snowflake.
        :param style: The style of widget required, if given.
        :return: A url pointing to this image
        """
        route = Route("GET", f"/guilds/{guild_id}/widget.png{f'?style={style}' if style else ''}")
        return route.path

    async def modify_guild_widget(self, guild_id: int, payload: dict) -> dict:
        """
        Modify a guild widget.

        :param guild_id: Guild ID snowflake.
        :param payload: Payload containing new widget attributes.
        :return: Updated widget attributes.
        """
        return await self._req.request(Route("PATCH", f"/guilds/{guild_id}/widget"), json=payload)

    async def get_guild_invites(self, guild_id: int) -> List[Invite]:
        """
        Retrieves a list of invite objects with their own metadata.

        :param guild_id: Guild ID snowflake.
        :return: A list of invite objects
        """
        return await self._req.request(Route("GET", f"/guilds/{guild_id}/invites"))

    async def get_guild_welcome_screen(self, guild_id: int) -> WelcomeScreen:
        """
        Retrieves from the API a welcome screen associated with the guild.

        :param guild_id: Guild ID snowflake.
        :return: Welcome Screen object
        """
        return await self._req.request(Route("GET", f"/guilds/{guild_id}/welcome-screen"))

    async def modify_guild_welcome_screen(
        self, guild_id: int, enabled: bool, welcome_channels: List[int], description: str
    ) -> WelcomeScreen:
        """
        Modify the guild's welcome screen.

        :param guild_id: Guild ID snowflake.
        :param enabled: Whether the welcome screen is enabled or not.
        :param welcome_channels: The new channels (by their ID) linked in the welcome screen and their display options
        :param description: The new server description to show in the welcome screen
        :return: Updated Welcome screen object.
        """
        return await self._req.request(
            Route("PATCH", f"/guilds/{guild_id}/welcome-screen"),
            json={
                "enabled": enabled,
                "welcome_channels": welcome_channels,
                "description": description,
            },
        )

    async def get_vanity_code(self, guild_id: int) -> dict:
        return await self._req.request(
            Route("GET", "/guilds/{guild_id}/vanity-url", guild_id=guild_id)
        )

    async def modify_vanity_code(
        self, guild_id: int, code: str, reason: Optional[str] = None
    ) -> None:
        payload: Dict[str, Any] = {"code": code}
        return await self._req.request(
            Route("PATCH", "/guilds/{guild_id}/vanity-url", guild_id=guild_id),
            json=payload,
            reason=reason,
        )

    async def get_guild_integrations(self, guild_id: int) -> List[dict]:
        """
        Gets a list of integration objects associated with the Guild from the API.

        :param guild_id: Guild ID snowflake.
        :return: An array of integration objects
        """
        return await self._req.request(Route("GET", f"/guilds/{guild_id}/integrations"))

    async def delete_guild_integration(self, guild_id: int, integration_id: int) -> None:
        """
        Deletes an integration from the guild.

        :param guild_id: Guild ID snowflake.
        :param integration_id: Integration ID snowflake.
        """
        return await self._req.request(
            Route("DELETE", f"/guilds/{guild_id}/integrations/{integration_id}")
        )

    async def modify_current_user_voice_state(
        self,
        guild_id: int,
        channel_id: int,
        suppress: Optional[bool] = None,
        request_to_speak_timestamp: Optional[str] = None,
    ) -> None:
        """
        Update the current user voice state.

        :param guild_id: Guild ID snowflake.
        :param channel_id: Voice channel ID snowflake.
        :param suppress: Toggle the user's suppress state, if given.
        :param request_to_speak_timestamp: Sets the user's request to speak, if given.
        """
        return await self._req.request(
            Route("PATCH", f"/guilds/{guild_id}/voice-states/@me"),
            json={
                k: v
                for k, v in {
                    "channel_id": channel_id,
                    "suppress": suppress,
                    "request_to_speak_timestamp": request_to_speak_timestamp,
                }.items()
                if v is not None
            },
        )

    async def modify_user_voice_state(
        self, guild_id: int, user_id: int, channel_id: int, suppress: Optional[bool] = None
    ) -> None:
        """
        Modify the voice state of a user.

        :param guild_id: Guild ID snowflake.
        :param user_id: User ID snowflake.
        :param channel_id: Voice channel ID snowflake.
        :param suppress: Toggles the user's suppress state, if given.
        """
        return await self._req.request(
            Route("PATCH", f"/guilds/{guild_id}/voice-states/{user_id}"),
            json={
                k: v
                for k, v in {"channel_id": channel_id, "suppress": suppress}.items()
                if v is not None
            },
        )

    async def create_guild_from_guild_template(
        self, template_code: str, name: str, icon: Optional[str] = None
    ) -> Guild:
        """
        Create a new guild based on a template.

        ..note::
            This endpoint can only be used by bots in less than 10 guilds.

        :param template_code: The code of the template to use.
        :param name: The name of the guild (2-100 characters)
        :param icon: Guild icon URI, if given.
        :return: The newly created guild object.
        """
        payload = {
            "name": name,
        }
        if icon:
            payload["icon"] = icon
        return await self._req.request(
            Route("POST", f"/guilds/templates/{template_code}", json=payload)
        )

    async def get_guild_templates(self, guild_id: int) -> List[GuildTemplate]:
        """
        Returns an array of guild templates.

        :param guild_id: Guild ID snowflake.
        :return: An array of guild templates
        """
        return await self._req.request(Route("GET", f"/guilds/{guild_id}/templates"))

    async def create_guild_template(
        self, guild_id: int, name: str, description: Optional[str] = None
    ) -> GuildTemplate:
        """
        Create a guild template for the guild.

        :param guild_id: Guild ID snowflake.
        :param name: The name of the template
        :param description: The description of the template, if given.
        :return: The created guild template
        """
        return await self._req.request(
            Route("POST", f"/guilds/{guild_id}/templates"),
            json={
                k: v for k, v in {"name": name, "description": description}.items() if v is not None
            },
        )

    async def sync_guild_template(self, guild_id: int, template_code: str) -> GuildTemplate:
        """
        Sync the template to the guild's current state.

        :param guild_id: Guild ID snowflake.
        :param template_code: The code for the template to sync
        :return: The updated guild template.
        """
        return await self._req.request(
            Route("PUT", f"/guilds/{guild_id}/templates/{template_code}")
        )

    async def modify_guild_template(
        self,
        guild_id: int,
        template_code: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> GuildTemplate:
        """
        Modify a guild template.

        :param guild_id: Guild ID snowflake.
        :param template_code: Template ID.
        :param name: The name of the template
        :param description: The description of the template
        :return: The updated guild template
        """
        return await self._req.request(
            Route("PATCH", f"/guilds/{guild_id}/templates/{template_code}"),
            json={
                k: v for k, v in {"name": name, "description": description}.items() if v is not None
            },
        )

    async def delete_guild_template(self, guild_id: int, template_code: str) -> GuildTemplate:
        """
        Delete the guild template.

        :param guild_id: Guild ID snowflake.
        :param template_code: Template ID.
        :return: The deleted template object
        """
        # According to Polls, this returns the object. Why, I don't know.
        return await self._req.request(
            Route("DELETE", f"/guilds/{guild_id}/templates/{template_code}")
        )

    async def get_all_channels(self, guild_id: int) -> List[dict]:
        """
        Requests from the API to get all channels in the guild.

        :param guild_id: Guild Snowflake ID
        :return: A list of channels.
        """
        request = await self._req.request(
            Route("GET", "/guilds/{guild_id}/channels", guild_id=guild_id)
        )

        for channel in request:
            if channel.get("id"):
                self.cache.channels.add(Item(id=channel["id"], value=Channel(**channel)))

        return request

    async def get_all_roles(self, guild_id: int) -> List[dict]:
        """
        Gets all roles from a Guild.

        :param guild_id: Guild ID snowflake
        :return: An array of Role objects as dictionaries.
        """
        request = await self._req.request(
            Route("GET", "/guilds/{guild_id}/roles", guild_id=guild_id)
        )

        for role in request:
            if role.get("id"):
                self.cache.roles.add(Item(id=role["id"], value=Role(**role)))

        return request

    async def create_guild_role(
        self, guild_id: int, data: dict, reason: Optional[str] = None
    ) -> Role:
        """
        Create a new role for the guild.

        :param guild_id: Guild ID snowflake.
        :param data: A dict containing metadata for the role.
        :param reason: The reason for this action, if given.
        :return: Role object
        """
        request = await self._req.request(
            Route("POST", f"/guilds/{guild_id}/roles"), json=data, reason=reason
        )
        if request.get("id"):
            self.cache.roles.add(Item(id=request["id"], value=Role(**request)))

        return request

    async def modify_guild_role_position(
        self, guild_id: int, role_id: int, position: int, reason: Optional[str] = None
    ) -> List[Role]:
        """
        Modify the position of a role in the guild.

        :param guild_id: Guild ID snowflake.
        :param role_id: Role ID snowflake.
        :param position: The new position of the associated role.
        :param reason: The reason for this action, if given.
        :return: List of guild roles with updated hierarchy.
        """
        return await self._req.request(
            Route("PATCH", f"/guilds/{guild_id}/roles"),
            json={"id": role_id, "position": position},
            reason=reason,
        )

    async def modify_guild_role(
        self, guild_id: int, role_id: int, data: dict, reason: Optional[str] = None
    ) -> Role:
        """
        Modify a given role for the guild.

        :param guild_id: Guild ID snowflake.
        :param role_id: Role ID snowflake.
        :param data: A dict containing updated metadata for the role.
        :param reason: The reason for this action, if given.
        :return: Updated role object.
        """
        return await self._req.request(
            Route("PATCH", f"/guilds/{guild_id}/roles/{role_id}"), json=data, reason=reason
        )

    async def delete_guild_role(self, guild_id: int, role_id: int, reason: str = None) -> None:
        """
        Delete a guild role.

        :param guild_id: Guild ID snowflake.
        :param role_id: Role ID snowflake.
        :param reason: The reason for this action, if any.
        """
        return await self._req.request(
            Route("DELETE", f"/guilds/{guild_id}/roles/{role_id}"), reason=reason
        )

    async def create_guild_kick(
        self, guild_id: int, user_id: int, reason: Optional[str] = None
    ) -> None:
        """
        Kicks a person from the guild.

        :param guild_id: Guild ID snowflake
        :param user_id: User ID snowflake
        :param reason: Optional Reason argument.
        """
        r = Route(
            "DELETE", "/guilds/{guild_id}/members/{user_id}", guild_id=guild_id, user_id=user_id
        )
        if reason:  # apparently, its an aiohttp thing?
            r.path += f"?reason={quote(reason)}"

        await self._req.request(r)

    async def create_guild_ban(
        self,
        guild_id: int,
        user_id: int,
        delete_message_days: Optional[int] = 0,
        reason: Optional[str] = None,
    ) -> None:
        """
        Bans a person from the guild, and optionally deletes previous messages sent by them.

        :param guild_id: Guild ID snowflake
        :param user_id: User ID snowflake
        :param delete_message_days: Number of days to delete messages, from 0 to 7. Defaults to 0
        :param reason: Optional reason to ban.
        """

        return await self._req.request(
            Route("PUT", f"/guilds/{guild_id}/bans/{user_id}"),
            json={"delete_message_days": delete_message_days},
            reason=reason,
        )

    async def remove_guild_ban(
        self, guild_id: int, user_id: int, reason: Optional[str] = None
    ) -> None:
        """
        Unbans someone using the API.

        :param guild_id: Guild ID snowflake
        :param user_id: User ID snowflake
        :param reason: Optional reason to unban.
        """

        return await self._req.request(
            Route("DELETE", f"/guilds/{guild_id}/bans/{user_id}"),
            json={},
            reason=reason,
        )

    async def get_guild_bans(self, guild_id: int) -> List[dict]:
        """
        Gets a list of banned users.

        :param guild_id: Guild ID snowflake.
        :return: A list of banned users.
        """
        return await self._req.request(Route("GET", f"/guilds/{guild_id}/bans"))

    async def get_user_ban(self, guild_id: int, user_id: int) -> Optional[dict]:
        """
        Gets an object pertaining to the user, if it exists. Returns a 404 if it doesn't.

        :param guild_id: Guild ID snowflake
        :param user_id: User ID snowflake.
        :return: Ban object if it exists.
        """
        return await self._req.request(Route("GET", f"/guilds/{guild_id}/bans/{user_id}"))

    async def add_guild_member(
        self,
        guild_id: int,
        user_id: int,
        access_token: str,
        nick: Optional[str] = None,
        roles: Optional[List[Role]] = None,
        mute: bool = None,
        deaf: bool = None,
    ) -> dict:
        """
        A low level method of adding a user to a guild with pre-defined attributes.

        :param guild_id: Guild ID snowflake.
        :param user_id: User ID snowflake.
        :param access_token: User access token.
        :param nick: User's nickname on join.
        :param roles: An array of roles that the user is assigned.
        :param mute: Whether the user is mute in voice channels.
        :param deaf: Whether the user is deafened in voice channels.
        :return: Guild member object as dictionary
        """
        request = await self._req.request(
            Route("PUT", f"/guilds/{guild_id}/members/{user_id}"),
            json={
                k: v
                for k, v in {
                    "access_token": access_token,
                    "nick": nick,
                    "roles": roles,
                    "mute": mute,
                    "deaf": deaf,
                }.items()
                if v is not None
            },
        )

        self.cache.members.add(Item(id=str(user_id), value=Member(**request)))

        return request

    async def remove_guild_member(
        self, guild_id: int, user_id: int, reason: Optional[str] = None
    ) -> None:
        """
        A low level method of removing a member from a guild. This is different from banning them.

        :param guild_id: Guild ID snowflake.
        :param user_id: User ID snowflake.
        :param reason: Reason to send to audit log, if any.
        """
        return await self._req.request(
            Route("DELETE", f"/guilds/{guild_id}/members/{user_id}"), reason=reason
        )

    async def get_guild_prune_count(
        self, guild_id: int, days: int = 7, include_roles: Optional[List[int]] = None
    ) -> dict:
        """
        Retrieves a dict from an API that results in how many members would be pruned given the amount of days.

        :param guild_id: Guild ID snowflake.
        :param days:  Number of days to count. Defaults to ``7``.
        :param include_roles: Role IDs to include, if given.
        :return: A dict denoting `{"pruned": int}`
        """
        payload = {"days": days}
        if include_roles:
            payload["include_roles"] = ", ".join(
                str(x) for x in include_roles
            )  # would still iterate

        return await self._req.request(Route("GET", f"/guilds/{guild_id}/prune"), params=payload)

    async def get_guild_auditlog(
        self,
        guild_id: int,
        user_id: Optional[int] = None,
        action_type: Optional[int] = None,
        before: Optional[int] = None,
        limit: int = 50,
    ) -> dict:
        """
        Returns an audit log object for the guild. Requires the 'VIEW_AUDIT_LOG' permission.
        :param guild_id: Guild ID snowflake.
        :param user_id: User ID snowflake. filter the log for actions made by a user.
        :param action_type: the type ID of audit log event.
        :param before: filter the log before a certain entry id.
        :param limit: how many entries are returned (default 50, minimum 1, maximum 100)
        """

        payload = {"limit": limit}
        if user_id:
            payload["user_id"] = user_id
        if action_type:
            payload["action_type"] = action_type
        if before:
            payload["before"] = before

        return await self._req.request(
            Route("GET", f"/guilds/{guild_id}/audit-logs"), params=payload
        )

    # Guild (Member) endpoint

    async def get_member(self, guild_id: int, member_id: int) -> Optional[Member]:
        """
        Uses the API to fetch a member from a guild.

        :param guild_id: Guild ID snowflake.
        :param member_id: Member ID snowflake.
        :return: A member object, if any.
        """
        return await self._req.request(
            Route(
                "GET",
                "/guilds/{guild_id}/members/{member_id}",
                guild_id=guild_id,
                member_id=member_id,
            )
        )

    async def get_list_of_members(
        self, guild_id: int, limit: int = 1, after: Optional[int] = None
    ) -> List[Member]:
        """
        Lists the members of a guild.

        :param guild_id: Guild ID snowflake
        :param limit: How many members to get from the API. Max is 1000. Defaults to 1.
        :param after: Get Member IDs after this snowflake. Defaults to None.
        :return: An array of Member objects.
        """
        payload = {"limit": limit}
        if after:
            payload["after"] = after

        return await self._req.request(Route("GET", f"/guilds/{guild_id}/members"), params=payload)

    async def search_guild_members(self, guild_id: int, query: str, limit: int = 1) -> List[Member]:
        """
        Search a guild for members whose username or nickname starts with provided string.

        :param guild_id: Guild ID snowflake.
        :param query: The string to search for
        :param limit: The number of members to return. Defaults to 1.
        """

        return await self._req.request(
            Route("GET", f"/guilds/{guild_id}/members/search"),
            params={"query": query, "limit": limit},
        )

    async def add_member_role(
        self, guild_id: int, user_id: int, role_id: int, reason: Optional[str] = None
    ) -> None:
        """
        Adds a role to a guild member.

        :param guild_id: The ID of the guild
        :param user_id: The ID of the user
        :param role_id: The ID of the role to add
        :param reason: The reason for this action. Defaults to None.
        """
        return await self._req.request(
            Route(
                "PUT",
                "/guilds/{guild_id}/members/{user_id}/roles/{role_id}",
                guild_id=guild_id,
                user_id=user_id,
                role_id=role_id,
            ),
            reason=reason,
        )

    async def remove_member_role(
        self, guild_id: int, user_id: int, role_id: int, reason: Optional[str] = None
    ) -> None:
        """
        Removes a role to a guild member.

        :param guild_id: The ID of the guild
        :param user_id: The ID of the user
        :param role_id: The ID of the role to add
        :param reason: The reason for this action. Defaults to None.
        """
        return await self._req.request(
            Route(
                "DELETE",
                "/guilds/{guild_id}/members/{user_id}/roles/{role_id}",
                guild_id=guild_id,
                user_id=user_id,
                role_id=role_id,
            ),
            reason=reason,
        )

    async def modify_member(
        self, user_id: int, guild_id: int, payload: dict, reason: Optional[str] = None
    ):
        """
        Edits a member.
        This can nick them, change their roles, mute/deafen (and its contrary), and moving them across channels and/or disconnect them.

        :param user_id: Member ID snowflake.
        :param guild_id: Guild ID snowflake.
        :param payload: Payload representing parameters (nick, roles, mute, deaf, channel_id)
        :param reason: The reason for this action. Defaults to None.
        :return: Modified member object.
        """

        return await self._req.request(
            Route(
                "PATCH", "/guilds/{guild_id}/members/{user_id}", guild_id=guild_id, user_id=user_id
            ),
            json=payload,
            reason=reason,
        )

    # Channel endpoint.

    async def get_channel(self, channel_id: int) -> dict:
        """
        Gets a channel by ID. If the channel is a thread, it also includes thread members (and other thread attributes).

        :param channel_id: Channel ID snowflake.
        :return: Dictionary of the channel object.
        """
        request = await self._req.request(Route("GET", f"/channels/{channel_id}"))
        self.cache.channels.add(Item(id=str(channel_id), value=Channel(**request)))

        return request

    async def delete_channel(self, channel_id: int) -> None:
        """
        Deletes a channel.

        :param channel_id: Channel ID snowflake
        """
        return await self._req.request(
            Route("DELETE", "/channels/{channel_id}", channel_id=channel_id)
        )

    async def get_channel_messages(
        self,
        channel_id: int,
        limit: int = 50,
        around: Optional[int] = None,
        before: Optional[int] = None,
        after: Optional[int] = None,
    ) -> List[Message]:
        """
        Get messages from a channel.

        ..note::
            around, before, and after arguments are mutually exclusive.

        :param channel_id: Channel ID snowflake.
        :param limit: How many messages to get. Defaults to 50, the max is 100.
        :param around: Get messages around this snowflake ID.
        :param before: Get messages before this snowflake ID.
        :param after: Get messages after this snowflake ID.
        :return: An array of Message objects.
        """
        params: Dict[str, Union[int, str]] = {"limit": limit}

        params_used = 0

        if before:
            params_used += 1
            params["before"] = before
        if after:
            params_used += 1
            params["after"] = after
        if around:
            params_used += 1
            params["around"] = around

        if params_used > 1:
            raise ValueError(
                "`before`, `after` and `around` are mutually exclusive. Please pass only one of them."
            )

        request = await self._req.request(
            Route("GET", f"/channels/{channel_id}/messages"), params=params
        )

        for message in request:
            if message.get("id"):
                self.cache.messages.add(Item(id=message["id"], value=Message(**message)))

        return request

    async def create_channel(
        self, guild_id: int, payload: dict, reason: Optional[str] = None
    ) -> dict:
        """
        Creates a channel within a guild.

        ..note::
            This does not handle payload in this method. Tread carefully.

        :param guild_id: Guild ID snowflake.
        :param payload: Payload data.
        :param reason: Reason to show in audit log, if needed.
        :return: Channel object as dictionary.
        """
        request = await self._req.request(
            Route("POST", f"/guilds/{guild_id}/channels"), json=payload, reason=reason
        )
        if request.get("id"):
            self.cache.channels.add(Item(id=request["id"], value=Channel(**request)))

        return request

    async def move_channel(
        self,
        guild_id: int,
        channel_id: int,
        new_pos: int,
        parent_id: Optional[int],
        lock_perms: bool = False,
        reason: Optional[str] = None,
    ):
        """
        Moves a channel to a new position.

        :param guild_id: Guild ID snowflake.
        :param channel_id: Channel ID snowflake.
        :param new_pos: The new channel position.
        :param parent_id: The category parent ID, if needed.
        :param lock_perms: Sync permissions with the parent associated with parent_id. Defaults to False.
        :param reason: Reason to display to the audit log, if any.
        :return: ?
        """
        payload = {"id": channel_id, "position": new_pos, "lock_permissions": lock_perms}
        if parent_id:
            payload["parent_id"] = parent_id

        return await self._req.request(
            Route("PATCH", f"/guilds/{guild_id}/channels"), json=payload, reason=reason
        )

    async def modify_channel(
        self, channel_id: int, data: dict, reason: Optional[str] = None
    ) -> Channel:
        """
        Update a channel's settings.

        :param channel_id: Channel ID snowflake.
        :param data: Data representing updated settings.
        :param reason: Reason, if any.
        :return: Channel with updated attributes, if successful.
        """
        return await self._req.request(
            Route("PATCH", f"/channels/{channel_id}"), json=data, reason=reason
        )

    async def get_channel_invites(self, channel_id: int) -> List[Invite]:
        """
        Get the invites for the channel.

        :param channel_id: Channel ID snowflake.
        :return: List of invite objects
        """
        return await self._req.request(Route("GET", f"/channels/{channel_id}/invites"))

    async def create_channel_invite(
        self, channel_id: int, data: dict, reason: Optional[str] = None
    ) -> Invite:
        """
        Creates an invite for the given channel.

        ..note::
            This method does not handle payload. It just sends it.

        :param channel_id: Channel ID snowflake.
        :param data: Data representing the payload/invite attributes.
        :param reason: Reason to show in the audit log, if any.
        :return: An invite object.
        """
        return await self._req.request(
            Route("POST", f"/channels/{channel_id}/invites"), json=data, reason=reason
        )

    async def delete_invite(self, invite_code: str, reason: Optional[str] = None) -> dict:
        """
        Delete an invite.

        :param invite_code: The code of the invite to delete
        :param reason: Reason to show in the audit log, if any.
        :return: The deleted invite object
        """
        return await self._req.request(Route("DELETE", f"/invites/{invite_code}"), reason=reason)

    async def edit_channel_permission(
        self,
        channel_id: int,
        overwrite_id: int,
        allow: str,
        deny: str,
        perm_type: int,
        reason: Optional[str] = None,
    ) -> None:
        """
        Edits the channel's permission overwrites for a user or role in a given channel.

        :param channel_id: Channel ID snowflake.
        :param overwrite_id: The ID of the overridden object.
        :param allow: the bitwise value of all allowed permissions
        :param deny: the bitwise value of all disallowed permissions
        :param perm_type: 0 for a role or 1 for a member
        :param reason: Reason to display in the Audit Log, if given.
        """
        return await self._req.request(
            Route("PUT", f"/channels/{channel_id}/permissions/{overwrite_id}"),
            json={"allow": allow, "deny": deny, "type": perm_type},
            reason=reason,
        )

    async def delete_channel_permission(
        self, channel_id: int, overwrite_id: int, reason: Optional[str] = None
    ) -> None:
        """
        Deletes a channel permission overwrite for a user or role in a channel.

        :param channel_id: Channel ID snowflake.
        :param overwrite_id: The ID of the overridden object.
        :param reason: Reason to display in the Audit Log, if given.
        """
        return await self._req.request(
            Route("DELETE", f"/channels/{channel_id}/{overwrite_id}"), reason=reason
        )

    async def trigger_typing(self, channel_id: int) -> None:
        """
        Posts "... is typing" in a given channel.

        ..note:
            By default, this lib doesn't use this endpoint, however, this is listed for third-party implementation.

        :param channel_id: Channel ID snowflake.
        """
        return await self._req.request(Route("POST", f"/channels/{channel_id}/typing"))

    async def get_pinned_messages(self, channel_id: int) -> List[Message]:
        """
        Get all pinned messages from a channel.

        :param channel_id: Channel ID snowflake.
        :return: A list of pinned message objects.
        """
        return await self._req.request(Route("GET", f"/channels/{channel_id}/pins"))

    async def create_stage_instance(
        self, channel_id: int, topic: str, privacy_level: int = 1, reason: Optional[str] = None
    ) -> StageInstance:
        """
        Create a new stage instance.

        :param channel_id: Channel ID snowflake.
        :param topic: The topic of the stage instance. Limited to 1-120 characters.
        :param privacy_level: The privacy_level of the stage instance (defaults to guild-only "1").
        :param reason: The reason for the creating the stage instance, if any.
        :return: The new stage instance
        """
        return await self._req.request(
            Route("POST", "/stage-instances"),
            json={
                "channel_id": channel_id,
                "topic": topic,
                "privacy_level": privacy_level,
            },
            reason=reason,
        )

    async def get_stage_instance(self, channel_id: int) -> StageInstance:
        """
        Get the stage instance associated with a given channel, if it exists.

        :param channel_id: Channel ID snowflake.
        :return: A stage instance.
        """
        return await self._req.request(Route("GET", f"/stage-instances/{channel_id}"))

    async def modify_stage_instance(
        self,
        channel_id: int,
        topic: Optional[str] = None,
        privacy_level: Optional[int] = None,
        reason: Optional[str] = None,
    ) -> StageInstance:
        """
        Update the fields of a given stage instance.

        :param channel_id: Channel ID snowflake.
        :param topic: The new topic of the stage instance, if given. Limited to 1-120 characters.
        :param privacy_level: The new privacy_level of the stage instance.
        :param reason: The reason for the creating the stage instance, if any.
        :return: The updated stage instance.
        """
        return await self._req.request(
            Route("PATCH", f"/stage-instances/{channel_id}"),
            json={
                k: v
                for k, v in {"topic": topic, "privacy_level": privacy_level}.items()
                if v is not None
            },
            reason=reason,
        )

    async def delete_stage_instance(self, channel_id: int, reason: Optional[str] = None) -> None:
        """
        Delete a stage instance.

        :param channel_id: Channel ID snowflake.
        :param reason: The reason for the creating the stage instance, if any.
        """
        return await self._req.request(
            Route("DELETE", f"/stage-instances/{channel_id}"), reason=reason
        )

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
        return await self._req.request(
            Route("PUT", f"/channels/{thread_id}/thread-members/{user_id}")
        )

    async def remove_member_from_thread(self, thread_id: int, user_id: int) -> None:
        """
        Remove another user from a thread.

        :param thread_id: The ID of the thread
        :param user_id: The ID of the user to remove
        """
        return await self._req.request(
            Route("DELETE", f"/channels/{thread_id}/thread-members/{user_id}")
        )

    async def get_member_from_thread(self, thread_id: int, user_id: int) -> dict:
        """
        Get a member from a thread.

        :param thread_id: The ID of the thread
        :param user_id: The ID of the user to find
        :return: A thread member object, if they're in the thread.
        """
        # Returns 404 if they don't
        return await self._req.request(
            Route("GET", f"/channels/{thread_id}/thread-members/{user_id}")
        )

    async def list_thread_members(self, thread_id: int) -> List[dict]:
        """
        Get a list of members in the thread.

        :param thread_id: the id of the thread
        :return: a list of thread member objects
        """
        return await self._req.request(Route("GET", f"/channels/{thread_id}/thread-members"))

    async def list_public_archived_threads(
        self, channel_id: int, limit: int = None, before: Optional[int] = None
    ) -> List[dict]:
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
        return await self._req.request(
            Route("GET", f"/channels/{channel_id}/threads/archived/public"), json=payload
        )

    async def list_private_archived_threads(
        self, channel_id: int, limit: int = None, before: Optional[int] = None
    ) -> List[dict]:
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
        return await self._req.request(
            Route("GET", f"/channels/{channel_id}/threads/archived/private"), json=payload
        )

    async def list_joined_private_archived_threads(
        self, channel_id: int, limit: int = None, before: Optional[int] = None
    ) -> List[dict]:
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
            Route("GET", f"/channels/{channel_id}/users/@me/threads/archived/private"), json=payload
        )

    async def list_active_threads(self, guild_id: int) -> List[dict]:
        """
        List active threads within a guild.

        :param guild_id: the guild id to get threads from
        :return: A list of active threads
        """
        return await self._req.request(Route("GET", f"/guilds/{guild_id}/threads/active"))

    async def create_thread(
        self,
        channel_id: int,
        name: str,
        thread_type: int = None,
        auto_archive_duration: Optional[int] = None,
        invitable: Optional[bool] = None,
        message_id: Optional[int] = None,
        reason: Optional[str] = None,
    ) -> dict:
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
        payload = {"name": name}
        if auto_archive_duration:
            payload["auto_archive_duration"] = auto_archive_duration
        if message_id:
            request = await self._req.request(
                Route("POST", f"/channels/{channel_id}/messages/{message_id}/threads"),
                json=payload,
                reason=reason,
            )
            if request.get("id"):
                self.cache.channels.add(Item(id=request["id"], value=request))
            return request

        payload["type"] = thread_type
        payload["invitable"] = invitable
        request = await self._req.request(
            Route("POST", f"/channels/{channel_id}/threads"), json=payload, reason=reason
        )
        if request.get("id"):
            self.cache.channels.add(Item(id=request["id"], value=request))

        return request

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

    async def remove_user_reaction(
        self, channel_id: int, message_id: int, emoji: str, user_id: int
    ) -> None:
        """
        Remove user's reaction from a message.

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
        Remove all reactions from a message.

        :param channel_id: The channel this is taking place in.
        :param message_id: The message to clear reactions from.
        """
        return await self._req.request(
            Route(
                "DELETE",
                "/channels/{channel_id}/messages/{message_id}/reactions",
                channel_id=channel_id,
                message_id=message_id,
            )
        )

    async def remove_all_reactions_of_emoji(
        self, channel_id: int, message_id: int, emoji: str
    ) -> None:
        """
        Remove all reactions of a certain emoji from a message.

        :param channel_id: Channel snowflake ID.
        :param message_id: Message snowflake ID.
        :param emoji: The emoji to remove (format: `name:id`)
        """
        return await self._req.request(
            Route(
                "DELETE",
                "/channels/{channel_id}/messages/{message_id}/reactions/{emoji}",
                channel_id=channel_id,
                message_id=message_id,
                emoji=emoji,
            )
        )

    async def get_reactions_of_emoji(
        self, channel_id: int, message_id: int, emoji: str
    ) -> List[User]:
        """
        Gets the users who reacted to the emoji.

        :param channel_id: Channel snowflake ID.
        :param message_id: Message snowflake ID.
        :param emoji: The emoji to get (format: `name:id`)
        :return A list of users who sent that emoji.
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

    async def create_guild_sticker(
        self, payload: FormData, guild_id: int, reason: Optional[str] = None
    ):
        """
        Create a new sticker for the guild. Requires the MANAGE_EMOJIS_AND_STICKERS permission.

        :param payload: the payload to send.
        :param guild_id: The guild to create sticker at.
        :param reason: The reason for this action.
        :return: The new sticker data on success.
        """
        return await self._req.request(
            Route("POST", f"/guild/{guild_id}/stickers"), json=payload, reason=reason
        )

    async def modify_guild_sticker(
        self, payload: dict, guild_id: int, sticker_id: int, reason: Optional[str] = None
    ):
        """
        Modify the given sticker. Requires the MANAGE_EMOJIS_AND_STICKERS permission.

        :param payload: the payload to send.
        :param guild_id: The guild of the target sticker.
        :param sticker_id:  The sticker to modify.
        :param reason: The reason for this action.
        :return: The updated sticker data on success.
        """
        return await self._req.request(
            Route("PATCH", f"/guild/{guild_id}/stickers/{sticker_id}"), json=payload, reason=reason
        )

    async def delete_guild_sticker(
        self, guild_id: int, sticker_id: int, reason: Optional[str] = None
    ) -> None:
        """
        Delete the given sticker. Requires the MANAGE_EMOJIS_AND_STICKERS permission.

        :param guild_id: The guild of the target sticker.
        :param sticker_id:  The sticker to delete.
        :param reason: The reason for this action.
        :return: Returns 204 No Content on success.
        """
        return await self._req.request(
            Route("DELETE", f"/guild/{guild_id}/stickers/{sticker_id}"), reason=reason
        )

    # Interaction endpoint (Application commands) **

    # TODO: Merge single and batch variants ?

    async def get_application_commands(
        self, application_id: Union[int, Snowflake], guild_id: Optional[int] = None
    ) -> List[dict]:
        """
        Get all application commands from an application.

        :param application_id: Application ID snowflake
        :param guild_id: Guild to get commands from, if specified. Defaults to global (None)
        :return: A list of Application commands.
        """
        application_id = int(application_id)

        if guild_id in (None, "None"):
            return await self._req.request(Route("GET", f"/applications/{application_id}/commands"))
        else:
            return await self._req.request(
                Route("GET", f"/applications/{application_id}/guilds/{guild_id}/commands")
            )

    async def create_application_command(
        self, application_id: Union[int, Snowflake], data: dict, guild_id: Optional[int] = None
    ):
        """
        Registers to the Discord API an application command.

        :param application_id: Application ID snowflake
        :param data: The dictionary that contains the command (name, description, etc)
        :param guild_id: Guild ID snowflake to put them in, if applicable.
        :return: An application command object.
        """

        application_id = int(application_id)

        url = (
            f"/applications/{application_id}/commands"
            if guild_id in (None, "None")
            else f"/applications/{application_id}/guilds/{guild_id}/commands"
        )

        return await self._req.request(Route("POST", url), json=data)

    async def overwrite_application_command(
        self, application_id: int, data: List[dict], guild_id: Optional[int] = None
    ) -> List[dict]:
        """
        Overwrites application command(s) from a scope to the new, updated commands.

        ..note:
            This applies to all forms of application commands (slash and context menus)

        :param application_id: Application ID snowflake
        :param data: The dictionary that contains the command (name, description, etc)
        :param guild_id: Guild ID snowflake to put them in, if applicable.
        :return: An array of application command objects.
        """
        url = (
            f"/applications/{application_id}/commands"
            if not guild_id
            else f"/applications/{application_id}/guilds/{guild_id}/commands"
        )

        return await self._req.request(Route("PUT", url), json=data)

    async def edit_application_command(
        self,
        application_id: Union[int, Snowflake],
        data: dict,
        command_id: Union[int, Snowflake],
        guild_id: Optional[int] = None,
    ) -> dict:
        """
        Edits an application command.

        :param application_id: Application ID snowflake.
        :param data: A dictionary containing updated attributes
        :param command_id: The application command ID snowflake
        :param guild_id: Guild ID snowflake, if given. Defaults to None/global.
        :return: The updated application command object.
        """
        application_id, command_id = int(application_id), int(command_id)
        r = (
            Route(
                "PATCH",
                "/applications/{application_id}/commands/{command_id}",
                application_id=application_id,
                command_id=command_id,
            )
            if guild_id in (None, "None")
            else Route(
                "PATCH",
                "/applications/{application_id}/guilds/{guild_id}/commands/{command_id}",
                application_id=application_id,
                command_id=command_id,
                guild_id=guild_id,
            )
        )
        return await self._req.request(r, json=data)

    async def delete_application_command(
        self, application_id: Union[int, Snowflake], command_id: int, guild_id: Optional[int] = None
    ) -> None:
        """
        Deletes an application command.

        :param application_id: Application ID snowflake.
        :param command_id: Application command ID snowflake.
        :param guild_id: Guild ID snowflake, if declared. Defaults to None (Global).
        """

        application_id = int(application_id)

        r = (
            Route(
                "DELETE",
                "/applications/{application_id}/guilds/{guild_id}/commands/{command_id}",
                application_id=application_id,
                command_id=command_id,
                guild_id=guild_id,
            )
            if guild_id not in (None, "None")
            else Route(
                "DELETE",
                "/applications/{application_id}/commands/{command_id}",
                application_id=application_id,
                command_id=command_id,
            )
        )
        return await self._req.request(r)

    async def edit_application_command_permissions(
        self, application_id: int, guild_id: int, command_id: int, data: List[dict]
    ) -> dict:
        """
        Edits permissions for an application command.

        :param application_id: Application ID snowflake
        :param guild_id: Guild ID snowflake
        :param command_id: Application command ID snowflake
        :param data: Permission data.
        :return: Returns an updated Application Guild permission object.
        """

        return await self._req.request(
            Route(
                "PUT",
                f"/applications/{application_id}/guilds/{guild_id}/commands/{command_id}/permissions",
            ),
            json=data,
        )

    async def batch_edit_application_command_permissions(
        self, application_id: int, guild_id: int, data: List[dict]
    ) -> List[dict]:
        """
        Edits permissions for all Application Commands in a guild.

        :param application_id: Application ID snowflake
        :param guild_id: Guild ID snowflake
        :param data: An array of permission dictionaries.
        :return: An updated array of application array permissions.
        """
        return await self._req.request(
            Route("PUT", f"/applications/{application_id}/guilds/{guild_id}/commands/permissions"),
            json=data,
        )

    async def get_application_command_permissions(
        self, application_id: int, guild_id: int, command_id: int
    ) -> dict:
        """
        Gets, from the Discord API, permissions from a specific Guild application command.

        :param application_id: Application ID snowflake
        :param guild_id: Guild ID snowflake
        :param command_id: Application Command ID snowflake
        :return: a Guild Application Command permissions object
        """
        return await self._req.request(
            Route(
                "GET",
                f"/applications/{application_id}/guilds/{guild_id}/commands/{command_id}/permissions",
            )
        )

    async def get_all_application_command_permissions(
        self, application_id: int, guild_id: int
    ) -> List[dict]:
        """
        Gets, from the Discord API, permissions from all Application commands at that Guild.

        :param application_id: Application ID snowflake
        :param guild_id: Guild ID snowflake
        :return: An array of Guild Application Command permissions
        """
        return await self._req.request(
            Route("GET", f"/applications/{application_id}/guilds/{guild_id}/commands/permissions")
        )

    async def create_interaction_response(
        self, token: str, application_id: int, data: dict
    ) -> None:
        """
        Posts initial response to an interaction, but you need to add the token.

        :param token: Token.
        :param application_id: Application ID snowflake
        :param data: The data to send.
        """
        return await self._req.request(
            Route("POST", f"/interactions/{application_id}/{token}/callback"), json=data
        )

    # This is still Interactions, but this also applies to webhooks
    # i.e. overlay
    async def get_original_interaction_response(
        self, token: str, application_id: str, message_id: int = "@original"
    ) -> dict:
        """
        Gets an existing interaction message.

        :param token: token
        :param application_id: Application ID snowflake.
        :param message_id: Message ID snowflake. Defaults to `@original` which represents the initial response msg.
        :return: Message data.
        """
        # ^ again, I don't know if python will let me
        return await self._req.request(
            Route("GET", f"/webhooks/{application_id}/{token}/messages/{message_id}")
        )

    async def edit_interaction_response(
        self, data: dict, token: str, application_id: str, message_id: str = "@original"
    ) -> dict:
        """
        Edits an existing interaction message, but token needs to be manually called.

        :param data: A dictionary containing the new response.
        :param token: the token of the interaction
        :param application_id: Application ID snowflake.
        :param message_id: Message ID snowflake. Defaults to `@original` which represents the initial response msg.
        :return: Updated message data.
        """
        # ^ again, I don't know if python will let me
        return await self._req.request(
            Route("PATCH", f"/webhooks/{application_id}/{token}/messages/{message_id}"),
            json=data,
        )

    async def delete_interaction_response(
        self, token: str, application_id: str, message_id: int = "original"
    ) -> None:
        """
        Deletes an existing interaction message.

        :param token: the token of the interaction
        :param application_id: Application ID snowflake.
        :param message_id: Message ID snowflake. Defaults to `@original` which represents the initial response msg.
        """

        # This is, basically, a helper method for the thing,
        # because interactions are webhooks

        await self.delete_webhook_message(
            webhook_id=int(application_id), webhook_token=token, message_id=message_id
        )

    async def _post_followup(self, data: dict, token: str, application_id: str) -> None:
        """
        Send a followup to an interaction.

        :param data: the payload to send
        :param application_id: the id of the application
        :param token: the token of the interaction
        """

        return await self._req.request(
            Route("POST", f"/webhooks/{application_id}/{token}"), json=data
        )

    # Webhook endpoints.
    # TODO: Not sure why, but there's no webhook models? Will rectify later.
    # Also, todo: figure out what avatar is

    async def create_webhook(self, channel_id: int, name: str, avatar: Any = None) -> dict:
        """
        Create a new webhook.

        :param channel_id: Channel ID snowflake.
        :param name: Name of the webhook (1-80 characters)
        :param avatar: The image for the default webhook avatar, if given.

        :return Webhook object
        """
        return await self._req.request(
            Route("POST", f"/channels/{channel_id}/webhooks"), json={"name": name, "avatar": avatar}
        )

    async def get_channel_webhooks(self, channel_id: int) -> List[dict]:
        """
        Return a list of channel webhook objects.

        :param channel_id: Channel ID snowflake.
        :return:List of webhook objects
        """
        return await self._req.request(Route("GET", f"/channels/{channel_id}/webhooks"))

    async def get_guild_webhooks(self, guild_id: int) -> List[dict]:
        """
        Return a list of guild webhook objects.

        :param guild_id: Guild ID snowflake

        :return: List of webhook objects
        """
        return await self._req.request(Route("GET", f"/guilds/{guild_id}/webhooks"))

    async def get_webhook(self, webhook_id: int, webhook_token: str = None) -> dict:
        """
        Return the new webhook object for the given id.

        :param webhook_id: Webhook ID snowflake.
        :param webhook_token: Webhook Token, if given.

        :return:Webhook object
        """
        endpoint = f"/webhooks/{webhook_id}{f'/{webhook_token}' if webhook_token else ''}"

        return await self._req.request(Route("GET", endpoint))

    async def modify_webhook(
        self,
        webhook_id: int,
        name: str,
        avatar: Any,
        channel_id: int,
        webhook_token: str = None,
    ) -> dict:
        """
        Modify a webhook.

        :param webhook_id: Webhook ID snowflake
        :param name: the default name of the webhook
        :param avatar: image for the default webhook avatar
        :param channel_id: Channel ID snowflake of new destination
        :param webhook_token: The token for the webhook, if given.

        :return: Modified webhook object.
        """
        endpoint = f"/webhooks/{webhook_id}{f'/{webhook_token}' if webhook_token else ''}"

        return await self._req.request(
            Route("PATCH", endpoint),
            json={"name": name, "avatar": avatar, "channel_id": channel_id},
        )

    async def delete_webhook(self, webhook_id: int, webhook_token: str = None):
        """
        Delete a webhook.

        :param webhook_id: Webhook ID snowflake.
        :param webhook_token: The token for the webhook, if given.
        """

        endpoint = f"/webhooks/{webhook_id}{f'/{webhook_token}' if webhook_token else ''}"

        return await self._req.request(Route("DELETE", endpoint))

    async def execute_webhook(
        self,
        webhook_id: int,
        webhook_token: str,
        payload: dict,
        wait: bool = False,
        thread_id: Optional[int] = None,
    ) -> Optional[Message]:
        """
        Sends a message as a webhook.

        :param webhook_id: Webhook ID snowflake.
        :param webhook_token: The token for the webhook.
        :param payload: Payload consisting of the message.
        :param wait: A bool that signifies waiting for server confirmation of a send before responding.
        :param thread_id: Optional, sends a message to the specified thread.
        :return: The message sent, if wait=True, else None.
        """

        return await self._req.request(
            Route("POST", f"/webhooks/{webhook_id}/{webhook_token}"),
            params={"wait": wait, "thread_id": thread_id},
            json=payload,
        )

    async def execute_slack_webhook(
        self, webhook_id: int, webhook_token: str, payload: dict
    ) -> None:
        """
        Sends a message to a Slack-compatible webhook.

        :param webhook_id: Webhook ID snowflake.
        :param webhook_token: The token for the webhook.
        :param payload: Payload consisting of the message.

        :return: ?

        .. note::
            Payload structure is different than Discord's. See `here <https://api.slack.com/messaging/webhooks>_` for more details.
        """

        return await self._req.request(
            Route("POST", f"/webhooks/{webhook_id}/{webhook_token}/slack"), json=payload
        )

    async def execute_github_webhook(
        self, webhook_id: int, webhook_token: str, payload: dict
    ) -> None:
        """
        Sends a message to a Github-compatible webhook.

        :param webhook_id: Webhook ID snowflake.
        :param webhook_token: The token for the webhook.
        :param payload: Payload consisting of the message.

        :return: ?

        .. note::
            Payload structure is different than Discord's. See `here <https://discord.com/developers/docs/resources/webhook#execute-githubcompatible-webhook>_` for more details.
        """

        return await self._req.request(
            Route("POST", f"/webhooks/{webhook_id}/{webhook_token}/slack"), json=payload
        )

    async def get_webhook_message(
        self, webhook_id: int, webhook_token: str, message_id: int
    ) -> Message:
        """
        Retrieves a message sent from a Webhook.

        :param webhook_id: Webhook ID snowflake.
        :param webhook_token: Webhook token.
        :param message_id: Message ID snowflake,
        :return: A Message object.
        """

        return await self._req.request(
            Route("GET", f"/webhooks/{webhook_id}/{webhook_token}/messages/{message_id}")
        )

    async def edit_webhook_message(
        self, webhook_id: int, webhook_token: str, message_id: int, data: dict
    ) -> Message:
        """
        Edits a message sent from a Webhook.

        :param webhook_id: Webhook ID snowflake.
        :param webhook_token: Webhook token.
        :param message_id: Message ID snowflake.
        :param data: A payload consisting of new message attributes.
        :return: An updated message object.
        """

        return await self._req.request(
            Route("PATCH", f"/webhooks/{webhook_id}/{webhook_token}/messages/{message_id}"),
            json=data,
        )

    async def delete_webhook_message(
        self, webhook_id: int, webhook_token: str, message_id: int
    ) -> None:
        """
        Deletes a message object.

        :param webhook_id: Webhook ID snowflake.
        :param webhook_token: Webhook token.
        :param message_id: Message ID snowflake.
        """

        return await self._req.request(
            Route("DELETE", f"/webhooks/{webhook_id}/{webhook_token}/messages/{message_id}")
        )

    async def delete_original_webhook_message(self, webhook_id: int, webhook_token: str) -> None:
        """
        Deletes the original message object sent.

        :param webhook_id: Webhook ID snowflake.
        :param webhook_token: Webhook token.
        """

        return await self._req.request(
            Route("DELETE", f"/webhooks/{webhook_id}/{webhook_token}/messages/@original")
        )

    # Emoji endpoints, a subset of guild but it should get its own thing...

    async def get_all_emoji(self, guild_id: int) -> List[Emoji]:
        """
        Gets all emojis from a guild.

        :param guild_id: Guild ID snowflake.
        :return: A list of emojis.
        """
        return await self._req.request(Route("GET", f"/guilds/{guild_id}/emojis"))

    async def get_guild_emoji(self, guild_id: int, emoji_id: int) -> Emoji:
        """
        Gets an emote from a guild.

        :param guild_id: Guild ID snowflake.
        :param emoji_id: Emoji ID snowflake.
        :return: Emoji object
        """
        return await self._req.request(Route("GET", f"/guilds/{guild_id}/emojis/{emoji_id}"))

    async def create_guild_emoji(
        self, guild_id: int, data: dict, reason: Optional[str] = None
    ) -> Emoji:
        """
        Creates an emoji.

        :param guild_id: Guild ID snowflake.
        :param data: Emoji parameters.
        :param reason: Optionally, give a reason.
        :return: An emoji object with the included parameters.
        """
        return await self._req.request(
            Route("POST", f"/guilds/{guild_id}/emojis"), json=data, reason=reason
        )

    async def modify_guild_emoji(
        self, guild_id: int, emoji_id: int, data: dict, reason: Optional[str] = None
    ) -> Emoji:
        """
        Modifies an emoji.

        :param guild_id: Guild ID snowflake.
        :param emoji_id: Emoji ID snowflake
        :param data: Emoji parameters with updated attributes
        :param reason: Optionally, give a reason.
        :return: An emoji object with updated attributes.
        """
        return await self._req.request(
            Route("PATCH", f"/guilds/{guild_id}/emojis/{emoji_id}"), json=data, reason=reason
        )

    async def delete_guild_emoji(
        self, guild_id: int, emoji_id: int, reason: Optional[str] = None
    ) -> None:
        """
        Deletes an emoji.

        :param guild_id: Guild ID snowflake.
        :param emoji_id: Emoji ID snowflake
        :param reason: Optionally, give a reason.
        """
        await self._req.request(
            Route("DELETE", f"/guilds/{guild_id}/emojis/{emoji_id}"), reason=reason
        )

    # Guild Scheduled Events endpoints

    async def create_scheduled_event(self, guild_id: Snowflake, data: dict) -> dict:
        """
        Creates a scheduled event.

        :param guild_id: Guild ID snowflake.
        :param data: The dictionary containing the parameters and values to edit the associated event.
        :return A dictionary containing the new guild scheduled event object on success.
        """
        guild_id = int(guild_id)
        valid_keys = (
            "channel_id",
            "name",
            "privacy_level",
            "scheduled_start_time",
            "scheduled_end_time",
            "entity_metadata",
            "description",
            "entity_type",
        )
        payload = {k: v for k, v in data.items() if k in valid_keys}

        return await self._req.request(
            Route("POST", "/guilds/{guild_id}/scheduled-events", guild_id=int(guild_id)),
            json=payload,
        )

    async def get_scheduled_event(
        self, guild_id: Snowflake, guild_scheduled_event_id: Snowflake, with_user_count: bool
    ) -> dict:
        """
        Gets a guild scheduled event.

        :param guild_id: Guild ID snowflake.
        :param guild_scheduled_event_id: Guild Scheduled Event ID snowflake.
        :param with_user_count: A boolean to include number of users subscribed to the associated event, if given.
        :return A dictionary containing the guild scheduled event object on success.
        """
        guild_id, event_id = int(guild_id), int(guild_scheduled_event_id)
        params = {}
        if with_user_count:
            params["with_user_count"] = with_user_count

        return await self._req.request(
            Route(
                "GET",
                "/guilds/{guild_id}/scheduled-events/{event_id}",
                guild_id=guild_id,
                event_id=event_id,
            ),
            params=params,
        )

    async def get_scheduled_events(self, guild_id: Snowflake, with_user_count: bool) -> List[dict]:
        """
        Gets all guild scheduled events in a guild.

        :param guild_id: Guild ID snowflake.
        :param with_user_count: A boolean to include number of users subscribed to the associated event, if given.
        :return A List of a dictionary containing the guild scheduled event objects on success.
        """
        guild_id = int(guild_id)
        params = {}
        if with_user_count:
            params["with_user_count"] = with_user_count

        return await self._req.request(
            Route("GET", "/guilds/{guild_id}/scheduled-events", guild_id=guild_id), params=params
        )

    async def modify_scheduled_event(
        self, guild_id: Snowflake, guild_scheduled_event_id: Snowflake, data: dict
    ) -> dict:
        """
        Modifies a scheduled event.

        :param guild_id: Guild ID snowflake.
        :param guild_scheduled_event_id: Guild Scheduled Event ID snowflake.
        :param data: The dictionary containing the parameters and values to edit the associated event.
        :return A dictionary containing the updated guild scheduled event object on success.
        """
        guild_id, event_id = int(guild_id), int(guild_scheduled_event_id)
        valid_keys = (
            "channel_id",
            "name",
            "privacy_level",
            "scheduled_start_time",
            "scheduled_end_time",
            "entity_metadata",
            "description",
            "entity_type",
        )
        payload = {k: v for k, v in data.items() if k in valid_keys}
        return await self._req.request(
            Route(
                "PATCH",
                "/guilds/{guild_id}/scheduled-events/{event_id}",
                guild_id=guild_id,
                event_id=event_id,
            ),
            json=payload,
        )

    async def delete_scheduled_event(
        self, guild_id: Snowflake, guild_scheduled_event_id: Snowflake
    ) -> None:
        """
        Deletes a guild scheduled event.

        :param guild_id: Guild ID snowflake.
        :param guild_scheduled_event_id: Guild Scheduled Event ID snowflake.
        :return Nothing on success.
        """
        guild_id, event_id = int(guild_id), int(guild_scheduled_event_id)

        return await self._req.request(
            Route(
                "DELETE",
                "/guilds/{guild_id}/scheduled-events/{event_id}",
                guild_id=guild_id,
                event_id=event_id,
            )
        )

    async def get_scheduled_event_users(
        self,
        guild_id: Snowflake,
        guild_scheduled_event_id: Snowflake,
        limit: int = 100,
        with_member: bool = False,
        before: Snowflake = None,
        after: Snowflake = None,
    ) -> dict:
        """
        Get the registered users of a scheduled event.

        :param guild_id: Guild ID snowflake.
        :param guild_scheduled_event_id: Guild Scheduled Event snowflake.
        :param limit: Limit of how many users to pull from the event. Defaults to 100.
        :param with_member: Include guild member data if it exists. Defaults to False.
        :param before: Considers only users before given user ID snowflake. Defaults to None.
        :param after: Considers only users after given user ID snowflake. Defaults to None.
        :return: Returns a list of guild scheduled event user objects on success.
        """
        guild_id, event_id = int(guild_id), int(guild_scheduled_event_id)
        params = {
            "limit": limit,
            "with_member": with_member,
        }
        if before:
            params["before"] = int(before)
        if after:
            params["after"] = int(after)

        return await self._req.request(
            Route(
                "GET",
                "/guilds/{guild_id}/scheduled-events/{event_id}/users",
                guild_id=guild_id,
                event_id=event_id,
            ),
            params=params,
        )
