from enum import Enum

from .misc import DictSerializerMixin, Snowflake


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


class WelcomeChannels(DictSerializerMixin):
    """
    A class object representing a welcome channel on the welcome screen.

    .. note::
        ``emoji_id`` and ``emoji_name`` are given values respectively if the welcome channel
        uses an emoji.

    :ivar int channel_id: The ID of the welcome channel.
    :ivar str description: The description of the welcome channel.
    :ivar typing.Optional[int] emoji_id: The ID of the emoji of the welcome channel.
    :ivar typing.Optional[str] emoji_name: The name of the emoji of the welcome channel.
    """

    __slots__ = ("_json", "channel_id", "description", "emoji_id", "emoji_name")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.channel_id = Snowflake(self.channel_id) if self.channel_id else None
        self.emoji_id = Snowflake(self.emoji_id) if self.emoji_id else None


class WelcomeScreen(DictSerializerMixin):
    """
    A class object representing the welcome screen shown for community guilds.

    .. note::
        ``description`` is ambiguous -- Discord poorly documented this. :)

        We assume it's for the welcome screen topic.

    :ivar typing.Optional[str] description: The description of the welcome sceen.
    :ivar typing.List[interactions.api.models.guild.WelcomeChannels] welcome_channels: A list of welcome channels of the welcome screen.
    """

    __slots__ = ("_json", "description", "welcome_channels")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class StageInstance(DictSerializerMixin):
    """
    A class object representing an instace of a stage channel in a guild.

    :ivar int id: The ID of the stage.
    :ivar int guild_id: The guild ID the stage is in.
    :ivar int channel_id: The channel ID the stage is instantiated from.
    :ivar str topic: The topic of the stage.
    :ivar int privacy_level: The "privacy"/inclusive accessibility level of the stage.
    :ivar bool discoverable_disabled: Whether the stage can be seen from the stage discovery.
    """

    __slots__ = (
        "_json",
        "id",
        "guild_id",
        "channel_id",
        "topic",
        "privacy_level",
        "discoverable_disabled",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = Snowflake(self.id) if self._json.get("id") else None
        self.guild_id = Snowflake(self.guild_id) if self._json.get("guild_id") else None
        self.channel_id = Snowflake(self.channel_id) if self._json.get("channel_id") else None


class Guild(DictSerializerMixin):
    """
    A class object representing how a guild is registered.

    .. note::
        Most of these optionals are actually declared with their value
        upon instantiation but are kept like this since this class object
        is meant to be more broad and generalized.

    :ivar Snowflake id: The ID of the guild.
    :ivar str name: The name of the guild.
    :ivar typing.Optional[str] icon: The icon of the guild.
    :ivar typing.Optional[str] icon_hash: The hashed version of the icon of the guild.
    :ivar typing.Optional[str] splash: The invite splash banner of the guild.
    :ivar typing.Optional[str] discovery_splash: The discovery splash banner of the guild.
    :ivar typing.Optional[bool] owner: Whether the guild is owned.
    :ivar Snowflake owner_id: The ID of the owner of the guild.
    :ivar typing.Optional[str] permissions: The permissions of the guild.
    :ivar typing.Optional[str] region: The geographical region of the guild.
    :ivar typing.Optional[Snowflake] afk_channel_id: The AFK voice channel of the guild.
    :ivar int afk_timeout: The timeout of the AFK voice channel of the guild.
    :ivar typing.Optional[bool] widget_enabled: Whether widgets are enabled in the guild.
    :ivar typing.Optional[int] widget_channel_id: The channel ID of the widget in the guild.
    :ivar int verification_level: The level of user verification of the guild.
    :ivar int default_message_notifications: The default message notifications setting of the guild.
    :ivar int explicit_content_filter: The explicit content filter setting level of the guild.
    :ivar typing.List[interactions.api.models.role.Role] roles: The list of roles in the guild.
    :ivar typing.List[interactions.api.models.message.Emoji] emojis: The list of emojis from the guild.
    :ivar typing.List[interactions.api.models.guild.GuildFeature] features: The list of features of the guild.
    :ivar int mfa_level: The MFA level of the guild.
    :ivar typing.Optional[int] application_id: The application ID of the guild.
    :ivar typing.Optional[int] system_channel_id: The channel ID of the system of the guild.
    :ivar typing.Optional[int] rules_channel_id: The channel ID of Discord's defined "rules" channel of the guild.
    :ivar typing.Optional[datetime.datetime] joined_at: The timestamp the member joined the guild.
    :ivar typing.Optional[bool] large: Whether the guild is considered "large."
    :ivar typing.Optional[bool] unavailable: Whether the guild is unavailable to access.
    :ivar typing.Optional[int] member_count: The amount of members in the guild.
    :ivar typing.Optional[typing.List[interactions.api.models.presence.PresenceUpdate]] presences: The list of presences in the guild.
    :ivar typing.Optional[int] max_presences: The maximum amount of presences allowed in the guild.
    :ivar typing.Optional[int] max_members: The maximum amount of members allowed in the guild.
    :ivar typing.Optional[str] vanity_url_code: The vanity URL of the guild.
    :ivar typing.Optional[str] description: The description of the guild.
    :ivar typing.Optional[str] banner: The banner of the guild.
    :ivar int premium_tier: The server boost level of the guild.
    :ivar typing.Optional[int] premium_subscription_count: The amount of server boosters in the guild.
    :ivar str preferred_locale: The "preferred" local region of the guild.
    :ivar typing.Optional[int] public_updates_channel_id: The channel ID for community updates of the guild.
    :ivar typing.Optional[int] max_video_channel_users: The maximum amount of video streaming members in a channel allowed in a guild.
    :ivar typing.Optional[int] approximate_member_count: The approximate amount of members in the guild.
    :ivar typing.Optional[int] approximate_presence_count: The approximate amount of presences in the guild.
    :ivar typing.Optional[interactions.api.models.guild.WelcomeScreen] welcome_screen: The welcome screen of the guild.
    :ivar int nsfw_level: The NSFW safety filter level of the guild.
    :ivar typing.Optional[interactions.api.models.guild.StageInstance] stage_instances: The stage instance of the guild.
    :ivar typing.Optional[typing.List[interactions.api.models.message.Sticker]] stickers: The list of stickers from the guild.
    """

    __slots__ = (
        "_json",
        "id",
        "name",
        "icon",
        "icon_hash",
        "splash",
        "discovery_splash",
        "owner",
        "owner_id",
        "permissions",
        "region",
        "afk_channel_id",
        "afk_timeout",
        "widget_enabled",
        "widget_channel_id",
        "verification_level",
        "default_message_notifications",
        "explicit_content_filter",
        "roles",
        "emojis",
        "features",
        "mfa_level",
        "application_id",
        "system_channel_id",
        "system_channel_flags",
        "rules_channel_id",
        "joined_at",
        "large",
        "unavailable",
        "member_count",
        "voice_states",
        "members",
        "channels",
        "threads",
        "presences",
        "max_presences",
        "max_members",
        "vanity_url_code",
        "description",
        "banner",
        "premium_tier",
        "premium_subscription_count",
        "preferred_locale",
        "public_updates_channel_id",
        "max_video_channel_users",
        "approximate_member_count",
        "approximate_presence_count",
        "welcome_screen",
        "nsfw_level",
        "stage_instances",
        "stickers",
        # TODO: Investigate all of these once Discord has them all documented.
        "guild_hashes",
        "embedded_activities",
        "guild_scheduled_events",
        "nsfw",
        "application_command_count",
        "premium_progress_bar_enabled",
        "hub_type",
        "lazy",  # lol what?
        "application_command_counts",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = Snowflake(self.id) if self._json.get("id") else None
        self.owner_id = Snowflake(self.owner_id) if self._json.get("owner_id") else None
        self.afk_channel_id = (
            Snowflake(self.afk_channel_id) if self._json.get("afk_channel_id") else None
        )


class GuildPreview(DictSerializerMixin):
    """
    A model representing the preview of a guild.

    ..note::
        This refers to the documentation `here <https://discord.com/developers/docs/resources/guild>_`

    :ivar int id: The ID of the guild.
    :ivar str name: The name of the guild.
    :ivar typing.Optional[str] icon: The icon of the guild.
    :ivar typing.Optional[str] splash: The invite splash banner of the guild.
    :ivar typing.Optional[str] discovery_splash: The discovery splash banner of the guild.
    :ivar typing.List[interactions.api.models.message.Emoji] emojis: The list of emojis from the guild.
    :ivar typing.List[interactions.api.models.guild.GuildFeature] features: The list of features of the guild.
    :ivar int approximate_member_count: The approximate amount of members in the guild.
    :ivar int approximate_presence_count: The approximate amount of presences in the guild.
    :ivar typing.Optional[str] description: The description of the guild.
    """

    __slots__ = (
        "_json",
        "id",
        "name",
        "icon",
        "splash",
        "discovery_splash",
        "emoji",
        "features",
        "approximate_member_count",
        "approximate_presence_count",
        "description",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = Snowflake(self.id) if self._json.get("id") else None


class Integration(DictSerializerMixin):

    __slots__ = (
        "_json",
        "id",
        "name",
        "type",
        "enabled",
        "syncing",
        "role_id",
        "enable_emoticons",
        "expire_behavior",
        "expire_grace_period",
        "user",
        "account",
        "synced_at",
        "subscriber_count",
        "revoked",
        "application",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = Snowflake(self.id) if self._json.get("id") else None
        self.role_id = Snowflake(self.role_id) if self._json.get("role_id") else None


class Invite(DictSerializerMixin):
    """
    The invite object.

    :ivar int uses: The amount of uses on the invite.
    :ivar int max_uses: The amount of maximum uses on the invite.
    :ivar int max_age: The maximum age of this invite.
    :ivar bool temporary: A detection of whether this invite is temporary or not.
    :ivar datetime created_at: The time when this invite was created.
    """

    __slots__ = ("_json", "uses", "max_uses", "max_age", "temporary", "created_at")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class GuildTemplate(DictSerializerMixin):
    """
    An object representing the snapshot of an existing guild.

    :ivar str code: The code of the guild template.
    :ivar str name: The name of the guild template.
    :ivar typing.Optional[str] description: The description of the guild template, if given.
    :ivar int usage_count: The amount of uses on the template.
    :ivar int creator_id: User ID of the creator of this template.
    :ivar User creator: The User object of the creator of this template.
    :ivar datetime created_at: The time when this template was created.
    :ivar datetime created_at: The time when this template was updated.
    :ivar int source_guild_id: The Guild ID that the template sourced from.
    :ivar Guild serialized_source_guild: A partial Guild object from the sourced template.
    :ivar typing.Optional[bool] is_dirty: A status that denotes if the changes are unsynced.
    """

    __slots__ = (
        "_json",
        "code",
        "name",
        "description",
        "usage_count",
        "creator_id",
        "creator",
        "created_at",
        "updated_at",
        "source_guild_id",
        "serialized_source_guild",
        "is_dirty",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.creator_id = Snowflake(self.creator_id) if self._json.get("creator_id") else None
        self.source_guild_id = (
            Snowflake(self.source_guild_id) if self._json.get("source_guild_id") else None
        )


class EventMetadata(DictSerializerMixin):
    """
    The metadata of an event entity, if any.

    :ivar typing.Optional[str] location: The location of the event, if any.
    """

    __slots__ = ("_json", "location")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class ScheduledEvents(DictSerializerMixin):
    """
    The scheduled events object in a guild.

    ..note::
        Some attributes are optional via creator_id/creator implementation by the API:
        "`creator_id` will be null and `creator` will not be included for events created before October 25th, 2021, when the concept of `creator_id` was introduced and tracked."

    :ivar Snowflake id: The ID of the scheduled event.
    :ivar Snowflake guild_id: The ID of the guild that this scheduled event belongs to.
    :ivar typing.Optional[Snowflake] channel_id: The channel ID in wich the scheduled event belongs to, if any.
    :ivar typing.Optional[Snowflake] creator_id: The ID of the user that created the scheduled event.
    :ivar str name: The name of the scheduled event.
    :ivar str description: The description of the scheduled event.
    :ivar datetime scheduled_start_time: The scheduled event start time.
    :ivar typing.Optional[datetime] scheduled_end_time: The scheduled event end time, if any.
    :ivar int privacy_level: The privacy level of the scheduled event.
    :ivar int entity_type: The type of the scheduled event.
    :ivar typing.Optional[Snowflake] entity_id: The ID of the entity associated with the scheduled event.
    :ivar typing.Optional[EventMetadata] entity_metadata: Additional metadata associated with the scheduled event.
    :ivar typing.Optional[User] creator: The user that created the scheduled event.
    :ivar typing.Optional[int] user_count: The number of users subscribed to the scheduled event.
    """

    __slots__ = (
        "_json",
        "id",
        "guild_id",
        "channel_id",
        "creator_id",
        "name",
        "description",
        "scheduled_start_time",
        "scheduled_end_time",
        "privacy_level",
        "entity_type",
        "entity_id",
        "entity_metadata",
        "creator",
        "user_count",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = Snowflake(self.id) if self._json.get("id") else None
        self.channel_id = Snowflake(self.channel_id) if self._json.get("channel_id") else None
        self.creator_id = Snowflake(self.creator_id) if self._json.get("creator_id") else None
        self.entity_id = Snowflake(self.entity_id) if self._json.get("entity_id") else None
