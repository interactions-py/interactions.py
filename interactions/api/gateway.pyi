from asyncio import (
    AbstractEventLoop,
    Event,
    Task,
)
from logging import Logger
from typing import Any, Dict, List, Optional, Tuple

from aiohttp import ClientWebSocketResponse

from ..base import get_logger
from ..api.models.misc import MISSING
from ..api.models.presence import ClientPresence
from .dispatch import Listener
from .http import HTTPClient
from .models.flags import Intents

log: Logger = get_logger("gateway")

__all__ = ("_Heartbeat", "WebSocketClient")

class _Heartbeat:
    event: Event
    delay: float
    def __init__(self, loop: AbstractEventLoop) -> None: ...

class WebSocketClient:
    _loop: AbstractEventLoop
    _dispatch: Listener
    _http: HTTPClient
    _client: Optional[ClientWebSocketResponse]
    _closed: bool
    _options: dict
    _intents: Intents
    _ready: dict
    __heartbeater: _Heartbeat
    __shard: Optional[List[Tuple[int]]]
    __presence: Optional[ClientPresence]
    __task: Optional[Task]
    session_id: int
    sequence: str
    def __init__(
        self,
        token: str,
        intents: Intents,
        session_id: Optional[int] = MISSING,
        sequence: Optional[int] = MISSING,
    ) -> None: ...
    async def _manage_heartbeat(self) -> None: ...
    async def __restart(self): ...
    async def _establish_connection(
        self, shard: Optional[List[Tuple[int]]] = MISSING, presence: Optional[ClientPresence] = MISSING
    ) -> None: ...
    async def _handle_connection(
        self,
        stream: Dict[str, Any],
        shard: Optional[List[Tuple[int]]] = MISSING,
        presence: Optional[ClientPresence] = MISSING,
    ) -> None: ...
    @property
    async def __receive_packet_stream(self) -> Optional[Dict[str, Any]]: ...
    async def _send_packet(self, data: Dict[str, Any]) -> None: ...
    async def __identify(
        self, shard: Optional[List[Tuple[int]]] = None, presence: Optional[ClientPresence] = None
    ) -> None: ...
    async def __resume(self) -> None: ...
    async def __heartbeat(self) -> None: ...
    @property
    def shard(self) -> None: ...
    @property
    def presence(self) -> None: ...
