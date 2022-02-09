from asyncio import (
    AbstractEventLoop,
    Event,
    Task,
)
from logging import Logger
from typing import Any, Dict, List, Optional, Tuple

from aiohttp import ClientWebSocketResponse

from ..api.models.gw import Presence
from ..base import get_logger
from ..models.misc import MISSING
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
    _client: ClientWebSocketResponse
    _closed: bool
    _options: dict
    _intents: Intents
    _ready: dict
    __heartbeater: _Heartbeat
    __shard: Optional[List[Tuple[int]]]
    __presence: Optional[Presence]
    __task: Task
    session_id: int
    sequence: str
    def __init__(
        self,
        token: str,
        intents: Intents,
        session_id: Optional[int] = MISSING,
        sequence: Optional[int] = MISSING,
    ) -> None: ...
    @property
    async def __heartbeat_manager(self) -> None: ...
    async def _establish_connection(
        self, shard: Optional[List[Tuple[int]]] = MISSING, presence: Optional[Presence] = MISSING
    ) -> None: ...
    async def __close(self): ...
    async def _handle_connection(
        self,
        stream: Dict[str, Any],
        shard: Optional[List[Tuple[int]]] = MISSING,
        presence: Optional[Presence] = MISSING,
    ) -> None: ...
    @property
    async def __receive_packet_stream(self) -> Optional[Dict[str, Any]]: ...
    async def _send_packet(self, data: Dict[str, Any]) -> None: ...
    async def __identify_packet(
        self, shard: Optional[List[Tuple[int]]] = None, presence: Optional[Presence] = None
    ) -> None: ...
    @property
    async def __resume_packet(self) -> None: ...
    @property
    async def __heartbeat_packet(self) -> None: ...
    @property
    def shard(self) -> None: ...
    @property
    def presence(self) -> None: ...
