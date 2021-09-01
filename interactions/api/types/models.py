import datetime
from typing import Optional, Union, List

# TODO: Reorganise these models based on which big obj uses little obj
# TODO: Figure out ? placements.
# TODO: Potentially rename some model references to enums, if applicable

# 'Optional[datetime.datetime]` is the Timestamp, just a mini note
from interactions.api.types.enums import GuildFeature


class MessageActivity(object):
    __slots__ = ("type", "party_id")
    type: int
    party_id: Optional[str]


class MessageReference(object):
    __slots__ = ("message_id", "channel_id", "guild_id", "fail_if_not_exists")
    message_id: Optional[int]
    channel_id: Optional[int]
    guild_id: Optional[int]
    fail_if_not_exists: Optional[bool]


class ThreadMetadata(object):
    __slots__ = ("archived", "auto_archive_duration", "archive_timestamp", "locked", "invitable")
    archived: bool
    auto_archive_duration: int
    archive_timestamp: datetime.datetime.timestamp
    locked: bool
    invitable: Optional[bool]


class ThreadMember(object):
    __slots__ = ("id", "user_id", "join_timestamp", "flags")
    id: Optional[int]  # intents
    user_id: Optional[int]
    join_timestamp: datetime.datetime.timestamp
    flags: int


class User(object):
    __slots__ = (
        "id",
        "username",
        "discriminator",
        "avatar",
        "bot",
        "system",
        "mfa_enabled",
        "banner",
        "accent_color",
        "locale",
        "verified",
        "email",
        "flags",
        "premium_type",
        "public_flags",
    )
    id: int
    username: str
    discriminator: str
    avatar: Optional[str]
    bot: Optional[bool]
    system: Optional[bool]
    mfa_enabled: Optional[bool]
    banner: Optional[str]
    accent_color: Optional[int]
    locale: Optional[str]
    verified: Optional[bool]
    email: Optional[str]
    flags: int
    premium_type: int
    public_flags: int

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class Member(object):
    """
    Also, the guild member obj (Or partial.)

    The methodology, instead of regular d.py conventions
    is to do member.user to get the pure User object, instead of
    d.py's option of merging.
    """

    __slots__ = (
        "user",
        "nick",
        "roles",
        "joined_at",
        "premium_since",
        "deaf",
        "mute",
        "pending",
        "permissions",
    )

    user: Optional[User]
    nick: Optional[str]
    roles: List[int]
    joined_at: datetime.datetime.timestamp
    premium_since: Optional[datetime.datetime]
    deaf: bool
    mute: bool
    pending: Optional[bool]
    permissions: Optional[str]


class Overwrite(object):
    """This is used for the PermissionOverride obj"""

    __slots__ = ("id", "type", "allow", "deny")
    id: int
    type: int
    allow: str
    deny: str


class Channel(object):
    """
    The big Channel model.

    The purpose of this model is to be used as a base class, and
    is never needed to be used directly.
    """

    __slots__ = (
        "id",
        "type",
        "guild_id",
        "position",
        "permission_overwrites",
        "name",
        "topic",
        "nsfw",
        "last_message_id",
        "bitrate",
        "user_limit",
        "rate_limit_per_user",
        "recipients",
        "icon",
        "owner_id",
        "application_id",
        "parent_id",
        "last_pin_timestamp",
        "rtc_region",
        "video_quality_mode",
        "message_count",
        "member_count",
        "thread_metadata",
        "member",
        "default_auto_archive_duration",
        "permissions",
    )

    id: int  # "Snowflake"
    type: int
    guild_id: Optional[int]
    position: Optional[int]
    permission_overwrites: List[Overwrite]
    name: str  # This apparently exists in DMs. Untested in v9, known in v6
    topic: Optional[str]
    nsfw: Optional[bool]
    last_message_id: Optional[int]
    bitrate: Optional[int]  # not really needed in our case
    user_limit: Optional[int]
    rate_limit_per_user: Optional[int]
    recipients: Optional[List[User]]
    icon: Optional[str]
    owner_id: Optional[int]
    application_id: Optional[int]
    parent_id: Optional[int]
    last_pin_timestamp: Optional[datetime.datetime]
    rtc_region: Optional[str]
    video_quality_mode: Optional[int]
    message_count: Optional[int]
    member_count: Optional[int]
    thread_metadata: Optional[ThreadMetadata]
    member: Optional[ThreadMember]
    default_auto_archive_duration: Optional[int]
    permissions: Optional[str]

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class TextChannel(Channel):
    __slots__ = super().__slots__

    ...


class DMChannel(Channel):
    __slots__ = super().__slots__

    ...


class ThreadChannel(Channel):
    __slots__ = super().__slots__

    ...


class Attachment(object):
    __slots__ = ("id", "filename", "content_type", "size", "url", "proxy_url", "height", "width")

    id: int
    filename: str
    content_type: Optional[str]
    size: int
    url: str
    proxy_url: str
    height: Optional[int]
    width: Optional[int]


class MessageInteraction(object):
    id: int
    type: int  # replace with Enum
    name: str
    user: User


class TeamMember(object):
    membership_state: int
    permissions: List[str]
    team_id: int
    user: User


class Team(object):
    icon: Optional[str]
    id: int
    members: List[TeamMember]
    name: str
    owner_user_id: int


class Application(object):
    id: int
    name: str
    icon: Optional[str]
    description: str
    rpc_origins: Optional[List[str]]
    bot_public: bool
    bot_require_code_grant: bool
    terms_of_service_url: Optional[str]
    privacy_policy_url: Optional[str]
    owner: Optional[User]
    summary: str
    verify_key: str
    team: Optional[Team]
    guild_id: Optional[int]
    primary_sku_id: Optional[int]
    slug: Optional[str]
    cover_image: Optional[str]
    flags: Optional[int]


class Message(object):
    """
    The big Message model.

    The purpose of this model is to be used as a base class, and
    is never needed to be used directly.
    """

    id: int
    channel_id: int
    guild_id: Optional[int]
    author: User
    member: Optional[Member]
    content: str
    timestamp: datetime.datetime.timestamp
    edited_timestamp: Optional[datetime.datetime]
    tts: bool
    mention_everyone: bool
    # mentions: array of Users, and maybe partial members
    mentions: Optional[List[Union[Member, User]]]
    mention_roles: Optional[List[str]]
    mention_channels: Optional[List["ChannelMention"]]
    attachments: Optional[List[Attachment]]
    embeds: List['Embed']
    reactions: Optional[List["ReactionObject"]]
    nonce: Union[int, str]
    pinned: bool
    webhook_id: Optional[int]
    type: int
    activity: Optional[MessageActivity]
    application: Optional[Application]
    application_id: int
    message_reference: Optional[MessageReference]
    flags: int
    referenced_message: Optional["Message"]  # pycharm says it works, idk
    interaction: Optional[MessageInteraction]
    thread: Optional[Channel]

    # components (Flow's side)
    sticker_items: Optional[List['PartialSticker']]
    stickers: Optional[List['Sticker']]  # deprecated

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class Emoji(object):
    id: Optional[int]
    name: Optional[str]
    roles: Optional[List[str]]
    user: Optional[User]
    require_colons: Optional[bool]
    managed: Optional[bool]
    animated: Optional[bool]
    available: Optional[bool]

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class ReactionObject(object):
    count: int
    me: bool
    emoji: Emoji


class RoleTags(object):
    bot_id: Optional[int]
    integration_id: Optional[int]
    premium_subscriber: Optional[int]

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class Role(object):
    id: int
    name: str
    color: int
    hoist: bool
    position: int
    permissions: str
    managed: bool
    mentionable: bool
    tags: Optional[RoleTags]

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class ChannelMention(object):
    id: int
    guild_id: int
    type: int  # Replace with enum from Channel Type, another PR
    name: str


class _PresenceParty(object):
    id: Optional[str]
    size: Optional[List[int]]


class _PresenceAssets(object):
    large_image: Optional[str]
    large_text: Optional[str]
    small_image: Optional[str]
    small_text: Optional[str]


class _PresenceSecrets(object):
    join: Optional[str]
    spectate: Optional[str]
    match: Optional[str]


class _PresenceButtons(object):
    label: str
    url: str


class PresenceActivity(object):
    name: str
    type: int
    url: Optional[str]
    created_at: int
    timestamps: Optional[datetime.datetime]
    application_id: Optional[int]
    details: Optional[str]
    state: Optional[str]
    emoji: Optional[Emoji]
    party: Optional[_PresenceParty]
    assets: Optional[_PresenceAssets]
    secrets: Optional[_PresenceSecrets]
    instance: Optional[bool]
    flags: Optional[int]
    buttons: Optional[_PresenceButtons]


class ClientStatus(object):
    __slots__ = ("desktop", "mobile", "web")

    desktop: Optional[str]
    mobile: Optional[str]
    web: Optional[str]


class PresenceUpdate(object):
    user: User
    guild_id: int
    status: str
    activities: List[PresenceActivity]
    client_status: ClientStatus


class WelcomeChannels(object):
    channel_id: int
    description: str
    emoji_id: Optional[int]
    emoji_name: Optional[str]


class WelcomeScreen(object):
    description: Optional[str]
    welcome_channels: List[WelcomeChannels]


class StageInstance(object):
    id: int
    guild_id: int
    channel_id: int
    topic: str
    privacy_level: int  # can be Enum'd
    discoverable_disabled: bool


class PartialSticker(object):
    """Partial object for a Sticker."""
    id: int
    name: str
    format_type: int


class Sticker(PartialSticker):
    """The full Sticker object."""

    pack_id: Optional[int]
    description: Optional[str]
    tags: str
    asset: str  # deprecated
    type: int  # has its own dedicated enum
    available: Optional[bool]
    guild_id: Optional[int]
    user: Optional[User]
    sort_value: Optional[int]


class VoiceState(object):
    guild_id: Optional[int]
    channel_id: Optional[int]
    user_id: int
    member: Member
    session_id: str
    deaf: bool
    mute: bool
    self_deaf: bool
    self_mute: bool
    self_stream: Optional[bool]
    self_video: bool
    suppress: bool
    request_to_speak_timestamp: Optional[datetime.datetime]


class EmbedImageStruct(object):
    """This is the internal structure denoted for thumbnails, images or videos"""
    url: Optional[str]
    proxy_url: Optional[str]
    height: Optional[str]
    width: Optional[str]


class EmbedProvider(object):
    name: Optional[str]
    url: Optional[str]


class EmbedAuthor(object):
    name: Optional[str]
    url: Optional[str]
    icon_url: Optional[str]
    proxy_icon_url: Optional[str]


class EmbedFooter(object):
    text: Optional[str]
    icon_url: Optional[str]
    proxy_icon_url: Optional[str]


class EmbedField(object):
    name: str
    inline: Optional[bool]
    value: str


class Embed(object):
    title: Optional[str]
    type: Optional[str]
    description: Optional[str]
    url: Optional[str]
    timestamp: Optional[datetime.datetime]
    color: Optional[int]
    footer: Optional[EmbedFooter]
    image: Optional[EmbedImageStruct]
    thumbnail: Optional[EmbedImageStruct]
    video: Optional[EmbedImageStruct]
    provider: Optional[EmbedProvider]
    author: Optional[EmbedAuthor]
    fields: Optional[List[EmbedField]]


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
    joined_at: Optional[datetime.datetime]
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
