from datetime import datetime
from typing import Any, List, Optional, Union, Dict
from enum import IntEnum

from .channel import Channel, ChannelType, Thread
from .member import Member
from .message import Emoji, Sticker
from .misc import DictSerializerMixin, MISSING, Snowflake, Overwrite, Image
from .presence import PresenceActivity
from .role import Role
from .user import User
from ..http.client import HTTPClient

class VerificationLevel(IntEnum):
    NONE: int
    LOW: int
    MEDIUM: int
    HIGH: int
    VERY_HIGH: int

class ExplicitContentFilterLevel(IntEnum):
    DISABLED: int
    MEMBERS_WITHOUT_ROLES: int
    ALL_MEMBERS: int

class DefaultMessageNotificationLevel(IntEnum):
    ALL_MESSAGES: int
    ONLY_MENTIONS: int

class EntityType(IntEnum):
    STAGE_INSTANCE: int
    VOICE: int
    EXTERNAL: int

class EventStatus(IntEnum):
    SCHEDULED: int
    ACTIVE: int
    COMPLETED: int
    CANCELED: int

class InviteTargetType(IntEnum):
    STREAM: int
    EMBEDDED_APPLICATION: int

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

class UnavailableGuild(DictSerializerMixin):
    _json: dict
    id: Snowflake
    unavailable: bool
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
    threads: Optional[List[Thread]]  # threads, because of their metadata
    presences: Optional[List[PresenceActivity]]
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
    def __repr__(self) -> str: ...
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
        reason: Optional[str] = None,
    ) -> None: ...
    async def remove_member_role(
        self,
        role: Union[Role, int],
        member_id: int,
        reason: Optional[str] = None,
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
        reason: Optional[str] = None,
    ) -> None: ...
    async def modify_role(
        self,
        role_id: int,
        name: Optional[str] = MISSING,
        # permissions,
        color: Optional[int] = MISSING,
        hoist: Optional[bool] = MISSING,
        # icon,
        # unicode_emoji,
        mentionable: Optional[bool] = MISSING,
        reason: Optional[str] = None,
    ) -> Role: ...
    async def create_thread(
        self,
        name: str,
        channel_id: int,
        type: Optional[ChannelType] = ChannelType.GUILD_PUBLIC_THREAD,
        auto_archive_duration: Optional[int] = MISSING,
        invitable: Optional[bool] = MISSING,
        message_id: Optional[int] = MISSING,
        reason: Optional[str] = None,
    ) -> Channel: ...
    async def create_channel(
        self,
        name: str,
        type: ChannelType,
        topic: Optional[str] = MISSING,
        bitrate: Optional[int] = MISSING,
        user_limit: Optional[int] = MISSING,
        rate_limit_per_user: Optional[int] = MISSING,
        position: Optional[int] = MISSING,
        permission_overwrites: Optional[List[Overwrite]] = MISSING,
        parent_id: Optional[int] = MISSING,
        nsfw: Optional[bool] = MISSING,
        reason: Optional[str] = None,
    ) -> Channel: ...
    async def modify_channel(
        self,
        channel_id: int,
        name: Optional[str] = MISSING,
        topic: Optional[str] = MISSING,
        bitrate: Optional[int] = MISSING,
        user_limit: Optional[int] = MISSING,
        rate_limit_per_user: Optional[int] = MISSING,
        position: Optional[int] = MISSING,
        permission_overwrites: Optional[List[Overwrite]] = MISSING,
        parent_id: Optional[int] = MISSING,
        nsfw: Optional[bool] = MISSING,
        archived: Optional[bool] = MISSING,
        auto_archive_duration: Optional[int] = MISSING,
        locked: Optional[bool] = MISSING,
        reason: Optional[str] = None,
    ) -> Channel: ...
    async def modify_member(
        self,
        member_id: int,
        nick: Optional[str] = MISSING,
        roles: Optional[List[int]] = MISSING,
        mute: Optional[bool] = MISSING,
        deaf: Optional[bool] = MISSING,
        channel_id: Optional[int] = MISSING,
        communication_disabled_until: Optional[datetime.isoformat] = MISSING,
        reason: Optional[str] = None,
    ) -> Member: ...
    async def get_preview(self) -> GuildPreview: ...
    async def leave(self) -> None: ...
    async def modify(
        self,
        name: Optional[str] = MISSING,
        verification_level: Optional[VerificationLevel] = MISSING,
        default_message_notifications: Optional[DefaultMessageNotificationLevel] = MISSING,
        explicit_content_filter: Optional[ExplicitContentFilterLevel] = MISSING,
        afk_channel_id: Optional[int] = MISSING,
        afk_timeout: Optional[int] = MISSING,
        icon: Optional[Image] = MISSING,
        owner_id: Optional[int] = MISSING,
        splash: Optional[Image] = MISSING,
        discovery_splash: Optional[Image] = MISSING,
        banner: Optional[Image] = MISSING,
        system_channel_id: Optional[int] = MISSING,
        suppress_join_notifications: Optional[bool] = MISSING,
        suppress_premium_subscriptions: Optional[bool] = MISSING,
        suppress_guild_reminder_notifications: Optional[bool] = MISSING,
        suppress_join_notification_replies: Optional[bool] = MISSING,
        rules_channel_id: Optional[int] = MISSING,
        public_updates_channel_id: Optional[int] = MISSING,
        preferred_locale: Optional[str] = MISSING,
        description: Optional[str] = MISSING,
        premium_progress_bar_enabled: Optional[bool] = MISSING,
        reason: Optional[str] = None,
    ) -> "Guild": ...
    async def set_name(
        self,
        name: str,
        *,
        reason: Optional[str] = None,
    ) -> "Guild": ...
    async def set_verification_level(
        self,
        verification_level: VerificationLevel,
        *,
        reason: Optional[str] = None,
    ) -> "Guild": ...
    async def set_default_message_notifications(
        self,
        default_message_notifications: DefaultMessageNotificationLevel,
        *,
        reason: Optional[str] = None,
    ) -> "Guild": ...
    async def set_explicit_content_filter(
        self,
        explicit_content_filter: ExplicitContentFilterLevel,
        *,
        reason: Optional[str] = None,
    ) -> "Guild": ...
    async def set_afk_channel(
        self,
        afk_channel_id: int,
        *,
        reason: Optional[str] = None,
    ) -> "Guild": ...
    async def set_afk_timeout(
        self,
        afk_timeout: int,
        *,
        reason: Optional[str] = None,
    ) -> "Guild": ...
    async def set_system_channel(
        self,
        system_channel_id: int,
        *,
        reason: Optional[str] = None,
    ) -> "Guild": ...
    async def set_rules_channel(
        self,
        rules_channel_id: int,
        *,
        reason: Optional[str] = None,
    ) -> "Guild": ...
    async def set_public_updates_channel(
        self,
        public_updates_channel_id: int,
        *,
        reason: Optional[str] = None,
    ) -> "Guild": ...
    async def set_preferred_locale(
        self,
        preferred_locale: str,
        *,
        reason: Optional[str] = None,
    ) -> "Guild": ...
    async def set_description(
        self,
        description: str,
        *,
        reason: Optional[str] = None,
    ) -> "Guild": ...
    async def set_premium_progress_bar_enabled(
        self,
        premium_progress_bar_enabled: bool,
        *,
        reason: Optional[str] = None,
    ) -> "Guild": ...
    async def set_icon(
        self,
        icon: Image,
        *,
        reason: Optional[str] = None,
    ) -> "Guild": ...
    async def set_splash(
        self,
        splash: Image,
        *,
        reason: Optional[str] = None,
    ) -> "Guild": ...
    async def set_discovery_splash(
        self,
        discovery_splash: Image,
        *,
        reason: Optional[str] = None,
    ) -> "Guild": ...
    async def set_banner(
        self,
        banner: Image,
        *,
        reason: Optional[str] = None,
    ) -> "Guild": ...
    async def create_scheduled_event(
        self,
        name: str,
        entity_type: EntityType,
        scheduled_start_time: datetime.isoformat,
        scheduled_end_time: Optional[datetime.isoformat] = MISSING,
        entity_metadata: Optional["EventMetadata"] = MISSING,
        channel_id: Optional[int] = MISSING,
        description: Optional[str] = MISSING,
        image: Optional[Image] = MISSING,
        # privacy_level, TODO: implement when more levels available
        ) -> "ScheduledEvents": ...
    async def modify_scheduled_event(
        self,
        event_id: int,
        name: Optional[str] = MISSING,
        entity_type: Optional[EntityType] = MISSING,
        scheduled_start_time: Optional[datetime.isoformat] = MISSING,
        scheduled_end_time: Optional[datetime.isoformat] = MISSING,
        entity_metadata: Optional["EventMetadata"] = MISSING,
        channel_id: Optional[int] = MISSING,
        description: Optional[str] = MISSING,
        image: Optional[Image] = MISSING,
        # privacy_level, TODO: implement when more levels available
    ) -> "ScheduledEvents": ...
    async def delete_scheduled_event(
        self,
        event_id: int
    ) -> None: ...
    async def get_all_channels(self) -> List[Channel]: ...
    async def get_all_roles(self) -> List[Role]: ...
    async def get_role(
        self,
        role_id: int,
    ) -> Role: ...
    async def modify_role_position(
        self,
        role_id: Union[Role, int],
        position: int,
        reason: Optional[str] = None,
    ) -> List[Role]: ...
    async def modify_role_positions(
        self,
        changes: List[dict],
        reason: Optional[str] = None,
    ) -> List[Role]: ...
    async def get_bans(
        self,
        limit: Optional[int] = 1000,
        before: Optional[int] = None,
        after: Optional[int] = None,
    ) -> List[dict]: ...
    async def get_all_bans(self) -> List[Dict[str, User]]: ...
    async def get_emoji(
        self,
        emoji_id: int
    ) -> Emoji: ...
    async def get_all_emoji(self) -> List[Emoji]: ...
    async def create_emoji(
        self,
        image: Image,
        name: Optional[str] = MISSING,
        roles: Optional[Union[List[Role], List[int]]] = MISSING,
        reason: Optional[str] = None,
    ) -> Emoji: ...
    async def delete_emoji(
        self,
        emoji: Union[Emoji, int],
        reason: Optional[str] = None,
    ) -> None: ...
    async def get_list_of_members(
        self,
        limit: Optional[int] = 1,
        after: Optional[Union[Member, int]] = MISSING,
    ) -> List[Member]: ...
    async def search_members(
        self,
        query: str,
        limit: Optional[int] = 1
    ) -> List[Member]: ...
    async def get_all_members(self) -> List[Member]: ...
    @property
    def icon_url(self) -> Optional[str]: ...
    @property
    def banner_url(self) -> Optional[str]: ...
    @property
    def splash_url(self) -> Optional[str]: ...
    @property
    def discovery_splash_url(self) -> Optional[str]: ...

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
    _client: HTTPClient
    type: str
    guild_id: Snowflake
    expires_at: Optional[datetime]
    code: str
    channel_id: Snowflake
    uses: int
    max_uses: int
    max_age: int
    temporary: bool
    created_at: datetime
    def __init__(self, **kwargs): ...
    async def delete(self) -> None: ...

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
    status: int
    image: Optional[str]
    def __init__(self, **kwargs): ...
