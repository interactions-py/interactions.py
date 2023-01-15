from datetime import datetime
from typing import Iterable, List, Optional, Union, Set

from interactions.client.const import Absent
from interactions.client.mixins.send import SendMixin
from interactions.models.discord.activity import Activity
from interactions.models.discord.asset import Asset
from interactions.models.discord.channel import DM, TYPE_GUILD_CHANNEL
from interactions.models.discord.color import Color
from interactions.models.discord.enums import Permissions, PremiumTypes, Status, UserFlags
from interactions.models.discord.file import UPLOADABLE_TYPE
from interactions.models.discord.guild import Guild
from interactions.models.discord.role import Role
from interactions.models.discord.snowflake import Snowflake_Type
from interactions.models.discord.timestamp import Timestamp
from interactions.models.discord.voice_state import VoiceState
from .base import DiscordObject

class _SendDMMixin(SendMixin):
    id: Snowflake_Type

class BaseUser(DiscordObject, _SendDMMixin):
    username: str
    discriminator: int
    avatar: Asset
    @property
    def tag(self) -> str: ...
    @property
    def mention(self) -> str: ...
    @property
    def display_name(self) -> str: ...
    @property
    def display_avatar(self) -> Asset: ...
    async def fetch_dm(self) -> DM: ...
    def get_dm(self) -> Optional["DM"]: ...
    @property
    def mutual_guilds(self) -> List["Guild"]: ...

class User(BaseUser):
    bot: bool
    system: bool
    public_flags: UserFlags
    premium_type: PremiumTypes
    banner: Optional["Asset"]
    accent_color: Optional["Color"]
    activities: list[Activity]
    status: Absent[Status]
    @property
    def member_instances(self) -> List["Member"]: ...

class NaffUser(User):
    verified: bool
    mfa_enabled: bool
    email: Optional[str]
    locale: Optional[str]
    bio: Optional[str]
    flags: UserFlags
    _guild_ids: Set[Snowflake_Type]
    @property
    def guilds(self) -> List["Guild"]: ...
    async def edit(self, username: Absent[str] = ..., avatar: Absent[UPLOADABLE_TYPE] = ...) -> None: ...

class Member(User):  # for typehinting purposes, we can lie
    bot: bool
    nick: Optional[str]
    deaf: bool
    mute: bool
    joined_at: Timestamp
    premium_since: Optional["Timestamp"]
    pending: Optional[bool]
    guild_avatar: Asset
    communication_disabled_until: Optional[Timestamp]
    _guild_id: Snowflake_Type
    _role_ids: List[Snowflake_Type]
    def update_from_dict(self, data) -> None: ...
    @property
    def user(self) -> User: ...
    @property
    def nickname(self) -> str: ...
    @nickname.setter
    def nickname(self, nickname: str) -> None: ...
    @property
    def guild(self) -> Guild: ...
    @property
    def roles(self) -> List["Role"]: ...
    @property
    def top_role(self) -> Role: ...
    @property
    def display_name(self) -> str: ...
    @property
    def display_avatar(self) -> Asset: ...
    @property
    def premium(self) -> bool: ...
    @property
    def guild_permissions(self) -> Permissions: ...
    @property
    def voice(self) -> Optional["VoiceState"]: ...
    def has_permission(self, *permissions: Permissions) -> bool: ...
    def channel_permissions(self, channel: TYPE_GUILD_CHANNEL) -> Permissions: ...
    async def edit_nickname(self, new_nickname: Absent[str] = ..., reason: Absent[str] = ...) -> None: ...
    async def add_role(self, role: Union[Snowflake_Type, Role], reason: Absent[str] = ...) -> None: ...
    async def add_roles(self, roles: Iterable[Union[Snowflake_Type, Role]], reason: Absent[str] = ...) -> None: ...
    async def remove_role(self, role: Union[Snowflake_Type, Role], reason: Absent[str] = ...) -> None: ...
    async def remove_roles(self, roles: Iterable[Union[Snowflake_Type, Role]], reason: Absent[str] = ...) -> None: ...
    def has_role(self, *roles: Union[Snowflake_Type, Role]) -> bool: ...
    async def timeout(
        self,
        communication_disabled_until: Union["Timestamp", datetime, int, float, str, None],
        reason: Absent[str] = ...,
    ) -> dict: ...
    async def move(self, channel_id: Snowflake_Type) -> None: ...
    async def edit(
        self,
        *,
        nickname: Absent[str] = ...,
        roles: Absent[Iterable[Snowflake_Type]] = ...,
        mute: Absent[bool] = ...,
        deaf: Absent[bool] = ...,
        channel_id: Absent["Snowflake_Type"] = ...,
        communication_disabled_until: Absent[Union["Timestamp", None]] = ...,
        reason: Absent[str] = ...,
    ) -> None: ...
    async def kick(self, reason: Absent[str] = ...) -> None: ...
    async def ban(self, delete_message_days: int = ..., reason: Absent[str] = ...) -> None: ...
