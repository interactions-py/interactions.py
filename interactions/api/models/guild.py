from datetime import datetime
from typing import List, Optional, Union

from .message import Emoji, Sticker
from .misc import DictSerializerMixin, Snowflake
from .presence import PresenceActivity
from .role import Role
from .team import Application
from .user import User


class WelcomeChannels(DictSerializerMixin):
    """
    A class object representing a welcome channel on the welcome screen.

    .. note::
        ``emoji_id`` and ``emoji_name`` are given values respectively if the welcome channel
        uses an emoji.

    :ivar Snowflake channel_id: The ID of the welcome channel.
    :ivar str description: The description of the welcome channel.
    :ivar Optional[Snowflake] emoji_id?: The ID of the emoji of the welcome channel.
    :ivar Optional[str] emoji_name?: The name of the emoji of the welcome channel.
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

    :ivar Optional[str] description?: The description of the welcome sceen.
    :ivar List[WelcomeChannels] welcome_channels: A list of welcome channels of the welcome screen.
    """

    __slots__ = ("_json", "description", "welcome_channels")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.welcome_channels = (
            [WelcomeChannels(**welcome_channel) for welcome_channel in self.welcome_channels]
            if self.welcome_channels
            else None
        )


class StageInstance(DictSerializerMixin):
    """
    A class object representing an instace of a stage channel in a guild.

    :ivar Snowflake id: The ID of the stage.
    :ivar Snowflake guild_id: The guild ID the stage is in.
    :ivar Snowflake channel_id: The channel ID the stage is instantiated from.
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
    :ivar Optional[str] icon?: The icon of the guild.
    :ivar Optional[str] icon_hash?: The hashed version of the icon of the guild.
    :ivar Optional[str] splash?: The invite splash banner of the guild.
    :ivar Optional[str] discovery_splash?: The discovery splash banner of the guild.
    :ivar Optional[bool] owner?: Whether the guild is owned.
    :ivar Snowflake owner_id: The ID of the owner of the guild.
    :ivar Optional[str] permissions?: The permissions of the guild.
    :ivar Optional[str] region?: The geographical region of the guild.
    :ivar Optional[Snowflake] afk_channel_id?: The AFK voice channel of the guild.
    :ivar int afk_timeout: The timeout of the AFK voice channel of the guild.
    :ivar Optional[bool] widget_enabled?: Whether widgets are enabled in the guild.
    :ivar Optional[Snowflake] widget_channel_id?: The channel ID of the widget in the guild.
    :ivar int verification_level: The level of user verification of the guild.
    :ivar int default_message_notifications: The default message notifications setting of the guild.
    :ivar int explicit_content_filter: The explicit content filter setting level of the guild.
    :ivar List[Role] roles: The list of roles in the guild.
    :ivar List[Emoji] emojis: The list of emojis from the guild.
    :ivar List[GuildFeature] features: The list of features of the guild.
    :ivar int mfa_level: The MFA level of the guild.
    :ivar Optional[Snowflake] application_id?: The application ID of the guild.
    :ivar Optional[Snowflake] system_channel_id?: The channel ID of the system of the guild.
    :ivar Optional[Snowflake] rules_channel_id?: The channel ID of Discord's defined "rules" channel of the guild.
    :ivar Optional[datetime] joined_at?: The timestamp the member joined the guild.
    :ivar Optional[bool] large?: Whether the guild is considered "large."
    :ivar Optional[bool] unavailable?: Whether the guild is unavailable to access.
    :ivar Optional[int] member_count?: The amount of members in the guild.
    :ivar Optional[List[PresenceUpdate]] presences?: The list of presences in the guild.
    :ivar Optional[int] max_presences?: The maximum amount of presences allowed in the guild.
    :ivar Optional[int] max_members?: The maximum amount of members allowed in the guild.
    :ivar Optional[str] vanity_url_code?: The vanity URL of the guild.
    :ivar Optional[str] description?: The description of the guild.
    :ivar Optional[str] banner?: The banner of the guild.
    :ivar int premium_tier: The server boost level of the guild.
    :ivar Optional[int] premium_subscription_count?: The amount of server boosters in the guild.
    :ivar str preferred_locale: The "preferred" local region of the guild.
    :ivar Optional[Snowflake] public_updates_channel_id?: The channel ID for community updates of the guild.
    :ivar Optional[int] max_video_channel_users?: The maximum amount of video streaming members in a channel allowed in a guild.
    :ivar Optional[int] approximate_member_count?: The approximate amount of members in the guild.
    :ivar Optional[int] approximate_presence_count?: The approximate amount of presences in the guild.
    :ivar Optional[WelcomeScreen] welcome_screen?: The welcome screen of the guild.
    :ivar int nsfw_level: The NSFW safety filter level of the guild.
    :ivar Optional[List[StageInstance]] stage_instances?: The stage instance of the guild.
    :ivar Optional[List[Sticker]] stickers?: The list of stickers from the guild.
    """

    __slots__ = (
        "_json",
        "id",
        "_client",
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
        # TODO: post-v4: Investigate all of these once Discord has them all documented.
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
        self.emojis = (
            [Emoji(**emoji) for emoji in self.emojis] if self._json.get("emojis") else None
        )
        self.joined_at = (
            datetime.fromisoformat(self._json.get("joined_at"))
            if self._json.get("joined_at")
            else None
        )
        self.presences = (
            [PresenceActivity(**presence) for presence in self.presences]
            if self._json.get("presences")
            else None
        )
        self.welcome_screen = (
            WelcomeScreen(**self.welcome_screen) if self._json.get("welcome_screen") else None
        )
        self.stage_instances = (
            [StageInstance(**stage_instance) for stage_instance in self.stage_instances]
            if self._json.get("stage_instances")
            else None
        )
        self.stickers = (
            [Sticker(**sticker) for sticker in self.stickers]
            if self._json.get("stickers")
            else None
        )

    async def ban(
        self,
        member_id: int,
        reason: Optional[str] = None,
        delete_message_days: Optional[int] = 0,
    ) -> None:
        """
        Bans a member from the guild
        :param member_id: The id of the member to ban
        :type member_id: int
        :param reason?: The reason of the ban
        :type reason: Optional[str]
        :param delete_message_days?: Number of days to delete messages, from 0 to 7. Defaults to 0
        :type delete_message_days: Optional[int]
        """
        await self._client.create_guild_ban(
            guild_id=int(self.id),
            user_id=member_id,
            reason=reason,
            delete_message_days=delete_message_days,
        )

    async def remove_ban(
        self,
        user_id: int,
        reason: Optional[str] = None,
    ) -> None:
        """
        Removes the ban of a user
        :param user_id: The id of the user to remove the ban from
        :type user_id: int
        :param reason?: The reason for the removal of the ban
        :type reason: Optional[str]
        """
        await self._client.remove_guild_ban(
            guild_id=int(self.id),
            user_id=user_id,
            reason=reason,
        )

    async def kick(
        self,
        member_id: int,
        reason: Optional[str] = None,
    ) -> None:
        """
        Kicks a member from the guild
        :param member_id: The id of the member to kick
        :type member_id: int
        :param reason?: The reason for the kick
        :type reason: Optional[str]
        """
        await self._client.create_guild_kick(
            guild_id=int(self.id),
            user_id=member_id,
            reason=reason,
        )

    async def add_member_roles(
        self,
        roles: Union[List[Union[Role, int]], Role, int],
        member_id: int,
        reason: Optional[str],
    ) -> None:
        """
        This method adds a or multiple role(s) to a member
        :param roles: The role(s) to add. Either ``Role`` object or role_id
        :type roles: Union[List[Union[Role, int]], Role, int]
        :param member_id: The id of the member to add the roles to
        :type member_id: int
        :param reason: The reason why the roles are added
        :type reason: Optional[str]
        """
        if isinstance(roles, list):
            roles = [int(role.id) if isinstance(role, Role) else role for role in roles]
            for role in roles:
                await self.client.add_member_role(
                    guild_id=int(self.id),
                    user_id=member_id,
                    role_id=role,
                    reason=reason,
                )
        elif isinstance(roles, Role):
            await self._client.add_member_role(
                guild_id=int(self.id),
                user_id=member_id,
                role_id=int(roles.id),
                reason=reason,
            )
        else:
            await self._client.add_member_role(
                guild_id=int(self.id),
                user_id=member_id,
                role_id=roles,
                reason=reason,
            )

    async def remove_member_roles(
        self,
        roles: Union[List[Role], Role, int],
        member_id: int,
        reason: Optional[str],
    ) -> None:
        """
        This method removes a or multiple role(s) from a member
        :param roles: The role(s) to remove. Either ``Role`` object or role_id
        :type roles: Union[List[Union[Role, int]], Role, int]
        :param member_id: The id of the member to remove the roles from
        :type member_id: int
        :param reason: The reason why the roles are removed
        :type reason: Optional[str]
        """
        if isinstance(roles, list):
            roles = [int(role.id) if isinstance(role, Role) else role for role in roles]
            for role in roles:
                await self._client.remove_member_role(
                    guild_id=int(self.id),
                    user_id=member_id,
                    role_id=role,
                    reason=reason,
                )
        elif isinstance(roles, Role):
            await self._client.remove_member_role(
                guild_id=int(self.id),
                user_id=member_id,
                role_id=int(roles.id),
                reason=reason,
            )
        else:
            await self.client.remove_member_role(
                guild_id=int(self.id),
                user_id=member_id,
                role_id=roles,
                reason=reason,
            )

    # TODO: role create, channel create, get_member, delete role


class GuildPreview(DictSerializerMixin):
    """
    A class object representing the preview of a guild.

    :ivar Snowflake id: The ID of the guild.
    :ivar str name: The name of the guild.
    :ivar Optional[str] icon?: The icon of the guild.
    :ivar Optional[str] splash?: The invite splash banner of the guild.
    :ivar Optional[str] discovery_splash?: The discovery splash banner of the guild.
    :ivar List[Emoji] emojis: The list of emojis from the guild.
    :ivar List[GuildFeature] features: The list of features of the guild.
    :ivar int approximate_member_count: The approximate amount of members in the guild.
    :ivar int approximate_presence_count: The approximate amount of presences in the guild.
    :ivar Optional[str] description?: The description of the guild.
    """

    __slots__ = (
        "_json",
        "id",
        "name",
        "icon",
        "splash",
        "discovery_splash",
        "emojis",
        "features",
        "approximate_member_count",
        "approximate_presence_count",
        "description",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = Snowflake(self.id) if self._json.get("id") else None
        self.emojis = (
            [Emoji(**emoji) for emoji in self.emojis] if self._json.get("emojis") else None
        )


class Integration(DictSerializerMixin):
    """
    A class object representing an integration in a guild.

    :ivar Snowflake id: The ID of the integration.
    :ivar str name: The name of the integration.
    :ivar str type: The type of integration.
    :ivar bool enabled: Whether the integration is enabled or not.
    :ivar bool syncing: Whether the integration is syncing or not.
    :ivar Snowflake role_id: The role ID that the integration uses for "subscribed" users.
    :ivar bool enable_emoticons: Whether emoticons should be enabled or not.
    :ivar int expire_behavior: The expiration behavior of the integration.
    :ivar int expire_grace_period: The "grace period" of the integration when expired -- how long it can still be used.
    :ivar User user: The user of the integration.
    :ivar Any account: The account of the integration.
    :ivar datetime synced_at: The time that the integration was last synced.
    :ivar int subscriber_count: The current subscriber count of the integration.
    :ivar bool revoked: Whether the integration was revoked for use or not.
    :ivar Application application: The application used for the integration.
    """

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
        self.user = User(**self.user) if self._json.get("user") else None
        # TODO: Create an "Integration account" data model. It's missing apparently?
        self.application = (
            Application(**self.application) if self._json.get("application") else None
        )


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
        self.created_at = (
            datetime.fromisoformat(self._json.get("created_at"))
            if self._json.get("created_at")
            else None
        )


class GuildTemplate(DictSerializerMixin):
    """
    An object representing the snapshot of an existing guild.

    :ivar str code: The code of the guild template.
    :ivar str name: The name of the guild template.
    :ivar Optional[str] description?: The description of the guild template, if given.
    :ivar int usage_count: The amount of uses on the template.
    :ivar Snowflake creator_id: User ID of the creator of this template.
    :ivar User creator: The User object of the creator of this template.
    :ivar datetime created_at: The time when this template was created.
    :ivar datetime created_at: The time when this template was updated.
    :ivar Snowflake source_guild_id: The Guild ID that the template sourced from.
    :ivar Guild serialized_source_guild: A partial Guild object from the sourced template.
    :ivar Optional[bool] is_dirty?: A status that denotes if the changes are unsynced.
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
        self.user = User(**self.user) if self._json.get("user") else None
        self.serialized_source_guild = (
            Guild(**self.serialized_source_guild)
            if self._json.get("serialized_source_guild")
            else None
        )


class EventMetadata(DictSerializerMixin):
    """
    A class object representing the metadata of an event entity.

    :ivar Optional[str] location?: The location of the event, if any.
    """

    __slots__ = ("_json", "location")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class ScheduledEvents(DictSerializerMixin):
    """
    A class object representing the scheduled events of a guild.

    .. note::
        Some attributes are optional via creator_id/creator implementation by the API:
        "`creator_id` will be null and `creator` will not be included for events created before October 25th, 2021, when the concept of `creator_id` was introduced and tracked."

    :ivar Snowflake id: The ID of the scheduled event.
    :ivar Snowflake guild_id: The ID of the guild that this scheduled event belongs to.
    :ivar Optional[Snowflake] channel_id?: The channel ID in wich the scheduled event belongs to, if any.
    :ivar Optional[Snowflake] creator_id?: The ID of the user that created the scheduled event.
    :ivar str name: The name of the scheduled event.
    :ivar str description: The description of the scheduled event.
    :ivar datetime scheduled_start_time?: The scheduled event start time.
    :ivar Optional[datetime] scheduled_end_time?: The scheduled event end time, if any.
    :ivar int privacy_level: The privacy level of the scheduled event.
    :ivar int entity_type: The type of the scheduled event.
    :ivar Optional[Snowflake] entity_id?: The ID of the entity associated with the scheduled event.
    :ivar Optional[EventMetadata] entity_metadata?: Additional metadata associated with the scheduled event.
    :ivar Optional[User] creator?: The user that created the scheduled event.
    :ivar Optional[int] user_count?: The number of users subscribed to the scheduled event.
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
        self.guild_id = Snowflake(self.guild_id) if self._json.get("guild_id") else None
        self.channel_id = Snowflake(self.channel_id) if self._json.get("channel_id") else None
        self.creator_id = Snowflake(self.creator_id) if self._json.get("creator_id") else None
        self.entity_id = Snowflake(self.entity_id) if self._json.get("entity_id") else None
        self.scheduled_start_time = (
            datetime.fromisoformat(self._json.get("scheduled_start_time"))
            if self._json.get("scheduled_start_time")
            else None
        )
        self.scheduled_end_time = (
            datetime.fromisoformat(self._json.get("scheduled_end_time"))
            if self._json.get("scheduled_end_time")
            else None
        )
        self.entity_metadata = (
            EventMetadata(**self.entity_metadata) if self._json.get("entity_metadata") else None
        )
        self.creator = User(**self.creator) if self._json.get("creator") else None
