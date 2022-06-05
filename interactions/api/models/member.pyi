from datetime import datetime
from typing import Any, List, Optional, Union

from .attrs_utils import ClientSerializerMixin, define
from .flags import Permissions
from .message import Message, Embed, MessageInteraction
from .misc import File, Snowflake
from .role import Role
from .user import User
from ... import ActionRow, Button, SelectMenu


@define()
class Member(ClientSerializerMixin):
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
    async def ban(
        self,
        guild_id: int,
        reason: Optional[str] = None,
        delete_message_days: Optional[int] = 0,
    ) -> None: ...
    async def kick(
        self,
        guild_id: int,
        reason: Optional[str] = None,
    ) -> None: ...
    async def add_role(
        self,
        role: Union[Role, int],
        guild_id: int,
        reason: Optional[str] = None,
    ) -> None: ...
    async def remove_role(
        self,
        role: Union[Role, int],
        guild_id: int,
        reason: Optional[str] = None,
    ) -> None: ...
    async def send(
        self,
        content: Optional[str] = MISSING,
        *,
        components: Optional[
            Union[
                ActionRow,
                Button,
                SelectMenu,
                List[ActionRow],
                List[Button],
                List[SelectMenu],
            ]
        ] = MISSING,
        tts: Optional[bool] = MISSING,
        files: Optional[Union[File, List[File]]] = MISSING,
        embeds: Optional[Union[Embed, List[Embed]]] = MISSING,
        allowed_mentions: Optional[MessageInteraction] = MISSING,
    ) -> Message: ...
    async def modify(
        self,
        guild_id: int,
        nick: Optional[str] = MISSING,
        roles: Optional[List[int]] = MISSING,
        mute: Optional[bool] = MISSING,
        deaf: Optional[bool] = MISSING,
        channel_id: Optional[int] = MISSING,
        communication_disabled_until: Optional[datetime.isoformat] = MISSING,
        reason: Optional[str] = None,
    ) -> Member: ...
    async def add_to_thread(
        self,
        thread_id: int,
    ) -> None: ...
    def get_avatar_url(self, guild_id: int) -> Optional[str]: ...
