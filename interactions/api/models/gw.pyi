from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from ...client.models.component import ActionRow, Button, SelectMenu
from .attrs_utils import ClientSerializerMixin, DictSerializerMixin, define
from .channel import Channel, ThreadMember
from .guild import EventMetadata
from .member import Member
from .message import Embed, Emoji, Message, MessageInteraction, Sticker
from .misc import AutoModAction, ClientStatus, File, Snowflake, AutoModTriggerMetadata
from .presence import PresenceActivity
from .role import Role
from .team import Application
from .user import User


class AutoModerationAction(DictSerializerMixin):
    guild_id: Snowflake
    action: AutoModAction
    rule_id: Snowflake
    rule_trigger_type: int
    channel_id: Optional[Snowflake]
    message_id: Optional[Snowflake]
    alert_system_message_id: Optional[Snowflake]
    content: str
    matched_keyword: Optional[str]
    matched_content: Optional[str]

class AutoModerationRule(DictSerializerMixin):
    _json: dict
    id: Snowflake
    guild_id: Snowflake
    name: str
    creator_id: str
    event_type: int
    trigger_type: int
    trigger_metadata: AutoModTriggerMetadata
    actions: List[AutoModAction]
    enabled: bool
    exempt_roles: List[Snowflake]
    exempt_channels: List[Snowflake]


@define()
class ApplicationCommandPermissions(ClientSerializerMixin):
    application_id: Snowflake
    guild_id: Snowflake
    id: Snowflake
    permissions: Any

@define()
class ChannelPins(DictSerializerMixin):
    guild_id: Optional[Snowflake]
    channel_id: Snowflake
    last_pin_timestamp: Optional[datetime]

@define()
class EmbeddedActivity(DictSerializerMixin):
    users: List[Snowflake]
    guild_id: Snowflake
    embedded_activity: PresenceActivity
    channel_id: Snowflake

@define()
class GuildBan(ClientSerializerMixin):
    guild_id: Snowflake
    user: User

@define()
class GuildEmojis(ClientSerializerMixin):
    guild_id: Snowflake
    emojis: List[Emoji]

@define()
class GuildIntegrations(DictSerializerMixin):
    guild_id: Snowflake

@define()
class GuildJoinRequest(DictSerializerMixin):
    user_id: Snowflake
    guild_id: Snowflake

@define()
class GuildMember(ClientSerializerMixin):
    guild_id: Snowflake
    roles: Optional[List[str]]
    user: Optional[User]
    nick: Optional[str]
    avatar: Optional[str]
    joined_at: Optional[datetime]
    premium_since: Optional[datetime]
    deaf: Optional[bool]
    mute: Optional[bool]
    pending: Optional[bool]
    @property
    def id(self) -> Snowflake: ...
    @property
    def mention(self) -> str: ...
    async def ban(
        self, reason: Optional[str] = ..., delete_message_days: Optional[int] = ...
    ) -> None: ...
    async def kick(self, reason: Optional[str] = ...) -> None: ...
    async def add_role(self, role: Union[Role, int], reason: Optional[str]) -> None: ...
    async def remove_role(self, role: Union[Role, int], reason: Optional[str]) -> None: ...
    async def send(
        self,
        content: Optional[str] = ...,
        *,
        components: Optional[
            Union[ActionRow, Button, SelectMenu, List[ActionRow], List[Button], List[SelectMenu]]
        ] = ...,
        tts: Optional[bool] = ...,
        files: Optional[Union[File, List[File]]] = ...,
        embeds: Optional[Union[Embed, List[Embed]]] = ...,
        allowed_mentions: Optional[MessageInteraction] = ...,
    ) -> Message: ...
    async def modify(
        self,
        nick: Optional[str] = ...,
        roles: Optional[List[int]] = ...,
        mute: Optional[bool] = ...,
        deaf: Optional[bool] = ...,
        channel_id: Optional[int] = ...,
        communication_disabled_until: Optional[datetime.isoformat] = ...,
        reason: Optional[str] = ...,
    ) -> GuildMember: ...
    async def add_to_thread(self, thread_id: int) -> None: ...

@define()
class GuildMembers(DictSerializerMixin):
    guild_id: Snowflake
    members: List[GuildMember]
    chunk_index: int
    chunk_count: int
    not_found: Optional[list]
    presences: Optional[List[PresenceActivity]]
    nonce: Optional[str]

@define()
class GuildRole(ClientSerializerMixin):
    guild_id: Snowflake
    role: Optional[Role]
    role_id: Optional[Snowflake]
    guild_hashes: Any
    def __attrs_post_init__(self): ...

@define()
class GuildStickers(DictSerializerMixin):
    guild_id: Snowflake
    stickers: List[Sticker]

@define()
class GuildScheduledEvent(ClientSerializerMixin):
    id: Snowflake
    guild_id: Snowflake
    channel_id: Optional[Snowflake]
    creator_id: Optional[Snowflake]
    name: str
    description: str
    scheduled_start_time: datetime
    scheduled_end_time: Optional[datetime]
    privacy_level: int
    entity_type: int
    entity_id: Optional[Snowflake]
    entity_metadata: Optional[EventMetadata]
    creator: Optional[User]
    user_count: Optional[int]
    status: int
    image: Optional[str]

@define()
class GuildScheduledEventUser(DictSerializerMixin):
    guild_scheduled_event_id: Snowflake
    user_id: Snowflake
    guild_id: Snowflake

@define()
class Integration(DictSerializerMixin):
    id: Snowflake
    name: str
    type: str
    enabled: bool
    syncing: bool
    role_id: Snowflake
    enable_emoticons: bool
    expire_behavior: int
    expire_grace_period: int
    user: User
    account: Any
    synced_at: datetime
    subscriber_count: int
    revoked: bool
    application: Application
    guild_id: Snowflake

@define()
class Presence(ClientSerializerMixin):
    user: User
    guild_id: Snowflake
    status: str
    activities: List[PresenceActivity]
    client_status: ClientStatus

@define()
class MessageReaction(DictSerializerMixin):
    user_id: Optional[Snowflake]
    channel_id: Snowflake
    message_id: Snowflake
    guild_id: Optional[Snowflake]
    member: Optional[Member]
    emoji: Optional[Emoji]

@define()
class ReactionRemove(MessageReaction): ...

@define()
class ThreadList(DictSerializerMixin):
    guild_id: Snowflake
    channel_ids: Optional[List[Snowflake]]
    threads: List[Channel]
    members: List[ThreadMember]

@define()
class ThreadMembers(DictSerializerMixin):
    id: Snowflake
    guild_id: Snowflake
    member_count: int
    added_members: Optional[List[ThreadMember]]
    removed_member_ids: Optional[List[Snowflake]]

@define()
class Webhooks(DictSerializerMixin):
    channel_id: Snowflake
    guild_id: Snowflake
