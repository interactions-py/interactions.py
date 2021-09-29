from asyncio import AbstractEventLoop
from threading import Event, Thread
from typing import Any, Optional, Union

from .dispatch import Listener
from .http import HTTPClient
from .models.intents import Intents

class Heartbeat(Thread):
    __slots__ = ("ws", "interval", "event")
    ws: Any
    interval: Union[int, float]
    event: Event
    def __init__(self, ws: Any, interval: int) -> None: ...
    def run(self) -> None: ...
    def stop(self) -> None: ...

class WebSocket:
    __slots__ = (
        "intents",
        "loop",
        "dispatch",
        "session",
        "session_id",
        "sequence",
        "keep_alive",
        "closed",
        "_http",
    )
    intents: Intents
    loop: AbstractEventLoop
    dispatch: Listener
    session: Any
    session_id: Optional[int]
    sequence: Optional[int]
    keep_alive: Optional[Heartbeat]
    closed: bool
    _http: Optional[HTTPClient]
    def __init__(
        self,
        intents: Intents,
        session_id: Optional[int] = None,
        sequence: Optional[int] = None,
    ) -> None: ...
    async def recv(self) -> Optional[Any]: ...
    async def connect(self, token: str) -> None: ...
    def handle(self, event: str, data: dict) -> None: ...
    async def send(self, data: Union[str, dict]) -> None: ...
    async def identify(self) -> None: ...
    async def resume(self) -> None: ...
    async def heartbeat(self) -> None: ...
