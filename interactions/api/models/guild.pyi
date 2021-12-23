from datetime import datetime
from enum import Enum
from typing import Any, List, Optional, Union

from .channel import Channel, ChannelType
from .member import Member
from .message import Emoji, Sticker
from .misc import DictSerializerMixin, Snowflake
from .presence import PresenceUpdate
from .role import Role
from .user import User
from ..http import HTTPClient

class WelcomeChannels(DictSerializerMixin):
    _json: dict
    channel_id: int
    description: str
    emoji_id: Optional[Snowflake]
    emoji_name: Optional[str]
    def __init__(self, **kwargs): ...

class WelcomeScreen(DictSerializerMixin):
    _json: dict
    description: Optional[str]
    welcome_channels: List[WelcomeChannels]
    def __init__(self, **kwargs): ...

class StageInstance(DictSerializerMixin):
    _json: dict
    id: int
    guild_id: int
    channel_id: int
    topic: str
    privacy_level: int  # can be Enum'd
    discoverable_disabled: bool
    def __init__(self, **kwargs): ...

class Guild(DictSerializerMixin):
    _json: dict
    _client: HTTPClient
    id: Snowflake
    name: str
    icon: Optional[str]
    icon_hash: Optional[str]
    splash: Optional[str]
    discovery_splash: Optional[str]
    owner: Optional[bool]
    owner_id: int
    permissions: Optional[str]
    region: Optional[str]  # None, we don't do Voices.
    afk_channel_id: Optional[Snowflake]
    afk_timeout: int
    widget_enabled: Optional[bool]
    widget_channel_id: Optional[Snowflake]
    verification_level: int
    default_message_notifications: int
    explicit_content_filter: int
    roles: List[Role]
    emojis: List[Emoji]
    mfa_level: int
    application_id: Optional[Snowflake]
    system_channel_id: Optional[Snowflake]
    system_channel_flags: int
    rules_channel_id: Optional[Snowflake]
    joined_at: Optional[datetime]
    large: Optional[bool]
    unavailable: Optional[bool]
    member_count: Optional[int]
    members: Optional[List[Member]]
    channels: Optional[List[Channel]]
    threads: Optional[List[Channel]]  # threads, because of their metadata
    presences: Optional[List[PresenceUpdate]]
    max_presences: Optional[int]
    max_members: Optional[int]
    vanity_url_code: Optional[str]
    description: Optional[str]
    banner: Optional[str]
    premium_tier: int
    premium_subscription_count: Optional[int]
    preferred_locale: str
    public_updates_channel_id: Optional[Snowflake]
    max_video_channel_users: Optional[int]
    approximate_member_count: Optional[int]
    approximate_presence_count: Optional[int]
    welcome_screen: Optional[WelcomeScreen]
    nsfw_level: int
    stage_instances: Optional[List[StageInstance]]
    stickers: Optional[List[Sticker]]

    # TODO: post-v4: Investigate all of these once Discord has them all documented.
    guild_hashes: Any
    embedded_activities: Any
    guild_scheduled_events: Any
    nsfw: Any
    application_command_count: Any
    premium_progress_bar_enabled: Any
    hub_type: Any
    lazy: Any
    application_command_counts: Any
    def __init__(self, **kwargs): ...
    async def ban(
        self,
        member_id: int,
        reason: Optional[str] = None,
        delete_message_days: Optional[int] = 0,
    ) -> None: ...
    async def remove_ban(
        self,
        user_id: int,
        reason: Optional[str] = None,
    ) -> None: ...
    async def kick(
        self,
        member_id: int,
        reason: Optional[str] = None,
    ) -> None: ...
    async def add_member_role(
        self,
        role: Union[Role, int],
        member_id: int,
        reason: Optional[str],
    ) -> None: ...
    async def remove_member_role(
        self,
        role: Union[Role, int],
        member_id: int,
        reason: Optional[str],
    ) -> None: ...
    async def create_role(
        self,
        name: str,
        # permissions,
        color: Optional[int] = 0,
        hoist: Optional[bool] = False,
        # icon,
        # unicode_emoji,
        mentionable: Optional[bool] = False,
        reason: Optional[str] = None,
    ) -> Role: ...
    async def get_member(
        self,
        member_id: int,
    ) -> Member: ...
    async def delete_channel(
        self,
        channel_id: int,
    ) -> None: ...
    async def delete_role(
        self,
        role_id: int,
        reason: Optional[str],
    ) -> None: ...
    async def modify_role(
        self,
        role_id: int,
        name: Optional[str] = None,
        # permissions,
        color: Optional[int] = None,
        hoist: Optional[bool] = None,
        # icon,
        # unicode_emoji,
        mentionable: Optional[bool] = None,
        reason: Optional[str] = None,
    ) -> Role: ...
    async def create_channel(
        self,
        name: str,
        type: ChannelType,
        topic: Optional[str] = None,
        bitrate: Optional[int] = None,
        user_limit: Optional[int] = None,
        rate_limit_per_user: Optional[int] = 0,
        position: Optional[int] = None,
        # permission_overwrites,
        parent_id: Optional[int] = None,
        nsfw: Optional[bool] = False,
        reason: Optional[str] = None
    ) -> Channel: ...
    async def modify_channel(
        self,
        channel_id: int,
        name: Optional[str] = None,
        topic: Optional[str] = None,
        bitrate: Optional[int] = None,
        user_limit: Optional[int] = None,
        rate_limit_per_user: Optional[int] = None,
        position: Optional[int] = None,
        # permission_overwrites,
        parent_id: Optional[int] = None,
        nsfw: Optional[bool] = False,
        reason: Optional[str] = None
    ) -> Channel: ...

    async def modify_member(
        self,
        member_id: int,
        nick: Optional[str] = "",  # can't be None because None would remove the nickname
        roles: Optional[List[int]] = None,
        mute: Optional[bool] = None,
        deaf: Optional[bool] = None,
        channel_id: Optional[int] = 0,  # can't be None because None would kick the member from the channel
        communication_disabled_until: Optional[datetime.isoformat] = 0,
        # can't be None because None would remove the timeout
        reason: Optional[str] = None,
    ) -> Member: ...

class GuildPreview(DictSerializerMixin):
    _json: dict
    id: int
    name: str
    icon: Optional[str]
    splash: Optional[str]
    discovery_splash: Optional[str]
    emoji: List[Emoji]
    approximate_member_count: int
    approximate_presence_count: int
    description: Optional[str]
    def __init__(self, **kwargs): ...

class Invite(DictSerializerMixin):
    _json: dict
    uses: int
    max_uses: int
    max_age: int
    temporary: bool
    created_at: datetime
    def __init__(self, **kwargs): ...

class GuildTemplate(DictSerializerMixin):
    _json: dict
    code: str
    name: str
    description: Optional[str]
    usage_count: int
    creator_id: int
    creator: User
    created_at: datetime
    updated_at: datetime
    source_guild_id: int
    serialized_source_guild: Guild  # partial
    is_dirty: Optional[bool]
    def __init__(self, **kwargs): ...

class EventMetadata(DictSerializerMixin):
    _json: dict
    location: Optional[str]
    def __init__(self, **kwargs): ...

class ScheduledEvents(DictSerializerMixin):
    _json: dict
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
    def __init__(self, **kwargs): ...
