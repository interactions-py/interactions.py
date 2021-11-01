from asyncio import AbstractEventLoop
from logging import Logger
from typing import Coroutine, Optional

log: Logger

class Listener:
    loop: AbstractEventLoop
    events: dict
    def __init__(self) -> None: ...
    def dispatch(self, name: str, *args, **kwargs) -> None: ...
    def register(self, coro: Coroutine, name: Optional[str] = None) -> None: ...
