from datetime import datetime
from enum import Enum
from typing import List, Optional

from .channel import Channel
from .member import Member
from .message import Emoji, Sticker
from .presence import PresenceUpdate
from .role import Role
from .voice import VoiceState


class GuildFeature(str, Enum):
    """
    An enumerable string-formatted class representing all of the features a guild can have.

    .. note:
        Equivalent of `Guild Features <https://discord.com/developers/docs/resources/guild#guild-object-guild-features>`_ in the Discord API.
    """

    ANIMATED_ICON = "ANIMATED_ICON"
    BANNER = "BANNER"
    COMMERCE = "COMMERCE"
    COMMUNITY = "COMMUNITY"
    DISCOVERABLE = "DISCOVERABLE"
    FEATURABLE = "FEATURABLE"
    INVITE_SPLASH = "INVITE_SPLASH"
    MEMBER_VERIFICATION_GATE_ENABLED = "MEMBER_VERIFICATION_GATE_ENABLED"
    NEWS = "NEWS"
    PARTNERED = "PARTNERED"
    PREVIEW_ENABLED = "PREVIEW_ENABLED"
    VANITY_URL = "VANITY_URL"
    VERIFIED = "VERIFIED"
    VIP_REGIONS = "VIP_REGIONS"
    WELCOME_SCREEN_ENABLED = "WELCOME_SCREEN_ENABLED"
    TICKETED_EVENTS_ENABLED = "TICKETED_EVENTS_ENABLED"
    MONETIZATION_ENABLED = "MONETIZATION_ENABLED"
    MORE_STICKERS = "MORE_STICKERS"
    THREE_DAY_THREAD_ARCHIVE = "THREE_DAY_THREAD_ARCHIVE"
    SEVEN_DAY_THREAD_ARCHIVE = "SEVEN_DAY_THREAD_ARCHIVE"
    PRIVATE_THREADS = "PRIVATE_THREADS"


class WelcomeChannels(object):
    """
    A class object representing a welcome channel on the welcome screen.

    :ivar int channel_id: The ID of the welcome channel.
    :ivar str description: The description of the welcome channel.
    :ivar typing.Optional[int] emoji_id: The ID of the emoji of the welcome channel.
    :ivar typing.Optional[str] emoji_name: The name of the emoji of the welcome channel.
    """
    channel_id: int
    description: str
    emoji_id: Optional[int]
    emoji_name: Optional[str]


class WelcomeScreen(object):
    """
    A class object representing the welcome screen shown for community guilds.
    
    :ivar typing.Optional[str] description: The description of the welcome sceen.
    :ivar typing.List[interactions.api.models.guild.WelcomeChannels] welcome_channels: A list of welcome channels of the welcome screen.
    """
    description: Optional[str]
    welcome_channels: List[WelcomeChannels]


class StageInstance(object):
    """
    A class object representing an instace of a stage channel in a guild.

    :ivar int id: The ID of the stage.
    :ivar int guild_id: The guild ID the stage is in.
    :ivar int channel_id: The channel ID the stage is instantiated from.
    :ivar str topic: The topic of the stage.
    :ivar int privacy_level: The "privacy"/inclusive accessibility level of the stage.
    :ivar bool discoverable_disabled: Whether the stage can be seen from the stage discovery.
    """
    id: int
    guild_id: int
    channel_id: int
    topic: str
    privacy_level: int  # can be Enum'd
    discoverable_disabled: bool


class Guild(object):
    """The big Guild object."""

    id: int
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
