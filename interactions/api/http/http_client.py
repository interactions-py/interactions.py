"""This file handles the interaction with discords http endpoints."""
import asyncio
import inspect
import os
import time
from logging import Logger
from typing import Any, cast, Callable
from urllib.parse import quote as _uriquote
from weakref import WeakValueDictionary

import aiohttp
import discord_typings
from aiohttp import BaseConnector, ClientSession, ClientWebSocketResponse, FormData, BasicAuth
from multidict import CIMultiDictProxy

import interactions.client.const as constants
from interactions import models
from interactions.api.http.http_requests import (
    BotRequests,
    ChannelRequests,
    EmojiRequests,
    GuildRequests,
    InteractionRequests,
    MemberRequests,
    MessageRequests,
    ReactionRequests,
    StickerRequests,
    ThreadRequests,
    UserRequests,
    WebhookRequests,
    ScheduledEventsRequests,
)
from interactions.client.const import (
    MISSING,
    __py_version__,
    __repo_url__,
    __version__,
    __api_version__,
)
from interactions.client.errors import (
    DiscordError,
    Forbidden,
    GatewayNotFound,
    HTTPException,
    NotFound,
    LoginError,
)
from interactions.client.mixins.serialization import DictSerializationMixin
from interactions.client.utils.input_utils import response_decode, FastJson
from interactions.client.utils.serializer import dict_filter, get_file_mimetype
from interactions.models.discord.file import UPLOADABLE_TYPE
from .route import Route

__all__ = ("HTTPClient",)


class GlobalLock:
    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self.max_requests = 45
        self._calls = self.max_requests
        self._reset_time = 0

    @property
    def calls_remaining(self) -> int:
        """Returns the amount of calls remaining."""
        return self.max_requests - self._calls

    def reset_calls(self) -> None:
        """Resets the calls to the max amount."""
        self._calls = self.max_requests
        self._reset_time = time.perf_counter() + 1

    def set_reset_time(self, delta: float) -> None:
        """
        Sets the reset time to the current time + delta.

        To be called if a 429 is received.

        Args:
            delta: The time to wait before resetting the calls.
        """
        self._reset_time = time.perf_counter() + delta
        self._calls = 0

    async def wait(self) -> None:
        """Throttles calls to prevent hitting the global rate limit."""
        async with self._lock:
            if self._reset_time <= time.perf_counter():
                self.reset_calls()
            elif self._calls <= 0:
                await asyncio.sleep(self._reset_time - time.perf_counter())
                self.reset_calls()
        self._calls -= 1


class BucketLock:
    """Manages the rate limit for each bucket."""

    DEFAULT_LIMIT = 1
    DEFAULT_REMAINING = 1
    DEFAULT_DELTA = 0.0

    def __init__(self, header: CIMultiDictProxy | None = None) -> None:
        self._semaphore: asyncio.Semaphore | None = None
        if header is None:
            self.bucket_hash: str | None = None
            self.limit: int = self.DEFAULT_LIMIT
            self.remaining: int = self.DEFAULT_REMAINING
            self.delta: float = self.DEFAULT_DELTA
        else:
            self.ingest_ratelimit_header(header)

        self.logger = constants.get_logger()

        self._lock: asyncio.Lock = asyncio.Lock()

    def __repr__(self) -> str:
        return f"<BucketLock: {self.bucket_hash or 'Generic'}, limit: {self.limit}, remaining: {self.remaining}, delta: {self.delta}>"

    @property
    def locked(self) -> bool:
        """Returns whether the bucket is locked."""
        if self._lock.locked():
            return True
        return self._semaphore is not None and self._semaphore.locked()

    def ingest_ratelimit_header(self, header: CIMultiDictProxy) -> None:
        """
        Ingests the rate limit header.

        Args:
            header: The header to ingest, containing rate limit information.

        Updates the bucket_hash, limit, remaining, and delta attributes with the information from the header.
        """
        self.bucket_hash = header.get("x-ratelimit-bucket")
        self.limit = int(header.get("x-ratelimit-limit", self.DEFAULT_LIMIT))
        self.remaining = int(header.get("x-ratelimit-remaining", self.DEFAULT_REMAINING))
        self.delta = float(header.get("x-ratelimit-reset-after", self.DEFAULT_DELTA))

        if self._semaphore is None or self._semaphore._value != self.limit:
            self._semaphore = asyncio.Semaphore(self.limit)

    async def acquire(self) -> None:
        """Acquires the semaphore."""
        if self._semaphore is None:
            return

        if self._lock.locked():
            self.logger.debug(f"Waiting for bucket {self.bucket_hash} to unlock.")
            async with self._lock:
                pass

        await self._semaphore.acquire()

    def release(self) -> None:
        """
        Releases the semaphore.

        Note: If the bucket has been locked with lock_for_duration, this will not release the lock.
        """
        if self._semaphore is None:
            return
        self._semaphore.release()

    async def lock_for_duration(self, duration: float, block: bool = False) -> None:
        """
        Locks the bucket for a given duration.

        Args:
            duration: The duration to lock the bucket for.
            block: Whether to block until the bucket is unlocked.

        Raises:
            RuntimeError: If the bucket is already locked.
        """
        if self._lock.locked():
            raise RuntimeError("Attempted to lock a bucket that is already locked.")

        async def _release() -> None:
            await asyncio.sleep(duration)
            self._lock.release()

        if block:
            await self._lock.acquire()
            await _release()
        else:
            await self._lock.acquire()
            _ = asyncio.create_task(_release())

    async def __aenter__(self) -> None:
        await self.acquire()

    async def __aexit__(self, *args) -> None:
        self.release()


class HTTPClient(
    BotRequests,
    ChannelRequests,
    EmojiRequests,
    GuildRequests,
    InteractionRequests,
    MemberRequests,
    MessageRequests,
    ReactionRequests,
    StickerRequests,
    ThreadRequests,
    UserRequests,
    WebhookRequests,
    ScheduledEventsRequests,
):
    """A http client for sending requests to the Discord API."""

    def __init__(
        self,
        connector: BaseConnector | None = None,
        logger: Logger = MISSING,
        show_ratelimit_tracebacks: bool = False,
        proxy: tuple[str | None, BasicAuth | None] | None = None,
    ) -> None:
        self.connector: BaseConnector | None = connector
        self.__session: ClientSession | None = None
        self.token: str | None = None
        self.global_lock: GlobalLock = GlobalLock()
        self._max_attempts: int = 3

        self.ratelimit_locks: WeakValueDictionary[str, BucketLock] = WeakValueDictionary()
        self.show_ratelimit_traceback: bool = show_ratelimit_tracebacks
        self._endpoints = {}

        self.user_agent: str = (
            f"DiscordBot ({__repo_url__} {__version__} Python/{__py_version__}) aiohttp/{aiohttp.__version__}"
        )
        self.proxy: tuple[str | None, BasicAuth | None] | None = proxy
        self.__proxy_validated: bool = False

        if logger is MISSING:
            logger = constants.get_logger()
        self.logger = logger

    def get_ratelimit(self, route: Route) -> BucketLock:
        """
        Get a route's rate limit bucket.

        Args:
            route: The route to fetch the ratelimit bucket for

        Returns:
            The BucketLock object for this route
        """
        if bucket_hash := self._endpoints.get(route.rl_bucket):
            if lock := self.ratelimit_locks.get(bucket_hash):
                # if we have an active lock on this route, it'll still be in the cache
                # return that lock
                return lock
        # if no cached lock exists, return a new lock
        return BucketLock()

    def ingest_ratelimit(self, route: Route, header: CIMultiDictProxy, bucket_lock: BucketLock) -> None:
        """
        Ingests a ratelimit header from discord to determine ratelimit.

        Args:
            route: The route we're ingesting ratelimit for
            header: The rate limit header in question
            bucket_lock: The rate limit bucket for this route
        """
        bucket_lock.ingest_ratelimit_header(header)

        if bucket_lock.bucket_hash:
            # We only ever try and cache the bucket if the bucket hash has been set (ignores unlimited endpoints)
            self.logger.debug(f"Caching ingested rate limit data for: {bucket_lock.bucket_hash}")
            self._endpoints[route.rl_bucket] = bucket_lock.bucket_hash
            self.ratelimit_locks[bucket_lock.bucket_hash] = bucket_lock

    @staticmethod
    def _process_payload(
        payload: dict | list[dict] | None, files: UPLOADABLE_TYPE | list[UPLOADABLE_TYPE] | None
    ) -> dict | list[dict] | FormData | None:
        """
        Processes a payload into a format safe for discord. Converts the payload into FormData where required

        Args:
            payload: The payload of the request
            files: A list of any files to send

        Returns:
            Either a dictionary or multipart data form
        """
        if isinstance(payload, FormData):
            return payload
        if payload is None:
            return None

        if isinstance(payload, dict):
            payload = dict_filter(payload)

            for k, v in payload.items():
                if isinstance(v, DictSerializationMixin):
                    payload[k] = v.to_dict()
                if isinstance(v, (list, tuple, set)):
                    payload[k] = [i.to_dict() if isinstance(i, DictSerializationMixin) else i for i in v]

        else:
            payload = [dict_filter(x) if isinstance(x, dict) else x for x in payload]

        if not files:
            return payload

        if not isinstance(files, list):
            files = (files,)

        attachments = []

        form_data = FormData(quote_fields=False)

        for index, file in enumerate(files):
            file_data = models.open_file(file).read()

            if isinstance(file, models.File):
                form_data.add_field(
                    f"files[{index}]",
                    file_data,
                    filename=file.file_name,
                    content_type=file.content_type or get_file_mimetype(file_data),
                )
                attachments.append({"id": index, "description": file.description, "filename": file.file_name})
            else:
                form_data.add_field(
                    f"files[{index}]",
                    file_data,
                    filename=file.split(os.sep)[-1],
                    content_type=get_file_mimetype(file_data),
                )
        if attachments:
            payload["attachments"] = attachments

        form_data.add_field("payload_json", FastJson.dumps(payload))
        return form_data

    async def request(  # noqa: C901
        self,
        route: Route,
        payload: list | dict | None = None,
        files: list[UPLOADABLE_TYPE] | None = None,
        reason: str | None = None,
        params: dict | None = None,
        **kwargs: dict,
    ) -> str | dict[str, Any] | None:
        """
        Make a request to discord.

        Args:
            route: The route to take
            payload: The payload for this request
            files: The files to send with this request
            reason: Attach a reason to this request, used for audit logs
            params: Query string parameters

        """
        # Assemble headers
        kwargs["headers"] = {"User-Agent": self.user_agent}
        if self.token:
            kwargs["headers"]["Authorization"] = f"Bot {self.token}"
        if reason:
            kwargs["headers"]["X-Audit-Log-Reason"] = _uriquote(reason, safe="/ ")

        if isinstance(payload, (list, dict)) and not files:
            kwargs["headers"]["Content-Type"] = "application/json"
        if isinstance(params, dict):
            kwargs["params"] = dict_filter(params)

        lock = self.get_ratelimit(route)
        # this gets a BucketLock for this route.
        # If this endpoint has been used before, it will get an existing ratelimit for the respective buckethash
        # otherwise a brand-new bucket lock will be returned

        for attempt in range(self._max_attempts):
            async with lock:
                try:
                    if self.__session.closed:
                        await self.login(cast(str, self.token))

                    processed_data = self._process_payload(payload, files)
                    if isinstance(processed_data, FormData):
                        kwargs["data"] = processed_data  # pyright: ignore
                    else:
                        kwargs["json"] = processed_data  # pyright: ignore
                    await self.global_lock.wait()

                    if self.proxy:
                        kwargs["proxy"] = self.proxy[0]
                        kwargs["proxy_auth"] = self.proxy[1]

                    async with self.__session.request(route.method, route.url, **kwargs) as response:
                        result = await response_decode(response)
                        self.ingest_ratelimit(route, response.headers, lock)

                        if response.status == 429:
                            # ratelimit exceeded
                            result = cast(dict[str, str], result)
                            if result.get("global", False):
                                # global ratelimit is reached
                                # if we get a global, that's pretty bad, this would usually happen if the user is hitting the api from 2 clients sharing a token
                                self.log_ratelimit(
                                    self.logger.warning,
                                    f"Bot has exceeded global ratelimit, locking REST API for {result['retry_after']} seconds",
                                )
                                self.global_lock.set_reset_time(float(result["retry_after"]))
                            elif result.get("message") == "The resource is being rate limited.":
                                # resource ratelimit is reached
                                self.log_ratelimit(
                                    self.logger.warning,
                                    f"{route.resolved_endpoint} The resource is being rate limited! "
                                    f"Reset in {result.get('retry_after')} seconds",
                                )
                                # lock this resource and wait for unlock
                                await lock.lock_for_duration(float(result["retry_after"]), block=True)
                            else:
                                # endpoint ratelimit is reached
                                # 429's are unfortunately unavoidable, but we can attempt to avoid them
                                # so long as these are infrequent we're doing well
                                self.log_ratelimit(
                                    self.logger.warning,
                                    f"{route.resolved_endpoint} Has exceeded its ratelimit ({lock.limit})! Reset in {lock.delta} seconds",
                                )
                                await lock.lock_for_duration(lock.delta, block=True)
                            continue
                        if lock.remaining == 0:
                            # Last call available in the bucket, lock until reset
                            self.log_ratelimit(
                                self.logger.debug,
                                f"{route.resolved_endpoint} Has exhausted its ratelimit ({lock.limit})! Locking route for {lock.delta} seconds",
                            )
                            await lock.lock_for_duration(
                                lock.delta
                            )  # lock this route, but continue processing the current response

                        elif response.status in {500, 502, 504}:
                            # Server issues, retry
                            self.logger.warning(
                                f"{route.resolved_endpoint} Received {response.status}... retrying in {1 + attempt * 2} seconds"
                            )
                            await asyncio.sleep(1 + attempt * 2)
                            continue

                        if not 300 > response.status >= 200:
                            await self._raise_exception(response, route, result)

                        self.logger.debug(
                            f"{route.resolved_endpoint} Received {response.status} :: [{lock.remaining}/{lock.limit} calls remaining]"
                        )
                        return result
                except OSError as e:
                    if attempt < self._max_attempts - 1 and e.errno in (54, 10054):
                        await asyncio.sleep(1 + attempt * 2)
                        continue
                    raise

    async def _raise_exception(self, response, route, result) -> None:
        self.logger.error(f"{route.method}::{route.url}: {response.status}")

        if response.status == 403:
            raise Forbidden(response, response_data=result, route=route)
        if response.status == 404:
            raise NotFound(response, response_data=result, route=route)
        if response.status >= 500:
            raise DiscordError(response, response_data=result, route=route)
        raise HTTPException(response, response_data=result, route=route)

    def log_ratelimit(self, log_func: Callable, message: str) -> None:
        """
        Logs a ratelimit message, optionally with a traceback if show_ratelimit_traceback is True

        Args:
            log_func: The logging function to use
            message: The message to log
        """
        if self.show_ratelimit_traceback:
            if frame := next(
                (frame for frame in inspect.stack() if constants.LIB_PATH not in frame.filename),
                None,
            ):
                frame_info = inspect.getframeinfo(frame[0])
                filename = os.path.relpath(frame_info.filename, os.getcwd())

                traceback = (
                    f"{filename}:{frame_info.lineno} in {frame_info.function}:: {frame_info.code_context[0].strip()}"
                )
                message = f"{message} | Caused By: {traceback}"

        log_func(message)

    async def request_cdn(self, url, asset) -> bytes:  # pyright: ignore [reportGeneralTypeIssues]
        self.logger.debug(f"{asset} requests {url} from CDN")
        async with self.__session.get(url) as response:
            if response.status == 200:
                return await response.read()
            await self._raise_exception(response, asset, await response_decode(response))

    async def login(self, token: str) -> dict[str, Any]:
        """
        "Login" to the gateway, basically validates the token and grabs user data.

        Args:
            token: the token to use

        Returns:
            The currently logged in bot's data

        """
        self.__session = ClientSession(
            connector=self.connector or aiohttp.TCPConnector(limit=self.global_lock.max_requests),
            json_serialize=FastJson.dumps,
        )
        if not self.__proxy_validated and self.proxy:
            try:
                self.logger.info(f"Validating Proxy @ {self.proxy[0]}")
                async with self.__session.get(
                    "http://icanhazip.com/", proxy=self.proxy[0], proxy_auth=self.proxy[1]
                ) as response:
                    if response.status != 200:
                        raise RuntimeError("Proxy configuration is invalid")
                    self.logger.info(f"Proxy Connected @ {(await response.text()).strip()}")
                    self.__proxy_validated = True
            except Exception as e:
                raise RuntimeError("Proxy configuration is invalid") from e

        self.token = token
        try:
            result = await self.request(Route("GET", "/users/@me"))
            return cast(dict[str, Any], result)
        except HTTPException as e:
            if e.status == 401:
                raise LoginError("An improper token was passed") from e
            raise

    async def close(self) -> None:
        """Close the session."""
        if self.__session and not self.__session.closed:
            await self.__session.close()

    async def get_gateway(self) -> str:
        """
        Gets the gateway url.

        Returns:
            The gateway url

        """
        try:
            result = await self.request(Route("GET", "/gateway"))
            result = cast(dict[str, Any], result)
        except HTTPException as exc:
            raise GatewayNotFound from exc
        return "{0}?encoding={1}&v={2}&compress=zlib-stream".format(result["url"], "json", __api_version__)

    async def get_gateway_bot(self) -> discord_typings.GetGatewayBotData:
        try:
            result = await self.request(Route("GET", "/gateway/bot"))
        except HTTPException as exc:
            raise GatewayNotFound from exc
        return cast(discord_typings.GetGatewayBotData, result)

    async def websocket_connect(self, url: str) -> ClientWebSocketResponse:
        """
        Connect to the websocket.

        Args:
            url: the url to connect to

        """
        return await self.__session.ws_connect(
            url,
            timeout=30,
            max_msg_size=0,
            autoclose=False,
            headers={"User-Agent": self.user_agent},
            compress=0,
            proxy=self.proxy[0] if self.proxy else None,
            proxy_auth=self.proxy[1] if self.proxy else None,
        )
