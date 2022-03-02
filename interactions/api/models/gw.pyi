from datetime import datetime
from typing import List, Optional, Any

from .channel import Channel, ThreadMember
from .member import Member
from .message import Emoji, Sticker
from .misc import ClientStatus, DictSerializerMixin, Snowflake
from .presence import PresenceActivity
from .role import Role
from .user import User
from .team import Application
from ..http.HTTPClient import HTTPClient
from ...models.command import Permission

class ApplicationCommandPermissions(DictSerializerMixin):
    _json: dict
    application_id: Snowflake
    guild_id: Snowflake
    id: Snowflake
    permissions: List[Permission]

    def __init__(self, **kwargs): ...


class ChannelPins(DictSerializerMixin):
    _json: dict
    guild_id: Optional[Snowflake]
    channel_id: Snowflake
    last_pin_timestamp: Optional[datetime]
    def __init__(self, **kwargs): ...

class EmbeddedActivity(DictSerializerMixin):
    _json: dict
    users: List[Snowflake]
    guild_id: Snowflake
    embedded_activity: PresenceActivity
    channel_id: Snowflake
    def __init__(self, **kwargs): ...

class GuildBan(DictSerializerMixin):
    _json: dict
    guild_id: Snowflake
    user: User
    _client: Optional[HTTPClient]
    def __init__(self, **kwargs): ...

class GuildEmojis(DictSerializerMixin):
    _json: dict
    guild_id: Snowflake
    emojis: List[Emoji]
    def __init__(self, **kwargs): ...

class GuildIntegrations(DictSerializerMixin):
    _json: dict
    guild_id: Snowflake
    def __init__(self, **kwargs): ...

class GuildJoinRequest(DictSerializerMixin):
    _json: dict
    user_id: Snowflake
    guild_id: Snowflake
    def __init__(self, **kwargs): ...

class GuildMember(DictSerializerMixin):
    _json: dict
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
    _client: Optional[HTTPClient]
    def __init__(self, **kwargs): ...

class GuildMembers(DictSerializerMixin):
    _json: dict
    guild_id: Snowflake
    members: List[Member]
    chunk_index: int
    chunk_count: int
    not_found: Optional[list]
    presences: Optional[List["Presence"]]
    nonce: Optional[str]
    def __init__(self, **kwargs): ...

class GuildRole(DictSerializerMixin):
    _json: dict
    guild_id: Snowflake
    role: Role
    role_id: Optional[Snowflake]
    _client: Optional[HTTPClient]
    def __init__(self, **kwargs): ...

class GuildStickers(DictSerializerMixin):
    _json: dict
    guild_id: Snowflake
    stickers: List[Sticker]
    def __init__(self, **kwargs): ...

class Integration(DictSerializerMixin):
    _json: dict
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

    def __init__(self, **kwargs): ...

class Presence(DictSerializerMixin):
    _json: dict
    user: User
    guild_id: Snowflake
    status: str
    activities: List[PresenceActivity]
    client_status: ClientStatus

class MessageReaction(DictSerializerMixin):
    # There's no official data model for this, so this is pseudo for the most part here.
    _json: dict
    user_id: Optional[Snowflake]
    channel_id: Snowflake
    message_id: Snowflake
    guild_id: Optional[Snowflake]
    member: Optional[Member]
    emoji: Optional[Emoji]
    def __init__(self, **kwargs): ...

class ReactionRemove(MessageReaction):
    # typehinting already subclassed
    def __init__(self, **kwargs): ...

class ThreadList(DictSerializerMixin):
    _json: dict
    guild_id: Snowflake
    channel_ids: Optional[List[Snowflake]]
    threads: List[Channel]
    members: List[ThreadMember]
    def __init__(self, **kwargs): ...

class ThreadMembers(DictSerializerMixin):
    _json: dict
    id: Snowflake
    guild_id: Snowflake
    member_count: int
    added_members: Optional[List[ThreadMember]]
    removed_member_ids: Optional[List[Snowflake]]
    def __init__(self, **kwargs): ...

class Webhooks(DictSerializerMixin):
    _json: dict
    channel_id: Snowflake
    guild_id: Snowflake
    def __init__(self, **kwargs): ...
