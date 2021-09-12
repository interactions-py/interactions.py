from asyncio import AbstractEventLoop, get_event_loop
from typing import Any, Callable, Coroutine, Optional

class Listener:
    __slots__ = ("loop", "events")
    loop: AbstractEventLoop
    events: dict
    def __init__(self) -> None: ...
    def dispatch(self, name: str, *args, **kwargs) -> None: ...
    def register(self, coro: Coroutine, name: Optional[str] = None) -> Callable[..., Any]: ...
