from datetime import datetime
from enum import Enum
from typing import List, Optional

from .channel import Channel
from .member import Member
from .message import Emoji, Sticker
from .misc import DictSerializerMixin, Snowflake
from .presence import PresenceUpdate
from .role import Role
from .user import User
from .voice import VoiceState

class GuildFeature(str, Enum):
    __slots__ = (
        "ANIMATED_ICON",
        "BANNER",
        "COMMERCE",
        "COMMUNITY",
        "DISCOVERABLE",
        "FEATURABLE",
        "INVITE_SPLASH",
        "MEMBER_VERIFICATION_GATE_ENABLED",
        "NEWS",
        "PARTNERED",
        "PREVIEW_ENABLED",
        "VANITY_URL",
        "VERIFIED",
        "VIP_REGIONS",
        "WELCOME_SCREEN_ENABLED",
        "TICKETED_EVENTS_ENABLED",
        "MONETIZATION_ENABLED",
        "MORE_STICKERS",
        "THREE_DAY_THREAD_ARCHIVE",
        "SEVEN_DAY_THREAD_ARCHIVE",
        "PRIVATE_THREADS",
    )

class WelcomeChannels(DictSerializerMixin):
    _json: dict
    channel_id: int
    description: str
    emoji_id: Optional[int]
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
    afk_channel_id: Optional[int]
    afk_timeout: int
    widget_enabled: Optional[bool]
    widget_channel_id: Optional[int]
    verification_level: int
    default_message_notifications: int
    explicit_content_filter: int
    roles: List[Role]
    emojis: List[Emoji]
    features: List[GuildFeature]
    mfa_level: int
    application_id: Optional[int]
    system_channel_id: Optional[int]
    system_channel_flags: int
    rules_channel_id: Optional[int]
    joined_at: Optional[datetime]
    large: Optional[bool]
    unavailable: Optional[bool]
    member_count: Optional[int]
    voice_states: Optional[List[VoiceState]]
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
    public_updates_channel_id: Optional[int]
    max_video_channel_users: Optional[int]
    approximate_member_count: Optional[int]
    approximate_presence_count: Optional[int]
    welcome_screen: Optional[WelcomeScreen]
    nsfw_level: int
    stage_instances: Optional[StageInstance]
    stickers: Optional[List[Sticker]]
    def __init__(self, **kwargs): ...

class GuildPreview(DictSerializerMixin):
    _json: dict
    id: int
    name: str
    icon: Optional[str]
    splash: Optional[str]
    discovery_splash: Optional[str]
    emoji: List[Emoji]
    features: List[GuildFeature]
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
