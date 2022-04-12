from asyncio import AbstractEventLoop
from types import ModuleType
from typing import Any, Callable, Coroutine, Dict, List, Optional, Tuple, Union

from ..api.cache import Cache
from ..api.gateway import WebSocketClient
from ..api.http.client import HTTPClient
from ..api.models.flags import Intents
from ..api.models.guild import Guild
from ..api.models.misc import MISSING, Snowflake, Image
from ..api.models.presence import ClientPresence
from ..api.models.team import Application
from ..api.models.user import User
from .enums import ApplicationCommandType, Locale
from .models.command import ApplicationCommand, Option
from .models.component import Button, Modal, SelectMenu

_token: str = ""  # noqa
_cache: Optional[Cache] = None

class Client:
    _loop: AbstractEventLoop
    _http: HTTPClient
    _websocket: WebSocketClient
    _intents: Intents
    _shard: Optional[List[Tuple[int]]]
    _presence: Optional[ClientPresence]
    _token: str
    _scopes: set[List[Union[int, Snowflake]]]
    _automate_sync: bool
    _extensions: Optional[Dict[str, Union[ModuleType, Extension]]]
    me: Optional[Application]
    def __init__(
        self,
        token: str,
        **kwargs,
    ) -> None: ...
    @property
    def guilds(self) -> List[Guild]: ...
    @property
    def latency(self) -> float: ...
    def start(self) -> None: ...
    def __register_events(self) -> None: ...
    async def __compare_sync(self, data: dict) -> None: ...
    async def __create_sync(self, data: dict) -> None: ...
    async def __bulk_update_sync(
        self, data: List[dict], delete: Optional[bool] = False
    ) -> None: ...
    async def _synchronize(self, payload: Optional[dict] = None) -> None: ...
    async def _ready(self) -> None: ...
    async def _login(self) -> None: ...
    async def wait_until_ready(self) -> None: ...
    def event(self, coro: Coroutine, name: Optional[str] = None) -> Callable[..., Any]: ...
    def change_presence(self, presence: ClientPresence) -> None: ...
    def __check_command(
        self,
        command: ApplicationCommand,
        coro: Coroutine,
        regex: str = r"^[a-z0-9_-]{1,32}$",
    )-> None: ...
    def command(
        self,
        *,
        type: Optional[Union[str, int, ApplicationCommandType]] = ApplicationCommandType.CHAT_INPUT,
        name: Optional[str] = MISSING,
        description: Optional[str] = MISSING,
        scope: Optional[Union[int, Guild, List[int], List[Guild]]] = MISSING,
        options: Optional[List[Option]] = MISSING,
        default_permission: Optional[bool] = MISSING,
        name_localizations: Optional[Dict[Union[str, Locale], str]] = MISSING,
        description_localizations: Optional[Dict[Union[str, Locale], str]]  = MISSING,
    ) -> Callable[..., Any]: ...
    def message_command(
        self,
        *,
        name: str,
        scope: Optional[Union[int, Guild, List[int], List[Guild]]] = MISSING,
        default_permission: Optional[bool] = MISSING,
        name_localizations: Optional[Dict[Union[str, Locale], str]]  = MISSING,
    ) -> Callable[..., Any]: ...
    def user_command(
        self,
        *,
        name: str,
        scope: Optional[Union[int, Guild, List[int], List[Guild]]] = MISSING,
        default_permission: Optional[bool] = MISSING,
        name_localizations: Optional[Dict[Union[str, Locale], str]]  = MISSING,
    ) -> Callable[..., Any]: ...
    def component(self, component: Union[Button, SelectMenu]) -> Callable[..., Any]: ...
    def autocomplete(
        self, name: str, command: Union[ApplicationCommand, int, str]
    ) -> Callable[..., Any]: ...
    def modal(self, modal: Union[Modal, str]) -> Callable[..., Any]: ...
    def load(
        self, name: str, package: Optional[str] = None, *args, **kwargs
    ) -> Optional["Extension"]: ...
    def remove(self, name: str, package: Optional[str] = None) -> None: ...
    def reload(
        self, name: str, package: Optional[str] = None, *args, **kwargs
    ) -> Optional["Extension"]: ...
    async def modify(
        self,
        username: Optional[str] = MISSING,
        avatar: Optional[Image] = MISSING,
    ) -> User: ...
    def get_extension(self, name: str) -> Union[ModuleType, "Extension"]: ...
    async def raw_socket_create(self, data: Dict[Any, Any]) -> dict: ...
    async def raw_channel_create(self, message) -> dict: ...
    async def raw_message_create(self, message) -> dict: ...
    async def raw_guild_create(self, guild) -> dict: ...
    @staticmethod
    def _find_command(commands: List[Dict], command: str) -> ApplicationCommand: ...

class Extension:
    client: Client
    _commands: dict
    _listeners: dict
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
def extension_component(component: Union[Button, SelectMenu, str]) -> Callable[..., Any]: ...
def extension_autocomplete(
    name: str, command: Union[ApplicationCommand, int]
) -> Callable[..., Any]: ...
def extension_modal(modal: Union[Modal, str]) -> Callable[..., Any]: ...
def extension_message_command(
    *,
    name: Optional[str] = None,
    scope: Optional[Union[int, Guild, List[int], List[Guild]]] = None,
    default_permission: Optional[bool] = None,
) -> Callable[..., Any]: ...
def extension_user_command(
    *,
    name: Optional[str] = None,
    scope: Optional[Union[int, Guild, List[int], List[Guild]]] = None,
    default_permission: Optional[bool] = None,
) -> Callable[..., Any]: ...
