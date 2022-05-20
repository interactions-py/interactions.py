from .channel import Channel as Channel
from .flags import Permissions as Permissions
from .misc import DictSerializerMixin as DictSerializerMixin, File as File, MISSING as MISSING, Snowflake as Snowflake, convert_int as convert_int, define as define, field as field
from .role import Role as Role
from .user import User as User
from datetime import datetime
from typing import Any, List, Optional, Union

from ..http.client import HTTPClient


class Member(DictSerializerMixin):
    _client: HTTPClient
    user: Optional[User]
    nick: Optional[str]
    roles: List[int]
    joined_at: datetime
    premium_since: Optional[datetime]
    deaf: bool
    mute: bool
    is_pending: Optional[bool]
    pending: Optional[bool]
    permissions: Optional[Permissions]
    communication_disabled_until: Optional[datetime.isoformat]
    hoisted_role: Optional[Any]
    flags: int
    @property
    def avatar(self) -> Optional[str]: ...
    @property
    def id(self) -> Snowflake: ...
    @property
    def mention(self) -> str: ...
    @property
    def name(self) -> str: ...
    async def ban(self, guild_id: int, reason: Optional[str] = ..., delete_message_days: Optional[int] = ...) -> None: ...
    async def kick(self, guild_id: int, reason: Optional[str] = ...) -> None: ...
    async def add_role(self, role: Union[Role, int], guild_id: int, reason: Optional[str] = ...) -> None: ...
    async def remove_role(self, role: Union[Role, int], guild_id: int, reason: Optional[str] = ...) -> None: ...
    async def send(self, content: Optional[str] = ..., *, components: Optional[Union['ActionRow', 'Button', 'SelectMenu', List['ActionRow'], List['Button'], List['SelectMenu']]] = ..., tts: Optional[bool] = ..., files: Optional[Union[File, List[File]]] = ..., embeds: Optional[Union['Embed', List['Embed']]] = ..., allowed_mentions: Optional['MessageInteraction'] = ...) -> Message: ...
    async def modify(self, guild_id: int, nick: Optional[str] = ..., roles: Optional[List[int]] = ..., mute: Optional[bool] = ..., deaf: Optional[bool] = ..., channel_id: Optional[int] = ..., communication_disabled_until: Optional[datetime.isoformat] = ..., reason: Optional[str] = ...) -> Member: ...
    async def add_to_thread(self, thread_id: int) -> None: ...
    def get_member_avatar_url(self, guild_id: int) -> Optional[str]: ...
