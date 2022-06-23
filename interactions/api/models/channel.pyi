from datetime import datetime
from enum import IntEnum
from typing import Any, Callable, List, Optional, Union

from ... import ActionRow, Button, SelectMenu
from .attrs_utils import ClientSerializerMixin, define
from .guild import Invite, InviteTargetType
from .message import Embed, Message, MessageInteraction
from .misc import File, Overwrite, Snowflake
from .user import User
from .webhook import Webhook

class ChannelType(IntEnum):
    GUILD_TEXT: int
    DM: int
    GUILD_VOICE: int
    GROUP_DM: int
    GUILD_CATEGORY: int
    GUILD_NEWS: int
    GUILD_STORE: int
    GUILD_NEWS_THREAD: int
    GUILD_PUBLIC_THREAD: int
    GUILD_PRIVATE_THREAD: int
    GUILD_STAGE_VOICE: int

@define()
class ThreadMetadata(ClientSerializerMixin):
    archived: bool
    auto_archive_duration: int
    archive_timestamp: datetime.timestamp
    locked: bool
    invitable: Optional[bool]

@define()
class ThreadMember(ClientSerializerMixin):
    id: Optional[Snowflake]
    user_id: Optional[Snowflake]
    join_timestamp: datetime.timestamp
    flags: int
    muted: bool
    mute_config: Optional[Any]

@define()
class Channel(ClientSerializerMixin):
    type: ChannelType
    id: Snowflake
    guild_id: Optional[Snowflake]
    position: Optional[int]
    permission_overwrites: Optional[List[Overwrite]]
    name: str
    topic: Optional[str]
    nsfw: Optional[bool]
    last_message_id: Optional[Snowflake]
    bitrate: Optional[int]
    user_limit: Optional[int]
    rate_limit_per_user: Optional[int]
    recipients: Optional[List[User]]
    icon: Optional[str]
    owner_id: Optional[Snowflake]
    application_id: Optional[Snowflake]
    parent_id: Optional[Snowflake]
    last_pin_timestamp: Optional[datetime]
    rtc_region: Optional[str]
    video_quality_mode: Optional[int]
    message_count: Optional[int]
    member_count: Optional[int]
    thread_metadata: Optional[ThreadMetadata]
    member: Optional[ThreadMember]
    default_auto_archive_duration: Optional[int]
    permissions: Optional[str]
    flags: Optional[int]
    @property
    def mention(self) -> str: ...
    async def send(
        self,
        content: Optional[str] = ...,
        *,
        tts: Optional[bool] = ...,
        files: Optional[Union[File, List[File]]] = ...,
        embeds: Optional[Union[Embed, List[Embed]]] = ...,
        allowed_mentions: Optional[MessageInteraction] = ...,
        attachments: Optional[List["Attachment"]] = MISSING,  # noqa
        components: Optional[
            Union[
                "ActionRow",
                "Button",
                "SelectMenu",
                List["ActionRow"],
                List["Button"],
                List["SelectMenu"],
            ]
        ] = ...
    ) -> Message: ...
    async def delete(self) -> None: ...
    async def modify(
        self,
        name: Optional[str] = ...,
        topic: Optional[str] = ...,
        bitrate: Optional[int] = ...,
        user_limit: Optional[int] = ...,
        rate_limit_per_user: Optional[int] = ...,
        position: Optional[int] = ...,
        permission_overwrites: Optional[List[Overwrite]] = ...,
        parent_id: Optional[int] = ...,
        nsfw: Optional[bool] = ...,
        archived: Optional[bool] = ...,
        auto_archive_duration: Optional[int] = ...,
        locked: Optional[bool] = ...,
        reason: Optional[str] = ...,
    ) -> Channel: ...
    async def set_name(self, name: str, *, reason: Optional[str] = ...) -> Channel: ...
    async def set_topic(self, topic: str, *, reason: Optional[str] = ...) -> Channel: ...
    async def set_bitrate(self, bitrate: int, *, reason: Optional[str] = ...) -> Channel: ...
    async def set_user_limit(self, user_limit: int, *, reason: Optional[str] = ...) -> Channel: ...
    async def set_rate_limit_per_user(
        self, rate_limit_per_user: int, *, reason: Optional[str] = ...
    ) -> Channel: ...
    async def set_position(self, position: int, *, reason: Optional[str] = ...) -> Channel: ...
    async def set_parent_id(self, parent_id: int, *, reason: Optional[str] = ...) -> Channel: ...
    async def set_nsfw(self, nsfw: bool, *, reason: Optional[str] = ...) -> Channel: ...
    async def archive(self, archived: bool = ..., *, reason: Optional[str] = ...) -> Channel: ...
    async def set_auto_archive_duration(
        self, auto_archive_duration: int, *, reason: Optional[str] = ...
    ) -> Channel: ...
    async def lock(self, locked: bool = ..., *, reason: Optional[str] = ...) -> Channel: ...
    async def add_member(self, member_id: Union[int, Snowflake, "Member"]) -> None: ...  # noqa
    async def remove_member(self, member_id: Union[int, Snowflake, "Member"]) -> None: ...  # noqa
    async def pin_message(self, message_id: Union[int, Snowflake, "Message"]) -> None: ...  # noqa
    async def unpin_message(self, message_id: Union[int, Snowflake, "Message"]) -> None: ...  # noqa
    async def publish_message(self, message_id: Union[int, Snowflake, "Message"]) -> Message: ...  # noqa
    async def get_pinned_messages(self) -> List[Message]: ...
    async def get_message(self, message_id: Union[int, Snowflake]) -> Message: ...
    async def purge(
        self,
        amount: int,
        check: Callable[[...], bool] = ...,
        before: Optional[int] = ...,
        reason: Optional[str] = ...,
        bulk: Optional[bool] = ...,
    ) -> List[Message]: ...
    async def create_thread(
        self,
        name: str,
        type: Optional[ChannelType] = ...,
        auto_archive_duration: Optional[int] = ...,
        invitable: Optional[bool] = ...,
        message_id: Optional[Union[int, Snowflake, "Message"]] = ...,  # noqa
        reason: Optional[str] = ...,
    ) -> Channel: ...
    @property
    def url(self) -> str: ...
    async def create_invite(
        self,
        max_age: Optional[int] = ...,
        max_uses: Optional[int] = ...,
        temporary: Optional[bool] = ...,
        unique: Optional[bool] = ...,
        target_type: Optional[InviteTargetType] = ...,
        target_user_id: Optional[int] = ...,
        target_application_id: Optional[int] = ...,
        reason: Optional[str] = ...,
    ) -> Invite: ...
    async def get_history(self, limit: int = ...) -> List[Message]: ...
    async def get_webhooks(self) -> List[Webhook]: ...
    async def get_members(self) -> List[ThreadMember]: ...
    async def leave_thread(self) -> None: ...
    async def join_thread(self) -> None: ...

@define()
class Thread(Channel): ...
