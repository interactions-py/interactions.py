from asyncio import AbstractEventLoop
from threading import Event, Thread
from typing import Any, List, Optional, Union

from .dispatch import Listener
from .http import HTTPClient
from .models.gw import Presence
from .models.intents import Intents

class Heartbeat(Thread):
    ws: Any
    interval: Union[int, float]
    event: Event
    def __init__(self, ws: Any, interval: int) -> None: ...
    def run(self) -> None: ...
    def stop(self) -> None: ...

class WebSocket:
    intents: Intents
    loop: AbstractEventLoop
    dispatch: Listener
    session: Any
    session_id: Optional[int]
    sequence: Optional[int]
    keep_alive: Optional[Heartbeat]
    closed: bool
    http: Optional[HTTPClient]
    options: dict
    def __init__(
        self,
        intents: Intents,
        session_id: Optional[int] = None,
        sequence: Optional[int] = None,
    ) -> None: ...
    async def recv(self) -> Optional[Any]: ...
    async def connect(self, token: str) -> None: ...
    async def handle_connection(self, stream: dict, shard: Optional[List[int]] = None) -> None: ...
    def handle_dispatch(self, event: str, data: dict) -> None: ...
    def contextualize(self, data: dict) -> object: ...
    async def send(self, data: Union[str, dict]) -> None: ...
    async def identify(
        self, shard: Optional[List[int]] = None, presence: Optional[Presence] = None
    ) -> None: ...
    async def resume(self) -> None: ...
    async def heartbeat(self) -> None: ...
