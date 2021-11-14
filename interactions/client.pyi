from asyncio import AbstractEventLoop
from typing import Any, Callable, Coroutine, Dict, List, Optional, Union

from .api.cache import Cache
from .api.gateway import WebSocket
from .api.http import HTTPClient
from .api.models.guild import Guild
from .api.models.intents import Intents
from .api.models.team import Application
from .enums import ApplicationCommandType
from .models.command import Option

cache: Cache

class Client:
    loop: AbstractEventLoop
    intents: Optional[Union[Intents, List[Intents]]]
    http: HTTPClient
    websocket: WebSocket
    me: Optional[Application]
    token: str
    def __init__(
        self, token: str, intents: Optional[Union[Intents, List[Intents]]] = Intents.DEFAULT
    ) -> None: ...
    async def login(self, token: str) -> None: ...
    def start(self) -> None: ...
    def synchronize_commands(self) -> None: ...
    def event(self, coro: Coroutine, name: Optional[str] = None) -> Callable[..., Any]: ...
    def command(
        self,
        *,
        type: Optional[Union[str, int, ApplicationCommandType]] = ApplicationCommandType.CHAT_INPUT,
        name: Optional[str] = None,
        description: Optional[str] = None,
        scope: Optional[Union[int, Guild, List[int], List[Guild]]] = None,
        options: Optional[List[Option]] = None,
        default_permission: Optional[bool] = None
        # permissions: Optional[List[Permission]] = None
    ) -> Callable[..., Any]: ...
    async def raw_socket_create(self, data: Dict[Any, Any]) -> dict: ...
    async def raw_guild_create(self, guild) -> None: ...
