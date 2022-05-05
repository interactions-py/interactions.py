from datetime import datetime
from typing import List, Optional, Union, Any

from ...models.component import ActionRow, Button, SelectMenu
from .channel import Channel, ThreadMember
from .member import Member
from .message import Embed, Emoji, Message, MessageInteraction, Sticker
from .misc import MISSING, ClientStatus, DictSerializerMixin, Snowflake, File
from .presence import PresenceActivity
from .role import Role
from .user import User
from .team import Application

from ..http.client import HTTPClient
from ...models.command import Permission

class ApplicationCommandPermissions(DictSerializerMixin):
    _json: dict
    application_id: Snowflake
    guild_id: Snowflake
    id: Snowflake
    permissions: List[Permission]
    _client: Optional[HTTPClient]

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
    @property
    def mention(self) -> str: ...
    @property
    def id(self) -> Snowflake: ...
    async def ban(
        self,
        reason: Optional[str] = None,
        delete_message_days: Optional[int] = 0,
    ) -> None: ...
    async def kick(
        self,
        reason: Optional[str] = None,
    ) -> None: ...
    async def add_role(
        self,
        role: Union[Role, int],
        reason: Optional[str],
    ) -> None: ...
    async def remove_role(
        self,
        role: Union[Role, int],
        reason: Optional[str],
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
        embeds: Optional[Union[Embed, List["Embed"]]] = MISSING,
        allowed_mentions: Optional[MessageInteraction] = MISSING,
    ) -> Message: ...
    async def modify(
        self,
        nick: Optional[str] = MISSING,
        roles: Optional[List[int]] = MISSING,
        mute: Optional[bool] = MISSING,
        deaf: Optional[bool] = MISSING,
        channel_id: Optional[int] = MISSING,
        communication_disabled_until: Optional[datetime.isoformat] = MISSING,
        reason: Optional[str] = None,
    ) -> "GuildMember": ...
    async def add_to_thread(
        self,
        thread_id: int,
    ) -> None: ...

class GuildMembers(DictSerializerMixin):
    _json: dict
    guild_id: Snowflake
    members: List[GuildMember]
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
    _client: HTTPClient
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
