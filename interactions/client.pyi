from asyncio import AbstractEventLoop
from typing import Any, Callable, Coroutine, Dict, List, Optional, Union

from interactions.api.models.gw import Presence

from .api.cache import Cache
from .api.gateway import WebSocket
from .api.http import HTTPClient
from .api.models.guild import Guild
from .api.models.flags import Intents
from .api.models.team import Application
from .enums import ApplicationCommandType
from .models.command import ApplicationCommand, Option
from .models.component import Button, Modal, SelectMenu

_token: str = ""  # noqa
_cache: Optional[Cache] = None

class Client:
    loop: AbstractEventLoop
    intents: Optional[Union[Intents, List[Intents]]]
    http: HTTPClient
    websocket: WebSocket
    me: Optional[Application]
    token: str
    automate_sync: Optional[bool]
    shard: Optional[List[int]]
    presence: Optional[Presence]
    extensions: Optional[Any]
    def __init__(
        self,
        token: str,
        intents: Optional[Union[Intents, List[Intents]]] = Intents.DEFAULT,
        disable_sync: Optional[bool] = None,
        log_level: Optional[int] = None,
        shard: Optional[List[int]] = None,
        presence: Optional[Presence] = None,
    ) -> None: ...
    async def login(self, token: str) -> None: ...
    def start(self) -> None: ...
    async def ready(self) -> None: ...
    async def synchronize(self, payload: Optional[ApplicationCommand] = None) -> None: ...
    def event(self, coro: Coroutine, name: Optional[str] = None) -> Callable[..., Any]: ...
    def command(
        self,
        *,
        type: Optional[Union[str, int, ApplicationCommandType]] = ApplicationCommandType.CHAT_INPUT,
        name: Optional[str] = None,
        description: Optional[str] = None,
        scope: Optional[Union[int, Guild, List[int], List[Guild]]] = None,
        options: Optional[List[Option]] = None,
        default_permission: Optional[bool] = None,
    ) -> Callable[..., Any]: ...
    def component(self, component: Union[Button, SelectMenu]) -> Callable[..., Any]: ...
    def autocomplete(self, name: str) -> Callable[..., Any]: ...
    def modal(self, modal: Modal) -> Callable[..., Any]: ...
    def load(self, name: str, package: Optional[str] = None) -> None: ...
    def remove(self, name: str, package: Optional[str] = None) -> None: ...
    def reload(self, name: str, package: Optional[str] = None) -> None: ...
    async def raw_socket_create(self, data: Dict[Any, Any]) -> dict: ...
    async def raw_channel_create(self, message) -> dict: ...
    async def raw_message_create(self, message) -> dict: ...
    async def raw_guild_create(self, guild) -> dict: ...
    def add_extension(self, extension: "Extension"): ...

class Extension:
    client: Client
    _commands: dict
    _listeners: dict
    _components: dict
    def __new__(cls, client: Client, *args, **kwargs) -> Extension: ...
    def teardown(self) -> None: ...

def extension_command(
    *,
    type: Optional[Union[int, ApplicationCommandType]] = ApplicationCommandType.CHAT_INPUT,
    name: Optional[str] = None,
    description: Optional[str] = None,
    scope: Optional[Union[int, Guild, List[int], List[Guild]]] = None,
    options: Optional[Union[Dict[str, Any], List[Dict[str, Any]], Option, List[Option]]] = None,
    default_permission: Optional[bool] = None,
): ...
def extension_listener(name=None) -> Callable[..., Any]: ...
def extension_component(component: Union[Button, SelectMenu]) -> Callable[..., Any]: ...
