from asyncio import AbstractEventLoop
from typing import Any, Dict, Optional
from aiohttp import ClientSession
from aiohttp import __version__ as http_version
from .limiter import Limiter
from .route import Route

class _Request:

    token: str
    _loop: AbstractEventLoop
    ratelimits: Dict[str, Limiter]
    buckets: Dict[str, str]
    _headers: dict
    _session: ClientSession
    _global_lock: Limiter

    def __init__(self, token: str) -> None: ...
    def _check_session(self) -> None: ...
    async def _check_lock(self) -> None: ...
    async def request(self, route: Route, **kwargs) -> Optional[Any]: ...
    async def close(self) -> None: ...
