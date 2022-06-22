from datetime import datetime
from typing import Any, List, Optional, Union

from ... import ActionRow, Button, SelectMenu
from .attrs_utils import ClientSerializerMixin, define
from .flags import Permissions as Permissions
from .message import Embed, Message, MessageInteraction
from .misc import File, Snowflake
from .role import Role as Role
from .user import User as User
from .channel import Channel

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
        guild_id: Union[int, Snowflake, "Guild"],  # noqa
        reason: Optional[str] = ...,
        delete_message_days: Optional[int] = ...
    ) -> None: ...
    async def kick(self, guild_id: Union[int, Snowflake, "Guild"], reason: Optional[str] = ...) -> None: ...  # noqa
    async def add_role(
        self,
        role: Union[Role, int, Snowflake],
        guild_id: Union[int, Snowflake, "Guild"],  # noqa
        reason: Optional[str] = ...
    ) -> None: ...
    async def remove_role(
        self,
        role: Union[Role, int, Snowflake],
        guild_id: Union[int, Snowflake, "Guild"],  # noqa
        reason: Optional[str] = ...
    ) -> None: ...
    async def send(
        self,
        content: Optional[str] = ...,
        *,
        components: Optional[
            Union[ActionRow, Button, SelectMenu, List[ActionRow], List[Button], List[SelectMenu]]
        ] = ...,
        attachments: Optional[List["Attachment"]] = ...,  # noqa
        tts: Optional[bool] = ...,
        files: Optional[Union[File, List[File]]] = ...,
        embeds: Optional[Union[Embed, List[Embed]]] = ...,
        allowed_mentions: Optional[MessageInteraction] = ...
    ) -> Message: ...
    async def modify(
        self,
        guild_id: Union[int, Snowflake, "Guild"],  # noqa
        nick: Optional[str] = ...,
        roles: Optional[List[int]] = ...,
        mute: Optional[bool] = ...,
        deaf: Optional[bool] = ...,
        channel_id: Optional[Union[Channel, int, Snowflake]] = ...,
        communication_disabled_until: Optional[datetime.isoformat] = ...,
        reason: Optional[str] = ...,
    ) -> Member: ...
    async def add_to_thread(self, thread_id: Union[int, Snowflake, Channel]) -> None: ...
    def get_member_avatar_url(self, guild_id: Union[int, Snowflake, "Guild"]) -> Optional[str]: ...  # noqa
