from datetime import datetime
from enum import IntEnum
from typing import List, Optional, Union

from .channel import Channel, ChannelType
from .member import Member
from .message import Emoji, Sticker
from .misc import DictSerializerMixin, Snowflake
from .presence import PresenceActivity
from .role import Role
from .team import Application
from .user import User


class VerificationLevel(IntEnum):
    """An enumerable object representing the verification level of a guild."""

    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    VERY_HIGH = 4


class ExplicitContentFilterLevel(IntEnum):
    """An enumerable object representing the explicit content filter level of a guild."""

    DISABLED = 0
    MEMBERS_WITHOUT_ROLES = 1
    ALL_MEMBERS = 2


class DefaultMessageNotificationLevel(IntEnum):
    """An enumerable object representing the default message notification level of a guild."""

    ALL_MESSAGES = 0
    ONLY_MENTIONS = 1


class EntityType(IntEnum):
    """An enumerable object representing the type of event."""

    STAGE_INSTANCE = 1
    VOICE = 2
    EXTERNAL = 3


class EventStatus(IntEnum):
    """An enumerable object representing the status of an event."""

    SCHEDULED = 1
    ACTIVE = 2
    COMPLETED = 3
    CANCELED = 4


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

    :ivar Optional[str] description?: The description of the welcome screen.
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
    A class object representing an instance of a stage channel in a guild.

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
    :ivar Optional[List[Member]] members?: The members in the guild.
    :ivar Optional[List[Channel]] channels?: The channels in the guild.
    :ivar Optional[List[Thread]] threads?: All known threads in the guild.
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
        self.members = (
            [Member(**member, _client=self._client) for member in self.members]
            if self._json.get("members")
            else None
        )
        if not self.members and self._client:

            if (
                not len(self._client.cache.self_guilds.view) > 1
                or not self._client.cache.self_guilds.values[str(self.id)].members
            ):
                pass
            else:
                members = self._client.cache.self_guilds.values[str(self.id)].members
                if all(isinstance(member, Member) for member in members):
                    self.members = members
                else:
                    self.members = [Member(**member, _client=self._client) for member in members]

    async def ban(
        self,
        member_id: int,
        reason: Optional[str] = None,
        delete_message_days: Optional[int] = 0,
    ) -> None:
        """
        Bans a member from the guild.

        :param member_id: The id of the member to ban
        :type member_id: int
        :param reason?: The reason of the ban
        :type reason: Optional[str]
        :param delete_message_days?: Number of days to delete messages, from 0 to 7. Defaults to 0
        :type delete_message_days: Optional[int]
        """
        if not self._client:
            raise AttributeError("HTTPClient not found!")
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
        Removes the ban of a user.

        :param user_id: The id of the user to remove the ban from
        :type user_id: int
        :param reason?: The reason for the removal of the ban
        :type reason: Optional[str]
        """
        if not self._client:
            raise AttributeError("HTTPClient not found!")
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
        Kicks a member from the guild.

        :param member_id: The id of the member to kick
        :type member_id: int
        :param reason?: The reason for the kick
        :type reason: Optional[str]
        """
        if not self._client:
            raise AttributeError("HTTPClient not found!")
        await self._client.create_guild_kick(
            guild_id=int(self.id),
            user_id=member_id,
            reason=reason,
        )

    async def add_member_role(
        self,
        role: Union[Role, int],
        member_id: int,
        reason: Optional[str],
    ) -> None:
        """
        This method adds a role to a member.

        :param role: The role to add. Either ``Role`` object or role_id
        :type role Union[Role, int]
        :param member_id: The id of the member to add the roles to
        :type member_id: int
        :param reason?: The reason why the roles are added
        :type reason: Optional[str]
        """
        if not self._client:
            raise AttributeError("HTTPClient not found!")
        if isinstance(role, Role):
            await self._client.add_member_role(
                guild_id=int(self.id),
                user_id=member_id,
                role_id=int(role.id),
                reason=reason,
            )
        else:
            await self._client.add_member_role(
                guild_id=int(self.id),
                user_id=member_id,
                role_id=role,
                reason=reason,
            )

    async def remove_member_role(
        self,
        role: Union[Role, int],
        member_id: int,
        reason: Optional[str],
    ) -> None:
        """
        This method removes a or multiple role(s) from a member.

        :param role: The role to remove. Either ``Role`` object or role_id
        :type role: Union[Role, int]
        :param member_id: The id of the member to remove the roles from
        :type member_id: int
        :param reason?: The reason why the roles are removed
        :type reason: Optional[str]
        """
        if not self._client:
            raise AttributeError("HTTPClient not found!")
        if isinstance(role, Role):
            await self._client.remove_member_role(
                guild_id=int(self.id),
                user_id=member_id,
                role_id=int(role.id),
                reason=reason,
            )
        else:
            await self._client.remove_member_role(
                guild_id=int(self.id),
                user_id=member_id,
                role_id=role,
                reason=reason,
            )

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
    ) -> Role:
        """
        Creates a new role in the guild.

        :param name: The name of the role
        :type name: str
        :param color?: RGB color value as integer, default ``0``
        :type color: Optional[int]
        :param hoist?: Whether the role should be displayed separately in the sidebar, default ``False``
        :type hoist: Optional[bool]
        :param mentionable?: Whether the role should be mentionable, default ``False``
        :type mentionable: Optional[bool]
        :param reason?: The reason why the role is created, default ``None``
        :type reason: Optional[str]
        :return: The created Role
        :rtype: Role
        """
        if not self._client:
            raise AttributeError("HTTPClient not found!")
        payload = Role(
            name=name,
            color=color,
            hoist=hoist,
            mentionable=mentionable,
        )
        res = await self._client.create_guild_role(
            guild_id=int(self.id),
            reason=reason,
            data=payload._json,
        )
        return Role(**res, _client=self._client)

    async def get_member(
        self,
        member_id: int,
    ) -> Member:
        """
        Searches for the member with specified id in the guild and returns the member as member object.

        :param member_id: The id of the member to search for
        :type member_id: int
        :return: The member searched for
        :rtype: Member
        """
        if not self._client:
            raise AttributeError("HTTPClient not found!")
        res = await self._client.get_member(
            guild_id=int(self.id),
            member_id=member_id,
        )
        return Member(**res, _client=self._client)

    async def delete_channel(
        self,
        channel_id: int,
    ) -> None:
        """
        Deletes a channel from the guild.

        :param channel_id: The id of the channel to delete
        :type channel_id: int
        """
        if not self._client:
            raise AttributeError("HTTPClient not found!")
        await self._client.delete_channel(
            channel_id=channel_id,
        )

    async def delete_role(
        self,
        role_id: int,
        reason: Optional[str] = None,
    ) -> None:
        """
        Deletes a role from the guild.

        :param role_id: The id of the role to delete
        :type role_id: int
        :param reason?: The reason of the deletion
        :type reason: Optional[str]
        """
        if not self._client:
            raise AttributeError("HTTPClient not found!")
        await self._client.delete_guild_role(
            guild_id=int(self.id),
            role_id=role_id,
            reason=reason,
        )

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
    ) -> Role:
        """
        Edits a role in the guild.

        :param role_id: The id of the role to edit
        :type role_id: int
        :param name?: The name of the role, defaults to the current value of the role
        :type name: Optional[str]
        :param color?: RGB color value as integer, defaults to the current value of the role
        :type color: Optional[int]
        :param hoist?: Whether the role should be displayed separately in the sidebar, defaults to the current value of the role
        :type hoist: Optional[bool]
        :param mentionable?: Whether the role should be mentionable, defaults to the current value of the role
        :type mentionable: Optional[bool]
        :param reason?: The reason why the role is edited, default ``None``
        :type reason: Optional[str]
        :return: The modified role object
        :rtype: Role
        """
        if not self._client:
            raise AttributeError("HTTPClient not found!")
        roles = await self._client.get_all_roles(guild_id=int(self.id))
        for i in roles:
            if int(i["id"]) == role_id:
                role = Role(**i)
                break
        _name = role.name if not name else name
        _color = role.color if not color else color
        _hoist = role.hoist if not hoist else hoist
        _mentionable = role.mentionable if mentionable is None else mentionable

        payload = Role(name=_name, color=_color, hoist=_hoist, mentionable=_mentionable)

        res = await self._client.modify_guild_role(
            guild_id=int(self.id),
            role_id=role_id,
            data=payload._json,
            reason=reason,
        )
        return Role(**res, _client=self._client)

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
        reason: Optional[str] = None,
    ) -> Channel:
        """
        Creates a channel in the guild.

        :param name: The name of the channel
        :type name: str
        :param type: The type of the channel
        :type type: ChannelType
        :param topic?: The topic of that channel
        :type topic: Optional[str]
        :param bitrate?: (voice channel only) The bitrate (in bits) of the voice channel
        :type bitrate Optional[int]
        :param user_limit?: (voice channel only) Maximum amount of users in the channel
        :type user_limit: Optional[int]
        :param rate_limit_per_use?: Amount of seconds a user has to wait before sending another message (0-21600)
        :type rate_limit_per_user: Optional[int]
        :param position?: Sorting position of the channel
        :type position: Optional[int]
        :param parent_id?: The id of the parent category for a channel
        :type parent_id: Optional[int]
        :param nsfw?: Whether the channel is nsfw or not, default ``False``
        :type nsfw: Optional[bool]
        :param reason: The reason for the creation
        :type reason: Optional[str]
        :return: The created channel
        :rtype: Channel
        """
        if not self._client:
            raise AttributeError("HTTPClient not found!")
        if type in [
            ChannelType.DM,
            ChannelType.DM.value,
            ChannelType.GROUP_DM,
            ChannelType.GROUP_DM.value,
        ]:
            raise ValueError(
                "ChannelType must not be a direct-message when creating Guild Channels!"  # TODO: move to custom error formatter
            )

        payload = Channel(
            name=name,
            type=type,
            topic=topic,
            bitrate=bitrate,
            user_limit=user_limit,
            rate_limit_per_user=rate_limit_per_user,
            position=position,
            parent_id=parent_id,
            nsfw=nsfw,
        )

        res = await self._client.create_channel(
            guild_id=int(self.id),
            reason=reason,
            payload=payload._json,
        )

        return Channel(**res, _client=self._client)

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
        reason: Optional[str] = None,
    ) -> Channel:
        """
        Edits a channel of the guild.

        :param channel_id: The id of the channel to modify
        :type channel_id: int
        :param name?: The name of the channel, defaults to the current value of the channel
        :type name: str
        :param topic?: The topic of that channel, defaults to the current value of the channel
        :type topic: Optional[str]
        :param bitrate?: (voice channel only) The bitrate (in bits) of the voice channel, defaults to the current value of the channel
        :type bitrate Optional[int]
        :param user_limit?: (voice channel only) Maximum amount of users in the channel, defaults to the current value of the channel
        :type user_limit: Optional[int]
        :param rate_limit_per_use?: Amount of seconds a user has to wait before sending another message (0-21600), defaults to the current value of the channel
        :type rate_limit_per_user: Optional[int]
        :param position?: Sorting position of the channel, defaults to the current value of the channel
        :type position: Optional[int]
        :param parent_id?: The id of the parent category for a channel, defaults to the current value of the channel
        :type parent_id: Optional[int]
        :param nsfw?: Whether the channel is nsfw or not, defaults to the current value of the channel
        :type nsfw: Optional[bool]
        :param reason: The reason for the edit
        :type reason: Optional[str]
        :return: The modified channel
        :rtype: Channel
        """
        if not self._client:
            raise AttributeError("HTTPClient not found!")
        ch = Channel(**await self._client.get_channel(channel_id=channel_id))

        _name = ch.name if not name else name
        _topic = ch.topic if not topic else topic
        _bitrate = ch.bitrate if not bitrate else bitrate
        _user_limit = ch.user_limit if not user_limit else user_limit
        _rate_limit_per_user = (
            ch.rate_limit_per_user if not rate_limit_per_user else rate_limit_per_user
        )
        _position = ch.position if not position else position
        _parent_id = ch.parent_id if not parent_id else parent_id
        _nsfw = ch.nsfw if not nsfw else nsfw
        _type = ch.type

        payload = Channel(
            name=_name,
            type=_type,
            topic=_topic,
            bitrate=_bitrate,
            user_limit=_user_limit,
            rate_limit_per_user=_rate_limit_per_user,
            position=_position,
            parent_id=_parent_id,
            nsfw=_nsfw,
        )

        res = await self._client.modify_channel(
            channel_id=channel_id,
            reason=reason,
            data=payload._json,
        )
        return Channel(**res, _client=self._client)

    async def modify_member(
        self,
        member_id: int,
        nick: Optional[str] = None,
        roles: Optional[List[int]] = None,
        mute: Optional[bool] = None,
        deaf: Optional[bool] = None,
        channel_id: Optional[int] = None,
        communication_disabled_until: Optional[datetime.isoformat] = None,
        reason: Optional[str] = None,
    ) -> Member:
        """
        Modifies a member of the guild.

        :param member_id: The id of the member to modify
        :type member_id: int
        :param nick?: The nickname of the member
        :type nick: Optional[str]
        :param roles?: A list of all role ids the member has
        :type roles: Optional[List[int]]
        :param mute?: whether the user is muted in voice channels
        :type mute: Optional[bool]
        :param deaf?: whether the user is deafened in voice channels
        :type deaf: Optional[bool]
        :param channel_id?: id of channel to move user to (if they are connected to voice)
        :type channel_id: Optional[int]
        :param communication_disabled_until?: when the user's timeout will expire and the user will be able to communicate in the guild again (up to 28 days in the future)
        :type communication_disabled_until: Optional[datetime.isoformat]
        :param reason?: The reason of the modifying
        :type reason: Optional[str]
        :return: The modified member
        :rtype: Member
        """
        if not self._client:
            raise AttributeError("HTTPClient not found!")
        payload = {}
        if nick:
            payload["nick"] = nick

        if roles:
            payload["roles"] = roles

        if channel_id:
            payload["channel_id"] = channel_id

        if mute:
            payload["mute"] = mute

        if deaf:
            payload["deaf"] = deaf

        if communication_disabled_until:
            payload["communication_disabled_until"] = communication_disabled_until

        res = await self._client.modify_member(
            user_id=member_id,
            guild_id=int(self.id),
            payload=payload,
            reason=reason,
        )
        return Member(**res, _client=self._client)

    async def get_preview(self) -> "GuildPreview":

        """
        Get the guild's preview.

        :return: the guild preview as object
        :rtype: GuildPreview
        """

        if not self._client:
            raise AttributeError("HTTPClient not found!")

        return GuildPreview(**await self._client.get_guild_preview(guild_id=int(self.id)))

    async def leave(self) -> None:
        """Removes the bot from the guild."""
        if not self._client:
            raise AttributeError("HTTPClient not found!")
        await self._client.leave_guild(guild_id=int(self.id))

    async def modify(
        self,
        name: Optional[str] = None,
        verification_level: Optional[VerificationLevel] = None,
        default_message_notifications: Optional[DefaultMessageNotificationLevel] = None,
        explicit_content_filter: Optional[ExplicitContentFilterLevel] = None,
        afk_channel_id: Optional[int] = None,
        afk_timeout: Optional[int] = None,
        # icon, TODO: implement images
        owner_id: Optional[int] = None,
        # splash, TODO: implement images
        # discovery_splash, TODO: implement images
        # banner, TODO: implement images
        system_channel_id: Optional[int] = None,
        suppress_join_notifications: Optional[bool] = None,
        suppress_premium_subscriptions: Optional[bool] = None,
        suppress_guild_reminder_notifications: Optional[bool] = None,
        suppress_join_notification_replies: Optional[bool] = None,
        rules_channel_id: Optional[int] = None,
        public_updates_channel_id: Optional[int] = None,
        preferred_locale: Optional[str] = None,
        description: Optional[str] = None,
        premium_progress_bar_enabled: Optional[bool] = None,
        reason: Optional[str] = None,
    ) -> "Guild":
        """
        Modifies the current guild.

        :param name?: The new name of the guild
        :type name: Optional[str]
        :param verification_level?: The verification level of the guild
        :type verification_level: Optional[VerificationLevel]
        :param default_message_notifications?: The default message notification level for members
        :type default_message_notifications: Optional[DefaultMessageNotificationLevel]
        :param explicit_content_filter?: The explicit content filter level for media content
        :type explicit_content_filter: Optional[ExplicitContentFilterLevel]
        :param afk_channel_id?: The id for the afk voice channel
        :type afk_channel_id: Optional[int]
        :param afk_timeout?: Afk timeout in seconds
        :type afk_timeout: Optional[int]
        :param owner_id?: The id of the user to transfer the guild ownership to. You must be the owner to perform this
        :type owner_id: Optional[int]
        :param system_channel_id?: The id of the channel where guild notices such as welcome messages and boost events are posted
        :type system_channel_id: Optional[int]
        :param suppress_join_notifications?: Whether to suppress member join notifications in the system channel or not
        :type suppress_join_notifications: Optional[bool]
        :param suppress_premium_subscriptions?: Whether to suppress server boost notifications in the system channel or not
        :type suppress_premium_subscriptions: Optional[bool]
        :param suppress_guild_reminder_notifications?: Whether to suppress server setup tips in the system channel or not
        :type suppress_guild_reminder_notifications: Optional[bool]
        :param suppress_join_notification_replies?: Whether to hide member join sticker reply buttons in the system channel or not
        :type suppress_join_notification_replies: Optional[bool]
        :param rules_channel_id?: The id of the channel where guilds display rules and/or guidelines
        :type rules_channel_id: Optional[int]
        :param public_updates_channel_id?: The id of the channel where admins and moderators of community guilds receive notices from Discord
        :type public_updates_channel_id: Optional[int]
        :param preferred_locale?: The preferred locale of a community guild used in server discovery and notices from Discord; defaults to "en-US"
        :type preferred_locale: Optional[str]
        :param description?: The description for the guild, if the guild is discoverable
        :type description: Optional[str]
        :param premium_progress_bar_enabled?: Whether the guild's boost progress bar is enabled
        :type premium_progress_bar_enabled: Optional[bool]
        :param reason?: The reason for the modifying
        :type reason: Optional[str]
        :return: The modified guild
        :rtype: Guild
        """
        if not self._client:
            raise AttributeError("HTTPClient not found!")
        if (
            suppress_join_notifications is None
            and suppress_premium_subscriptions is None
            and suppress_guild_reminder_notifications is None
            and suppress_join_notification_replies is None
        ):
            system_channel_flags = None
        else:
            _suppress_join_notifications = (1 << 0) if suppress_join_notifications else 0
            _suppress_premium_subscriptions = (1 << 1) if suppress_premium_subscriptions else 0
            _suppress_guild_reminder_notifications = (
                (1 << 2) if suppress_guild_reminder_notifications else 0
            )
            _suppress_join_notification_replies = (
                (1 << 3) if suppress_join_notification_replies else 0
            )
            system_channel_flags = (
                _suppress_join_notifications
                | _suppress_premium_subscriptions
                | _suppress_guild_reminder_notifications
                | _suppress_join_notification_replies
            )

        payload = {}

        if name:
            payload["name"] = name
        if verification_level:
            payload["verification_level"] = verification_level.value
        if default_message_notifications:
            payload["default_message_notifications"] = default_message_notifications.value
        if explicit_content_filter:
            payload["explicit_content_filter"] = explicit_content_filter.value
        if afk_channel_id:
            payload["afk_channel_id"] = afk_channel_id
        if afk_timeout:
            payload["afk_timeout"] = afk_timeout
        if owner_id:
            payload["owner_id"] = owner_id
        if system_channel_id:
            payload["system_channel_id"] = system_channel_id
        if system_channel_flags:
            payload["system_channel_flags"] = system_channel_flags
        if rules_channel_id:
            payload["rules_channel_id"] = rules_channel_id
        if public_updates_channel_id:
            payload["public_updates_channel_id"] = rules_channel_id
        if preferred_locale:
            payload["preferred_locale"] = preferred_locale
        if description:
            payload["description"] = description
        if premium_progress_bar_enabled:
            payload["premium_progress_bar_enabled"] = premium_progress_bar_enabled

        res = await self._client.modify_guild(
            guild_id=int(self.id),
            payload=payload,
            reason=reason,
        )
        return Guild(**res, _client=self._client)

    async def create_scheduled_event(
        self,
        name: str,
        entity_type: EntityType,
        scheduled_start_time: datetime.isoformat,
        scheduled_end_time: Optional[datetime.isoformat] = None,
        entity_metadata: Optional["EventMetadata"] = None,
        channel_id: Optional[int] = None,
        description: Optional[str] = None,
        # privacy_level, TODO: implement when more levels available
    ) -> "ScheduledEvents":
        """
        creates a scheduled event for the guild.

        :param name: The name of the event
        :type name: str
        :param entity_type: The entity type of the scheduled event
        :type entity_type: EntityType
        :param scheduled_start_time: The time to schedule the scheduled event
        :type scheduled_start_time: datetime.isoformat
        :param scheduled_end_time?: The time when the scheduled event is scheduled to end
        :type scheduled_end_time: Optional[datetime.isoformat]
        :param entity_metadata?: The entity metadata of the scheduled event
        :type entity_metadata: Optional[EventMetadata]
        :param channel_id?: The channel id of the scheduled event.
        :type channel_id: Optional[int]
        :param description?: The description of the scheduled event
        :type description: Optional[str]
        :return: The created event
        :rtype: ScheduledEvents
        """
        if not self._client:
            raise AttributeError("HTTPClient not found!")
        if entity_type != EntityType.EXTERNAL and not channel_id:
            raise ValueError(
                "channel_id is required when entity_type is not external!"
            )  # TODO: replace with custom error formatter
        if entity_type == EntityType.EXTERNAL and not entity_metadata:
            raise ValueError(
                "entity_metadata is required for external events!"
            )  # TODO: replace with custom error formatter

        payload = {}

        payload["name"] = name
        payload["entity_type"] = entity_type.value
        payload["scheduled_start_time"] = scheduled_start_time
        payload["privacy_level"] = 2
        if scheduled_end_time:
            payload["scheduled_end_time"] = scheduled_end_time
        if entity_metadata:
            payload["entity_metadata"] = entity_metadata
        if channel_id:
            payload["channel_id"] = channel_id
        if description:
            payload["description"] = description

        res = await self._client.create_scheduled_event(
            guild_id=self.id,
            data=payload,
        )
        return ScheduledEvents(**res)

    async def modify_scheduled_event(
        self,
        event_id: int,
        name: Optional[str] = None,
        entity_type: Optional[EntityType] = None,
        scheduled_start_time: Optional[datetime.isoformat] = None,
        scheduled_end_time: Optional[datetime.isoformat] = None,
        entity_metadata: Optional["EventMetadata"] = None,
        channel_id: Optional[int] = None,
        description: Optional[str] = None,
        status: Optional[EventStatus] = None,
        # privacy_level, TODO: implement when more levels available
    ) -> "ScheduledEvents":
        """
        Edits a scheduled event of the guild.

        :param event_id: The id of the event to edit
        :type event_id: int
        :param name: The name of the event
        :type name: Optional[str]
        :param entity_type: The entity type of the scheduled event
        :type entity_type: Optional[EntityType]
        :param scheduled_start_time: The time to schedule the scheduled event
        :type scheduled_start_time: Optional[datetime.isoformat]
        :param scheduled_end_time?: The time when the scheduled event is scheduled to end
        :type scheduled_end_time: Optional[datetime.isoformat]
        :param entity_metadata?: The entity metadata of the scheduled event
        :type entity_metadata: Optional[EventMetadata]
        :param channel_id?: The channel id of the scheduled event.
        :type channel_id: Optional[int]
        :param description?: The description of the scheduled event
        :type description: Optional[str]
        :param status?: The status of the scheduled event
        :type status: Optional[EventStatus]
        :return: The modified event
        :rtype: ScheduledEvents
        """
        if not self._client:
            raise AttributeError("HTTPClient not found!")
        if entity_type == EntityType.EXTERNAL and not entity_metadata:
            raise ValueError(
                "entity_metadata is required for external events!"
            )  # TODO: replace with custom error formatter
        if entity_type == EntityType.EXTERNAL and not scheduled_end_time:
            raise ValueError(
                "External events require an end time!"
            )  # TODO: replace with custom error formatter

        payload = {}
        if name:
            payload["name"] = name
        if channel_id:
            payload["channel_id"] = channel_id
        if scheduled_start_time:
            payload["scheduled_start_time"] = scheduled_start_time
        if entity_type:
            payload["entity_type"] = entity_type.value
            payload["channel_id"] = None
        if scheduled_end_time:
            payload["scheduled_end_time"] = scheduled_end_time
        if entity_metadata:
            payload["entity_metadata"] = entity_metadata
        if description:
            payload["description"] = description
        if status:
            payload["status"] = status

        res = await self._client.modify_scheduled_event(
            guild_id=self.id,
            guild_scheduled_event_id=Snowflake(event_id),
            data=payload,
        )
        return ScheduledEvents(**res)

    async def delete_scheduled_event(self, event_id: int) -> None:
        """
        Deletes a scheduled event of the guild.

        :param event_id: The id of the event to delete
        :type event_id: int
        """
        if not self._client:
            raise AttributeError("HTTPClient not found!")
        await self._client.delete_scheduled_event(
            guild_id=self.id,
            guild_scheduled_event_id=Snowflake(event_id),
        )

    async def get_all_channels(self) -> List[Channel]:
        """
        Gets all channels of the guild as list.

        :return: The channels of the guild.
        :rtype: List[Channel]
        """
        if not self._client:
            raise AttributeError("HTTPClient not found!")
        res = self._client.get_all_channels(int(self.id))
        channels = [Channel(**channel, _client=self._client) for channel in res]
        return channels

    async def get_all_roles(self) -> List[Role]:
        """
        Gets all roles of the guild as list.

        :return: The roles of the guild.
        :rtype: List[Role]
        """
        if not self._client:
            raise AttributeError("HTTPClient not found!")
        res = self._client.get_all_roles(int(self.id))
        roles = [Role(**role, _client=self._client) for role in res]
        return roles

    async def modify_role_position(
        self,
        role_id: Union[Role, int],
        position: int,
        reason: Optional[str] = None,
    ) -> List[Role]:
        """
        Modifies the position of a role in the guild.

        :param role_id: The id of the role to modify the position of
        :type role_id: Union[Role, int]
        :param position: The new position of the role
        :type position: int
        :param reason?: The reason for the modifying
        :type reason: Optional[str]
        :return: List of guild roles with updated hierarchy
        :rtype: List[Role]
        """
        if not self._client:
            raise AttributeError("HTTPClient not found!")
        _role_id = role_id.id if isinstance(role_id, Role) else role_id
        res = await self._client.modify_guild_role_position(
            guild_id=int(self.id), position=position, role_id=_role_id, reason=reason
        )
        roles = [Role(**role, _client=self._client) for role in res]
        return roles

    async def get_bans(self) -> List[dict]:
        """
        Gets a list of banned users.

        :return: List of banned users with reasons
        :rtype: List[dict]
        """
        if not self._client:
            raise AttributeError("HTTPClient not found!")
        res = await self._client.get_guild_bans(int(self.id))
        for ban in res:
            ban["user"] = User(**ban["user"])
        return res


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

    __slots__ = (
        "_json",
        "_client",
        "uses",
        "max_uses",
        "max_age",
        "temporary",
        "created_at",
        # TODO: Investigate their purposes and document.
        "types",
        "inviter",
        "guild_id",
        "expires_at",
        "code",
        "channel_id",
    )

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
    :ivar Optional[Snowflake] channel_id?: The channel ID in which the scheduled event belongs to, if any.
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
    :ivar int status: The status of the scheduled event
    :ivar Optional[str] image: The hash containing the image of an event, if applicable.
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
        "status",
        "image",
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
