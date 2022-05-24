from asyncio import AbstractEventLoop
from types import ModuleType
from typing import Any, Callable, Coroutine, Dict, List, Optional, Tuple, Union, overload, Type

from ..api import Cache
from ..api import Item as Build
from ..api.gateway.client import WebSocketClient
from ..api.http.client import HTTPClient
from ..api.models.flags import Intents, Permissions
from ..api.models.channel import Channel
from ..api.models.guild import Guild
from ..api.models.member import Member
from ..api.models.message import Message, Emoji, Sticker
from ..api.models.misc import MISSING, Image, Snowflake
from ..api.models.presence import ClientPresence
from ..api.models.role import Role
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
    __command_coroutines: List[Coroutine]
    __global_commands: Dict[str, Union[List[dict], bool]]
    __guild_commands: Dict[int, Dict[str, Union[List[dict], bool]]]
    __name_autocomplete: dict
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
    async def __register_name_autocomplete(self) -> None: ...
    @staticmethod
    async def __compare_sync(data: dict, pool: List[dict]) -> Tuple[bool, dict]: ...
    async def _ready(self) -> None: ...
    async def _login(self) -> None: ...
    async def wait_until_ready(self) -> None: ...
    async def __get_all_commands(self) -> None: ...
    async def __sync(self) -> None: ...
    def event(self, coro: Optional[Coroutine] = MISSING, *, name: Optional[str] = None) -> Callable[..., Any]: ...
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
        name_localizations: Optional[Dict[Union[str, Locale], str]] = MISSING,
        description_localizations: Optional[Dict[Union[str, Locale], str]]  = MISSING,
        default_member_permissions: Optional[Union[int, Permissions]] = MISSING,
        dm_permission: Optional[bool] = MISSING
    ) -> Callable[..., Any]: ...
    def message_command(
        self,
        *,
        name: str,
        scope: Optional[Union[int, Guild, List[int], List[Guild]]] = MISSING,
        name_localizations: Optional[Dict[Union[str, Locale], str]]  = MISSING,
        default_member_permissions: Optional[Union[int, Permissions]] = MISSING,
        dm_permission: Optional[bool] = MISSING
    ) -> Callable[..., Any]: ...
    def user_command(
        self,
        *,
        name: str,
        scope: Optional[Union[int, Guild, List[int], List[Guild]]] = MISSING,
        name_localizations: Optional[Dict[Union[str, Locale], str]]  = MISSING,
        default_member_permissions: Optional[Union[int, Permissions]] = MISSING,
        dm_permission: Optional[bool] = MISSING
    ) -> Callable[..., Any]: ...
    def component(self, component: Union[Button, SelectMenu]) -> Callable[..., Any]: ...
    def autocomplete(
        self, command: Union[ApplicationCommand, int, str, Snowflake], name: str
    ) -> Callable[..., Any]: ...
    def modal(self, modal: Union[Modal, str]) -> Callable[..., Any]: ...
    def load(
        self, name: str, package: Optional[str] = None, *args, **kwargs
    ) -> Optional["Extension"]: ...
    def remove(self, name: str, package: Optional[str] = None) -> None: ...
    def reload(
        self, name: str, package: Optional[str] = None, *args, **kwargs
    ) -> Optional["Extension"]: ...
    def get_extension(self, name: str) -> Union[ModuleType, "Extension"]: ...
    async def modify(
        self,
        username: Optional[str] = MISSING,
        avatar: Optional[Image] = MISSING,
    ) -> User: ...
    def _find_command(self, command: str) -> ApplicationCommand: ...
    @overload
    async def get(self, obj: Type[Channel], *, channel_id: int) -> Channel: ...
    @overload
    async def get(self, obj: Type[Emoji], *, guild_id: int, emoji_id: int) -> Emoji: ...
    @overload
    async def get(self, obj: Type[Guild], *, guild_id: int) -> Guild: ...
    @overload
    async def get(self, obj: Type[Member], *, guild_id: int, user_id: int) -> Member: ...
    @overload
    async def get(
        self,
        obj: Type[Message],
        *,
        channel_id: int,
        message_id: int,
    ) -> Message: ...
    @overload
    async def get(self, obj: Type[Role], *, guild_id: int, role_id: int) -> Role: ...
    @overload
    async def get(self, obj: Type[Sticker], *, sticker_id: int) -> Sticker: ...
    @overload
    async def get(self, obj: Type[User], *, user_id: int) -> User: ...
    async def __raw_channel_create(self, message) -> dict: ...
    async def __raw_message_create(self, message) -> dict: ...
    async def __raw_guild_create(self, guild) -> dict: ...

class Extension:
    client: Client
    _commands: dict
    _listeners: dict
    def __new__(cls, client: Client, *args, **kwargs) -> Extension: ...
    async def teardown(self) -> None: ...

def extension_command(
    *,
    type: Optional[Union[int, ApplicationCommandType]] = ApplicationCommandType.CHAT_INPUT,
    name: Optional[str] = None,
    description: Optional[str] = None,
    scope: Optional[Union[int, Guild, List[int], List[Guild]]] = None,
    options: Optional[Union[Dict[str, Any], List[Dict[str, Any]], Option, List[Option]]] = None,
    name_localizations: Optional[Dict[Union[str, Locale], str]] = None,
    description_localizations: Optional[Dict[Union[str, Locale], str]] = None,
    default_member_permissions: Optional[Union[int, Permissions]] = None,
    dm_permission: Optional[bool] = None
): ...
def extension_listener(func: Optional[Coroutine] = None, name: Optional[str] = None) -> Callable[..., Any]: ...
def extension_component(component: Union[Button, SelectMenu, str]) -> Callable[..., Any]: ...
def extension_autocomplete(command: Union[ApplicationCommand, int, str, Snowflake], name: str,) -> Callable[..., Any]: ...
def extension_modal(modal: Union[Modal, str]) -> Callable[..., Any]: ...
def extension_message_command(
    *,
    name: Optional[str] = None,
    scope: Optional[Union[int, Guild, List[int], List[Guild]]] = None,
    name_localizations: Optional[Dict[Union[str, Locale], Any]] = None,
    default_member_permissions: Optional[Union[int, Permissions]] = None,
    dm_permission: Optional[bool] = None,
) -> Callable[..., Any]: ...
def extension_user_command(
    *,
    name: Optional[str] = None,
    name_localizations: Optional[Dict[Union[str, Locale], Any]] = None,
    default_member_permissions: Optional[Union[int, Permissions]] = None,
    dm_permission: Optional[bool] = None,
) -> Callable[..., Any]: ...
