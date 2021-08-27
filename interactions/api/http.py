# Normal libraries
from asyncio import AbstractEventLoop, Lock, get_event_loop
from datetime import datetime
from logging import DEBUG, Logger, basicConfig, getLogger
from platform import python_version as __py_version__
from typing import Any, Dict, Optional, Union

from aiohttp import ClientResponse, ClientSession, FormData
from aiohttp import __version__ as aio_version
from orjson import loads

# 3rd-party libraries
from ..base import Data, Route, __repo_url__, __version__

basicConfig(level=DEBUG)
log: Logger = getLogger(Data.LOGGER)


class Request:
    """
    The HTTP class for the internal API.

    :ivar loop: The current asynchronous coroutine loop.
    :ivar session: The current established client session.
    :ivar token: The token used for authentication.
    :ivar user_agent: The HTTP User Agent sent with bot authentication.
    """

    __slots__ = ("loop", "session", "token", "user_agent")
    loop: Optional[AbstractEventLoop]
    session: ClientSession
    token: Optional[str]
    user_agent: str

    def __init__(self, loop: Optional[AbstractEventLoop] = None) -> None:
        """
        An object representing how HTTP requests are made to the Discord API.

        :param loop: The loop to set a coroutine to. Defaults to ``None``.
        :type loop: typing.Optional[asyncio.AbstractEventLoop]
        :return: None
        """
        self.loop = get_event_loop() if loop is None else loop
        self.token = None
        self.user_agent = (
            f"{__repo_url__} {__version__} Python/{__py_version__()} aiohttp/{aio_version}"
        )

    async def request(
        self, method: str, route: str, data: Optional[Union[list, dict, FormData]] = None, **kwargs
    ) -> Any:
        r"""
        Makes an HTTP request with the Discord API.

        :param method: The request method to use.
        :type method: str
        :param route: The HTTP URL route you want to take. This extends off of :attr:`interactions.base.Route.API`.
        :type route: str
        :param data: The information you want to send as JSON.
        :type data: typing.Optional[typing.Union[list, dict, aiohttp.FormData]]
        :param \**kwargs: Keyword-arguments to pass as additional information.
        :return: typing.Any
        """
        headers: Dict[str, str] = {"User-Agent": self.user_agent}

        if self.token is not None:
            headers.update({"Authorization": f"Bot {self.token}"})
        if isinstance(data, (list, dict)):
            kwargs.update({"Content-Type": "application/json", "json": data})
        elif isinstance(data, FormData):
            kwargs.update({"data": data})

        lock: Lock = Lock()
        response: Optional[ClientResponse] = None
        result: Any = None

        await lock.acquire()
        try:
            async with self.session.request(method, Route.API + route, **kwargs) as response:
                result = await response.text(encoding="utf-8")

                if response.headers.get("Content-Type") == "application/json":
                    result = loads(result)

                ratelimit: Dict[str] = {
                    "remaining": response.headers.get("X-Ratelimit-Remaining"),
                    "bucket": response.headers.get("X-Ratelimit-Bucket"),
                    "delta": float(response.headers.get("X-Ratelimit-Reset-After", 0)),
                    "time": datetime.utcfromtimestamp(
                        float(response.headers.get("X-Ratelimit-Reset", 0))
                    ),
                }

                if ratelimit == "0" and response.status != 429:
                    log.debug("We've encountered a ratelimit from a HTTP request.")
                    return

                if 300 > response.status >= 200:
                    lock.release()
                    return result

                if response.status in (500, 502, 504):
                    log.debug("We've hit some difficulties in a HTTP request.")
                    return
        except Exception as exc:  # noqa
            lock.release()

    async def close(self) -> None:
        """Closes the client session established."""
        if self.session:
            await self.session.close()

    async def logout(self) -> None:
        """
        Sends an HTTP request to log out of the current session.

        This method relies on :meth:`interactions.api.http.Request.request`.
        """
        await self.request("POST", "/auth/logout")
