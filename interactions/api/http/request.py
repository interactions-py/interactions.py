import asyncio
import traceback
from asyncio import AbstractEventLoop, Lock, get_event_loop, get_running_loop, new_event_loop
from contextlib import suppress
from json import dumps
from logging import Logger
from sys import version_info
from typing import Any, Dict, Optional
from urllib.parse import quote

from aiohttp import ClientSession
from aiohttp import __version__ as http_version

from ...api.error import LibraryException
from ...base import __version__, get_logger
from .limiter import Limiter
from .route import Route

__all__ = ("_Request",)
log: Logger = get_logger("http")


class _Request:
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
        self._session = ClientSession()
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
        :type \**kwargs?: dict
        :return: The contents of the request if any.
        :rtype: Optional[Any]
        """
        # sourcery skip: low-code-quality

        kwargs["headers"] = {**self._headers, **kwargs.get("headers", {})}

        if kwargs.get("json"):
            kwargs["headers"]["Content-Type"] = "application/json"

        if reason := kwargs.pop("reason", None):
            kwargs["headers"]["X-Audit-Log-Reason"] = quote(reason, safe="/ ")

        # Huge credit and thanks to LordOfPolls for the lock/retry logic.

        bucket = route.get_bucket(
            self.buckets.get(route.endpoint)
        )  # string returning path OR prioritised hash bucket metadata.

        # The idea is that its regulated by the priority of Discord's bucket header and not just self-computation.
        # This implementation is based on JDA's bucket implementation, which we heavily use in favour of allowing routes
        # and other resources to be exhausted first on a separate lock call before hitting global limits.

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
                    if response.content_type == "application/json":
                        data = await response.json()
                        if isinstance(data, dict):
                            message: Optional[str] = data.get("message")
                            code: int = data.get("code", response.status)
                        else:
                            message, code = None, response.status
                    else:
                        data, message, code = None, None, response.status

                    reset_after: float = float(
                        response.headers.get(
                            "X-RateLimit-Reset-After", response.headers.get("Retry-After", "0.0")
                        )
                    )
                    remaining: str = response.headers.get("X-RateLimit-Remaining")
                    _bucket: str = response.headers.get("X-RateLimit-Bucket")
                    is_global: bool = response.headers.get("X-RateLimit-Global", False)

                    log.debug(f"{route.method}: {route.__api__ + route.path}: {kwargs}")

                    if _bucket is not None:
                        self.buckets[route.endpoint] = _bucket
                        # real-time replacement/update/add if needed.

                    if code in {429, 31001}:
                        hours = int(reset_after // 3600)
                        minutes = int((reset_after % 3600) // 60)
                        seconds = int(reset_after % 60)
                        log.warning(
                            "(429/31001) The Bot has encountered a rate-limit. Resuming future requests after "
                            f"{f'{hours} hours ' if hours else ''}"
                            f"{f'{minutes} minutes ' if minutes else ''}"
                            f"{f'{seconds} seconds ' if seconds else ''}"
                        )
                        if is_global:
                            self._global_lock.reset_after = reset_after
                            self._loop.call_later(
                                self._global_lock.reset_after, self._global_lock.lock.release
                            )
                        else:
                            _limiter.reset_after = reset_after
                            await asyncio.sleep(_limiter.reset_after)
                            continue

                    if remaining is not None and int(remaining) == 0:
                        log.debug(
                            f"The HTTP client has exhausted a per-route ratelimit. Locking route for {reset_after} seconds."
                        )
                        self._loop.call_later(reset_after, _limiter.release_lock)

                    if isinstance(data, dict) and (
                        data.get("errors") or (not (200 <= code <= 300) and message)
                    ):
                        log.debug(
                            f"RETURN {response.status}: {dumps(data, indent=4, sort_keys=True)}"
                        )
                        # This "redundant" debug line is for debug use and tracing back the error codes.

                        raise LibraryException(message=message, code=code, severity=40, data=data)
                    elif isinstance(data, dict) and code == 0 and message:
                        log.debug(
                            f"RETURN {response.status}: {dumps(data, indent=4, sort_keys=True)}"
                        )
                        # This "redundant" debug line is for debug use and tracing back the error codes.

                        raise LibraryException(
                            message=f"'{message}'. Make sure that your token is set properly.",
                            severity=50,
                        )

                    log.debug(f"RETURN {response.status}: {dumps(data, indent=4, sort_keys=True)}")

                    _limiter.release_lock()  # checks if its locked, then releases upon success.

                    return data

            # These account for general/specific exceptions. (Windows...)
            except OSError as e:
                if tries < 4 and e.errno in (54, 10054):
                    await asyncio.sleep(2 * tries + 1)
                    continue
                with suppress(RuntimeError):
                    _limiter.lock.release()
                raise

            # For generic exceptions we give a traceback for debug reasons.
            except Exception as e:
                with suppress(RuntimeError):
                    _limiter.lock.release()
                if isinstance(e, LibraryException):
                    raise
                log.error("".join(traceback.format_exception(type(e), e, e.__traceback__)))
                break

    async def close(self) -> None:
        """Closes the current session."""
        await self._session.close()
