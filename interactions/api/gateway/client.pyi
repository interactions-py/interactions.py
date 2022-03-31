from asyncio import (
    AbstractEventLoop,
    Event,
    Task,
)
from logging import Logger
from typing import Any, Dict, List, Optional, Tuple, Union, Iterable

from aiohttp import ClientWebSocketResponse

from .heartbeat import _Heartbeat
from ...client.models import Option
from ...api.models.misc import MISSING
from ...api.models.presence import ClientPresence
from ..dispatch import Listener
from ..http.client import HTTPClient
from ..models.flags import Intents

log: Logger
__all__: Iterable[str]

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
    session_id: Optional[str]
    sequence: Optional[int]
    _last_send: float
    _last_ack: float
    latency: float
    ready: Event
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
        self,
        shard: Optional[List[Tuple[int]]] = MISSING,
        presence: Optional[ClientPresence] = MISSING,
    ) -> None: ...
    async def _handle_connection(
        self,
        stream: Dict[str, Any],
        shard: Optional[List[Tuple[int]]] = MISSING,
        presence: Optional[ClientPresence] = MISSING,
    ) -> None: ...
    async def wait_until_ready(self) -> None: ...
    def _dispatch_event(self, event: str, data: dict) -> None: ...
    def __contextualize(self, data: dict) -> object: ...
    def __sub_command_context(
        self, data: Union[dict, Option], _context: Optional[object] = MISSING
    ) -> Union[Tuple[str], dict]: ...
    def __option_type_context(self, context: object, type: int) -> dict: ...
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
    async def restart(self): ...
    async def _update_presence(self, presence: ClientPresence) -> None: ...
