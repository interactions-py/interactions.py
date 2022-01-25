from asyncio import AbstractEventLoop
from threading import Event, Thread
from typing import Any, Dict, List, Optional, Union, List, Tuple

from aiohttp import ClientWebSocketResponse
from .models.team import Application
from .models.guild import UnavailableGuild

from .models.user import User

from ..models.misc import MISSING

from .dispatch import Listener
from .http import HTTPClient
from .models.gw import Presence
from .models.flags import Intents

class WebSocketClient:
    _loop: AbstractEventLoop
    _dispatch: Listener
    _http: HTTPClient
    _client: Optional[ClientWebSocketResponse]
    _closed: bool
    _options: Dict[str, Union[int, bool]]
    _intents: Intents
    __heartbeater: Event
    session_id: Optional[int]
    sequence: Optional[str]
    ready: Optional[Dict[str, Union[int, User, UnavailableGuild, str, List[int], Application]]]
    def __init__(
        self,
        intents: Intents,
        session_id: Optional[int] = MISSING,
        sequence: Optional[int] = MISSING,
    ) -> None: ...
    async def _establish_connection(self) -> None: ...
    @property
    async def _received_packet_stream(self) -> Optional[Dict[str, Any]]: ...
    async def _send_packet(self, data: Dict[str, Any]) -> None: ...
    async def __identify_packet(
        self, shard: Optional[List[int]] = MISSING, presence: Optional[Presence] = MISSING
    ) -> None: ...
    @property
    async def __resume_packet(self) -> None: ...
    @property
    async def __heartbeat_packet(self) -> None: ...

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
    async def connect(
        self, token: str, shard: Optional[List[int]] = None, presence: Optional[Presence] = None
    ) -> None: ...
    async def handle_connection(
        self, stream: dict, shard: Optional[List[int]] = None, presence: Optional[Presence] = None
    ) -> None: ...
    def handle_dispatch(self, event: str, data: dict) -> None: ...
    def contextualize(self, data: dict) -> object: ...
    async def send(self, data: Union[str, dict]) -> None: ...
    async def identify(
        self, shard: Optional[List[int]] = None, presence: Optional[Presence] = None
    ) -> None: ...
    async def resume(self) -> None: ...
    async def heartbeat(self) -> None: ...
    def check_sub_auto(self, option) -> tuple: ...
    def check_sub_command(self, option) -> dict: ...
