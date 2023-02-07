from datetime import datetime
from inspect import isawaitable
from math import inf
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Dict,
    List,
    Literal,
    Optional,
    Tuple,
    Union,
)
from warnings import warn

from ...client.enums import IntEnum, StrEnum
from ...utils.abc.base_iterators import DiscordPaginationIterator
from ...utils.attrs_utils import (
    ClientSerializerMixin,
    DictSerializerMixin,
    convert_int,
    convert_list,
    define,
    field,
)
from ...utils.missing import MISSING
from ..error import LibraryException
from .audit_log import AuditLogEvents, AuditLogs
from .channel import Channel, ChannelType, Thread, ThreadMember
from .emoji import Emoji
from .flags import Permissions
from .member import Member
from .message import Sticker, StickerPack
from .misc import (
    AutoModAction,
    AutoModTriggerMetadata,
    AutoModTriggerType,
    File,
    IDMixin,
    Image,
    Overwrite,
    Snowflake,
)
from .presence import PresenceActivity
from .role import Role
from .team import Application
from .user import User
from .webhook import Webhook

if TYPE_CHECKING:
    from ..http.client import HTTPClient
    from .gw import AutoModerationRule, VoiceState
    from .message import Message

__all__ = (
    "VerificationLevel",
    "EntityType",
    "DefaultMessageNotificationLevel",
    "EventMetadata",
    "EventStatus",
    "GuildTemplate",
    "Integration",
    "InviteTargetType",
    "StageInstance",
    "UnavailableGuild",
    "WelcomeChannels",
    "ExplicitContentFilterLevel",
    "ScheduledEvents",
    "WelcomeScreen",
    "Guild",
    "GuildPreview",
    "Invite",
    "AsyncMembersIterator",
)


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


class InviteTargetType(IntEnum):
    """An enumerable object representing the different invite target types"""

    STREAM = 1
    EMBEDDED_APPLICATION = 2


class GuildFeatures(StrEnum):
    ANIMATED_BANNER = "ANIMATED_BANNER"
    ANIMATED_ICON = "ANIMATED_ICON"
    BANNER = "BANNER"
    COMMERCE = "COMMERCE"
    COMMUNITY = "COMMUNITY"
    DISCOVERABLE = "DISCOVERABLE"
    FEATURABLE = "FEATURABLE"
    INVITE_SPLASH = "INVITE_SPLASH"
    MEMBER_VERIFICATION_GATE_ENABLED = "MEMBER_VERIFICATION_GATE_ENABLED"
    MONETIZATION_ENABLED = "MONETIZATION_ENABLED"
    MORE_STICKERS = "MORE_STICKERS"
    NEWS = "NEWS"
    PARTNERED = "PARTNERED"
    PREVIEW_ENABLED = "PREVIEW_ENABLED"
    PRIVATE_THREADS = "PRIVATE_THREADS"
    ROLE_ICONS = "ROLE_ICONS"
    ROLE_SUBSCRIPTIONS_AVAILABLE_FOR_PURCHASE = "ROLE_SUBSCRIPTIONS_AVAILABLE_FOR_PURCHASE"
    ROLE_SUBSCRIPTIONS_ENABLED = "ROLE_SUBSCRIPTIONS_ENABLED"
    TICKETED_EVENTS_ENABLED = "TICKETED_EVENTS_ENABLED"
    VANITY_URL = "VANITY_URL"
    VERIFIED = "VERIFIED"
    VIP_REGIONS = "VIP_REGIONS"
    WELCOME_SCREEN_ENABLED = "WELCOME_SCREEN_ENABLED"


@define()
class WelcomeChannels(DictSerializerMixin):
    """
    A class object representing a welcome channel on the welcome screen.

    .. note::
        ``emoji_id`` and ``emoji_name`` are given values respectively if the welcome channel
        uses an emoji.

    :ivar Snowflake channel_id: The ID of the welcome channel.
    :ivar str description: The description of the welcome channel.
    :ivar Optional[Snowflake] emoji_id: The ID of the emoji of the welcome channel.
    :ivar Optional[str] emoji_name: The name of the emoji of the welcome channel.
    """

    channel_id: int = field()
    description: str = field()
    emoji_id: Optional[Snowflake] = field(converter=Snowflake, default=None)
    emoji_name: Optional[str] = field(default=None)


@define()
class WelcomeScreen(DictSerializerMixin):
    """
    A class object representing the welcome screen shown for community guilds.

    :ivar Optional[str] description: The description of the welcome screen.
    :ivar List[WelcomeChannels] welcome_channels: A list of welcome channels of the welcome screen.
    """

    description: Optional[str] = field(default=None)
    welcome_channels: Optional[List[WelcomeChannels]] = field(
        converter=convert_list(WelcomeChannels), default=None
    )


@define()
class StageInstance(DictSerializerMixin, IDMixin):
    """
    A class object representing an instance of a stage channel in a guild.

    :ivar Snowflake id: The ID of the stage.
    :ivar Snowflake guild_id: The guild ID the stage is in.
    :ivar Snowflake channel_id: The channel ID the stage is instantiated from.
    :ivar str topic: The topic of the stage.
    :ivar int privacy_level: The "privacy"/inclusive accessibility level of the stage.
    :ivar bool discoverable_disabled: Whether the stage can be seen from the stage discovery.
    """

    id: Snowflake = field(converter=Snowflake)
    guild_id: Snowflake = field(converter=Snowflake)
    channel_id: Snowflake = field(converter=Snowflake)
    topic: str = field()
    privacy_level: int = field()  # can be Enum'd
    discoverable_disabled: bool = field()


@define()
class UnavailableGuild(DictSerializerMixin, IDMixin):
    """
    A class object representing how a guild that is unavailable.

    .. note::
        This object only seems to show up during the connection process
        of the client to the Gateway when the ``READY`` event is dispatched.
        This event will pass fields with ``guilds`` where this becomes
        present.

    :ivar Snowflake id: The ID of the unavailable guild.
    :ivar bool unavailable: Whether the guild is unavailable or not.
    """

    id: Snowflake = field(converter=Snowflake)
    unavailable: bool = field()


class AsyncMembersIterator(DiscordPaginationIterator):
    """
    .. versionadded:: 4.3.2

    A class object that allows iterating through a channel's history.

    :param HTTPClient _client: The HTTPClient of the bot
    :param Union[int, str, Snowflake, Guild] obj: The guild to get the members from
    :param Optional[Union[int, str, Snowflake, Member]] start_at: The member ID to start getting members from (gets all members after that member)
    :param Optional[Callable[[Member], Union[bool, Awaitable[bool]]]] check: A check to ignore certain members
    :param Optional[int] maximum: A set maximum of members to get before stopping the iteration
    """

    def __init__(
        self,
        _client: "HTTPClient",
        obj: Union[int, str, Snowflake, "Guild"],
        maximum: Optional[int] = inf,
        start_at: Optional[Union[int, str, Snowflake, Member]] = MISSING,
        check: Optional[Callable[[Member], Union[bool, Awaitable[bool]]]] = None,
    ):
        self.__stop: bool = False

        super().__init__(obj, _client, maximum=maximum, start_at=start_at, check=check)

        self.after = self.start_at

        self.objects: Optional[List[Member]]

    async def get_first_objects(self) -> None:
        limit = min(self.maximum, 1000)

        if self.maximum == limit:
            self.__stop = True

        members = await self._client.get_list_of_members(
            guild_id=self.object_id, after=self.after, limit=limit
        )
        self.after = int(members[-1]["user"]["id"])

        if len(members) < 1000:
            # already all messages resolved with one operation
            self.__stop = True

        self.object_count += limit

        self.objects = [
            Member(**member, _client=self._client, guild_id=self.object_id) for member in members
        ]

    async def get_objects(self) -> None:
        limit = min(500, self.maximum - self.object_count)
        members = await self._client.get_list_of_members(
            guild_id=self.object_id, after=self.after, limit=limit
        )
        self.after = int(members[-1]["user"]["id"])

        if len(members) < limit or limit == self.maximum - self.object_count:
            # end of messages reached again
            self.__stop = True

        self.object_count += limit

        self.objects.extend(
            [Member(**member, _client=self._client, guild_id=self.object_id) for member in members]
        )

    async def flatten(self) -> List[Member]:
        """Returns all remaining items of the iterator as list."""
        return [item async for item in self]

    async def __anext__(self) -> Member:
        if self.objects is None:
            await self.get_first_objects()

        try:
            obj = self.objects.pop(0)

            if self.check:
                res = self.check(obj)
                _res = await res if isawaitable(res) else res
                while not _res:
                    if (
                        not self.__stop
                        and len(self.objects) < 5
                        and self.object_count >= self.maximum
                    ):
                        await self.get_objects()

                    self.object_count -= 1
                    obj = self.objects.pop(0)

                    _res = self.check(obj)

            if not self.__stop and len(self.objects) < 5 and self.object_count <= self.maximum:
                await self.get_objects()
        except IndexError as e:
            raise StopAsyncIteration from e
        else:
            return obj


@define()
class Guild(ClientSerializerMixin, IDMixin):
    """
    A class object representing how a guild is registered.

    .. note::
        Most of these optionals are actually declared with their value
        upon instantiation but are kept like this since this class object
        is meant to be more broad and generalized.

    :ivar Snowflake id: The ID of the guild.
    :ivar str name: The name of the guild.
    :ivar Optional[str] icon: The icon of the guild.
    :ivar Optional[str] icon_hash: The hashed version of the icon of the guild.
    :ivar Optional[str] splash: The invite splash banner of the guild.
    :ivar Optional[str] discovery_splash: The discovery splash banner of the guild.
    :ivar Optional[bool] owner: Whether the guild is owned.
    :ivar Snowflake owner_id: The ID of the owner of the guild.
    :ivar Optional[Permissions] permissions: The permissions of the guild.
    :ivar Optional[str] region: The geographical region of the guild.
    :ivar Optional[Snowflake] afk_channel_id: The AFK voice channel of the guild.
    :ivar int afk_timeout: The timeout of the AFK voice channel of the guild.
    :ivar Optional[bool] widget_enabled: Whether widgets are enabled in the guild.
    :ivar Optional[Snowflake] widget_channel_id: The channel ID of the widget in the guild.
    :ivar int verification_level: The level of user verification of the guild.
    :ivar int default_message_notifications: The default message notifications setting of the guild.
    :ivar int explicit_content_filter: The explicit content filter setting level of the guild.
    :ivar List[Role] roles: The list of roles in the guild.
    :ivar List[Emoji] emojis: The list of emojis from the guild.
    :ivar List[GuildFeature] features: The list of features of the guild.
    :ivar int mfa_level: The MFA level of the guild.
    :ivar Optional[Snowflake] application_id: The application ID of the guild.
    :ivar Optional[Snowflake] system_channel_id: The channel ID of the system of the guild.
    :ivar Optional[Snowflake] rules_channel_id: The channel ID of Discord's defined "rules" channel of the guild.
    :ivar Optional[datetime] joined_at: The timestamp the member joined the guild.
    :ivar Optional[bool] large: Whether the guild is considered "large."
    :ivar Optional[bool] unavailable: Whether the guild is unavailable to access.
    :ivar Optional[int] member_count: The amount of members in the guild.
    :ivar Optional[List[Member]] members: The members in the guild.
    :ivar Optional[List[Channel]] channels: The channels in the guild.
    :ivar Optional[List[Thread]] threads: All known threads in the guild.
    :ivar Optional[List[PresenceUpdate]] presences: The list of presences in the guild.
    :ivar Optional[int] max_presences: The maximum amount of presences allowed in the guild.
    :ivar Optional[int] max_members: The maximum amount of members allowed in the guild.
    :ivar Optional[str] vanity_url_code: The vanity URL of the guild.
    :ivar Optional[str] description: The description of the guild.
    :ivar Optional[str] banner: The banner of the guild.
    :ivar int premium_tier: The server boost level of the guild.
    :ivar Optional[int] premium_subscription_count: The amount of server boosters in the guild.
    :ivar str preferred_locale: The "preferred" local region of the guild.
    :ivar Optional[Snowflake] public_updates_channel_id: The channel ID for community updates of the guild.
    :ivar Optional[int] max_video_channel_users: The maximum amount of video streaming members in a channel allowed in a guild.
    :ivar Optional[int] approximate_member_count: The approximate amount of members in the guild.
    :ivar Optional[int] approximate_presence_count: The approximate amount of presences in the guild.
    :ivar Optional[WelcomeScreen] welcome_screen: The welcome screen of the guild.
    :ivar int nsfw_level: The NSFW safety filter level of the guild.
    :ivar Optional[List[StageInstance]] stage_instances: The stage instance of the guild.
    :ivar Optional[List[Sticker]] stickers: The list of stickers from the guild.
    :ivar Optional[bool] premium_progress_bar_enabled: Whether the guild has the boost progress bar enabled.
    """

    id: Snowflake = field(converter=Snowflake)
    name: str = field()
    icon: Optional[str] = field(default=None, repr=False)
    icon_hash: Optional[str] = field(default=None, repr=False)
    splash: Optional[str] = field(default=None, repr=False)
    discovery_splash: Optional[str] = field(default=None, repr=False)
    owner: Optional[bool] = field(default=None)
    owner_id: Snowflake = field(converter=Snowflake, default=None)
    permissions: Optional[Permissions] = field(
        converter=convert_int(Permissions), default=None, repr=False
    )
    region: Optional[str] = field(default=None, repr=False)  # None, we don't do Voices.
    afk_channel_id: Optional[Snowflake] = field(converter=Snowflake, default=None)
    afk_timeout: Optional[int] = field(default=None)
    widget_enabled: Optional[bool] = field(default=None, repr=False)
    widget_channel_id: Optional[Snowflake] = field(converter=Snowflake, default=None, repr=False)
    verification_level: int = field(default=0)
    default_message_notifications: int = field(default=0)
    explicit_content_filter: int = field(default=0)
    roles: List[Role] = field(converter=convert_list(Role), factory=list, add_client=True)
    emojis: List[Emoji] = field(converter=convert_list(Emoji), factory=list, add_client=True)
    mfa_level: int = field(default=0)
    application_id: Optional[Snowflake] = field(converter=Snowflake, default=None)
    system_channel_id: Optional[Snowflake] = field(converter=Snowflake, default=None)
    system_channel_flags: int = field(default=None)
    rules_channel_id: Optional[Snowflake] = field(converter=Snowflake, default=None)
    joined_at: Optional[datetime] = field(converter=datetime.fromisoformat, default=None)
    large: Optional[bool] = field(default=None)
    unavailable: Optional[bool] = field(default=None)
    member_count: Optional[int] = field(default=None)
    members: Optional[List[Member]] = field(
        converter=convert_list(Member), default=None, add_client=True
    )
    channels: Optional[List[Channel]] = field(
        converter=convert_list(Channel), default=None, add_client=True
    )
    threads: Optional[List[Thread]] = field(
        converter=convert_list(Thread), default=None, add_client=True
    )  # threads, because of their metadata
    presences: Optional[List[PresenceActivity]] = field(
        converter=convert_list(PresenceActivity), default=None
    )
    max_presences: Optional[int] = field(default=None)
    max_members: Optional[int] = field(default=None)
    vanity_url_code: Optional[str] = field(default=None)
    description: Optional[str] = field(default=None)
    banner: Optional[str] = field(default=None, repr=False)
    premium_tier: int = field(default=0)
    premium_subscription_count: Optional[int] = field(default=None, repr=False)
    preferred_locale: str = field(default=None)
    public_updates_channel_id: Optional[Snowflake] = field(converter=Snowflake, default=None)
    max_video_channel_users: Optional[int] = field(default=None, repr=False)
    approximate_member_count: Optional[int] = field(default=None)
    approximate_presence_count: Optional[int] = field(default=None)
    welcome_screen: Optional[WelcomeScreen] = field(
        converter=WelcomeScreen, default=None, repr=False
    )
    nsfw_level: int = field(default=0)
    stage_instances: Optional[List[StageInstance]] = field(
        converter=convert_list(StageInstance), default=None
    )
    stickers: Optional[List[Sticker]] = field(converter=convert_list(Sticker), default=None)
    features: List[str] = field()
    premium_progress_bar_enabled: Optional[bool] = field(default=None)

    # todo assign the correct type

    def __attrs_post_init__(self):  # sourcery skip: last-if-guard
        if self._client:
            # update the cache to include info found from guilds
            # these values wouldn't be "found out" until an update for them happened otherwise
            if self.channels:
                self._client.cache[Channel].update({c.id: c for c in self.channels})
            if self.threads:
                self._client.cache[Thread].update({t.id: t for t in self.threads})
            if self.roles:
                self._client.cache[Role].update({r.id: r for r in self.roles})
            if self.members:
                self._client.cache[Member].update({(self.id, m.id): m for m in self.members})

            if guild := self._client.cache[Guild].get(self.id):
                if not self.channels:
                    self.channels = guild.channels
                if not self.threads:
                    self.threads = guild.threads
                if not self.roles:
                    self.roles = guild.roles
                if not self.members:
                    self.members = guild.members
                if not self.member_count:
                    self.member_count = guild.member_count
                if not self.presences:
                    self.presences = guild.presences
                if not self.emojis:
                    self.emojis = guild.emojis

        if self.members:
            for member in self.members:
                if (
                    not member._extras.get("guild_id")
                    or hasattr(member, "_guild_id")
                    and not member._guild_id
                ):
                    member._extras["guild_id"] = self.id

    @property
    def voice_states(self) -> List["VoiceState"]:
        """
        .. versionadded:: 4.4.0

        Gets all voice states of the guild.

        :rtype: List[VoiceState]
        """

        if not self._client:
            raise LibraryException(code=13)

        from .gw import VoiceState

        states: List[VoiceState] = []

        data = self._client.cache[VoiceState].values.values()
        states.extend(state for state in data if state.guild_id == self.id)
        return states

    @property
    def mapped_voice_states(self) -> Dict[int, List["VoiceState"]]:
        """
        .. versionadded:: 4.4.0

        Returns all the voice states mapped after their channel id.

        :rtype: Dict[int, List[VoiceState]]
        """
        states = self.voice_states
        _states: Dict[int, List[VoiceState]] = {int(state.channel_id): [] for state in states}

        for state in states:
            _states[int(state.channel_id)].append(state)

        return _states

    @property
    def created_at(self) -> datetime:
        """
        .. versionadded:: 4.4.0

        Returns when the guild was created.
        """
        return self.id.timestamp

    async def ban(
        self,
        member_id: Union[int, Member, Snowflake],
        seconds: Optional[int] = 0,
        minutes: Optional[int] = MISSING,
        hours: Optional[int] = MISSING,
        days: Optional[int] = MISSING,
        reason: Optional[str] = None,
    ) -> None:
        """
        .. versionadded:: 4.0.2

        .. versionchanged:: 4.3.2
            Method has been aligned to changes in the Discord API. You can now input days, hours, minutes and seconds,
            as long as it doesn't exceed 604800 seconds in total for deleting messages, instead of only days.

        Bans a member from the guild.

        :param Union[int, Member, Snowflake] member_id: The id of the member to ban
        :param Optional[int] seconds: Number of seconds to delete messages, from 0 to 604800. Defaults to 0
        :param Optional[int] minutes: Number of minutes to delete messages, from 0 to 10080
        :param Optional[int] hours: Number of hours to delete messages, from 0 to 168
        :param Optional[int] days: Number of days to delete messages, from 0 to 7
        :param Optional[str] reason: The reason of the ban
        """
        if not self._client:
            raise LibraryException(code=13)

        if days is not MISSING:
            seconds += days * 24 * 3600
        if hours is not MISSING:
            seconds += hours * 3600
        if minutes is not MISSING:
            seconds += minutes * 60

        if seconds > 604800:
            raise LibraryException(
                code=12,
                message="The amount of total seconds to delete messages exceeds the limit Discord provides (604800)",
            )

        _member_id = int(member_id.id) if isinstance(member_id, Member) else int(member_id)
        await self._client.create_guild_ban(
            guild_id=int(self.id),
            user_id=_member_id,
            reason=reason,
            delete_message_seconds=seconds,
        )

        if not self.members:
            return
        for member in self.members:
            if int(member.id) == _member_id:
                return self.members.remove(member)

    async def remove_ban(
        self,
        user_id: Union[int, Snowflake],  # only support ID since there's no member on the guild
        reason: Optional[str] = None,
    ) -> None:
        """
        .. versionadded:: 4.0.2

        Removes the ban of a user.

        :param Union[int, Snowflake] user_id: The id of the user to remove the ban from
        :param Optional[str] reason: The reason for the removal of the ban
        """
        if not self._client:
            raise LibraryException(code=13)
        await self._client.remove_guild_ban(
            guild_id=int(self.id),
            user_id=user_id,
            reason=reason,
        )

    async def kick(
        self,
        member_id: Union[int, Member, Snowflake],
        reason: Optional[str] = None,
    ) -> None:
        """
        .. versionadded:: 4.0.2

        Kicks a member from the guild.

        :param Union[int, Member, Snowflake] member_id: The id of the member to kick
        :param Optional[str] reason: The reason for the kick
        """
        if not self._client:
            raise LibraryException(code=13)

        _member_id = int(member_id.id) if isinstance(member_id, Member) else int(member_id)
        await self._client.create_guild_kick(
            guild_id=int(self.id),
            user_id=_member_id,
            reason=reason,
        )
        for member in self.members:
            if int(member.id) == _member_id:
                return self.members.remove(member)

    async def add_member_role(
        self,
        role: Union[Role, int, Snowflake],
        member_id: Union[Member, int, Snowflake],
        reason: Optional[str] = None,
    ) -> None:
        """
        .. versionadded:: 4.0.2

        This method adds a role to a member.

        :param Union[Role, int, Snowflake] role: The role to add. Either ``Role`` object or role_id
        :param Union[Member, int, Snowflake] member_id: The id of the member to add the roles to
        :param Optional[str] reason: The reason why the roles are added
        """
        if not self._client:
            raise LibraryException(code=13)

        _role_id = int(role.id) if isinstance(role, Role) else int(role)
        _member_id = int(member_id.id) if isinstance(member_id, Member) else int(member_id)

        await self._client.add_member_role(
            guild_id=int(self.id),
            user_id=_member_id,
            role_id=_role_id,
            reason=reason,
        )

    async def remove_member_role(
        self,
        role: Union[Role, int, Snowflake],
        member_id: Union[Member, int, Snowflake],
        reason: Optional[str] = None,
    ) -> None:
        """
        .. versionadded:: 4.0.2

        This method removes a or multiple role(s) from a member.

        :param Union[Role, int, Snowflake] role: The role to remove. Either ``Role`` object or role_id
        :param Union[Member, int, Snowflake] member_id: The id of the member to remove the roles from
        :param Optional[str] reason: The reason why the roles are removed
        """
        if not self._client:
            raise LibraryException(code=13)

        _role_id = int(role.id) if isinstance(role, Role) else int(role)
        _member_id = int(member_id.id) if isinstance(member_id, Member) else int(member_id)

        await self._client.remove_member_role(
            guild_id=int(self.id),
            user_id=_member_id,
            role_id=_role_id,
            reason=reason,
        )

    async def create_role(
        self,
        name: str,
        permissions: Optional[Union[Permissions, int]] = MISSING,
        color: Optional[int] = 0,
        hoist: Optional[bool] = False,
        icon: Optional[Image] = MISSING,
        unicode_emoji: Optional[str] = MISSING,
        mentionable: Optional[bool] = False,
        reason: Optional[str] = None,
    ) -> Role:
        """
        .. versionadded:: 4.0.2

        Creates a new role in the guild.

        :param str name: The name of the role
        :param Optional[int] color: RGB color value as integer, default ``0``
        :param Optional[Union[Permissions, int]] permissions: Bitwise value of the enabled/disabled permissions
        :param Optional[bool] hoist: Whether the role should be displayed separately in the sidebar, default ``False``
        :param Optional[Image] icon: The role's icon image (if the guild has the ROLE_ICONS feature)
        :param Optional[str] unicode_emoji: The role's unicode emoji as a standard emoji (if the guild has the ROLE_ICONS feature)
        :param Optional[bool] mentionable: Whether the role should be mentionable, default ``False``
        :param Optional[str] reason: The reason why the role is created, default ``None``
        :return: The created Role
        :rtype: Role
        """
        if not self._client:
            raise LibraryException(code=13)

        _permissions = int(permissions) if permissions is not MISSING else None
        _icon = icon if icon is not MISSING else None
        _unicode_emoji = unicode_emoji if unicode_emoji is not MISSING else None
        payload = dict(
            name=name,
            permissions=_permissions,
            icon=_icon,
            unicode_emoji=_unicode_emoji,
            color=color,
            hoist=hoist,
            mentionable=mentionable,
        )
        res = await self._client.create_guild_role(
            guild_id=int(self.id),
            reason=reason,
            payload=payload,
        )
        if self.roles is None:
            self.roles = []
        role = Role(**res, _client=self._client)
        self.roles.append(role)
        return role

    async def get_member(
        self,
        member_id: Union[int, Snowflake],
    ) -> Member:
        """
        .. versionadded:: 4.0.2

        Searches for the member with specified id in the guild and returns the member as member object.

        :param Union[int, Snowflake] member_id: The id of the member to search for
        :return: The member searched for
        :rtype: Member
        """
        if not self._client:
            raise LibraryException(code=13)
        res = await self._client.get_member(
            guild_id=int(self.id),
            member_id=int(member_id),
        )
        member = Member(**res, _client=self._client, guild_id=self.id)
        if self.members is None:
            self.members = []
        for index, _member in enumerate(self.members):
            if int(_member.id) == int(member_id):
                self.members[index] = member
                break
        else:
            self.members.append(member)
        return member

    async def delete_channel(
        self,
        channel_id: Union[int, Snowflake, Channel],
    ) -> None:
        """
        .. versionadded:: 4.0.2

        Deletes a channel from the guild.

        :param Union[int, Snowflake, Channel] channel_id: The id of the channel to delete
        """
        if not self._client:
            raise LibraryException(code=13)

        _channel_id = int(channel_id.id) if isinstance(channel_id, Channel) else int(channel_id)
        await self._client.delete_channel(_channel_id)

        if not self.channels:
            return
        for channel in self.channels:
            if int(channel.id) == _channel_id:
                return self.channels.remove(channel)

    async def delete_role(
        self,
        role_id: Union[int, Snowflake, Role],
        reason: Optional[str] = None,
    ) -> None:
        """
        .. versionadded:: 4.0.2

        Deletes a role from the guild.

        :param Union[int, Snowflake, Role] role_id: The id of the role to delete
        :param Optional[str] reason: The reason of the deletion
        """
        if not self._client:
            raise LibraryException(code=13)

        _role_id = int(role_id.id) if isinstance(role_id, Role) else int(role_id)

        await self._client.delete_guild_role(
            guild_id=int(self.id),
            role_id=_role_id,
            reason=reason,
        )

        if not self.roles:
            return
        for role in self.roles:
            if int(role.id) == _role_id:
                return self.roles.remove(role)

    async def modify_role(
        self,
        role_id: Union[int, Snowflake, Role],
        name: Optional[str] = MISSING,
        permissions: Optional[Union[Permissions, int]] = MISSING,
        color: Optional[int] = MISSING,
        hoist: Optional[bool] = MISSING,
        icon: Optional[Image] = MISSING,
        unicode_emoji: Optional[str] = MISSING,
        mentionable: Optional[bool] = MISSING,
        reason: Optional[str] = None,
    ) -> Role:
        """
        .. versionadded:: 4.0.2

        Edits a role in the guild.

        :param Union[int, Snowflake, Role] role_id: The id of the role to edit
        :param Optional[str] name: The name of the role, defaults to the current value of the role
        :param Optional[int] color: RGB color value as integer, defaults to the current value of the role
        :param Optional[Union[Permissions, int]] permissions: Bitwise value of the enabled/disabled permissions, defaults to the current value of the role
        :param Optional[bool] hoist: Whether the role should be displayed separately in the sidebar, defaults to the current value of the role
        :param Optional[Image] icon: The role's icon image (if the guild has the ROLE_ICONS feature), defaults to the current value of the role
        :param Optional[str] unicode_emoji: The role's unicode emoji as a standard emoji (if the guild has the ROLE_ICONS feature), defaults to the current value of the role
        :param Optional[bool] mentionable: Whether the role should be mentionable, defaults to the current value of the role
        :param Optional[str] reason: The reason why the role is edited, default ``None``
        :return: The modified role object
        :rtype: Role
        """
        if not self._client:
            raise LibraryException(code=13)

        if isinstance(role_id, Role):
            role = role_id
        else:
            role = await self.get_role(int(role_id))

        _name = role.name if name is MISSING else name
        _color = role.color if color is MISSING else color
        _hoist = role.hoist if hoist is MISSING else hoist
        _mentionable = role.mentionable if mentionable is MISSING else mentionable
        _permissions = int(role.permissions if permissions is MISSING else permissions)
        _icon = role.icon if icon is MISSING else icon
        _unicode_emoji = role.unicode_emoji if unicode_emoji is MISSING else unicode_emoji

        payload = dict(
            name=_name,
            color=_color,
            hoist=_hoist,
            mentionable=_mentionable,
            permissions=_permissions,
            unicode_emoji=_unicode_emoji,
            icon=_icon,
        )

        res = await self._client.modify_guild_role(
            guild_id=int(self.id),
            role_id=role_id,
            payload=payload,
            reason=reason,
        )
        _role = Role(**res, _client=self._client)
        if self.roles is None:
            self.roles = []
        for index, item in enumerate(self.roles):
            if int(item.id) == int(role.id):
                self.roles[index] = _role
                break
        else:
            self.roles.append(_role)
        return _role

    async def create_thread(
        self,
        name: str,
        channel_id: Union[int, Snowflake, Channel],
        type: Optional[ChannelType] = ChannelType.PUBLIC_THREAD,
        auto_archive_duration: Optional[int] = MISSING,
        invitable: Optional[bool] = MISSING,
        message_id: Optional[Union[int, Snowflake, "Message"]] = MISSING,
        reason: Optional[str] = None,
    ) -> Channel:
        """
        .. versionadded:: 4.1.0

        Creates a thread in the specified channel.

        :param str name: The name of the thread
        :param Union[int, Snowflake, Channel] channel_id: The id of the channel to create the thread in
        :param Optional[int] auto_archive_duration: duration in minutes to automatically archive the thread after recent activity, can be set to: 60, 1440, 4320, 10080
        :param Optional[ChannelType] type: The type of thread, defaults to public. ignored if creating thread from a message
        :param Optional[bool] invitable: Boolean to display if the Thread is open to join or private.
        :param Optional[Union[int, Snowflake, Message]] message_id: An optional message to create a thread from.
        :param Optional[str] reason: An optional reason for the audit log
        :return: The created thread
        :rtype: Channel
        """
        if not self._client:
            raise LibraryException(code=13)
        if type not in [
            ChannelType.ANNOUNCEMENT_THREAD,
            ChannelType.PUBLIC_THREAD,
            ChannelType.PRIVATE_THREAD,
        ]:
            raise LibraryException(message="type must be a thread type!", code=12)

        _auto_archive_duration = None if auto_archive_duration is MISSING else auto_archive_duration
        _invitable = None if invitable is MISSING else invitable
        _message_id = (
            None
            if message_id is MISSING
            else (
                int(message_id) if isinstance(message_id, (int, Snowflake)) else int(message_id.id)
            )
        )  # work around Message import
        _channel_id = int(channel_id.id) if isinstance(channel_id, Channel) else int(channel_id)
        res = await self._client.create_thread(
            channel_id=_channel_id,
            thread_type=type if isinstance(type, int) else type.value,
            name=name,
            auto_archive_duration=_auto_archive_duration,
            invitable=_invitable,
            message_id=_message_id,
            reason=reason,
        )

        return Channel(**res, _client=self._client)

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
        parent_id: Optional[Union[int, Channel, Snowflake]] = MISSING,
        nsfw: Optional[bool] = MISSING,
        reason: Optional[str] = None,
    ) -> Channel:
        """
        .. versionadded:: 4.0.2

        Creates a channel in the guild.

        :param str name: The name of the channel
        :param ChannelType type: The type of the channel
        :param Optional[str] topic: The topic of that channel
        :param Optional[int] bitrate: (voice channel only) The bitrate (in bits) of the voice channel
        :param Optional[int] user_limit: (voice channel only) Maximum amount of users in the channel
        :param Optional[int] rate_limit_per_use: Amount of seconds a user has to wait before sending another message (0-21600)
        :param Optional[int] position: Sorting position of the channel
        :param Optional[Union[int, Channel, Snowflake]] parent_id: The id of the parent category for a channel
        :param Optional[List[Overwrite]] permission_overwrites: The permission overwrites, if any
        :param Optional[bool] nsfw: Whether the channel is nsfw or not, default ``False``
        :param Optional[str] reason: The reason for the creation
        :return: The created channel
        :rtype: Channel
        """
        if not self._client:
            raise LibraryException(code=13)
        if type in [
            ChannelType.DM,
            ChannelType.DM.value,
            ChannelType.GROUP_DM,
            ChannelType.GROUP_DM.value,
        ]:
            raise LibraryException(
                message="ChannelType must not be a direct-message when creating Guild Channels!",
                code=12,
            )

        if type in [
            ChannelType.ANNOUNCEMENT_THREAD,
            ChannelType.PUBLIC_THREAD,
            ChannelType.PRIVATE_THREAD,
        ]:
            raise LibraryException(
                message="Please use `create_thread` for creating threads!", code=12
            )

        payload = {"name": name, "type": type}

        if topic is not MISSING:
            payload["topic"] = topic
        if bitrate is not MISSING:
            payload["bitrate"] = bitrate
        if user_limit is not MISSING:
            payload["user_limit"] = user_limit
        if rate_limit_per_user is not MISSING:
            payload["rate_limit_per_user"] = rate_limit_per_user
        if position is not MISSING:
            payload["position"] = position
        if parent_id is not MISSING:
            payload["parent_id"] = (
                int(parent_id.id) if isinstance(parent_id, Channel) else int(parent_id)
            )
        if nsfw is not MISSING:
            payload["nsfw"] = nsfw
        if permission_overwrites is not MISSING:
            payload["permission_overwrites"] = [
                overwrite._json for overwrite in permission_overwrites
            ]

        res = await self._client.create_channel(
            guild_id=int(self.id),
            reason=reason,
            payload=payload,
        )

        if self.channels is None:
            self.channels = []
        channel = Channel(**res, _client=self._client)
        self.channels.append(channel)
        return channel

    async def clone_channel(self, channel_id: Union[int, Snowflake, Channel]) -> Channel:
        """
        .. versionadded:: 4.3.0

        Clones a channel of the guild.

        :param Union[int, Snowflake, Channel] channel_id: The id of the channel to clone
        :return: The cloned channel
        :rtype: Channel
        """
        if not self._client:
            raise LibraryException(code=13)

        res = (
            channel_id._json
            if isinstance(channel_id, Channel)
            else await self._client.get_channel(channel_id=int(channel_id))
        )

        res["permission_overwrites"] = [Overwrite(**_) for _ in res["permission_overwrites"]]
        for attr in {"flags", "guild_id", "id", "last_message_id", "last_pin_timestamp"}:
            res.pop(attr, None)

        return await self.create_channel(**res)

    async def modify_channel(
        self,
        channel_id: Union[int, Snowflake, Channel],
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
        auto_archive_duration: Optional[Literal[60, 1440, 4320, 10080]] = MISSING,
        locked: Optional[bool] = MISSING,
        reason: Optional[str] = None,
    ) -> Channel:  # sourcery skip: low-code-quality
        """
        .. versionadded:: 4.0.2

        Edits a channel of the guild.

        .. versionadded:: 4.2.0::
            The fields ``archived``, ``auto_archive_duration`` and ``locked`` require the provided channel to be a thread.

        :param Union[int, Snowflake, Channel] channel_id: The id of the channel to modify
        :param str name: The name of the channel, defaults to the current value of the channel
        :param Optional[str] topic: The topic of that channel, defaults to the current value of the channel
        :param Optional[int] bitrate: (voice channel only) The bitrate (in bits) of the voice channel, defaults to the current value of the channel
        :param Optional[int] user_limit: (voice channel only) Maximum amount of users in the channel, defaults to the current value of the channel
        :param Optional[int] rate_limit_per_user: Amount of seconds a user has to wait before sending another message (0-21600), defaults to the current value of the channel
        :param Optional[int] position: Sorting position of the channel, defaults to the current value of the channel
        :param Optional[int] parent_id: The id of the parent category for a channel, defaults to the current value of the channel
        :param Optional[Overwrite] permission_overwrites: The permission overwrites, if any
        :param Optional[bool] nsfw: Whether the channel is nsfw or not, defaults to the current value of the channel
        :param Optional[bool] archived:
            .. versionadded:: 4.2.0

            Whether the thread is archived
        :param Optional[Literal[60, 1440, 4320, 10080]] auto_archive_duration:
            .. versionadded:: 4.2.0

            The time after the thread is automatically archived. One of 60, 1440, 4320, 10080
        :param Optional[bool] locked:
            .. versionadded:: 4.2.0

            Whether the thread is locked
        :param Optional[str] reason: The reason for the edit
        :return: The modified channel
        :rtype: Channel
        """
        if not self._client:
            raise LibraryException(code=13)

        if isinstance(channel_id, Channel):
            ch = channel_id
        else:
            ch = Channel(**await self._client.get_channel(channel_id=int(channel_id)))

        _name = ch.name if name is MISSING else name
        _topic = ch.topic if topic is MISSING else topic
        _bitrate = ch.bitrate if bitrate is MISSING else bitrate
        _user_limit = ch.user_limit if user_limit is MISSING else user_limit
        _rate_limit_per_user = (
            ch.rate_limit_per_user if rate_limit_per_user is MISSING else rate_limit_per_user
        )
        _position = ch.position if position is MISSING else position
        _parent_id = (
            (int(ch.parent_id) if ch.parent_id else None) if parent_id is MISSING else parent_id
        )
        _nsfw = ch.nsfw if nsfw is MISSING else nsfw
        _permission_overwrites = (
            [overwrite._json for overwrite in ch.permission_overwrites]
            if ch.permission_overwrites
            else None
            if permission_overwrites is MISSING
            else [overwrite._json for overwrite in permission_overwrites]
        )
        _type = ch.type

        payload = dict(
            name=_name,
            type=_type,
            topic=_topic,
            bitrate=_bitrate,
            user_limit=_user_limit,
            rate_limit_per_user=_rate_limit_per_user,
            permission_overwrites=_permission_overwrites,
            position=_position,
            parent_id=_parent_id,
            nsfw=_nsfw,
        )

        if (
            archived is not MISSING or auto_archive_duration is not MISSING or locked is not MISSING
        ) and not ch.thread_metadata:
            raise LibraryException(message="The specified channel is not a Thread!", code=12)

        if archived is not MISSING:
            payload["archived"] = archived
        if auto_archive_duration is not MISSING:
            payload["auto_archive_duration"] = auto_archive_duration
        if locked is not MISSING:
            payload["locked"] = locked

        res = await self._client.modify_channel(
            channel_id=channel_id,
            reason=reason,
            payload=payload,
        )

        _channel = Channel(**res, _client=self._client)

        if self.channels is None:
            self.channels = []

        for index, item in enumerate(self.channels):
            if int(item.id) == int(ch.id):
                self.channels[index] = _channel
                break
        else:
            self.channels.append(_channel)

        return _channel

    async def modify_member(
        self,
        member_id: Union[int, Snowflake, Member],
        nick: Optional[str] = MISSING,
        roles: Optional[List[int]] = MISSING,
        mute: Optional[bool] = MISSING,
        deaf: Optional[bool] = MISSING,
        channel_id: Optional[int] = MISSING,
        communication_disabled_until: Optional[datetime.isoformat] = MISSING,
        reason: Optional[str] = None,
    ) -> Member:
        """
        .. versionadded:: 4.0.2

        Modifies a member of the guild.

        :param Union[int, Snowflake, Member] member_id: The id of the member to modify
        :param Optional[str] nick: The nickname of the member
        :param Optional[List[int]] roles: A list of all role ids the member has
        :param Optional[bool] mute: whether the user is muted in voice channels
        :param Optional[bool] deaf: whether the user is deafened in voice channels
        :param Optional[int] channel_id: id of channel to move user to (if they are connected to voice)
        :param Optional[datetime.isoformat] communication_disabled_until: when the user's timeout will expire and the user will be able to communicate in the guild again (up to 28 days in the future)
        :param Optional[str] reason: The reason of the modifying
        :return: The modified member
        :rtype: Member
        """
        if not self._client:
            raise LibraryException(code=13)
        payload = {}
        if nick is not MISSING:
            payload["nick"] = nick

        if roles is not MISSING:
            payload["roles"] = roles

        if channel_id is not MISSING:
            payload["channel_id"] = channel_id

        if mute is not MISSING:
            payload["mute"] = mute

        if deaf is not MISSING:
            payload["deaf"] = deaf

        if communication_disabled_until is not MISSING:
            payload["communication_disabled_until"] = communication_disabled_until

        _member_id = int(member_id.id) if isinstance(member_id, Member) else int(member_id)

        res = await self._client.modify_member(
            user_id=_member_id,
            guild_id=int(self.id),
            payload=payload,
            reason=reason,
        )

        _member = Member(**res, _client=self._client, guild_id=self.id)
        if self.members is None:
            self.members = []
        for index, member in enumerate(self.members):
            if int(member.id) == _member_id:
                self.members[index] = _member
                break
        else:
            self.members.append(_member)

        return _member

    async def get_preview(self) -> "GuildPreview":
        """
        .. versionadded:: 4.0.2

        Get the guild's preview.

        :return: the guild preview as object
        :rtype: GuildPreview
        """

        if not self._client:
            raise LibraryException(code=13)

        return GuildPreview(**await self._client.get_guild_preview(guild_id=int(self.id)))

    async def leave(self) -> None:
        """
        .. versionadded:: 4.0.2

        Removes the bot from the guild.
        """
        if not self._client:
            raise LibraryException(code=13)
        await self._client.leave_guild(guild_id=int(self.id))

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
    ) -> "Guild":  # sourcery skip: low-code-quality
        """
        .. versionadded:: 4.0.2

        Modifies the current guild.

        :param Optional[str] name: The new name of the guild
        :param Optional[VerificationLevel] verification_level: The verification level of the guild
        :param Optional[DefaultMessageNotificationLevel] default_message_notifications: The default message notification level for members
        :param Optional[ExplicitContentFilterLevel] explicit_content_filter: The explicit content filter level for media content
        :param Optional[int] afk_channel_id: The id for the afk voice channel
        :param Optional[int] afk_timeout: Afk timeout in seconds
        :param Optional[Image] icon:
            .. versionadded:: 4.2.0

            1024x1024 png/jpeg/gif image for the guild icon (can be animated gif when the server has the ANIMATED_ICON feature)
        :param Optional[int] owner_id: The id of the user to transfer the guild ownership to. You must be the owner to perform this
        :param Optional[Image] splash:
            .. versionadded:: 4.2.0

            16:9 png/jpeg image for the guild splash (when the server has the INVITE_SPLASH feature)
        :param Optional[Image] discovery_splash:
            .. versionadded:: 4.2.0

            16:9 png/jpeg image for the guild discovery splash (when the server has the DISCOVERABLE feature)
        :param Optional[Image] banner:
            .. versionadded:: 4.2.0

            16:9 png/jpeg image for the guild banner (when the server has the BANNER feature; can be animated gif when the server has the ANIMATED_BANNER feature)
        :param Optional[int] system_channel_id: The id of the channel where guild notices such as welcome messages and boost events are posted
        :param Optional[bool] suppress_join_notifications: Whether to suppress member join notifications in the system channel or not
        :param Optional[bool] suppress_premium_subscriptions: Whether to suppress server boost notifications in the system channel or not
        :param Optional[bool] suppress_guild_reminder_notifications: Whether to suppress server setup tips in the system channel or not
        :param Optional[bool] suppress_join_notification_replies: Whether to hide member join sticker reply buttons in the system channel or not
        :param Optional[int] rules_channel_id: The id of the channel where guilds display rules and/or guidelines
        :param Optional[int] public_updates_channel_id: The id of the channel where admins and moderators of community guilds receive notices from Discord
        :param Optional[str] preferred_locale: The preferred locale of a community guild used in server discovery and notices from Discord; defaults to "en-US"
        :param Optional[str] description: The description for the guild, if the guild is discoverable
        :param Optional[bool] premium_progress_bar_enabled: Whether the guild's boost progress bar is enabled
        :param Optional[str] reason: The reason for the modifying
        :return: The modified guild
        :rtype: Guild
        """
        if not self._client:
            raise LibraryException(code=13)
        if (
            suppress_join_notifications is MISSING
            and suppress_premium_subscriptions is MISSING
            and suppress_guild_reminder_notifications is MISSING
            and suppress_join_notification_replies is MISSING
        ):
            system_channel_flags = MISSING
        else:
            #  sourcery skip: hoist-if-from-if
            system_channel_flags = self.system_channel_flags or 0

            if suppress_join_notifications is not MISSING:
                if suppress_join_notifications:
                    system_channel_flags |= 1 << 0
                else:
                    system_channel_flags &= ~(1 << 0)

            if suppress_premium_subscriptions is not MISSING:
                if suppress_premium_subscriptions:
                    system_channel_flags |= 1 << 1
                else:
                    system_channel_flags &= ~(1 << 1)

            if suppress_guild_reminder_notifications is not MISSING:
                if suppress_guild_reminder_notifications:
                    system_channel_flags |= 1 << 2
                else:
                    system_channel_flags &= ~(1 << 2)

            if suppress_join_notification_replies is not MISSING:
                if suppress_join_notification_replies:
                    system_channel_flags |= 1 << 3
                else:
                    system_channel_flags &= ~(1 << 3)

        payload = {}

        if name is not MISSING:
            payload["name"] = name
        if verification_level is not MISSING:
            payload["verification_level"] = verification_level.value
        if default_message_notifications is not MISSING:
            payload["default_message_notifications"] = default_message_notifications.value
        if explicit_content_filter is not MISSING:
            payload["explicit_content_filter"] = explicit_content_filter.value
        if afk_channel_id is not MISSING:
            payload["afk_channel_id"] = afk_channel_id
        if afk_timeout is not MISSING:
            payload["afk_timeout"] = afk_timeout
        if owner_id is not MISSING:
            payload["owner_id"] = owner_id
        if system_channel_id is not MISSING:
            payload["system_channel_id"] = system_channel_id
        if system_channel_flags is not MISSING:
            payload["system_channel_flags"] = system_channel_flags
        if rules_channel_id is not MISSING:
            payload["rules_channel_id"] = rules_channel_id
        if public_updates_channel_id is not MISSING:
            payload["public_updates_channel_id"] = rules_channel_id
        if preferred_locale is not MISSING:
            payload["preferred_locale"] = preferred_locale
        if description is not MISSING:
            payload["description"] = description
        if premium_progress_bar_enabled is not MISSING:
            payload["premium_progress_bar_enabled"] = premium_progress_bar_enabled
        if icon is not MISSING:
            payload["icon"] = icon.data if isinstance(icon, Image) else icon  # in case it is `None`
        if splash is not MISSING:
            payload["splash"] = splash.data if isinstance(splash, Image) else splash
        if discovery_splash is not MISSING:
            payload["discovery_splash"] = (
                splash.data if isinstance(discovery_splash, Image) else discovery_splash
            )
        if banner is not MISSING:
            payload["banner"] = banner.data if isinstance(banner, Image) else banner

        res = await self._client.modify_guild(
            guild_id=int(self.id),
            payload=payload,
            reason=reason,
        )

        self.update(res)
        return self

    async def set_name(
        self,
        name: str,
        *,
        reason: Optional[str] = None,
    ) -> "Guild":
        """
        .. versionadded:: 4.2.0

        Sets the name of the guild.

        :param str name: The new name of the guild
        :param Optional[str] reason: The reason of the edit
        """
        return await self.modify(name=name, reason=reason)

    async def set_verification_level(
        self,
        verification_level: VerificationLevel,
        *,
        reason: Optional[str] = None,
    ) -> "Guild":
        """
        .. versionadded:: 4.2.0

        Sets the verification level of the guild.

        :param VerificationLevel verification_level: The new verification level of the guild
        :param Optional[str] reason: The reason of the edit
        """
        return await self.modify(verification_level=verification_level, reason=reason)

    async def set_default_message_notifications(
        self,
        default_message_notifications: DefaultMessageNotificationLevel,
        *,
        reason: Optional[str] = None,
    ) -> "Guild":
        """
        .. versionadded:: 4.2.0

        Sets the default message notifications level of the guild.

        :param DefaultMessageNotificationLevel default_message_notifications: The new default message notification level of the guild
        :param Optional[str] reason: The reason of the edit
        """
        return await self.modify(
            default_message_notifications=default_message_notifications, reason=reason
        )

    async def set_explicit_content_filter(
        self,
        explicit_content_filter: ExplicitContentFilterLevel,
        *,
        reason: Optional[str] = None,
    ) -> "Guild":
        """
        .. versionadded:: 4.2.0

        Sets the explicit content filter level of the guild.

        :param ExplicitContentFilterLevel explicit_content_filter: The new explicit content filter level of the guild
        :param Optional[str] reason: The reason of the edit
        """
        return await self.modify(explicit_content_filter=explicit_content_filter, reason=reason)

    async def set_afk_channel(
        self,
        afk_channel_id: int,
        *,
        reason: Optional[str] = None,
    ) -> "Guild":
        """
        .. versionadded:: 4.2.0

        Sets the afk channel of the guild.

        :param int afk_channel_id: The new name of the guild
        :param Optional[str] reason: The reason of the edit
        """
        return await self.modify(afk_channel_id=afk_channel_id, reason=reason)

    async def set_afk_timeout(
        self,
        afk_timeout: int,
        *,
        reason: Optional[str] = None,
    ) -> "Guild":
        """
        .. versionadded:: 4.2.0

        Sets the afk timeout of the guild.

        :param int afk_timeout: The new afk timeout of the guild
        :param Optional[str] reason: The reason of the edit
        """
        return await self.modify(afk_timeout=afk_timeout, reason=reason)

    async def set_system_channel(
        self,
        system_channel_id: int,
        *,
        reason: Optional[str] = None,
    ) -> "Guild":
        """
        .. versionadded:: 4.2.0

        Sets the system channel of the guild.

        :param int system_channel_id: The new system channel id of the guild
        :param Optional[str] reason: The reason of the edit
        """
        return await self.modify(system_channel_id=system_channel_id, reason=reason)

    async def set_rules_channel(
        self,
        rules_channel_id: int,
        *,
        reason: Optional[str] = None,
    ) -> "Guild":
        """
        .. versionadded:: 4.2.0

        Sets the rules channel of the guild.

        :param int rules_channel_id: The new rules channel id of the guild
        :param Optional[str] reason: The reason of the edit
        """
        return await self.modify(rules_channel_id=rules_channel_id, reason=reason)

    async def set_public_updates_channel(
        self,
        public_updates_channel_id: int,
        *,
        reason: Optional[str] = None,
    ) -> "Guild":
        """
        .. versionadded:: 4.2.0

        Sets the public updates channel of the guild.

        :param int public_updates_channel_id: The new public updates channel id of the guild
        :param Optional[str] reason: The reason of the edit
        """
        return await self.modify(public_updates_channel_id=public_updates_channel_id, reason=reason)

    async def set_preferred_locale(
        self,
        preferred_locale: str,
        *,
        reason: Optional[str] = None,
    ) -> "Guild":
        """
        .. versionadded:: 4.2.0

        Sets the preferred locale of the guild.

        :param str preferred_locale: The new preferredlocale of the guild
        :param Optional[str] reason: The reason of the edit
        """
        return await self.modify(preferred_locale=preferred_locale, reason=reason)

    async def set_description(
        self,
        description: str,
        *,
        reason: Optional[str] = None,
    ) -> "Guild":
        """
        .. versionadded:: 4.2.0

        Sets the description of the guild.

        :param str description: The new description of the guild
        :param Optional[str] reason: The reason of the edit
        """
        return await self.modify(description=description, reason=reason)

    async def set_premium_progress_bar_enabled(
        self,
        premium_progress_bar_enabled: bool,
        *,
        reason: Optional[str] = None,
    ) -> "Guild":
        """
        .. versionadded:: 4.2.0

        Sets the visibility of the premium progress bar of the guild.

        :param bool premium_progress_bar_enabled: Whether the bar is enabled or not
        :param Optional[str] reason: The reason of the edit
        """
        return await self.modify(
            premium_progress_bar_enabled=premium_progress_bar_enabled, reason=reason
        )

    async def set_icon(
        self,
        icon: Image,
        *,
        reason: Optional[str] = None,
    ) -> "Guild":
        """
        .. versionadded:: 4.2.0

        Sets the icon of the guild.

        :param Image icon: The new icon of the guild
        :param Optional[str] reason: The reason of the edit
        """
        return await self.modify(icon=icon, reason=reason)

    async def set_splash(
        self,
        splash: Image,
        *,
        reason: Optional[str] = None,
    ) -> "Guild":
        """
        .. versionadded:: 4.2.0

        Sets the splash of the guild.

        :param Image splash: The new splash of the guild
        :param Optional[str] reason: The reason of the edit
        """
        return await self.modify(splash=splash, reason=reason)

    async def set_discovery_splash(
        self,
        discovery_splash: Image,
        *,
        reason: Optional[str] = None,
    ) -> "Guild":
        """
        .. versionadded:: 4.2.0

        Sets the discovery_splash of the guild.

        :param Image discovery_splash: The new discovery_splash of the guild
        :param Optional[str] reason: The reason of the edit
        """
        return await self.modify(discovery_splash=discovery_splash, reason=reason)

    async def set_banner(
        self,
        banner: Image,
        *,
        reason: Optional[str] = None,
    ) -> "Guild":
        """
        .. versionadded:: 4.2.0

        Sets the banner of the guild.

        :param Image banner: The new banner of the guild
        :param Optional[str] reason: The reason of the edit
        """
        return await self.modify(banner=banner, reason=reason)

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
    ) -> "ScheduledEvents":
        """
        .. versionadded:: 4.0.2

        Creates a scheduled event for the guild.

        :param str name: The name of the event
        :param EntityType entity_type: The entity type of the scheduled event
        :param datetime.isoformat scheduled_start_time: The time to schedule the scheduled event
        :param Optional[datetime.isoformat] scheduled_end_time: The time when the scheduled event is scheduled to end
        :param Optional[EventMetadata] entity_metadata: The entity metadata of the scheduled event
        :param Optional[int] channel_id: The channel id of the scheduled event.
        :param Optional[str] description: The description of the scheduled event
        :param Optional[Image] image: The cover image of the scheduled event
        :return: The created event
        :rtype: ScheduledEvents
        """
        if not self._client:
            raise LibraryException(code=13)
        if entity_type != EntityType.EXTERNAL and channel_id is MISSING:
            raise LibraryException(
                message="channel_id is required when entity_type is not external!", code=12
            )
        if entity_type == EntityType.EXTERNAL and entity_metadata is MISSING:
            raise LibraryException(
                message="entity_metadata is required for external events!", code=12
            )
        if entity_type == EntityType.EXTERNAL and scheduled_end_time is MISSING:
            raise LibraryException(message="External events require an end time!", code=12)

        payload = {
            "name": name,
            "entity_type": entity_type.value,
            "scheduled_start_time": scheduled_start_time,
            "privacy_level": 2,
        }

        if scheduled_end_time is not MISSING:
            payload["scheduled_end_time"] = scheduled_end_time
        if entity_metadata is not MISSING:
            payload["entity_metadata"] = entity_metadata._json
        if channel_id is not MISSING:
            payload["channel_id"] = channel_id
        if description is not MISSING:
            payload["description"] = description
        if image is not MISSING:
            payload["image"] = image.data if isinstance(image, Image) else image

        res = await self._client.create_scheduled_event(
            guild_id=self.id,
            payload=payload,
        )
        return ScheduledEvents(**res)

    async def get_scheduled_events(self, with_user_count: bool) -> List["ScheduledEvents"]:
        """
        .. versionadded:: 4.3.2

        Gets all scheduled events of the guild.

        :param bool with_user_count: A boolean to include number of users subscribed to the associated event, if given.
        :return: The sheduled events of the guild.
        :rtype: List[ScheduledEvents]
        """
        if not self._client:
            raise LibraryException(code=13)
        res = await self._client.get_scheduled_events(
            guild_id=self.id, with_user_count=with_user_count
        )
        return [ScheduledEvents(**scheduled_event) for scheduled_event in res] if res else []

    async def modify_scheduled_event(
        self,
        event_id: Union[int, "ScheduledEvents", Snowflake],
        name: Optional[str] = MISSING,
        entity_type: Optional[EntityType] = MISSING,
        scheduled_start_time: Optional[datetime.isoformat] = MISSING,
        scheduled_end_time: Optional[datetime.isoformat] = MISSING,
        entity_metadata: Optional["EventMetadata"] = MISSING,
        channel_id: Optional[int] = MISSING,
        description: Optional[str] = MISSING,
        status: Optional[EventStatus] = MISSING,
        image: Optional[Image] = MISSING,
        # privacy_level, TODO: implement when more levels available
    ) -> "ScheduledEvents":
        """
        .. versionadded:: 4.0.2

        Edits a scheduled event of the guild.

        :param Union[int, ScheduledEvents, Snowflake] event_id: The id of the event to edit
        :param Optional[str] name: The name of the event
        :param Optional[EntityType] entity_type: The entity type of the scheduled event
        :param Optional[datetime.isoformat] scheduled_start_time: The time to schedule the scheduled event
        :param Optional[datetime.isoformat] scheduled_end_time: The time when the scheduled event is scheduled to end
        :param Optional[EventMetadata] entity_metadata: The entity metadata of the scheduled event
        :param Optional[int] channel_id: The channel id of the scheduled event.
        :param Optional[str] description: The description of the scheduled event
        :param Optional[EventStatus] status: The status of the scheduled event
        :param Optional[Image] image: The cover image of the scheduled event
        :return: The modified event
        :rtype: ScheduledEvents
        """
        if not self._client:
            raise LibraryException(code=13)
        if entity_type == EntityType.EXTERNAL and entity_metadata is MISSING:
            raise LibraryException("entity_metadata is required for external events!", code=12)
        if entity_type == EntityType.EXTERNAL and scheduled_end_time is MISSING:
            raise LibraryException("External events require an end time!")

        payload = {}
        if name is not MISSING:
            payload["name"] = name
        if channel_id is not MISSING:
            payload["channel_id"] = channel_id
        if scheduled_start_time is not MISSING:
            payload["scheduled_start_time"] = scheduled_start_time
        if entity_type is not MISSING:
            payload["entity_type"] = entity_type.value
            payload["channel_id"] = None
        if scheduled_end_time is not MISSING:
            payload["scheduled_end_time"] = scheduled_end_time
        if entity_metadata is not MISSING:
            payload["entity_metadata"] = entity_metadata._json
        if description is not MISSING:
            payload["description"] = description
        if status is not MISSING:
            payload["status"] = status
        if image is not MISSING:
            payload["image"] = image.data if isinstance(image, Image) else image

        _event_id = event_id.id if isinstance(event_id, ScheduledEvents) else event_id

        res = await self._client.modify_scheduled_event(
            guild_id=self.id,
            guild_scheduled_event_id=_event_id,
            payload=payload,
        )
        return ScheduledEvents(**res)

    async def delete_scheduled_event(
        self, event_id: Union[int, "ScheduledEvents", Snowflake]
    ) -> None:
        """
        .. versionadded:: 4.0.2

        Deletes a scheduled event of the guild.

        :param Union[int, ScheduledEvents, Snowflake] event_id: The id of the event to delete
        """
        if not self._client:
            raise LibraryException(code=13)

        _event_id = event_id.id if isinstance(event_id, ScheduledEvents) else event_id

        await self._client.delete_scheduled_event(
            guild_id=self.id,
            guild_scheduled_event_id=Snowflake(_event_id),
        )

    async def get_all_channels(self) -> List[Channel]:
        """
        .. versionadded:: 4.0.2

        Gets all channels of the guild as list.

        :return: The channels of the guild.
        :rtype: List[Channel]
        """
        if not self._client:
            raise LibraryException(code=13)
        res = await self._client.get_all_channels(int(self.id))
        self.channels = [Channel(**channel, _client=self._client) for channel in res]
        return self.channels

    async def get_all_active_threads(self) -> List[Channel]:
        """
        .. versionadded:: 4.3.0

        Gets all active threads of the guild.

        :return: The threads of the guild.
        :rtype: List[Thread]
        """
        if not self._client:
            raise LibraryException(code=13)
        res = await self._client.list_active_threads(int(self.id))
        threads = [Thread(**thread, _client=self._client) for thread in res["threads"]]
        members = [ThreadMember(**member, _client=self._client) for member in res["members"]]
        for member in members:
            for thread in threads:
                if int(thread.id) == int(member.id):
                    thread.member = member
                    break
        self.threads = threads
        return self.threads

    async def get_all_roles(self) -> List[Role]:
        """
        .. versionadded:: 4.0.2

        Gets all roles of the guild as list.

        :return: The roles of the guild.
        :rtype: List[Role]
        """
        if not self._client:
            raise LibraryException(code=13)
        res = await self._client.get_all_roles(int(self.id))
        self.roles = [Role(**role, _client=self._client) for role in res]
        return self.roles

    async def get_role(
        self,
        role_id: int,
    ) -> Role:
        """
        .. versionadded:: 4.2.0

        Gets a role of the guild.

        :param int role_id: The id of the role to get
        :return: The role as object
        :rtype: Role
        """

        for role in self.roles:
            if int(role.id) == role_id:
                return role
        if not self._client:
            raise LibraryException(code=13)
        roles = await self._client.get_all_roles(guild_id=int(self.id))
        self.roles = [Role(**_) for _ in roles]
        for role in self.roles:
            if int(role.id) == role_id:
                return role
        raise LibraryException(
            message="The role you looked for was not found!", code=0, severity=30
        )

    async def modify_role_position(
        self,
        role_id: Union[Role, int],
        position: int,
        reason: Optional[str] = None,
    ) -> List[Role]:
        """
        .. versionadded:: 4.0.2

        Modifies the position of a role in the guild.

        :param Union[Role, int] role_id: The id of the role to modify the position of
        :param int position: The new position of the role
        :param Optional[str] reason: The reason for the modifying
        :return: List of guild roles with updated hierarchy
        :rtype: List[Role]
        """
        return await self.modify_role_positions(
            changes=[
                {"id": role_id.id if isinstance(role_id, Role) else role_id, "position": position}
            ],
            reason=reason,
        )

    async def modify_role_positions(
        self,
        changes: List[dict],
        reason: Optional[str] = None,
    ) -> List[Role]:
        """
        .. versionadded:: 4.2.0

        Modifies the positions of multiple roles in the guild.

        :param List[dict] changes: A list of dicts containing roles (id) and their new positions (position)
        :param Optional[str] reason: The reason for the modifying
        :return: List of guild roles with updated hierarchy
        :rtype: List[Role]
        """
        if not self._client:
            raise LibraryException(code=13)
        res = await self._client.modify_guild_role_positions(
            guild_id=int(self.id),
            payload=[
                {"id": int(change["id"].id), "position": change["position"]}
                if isinstance(change["id"], Role)
                else change
                for change in changes
            ],
            reason=reason,
        )
        self.roles = [Role(**role, _client=self._client) for role in res]
        return self.roles

    async def get_bans(
        self,
        limit: Optional[int] = 1000,
        before: Optional[int] = MISSING,
        after: Optional[int] = MISSING,
    ) -> List[Dict[str, User]]:
        """
        .. versionadded:: 4.0.2

        .. versionchanged:: 4.2.0
            The method now gets an amount of bans as the endpoint on the Discord API has been paginated.
            To get all bans use the :meth:`.get_all_bans` method.

        Gets a list of banned users.

        :param Optional[int] limit: Number of users to return. Defaults to 1000.
        :param Optional[int] before: Consider only users before the given User ID snowflake.
        :param Optional[int] after: Consider only users after the given User ID snowflake.
        :return: List of banned users with reasons
        :rtype: List[Dict[str, User]]
        """
        if not self._client:
            raise LibraryException(code=13)
        _before = before if before is not MISSING else None
        _after = after if after is not MISSING else None
        res = await self._client.get_guild_bans(int(self.id), limit, _before, _after)
        for ban in res:
            ban["user"] = User(**ban["user"])
        return res

    async def get_all_bans(self) -> List[Dict[str, User]]:
        """
        .. versionadded:: 4.2.0

        Gets all bans of the guild.

        :return: List of banned users with reasons
        :rtype: List[Dict[str, User]]
        """

        if not self._client:
            raise LibraryException(code=13)

        _after = None
        _all: list = []

        res: list = await self._client.get_guild_bans(int(self.id), limit=1000)

        while len(res) >= 1000:
            for ban in res:
                ban["user"] = User(**ban["user"])
            _all.extend(res)
            _after = int(res[-1]["user"].id)

            res = await self._client.get_guild_bans(
                int(self.id),
                after=_after,
            )

        for ban in res:
            ban["user"] = User(**ban["user"])
        _all.extend(res)

        return _all

    async def prune(
        self,
        days: int = 7,
        compute_prune_count: bool = True,
        include_roles: Optional[Union[List[Role], List[int], List[Snowflake], List[str]]] = MISSING,
    ) -> Optional[int]:
        """
        .. versionadded:: 4.3.2

        Begins a prune operation.

        :param Optional[int] days: Number of days to count, minimum 1, maximum 30. Defaults to 7.
        :param Optional[bool] compute_prune_count: Whether the returned "pruned" dict contains the computed prune count or None.
        :param Optional[Union[List[Role], List[int], List[Snowflake], List[str]]] include_roles: Role IDs to include, if given.
        :return: The number of pruned members, if compute_prune_count is not false. Otherwise returns None.
        :rtype: Optional[int]
        """
        if not self._client:
            raise LibraryException(code=13)

        if include_roles is not MISSING:
            _roles = [
                int(role.id) if isinstance(role, Role) else int(role) for role in include_roles
            ]
        else:
            _roles = None

        res: dict = await self._client.begin_guild_prune(
            guild_id=int(self.id),
            days=days,
            compute_prune_count=compute_prune_count,
            include_roles=_roles,
        )

        return res.get("pruned")

    async def get_prune_count(
        self,
        days: int = 7,
        include_roles: Optional[Union[List[Role], List[int], List[Snowflake], List[str]]] = MISSING,
    ) -> int:
        """
         .. versionadded:: 4.3.2

        Returns the number of members that would be removed in a prune operation.

        :param Optional[int] days: Number of days to count, minimum 1, maximum 30. Defaults to 7.
        :param Optional[Union[List[Role], List[int], List[Snowflake], List[str]]] include_roles: Role IDs to include, if given.
        :return: The number of members that would be pruned.
        :rtype: int
        """
        if not self._client:
            raise LibraryException(code=13)

        if include_roles is not MISSING:
            _roles = [
                int(role.id) if isinstance(role, Role) else int(role) for role in include_roles
            ]
        else:
            _roles = None

        res: dict = await self._client.get_guild_prune_count(
            guild_id=int(self.id),
            days=days,
            include_roles=_roles,
        )

        return res.get("pruned")

    async def get_emoji(
        self,
        emoji_id: int,
    ) -> Emoji:
        """
        .. versionadded:: 4.2.0

        Gets an emoji of the guild and returns it.

        :param int emoji_id: The id of the emoji
        :return: The specified Emoji, if found
        :rtype: Emoji
        """
        if not self._client:
            raise LibraryException(code=13)

        res = await self._client.get_guild_emoji(guild_id=int(self.id), emoji_id=emoji_id)
        _emoji = Emoji(**res, _client=self._client)

        if self.emojis is None:
            self.emojis = []

        for index, emoji in enumerate(self.emojis):
            if int(emoji.id) == emoji_id:
                self.emojis[index] = _emoji
                break
        else:
            self.emojis.append(_emoji)
        return _emoji

    async def get_all_emoji(self) -> List[Emoji]:
        """
        .. versionadded:: 4.2.0

        Gets all emojis of a guild.

        :return: All emojis of the guild
        :rtype: List[Emoji]
        """
        if not self._client:
            raise LibraryException(code=13)
        res = await self._client.get_all_emoji(guild_id=int(self.id))
        self.emojis = [Emoji(**emoji, _client=self._client) for emoji in res]
        return self.emojis

    async def create_emoji(
        self,
        image: Image,
        name: Optional[str] = MISSING,
        roles: Optional[Union[List[Role], List[int]]] = MISSING,
        reason: Optional[str] = None,
    ) -> Emoji:
        """
        .. versionadded:: 4.2.0

        Creates an Emoji in the guild.

        :param Image image: The image of the emoji.
        :param Optional[str] name: The name of the emoji. If not specified, the filename will be used
        :param Optional[Union[List[Role], List[int]]] roles: Roles allowed to use this emoji
        :param Optional[str] reason: The reason of the creation
        """
        if not self._client:
            raise LibraryException(code=13)

        _name = name if name is not MISSING else image.filename

        payload: dict = {
            "name": _name,
            "image": image.data,
        }

        if roles is not MISSING:
            _roles = [role.id if isinstance(role, Role) else role for role in roles]
            payload["roles"] = _roles

        res = await self._client.create_guild_emoji(
            guild_id=int(self.id), payload=payload, reason=reason
        )

        if self.emojis is None:
            self.emojis = []

        _emoji = Emoji(**res)
        self.emojis.append(_emoji)
        return _emoji

    async def modify_emoji(
        self,
        emoji_id: Union[int, Snowflake, Emoji],
        name: Optional[str] = MISSING,
        roles: Optional[Union[List[Role], List[int]]] = MISSING,
        reason: Optional[str] = None,
    ) -> Emoji:
        """
        .. versionadded:: 4.4.0

        Edits an Emoji in the guild.

        :param Union[int, Snowflake, Emoji] emoji_id: The id of the emoji to edit
        :param Optional[str] name: The name of the emoji. If not specified, the filename will be used
        :param Optional[Union[List[Role], List[int]]] roles: Roles allowed to use this emoji
        :param Optional[str] reason: The reason of the modification
        :return: The modified emoji object
        :rtype: Emoji
        """
        if not self._client:
            raise LibraryException(code=13)

        emoji_id = int(emoji_id.id if isinstance(emoji_id, Emoji) else emoji_id)

        payload: dict = {}

        if name is not MISSING:
            payload["name"] = name

        if roles is not MISSING:
            payload["roles"] = [int(role.id if isinstance(role, Role) else role) for role in roles]

        res = await self._client.modify_guild_emoji(
            guild_id=int(self.id), emoji_id=emoji_id, payload=payload, reason=reason
        )

        _emoji = Emoji(**res, _client=self._client)
        if self.emojis is None:
            self.emojis = []
        for index, item in enumerate(self.emojis):
            if item.id == emoji_id:
                self.roles[index] = _emoji
                break
        else:
            self.roles.append(_emoji)
        return _emoji

    async def delete_emoji(
        self,
        emoji: Union[Emoji, int],
        reason: Optional[str] = None,
    ) -> None:
        """
        .. versionadded:: 4.2.0

        Deletes an emoji of the guild.

        :param Union[Emoji, int] emoji: The emoji or the id of the emoji to delete
        :param Optional[str] reason: The reason of the deletion
        """
        if not self._client:
            raise LibraryException(code=13)
        emoji_id = emoji.id if isinstance(emoji, Emoji) else emoji
        await self._client.delete_guild_emoji(
            guild_id=int(self.id),
            emoji_id=emoji_id,
            reason=reason,
        )

        if not self.emojis:
            return
        for item in self.emojis:
            if int(item.id) == int(emoji_id):
                return self.emojis.remove(item)

    async def get_stickers(self) -> Optional[List[Sticker]]:
        """
        .. versionadded:: 4.3.2

        Get the stickers for a guild.

        :return: List of stickers of the guild.
        :rtype: Optional[List[Sticker]]
        """
        if not self._client:
            raise LibraryException(code=13)

        res = await self._client.list_guild_stickers(guild_id=int(self.id))

        stickers = [Sticker(**sticker) for sticker in res]
        self.stickers = stickers

        return self.stickers

    async def get_nitro_sticker_packs(self) -> List[StickerPack]:
        """
        .. versionadded:: 4.3.2

        Gets the list of sticker packs available to Nitro subscribers.

        :return: List of sticker packs.
        :rtype: List[StickerPack]
        """
        if not self._client:
            raise LibraryException(code=13)

        res = await self._client.list_nitro_sticker_packs()

        return [StickerPack(**sticker_pack) for sticker_pack in res["sticker_packs"]]

    async def create_sticker(
        self,
        file: File,
        tags: str,
        name: Optional[str] = MISSING,
        description: Optional[str] = MISSING,
        reason: Optional[str] = None,
    ) -> Sticker:
        """
        .. versionadded:: 4.3.2

        Creates a new sticker for the guild.

        :param File file: The file of the sticker.
        :param str tags: The tags of the sticker.
        :param Optional[str] name: The name of the sticker.
        :param Optional[str] description: The description of the sticker.
        :param Optional[str] reason: The reason of the creation.
        :return: Created sticker for the guild.
        :rtype: Sticker
        """
        if not self._client:
            raise LibraryException(code=13)

        _name = name if name is not MISSING else file._filename

        payload: dict = {
            "name": _name,
            "tags": tags,
        }

        if description is not MISSING:
            payload["description"] = description

        res = await self._client.create_guild_sticker(
            payload=payload, file=file, guild_id=int(self.id), reason=reason
        )

        if self.stickers is None:
            self.stickers = []

        _sticker = Sticker(**res)
        self.stickers.append(_sticker)
        return _sticker

    async def modify_sticker(
        self,
        sticker_id: Union[Sticker, Snowflake, int, str],
        name: Optional[str] = MISSING,
        description: Optional[str] = MISSING,
        reason: Optional[str] = None,
    ) -> Sticker:
        """
        .. versionadded:: 4.3.2

        Modifies the sticker of the guild.

        :param Union[Sticker, Snowflake, int] sticker_id: The sticker or ID of the sticker.
        :param Optional[str] name: The name of the sticker.
        :param Optional[str] description: The description of the sticker.
        :param Optional[str] reason: The reason of the modification.
        :return: Modified sticker.
        :rtype: Sticker
        """
        if not self._client:
            raise LibraryException(code=13)

        _id = int(sticker_id.id) if isinstance(sticker_id, Sticker) else int(sticker_id)

        payload: dict = {}

        if name is not MISSING:
            payload["name"] = name
        if description is not MISSING:
            payload["description"] = description

        res = await self._client.modify_guild_sticker(
            payload=payload, guild_id=int(self.id), sticker_id=_id, reason=reason
        )
        _sticker = Sticker(**res)

        if not self.stickers:
            self.stickers = [_sticker]
            return _sticker

        for sticker in self.stickers:
            if sticker.id == _sticker.id:
                sticker.update(res)
                return sticker

    async def delete_sticker(
        self,
        sticker_id: Union[Sticker, Snowflake, int, str],
        reason: Optional[str] = None,
    ):
        """
        .. versionadded:: 4.3.2

        Deletes the sticker of the guild.

        :param Union[Sticker, Snowflake, int] sticker_id: The sticker or ID of the sticker.
        :param  Optional[str] reason: The reason of the deletion.
        """
        if not self._client:
            raise LibraryException(code=13)

        _id = int(sticker_id.id) if isinstance(sticker_id, Sticker) else int(sticker_id)

        await self._client.delete_guild_sticker(
            guild_id=int(self.id), sticker_id=_id, reason=reason
        )

        if not self.stickers:
            return
        for sticker in self.stickers:
            if int(sticker.id) == _id:
                self.stickers.remove(sticker)
                break

    async def get_list_of_members(
        self,
        limit: Optional[int] = 1,
        after: Optional[Union[Member, int]] = MISSING,
    ) -> List[Member]:
        """
        .. versionadded:: 4.2.0

        Lists the members of a guild.

        :param Optional[int] limit: How many members to get from the API. Max is 1000.
        :param Optional[Union[Member, int]] after: Get only Members after this member.
        :return: A list of members
        :rtype: List[Member]
        """
        if not self._client:
            raise LibraryException(code=13)
        if after is not MISSING:
            _after = after if isinstance(after, int) else int(after.id)
        else:
            _after = None
        res = await self._client.get_list_of_members(
            guild_id=int(self.id), limit=limit, after=_after
        )
        _members = [Member(**member, _client=self._client, guild_id=self.id) for member in res]
        if self.members is None:
            self.members = []
        for member in _members:
            if member not in self.members:
                self.members.append(member)
        return _members

    async def search_members(self, query: str, limit: Optional[int] = 1) -> List[Member]:
        """
        .. versionadded:: 4.2.0
        Search the guild for members whose username or nickname starts with provided string.

        :param str query: The string to search for
        :param Optional[int] limit: The number of members to return.
        :return: A list of matching members
        :rtype: List[Member]
        """
        if not self._client:
            raise LibraryException(code=13)
        res = await self._client.search_guild_members(
            guild_id=int(self.id), query=query, limit=limit
        )
        return [Member(**member, _client=self._client, guild_id=self.id) for member in res]

    async def get_all_members(self) -> List[Member]:
        """
        .. versionadded:: 4.2.0

        .. deprecated:: 4.3.2
            Use :meth:`.get_members` instead.

        Gets all members of a guild.

        .. warning:: Calling this method can lead to rate-limits in larger guilds.

        :return: Returns a list of all members of the guild
        :rtype: List[Member]
        """
        warn(
            "This method has been deprecated in favour of the 'get_members' method.",
            DeprecationWarning,
        )

        if not self._client:
            raise LibraryException(code=13)

        _all_members: List[dict] = []
        _last_member: Member
        _members: List[dict] = await self._client.get_list_of_members(
            guild_id=int(self.id), limit=100
        )
        if len(_members) == 100:
            while len(_members) >= 100:
                _all_members.extend(_members)
                _last_member = Member(**_members[-1])
                _members = await self._client.get_list_of_members(
                    guild_id=int(self.id), limit=100, after=int(_last_member.id)
                )
        _all_members.extend(_members)
        self.members = [Member(**_, _client=self._client, guild_id=self.id) for _ in _all_members]
        return self.members

    def get_members(
        self,
        start_at: Optional[Union[int, str, Snowflake, "Message"]] = MISSING,
        maximum: Optional[int] = inf,
        check: Optional[Callable[[Member], Union[bool, Awaitable[bool]]]] = None,
    ) -> AsyncMembersIterator:
        """
        .. versionadded:: 4.3.2

        :param Optional[Union[int, str, Snowflake, Member]] start_at: The member to begin getting the members from
        :param Optional[int] maximum: A set maximum of members to get before stopping the iteration
        :param Optional[Callable[[Member], Union[bool, Awaitable[bool]]]] check: A custom check to ignore certain members

        :return: An asynchronous iterator over the members of the guild
        :rtype: AsyncMembersIterator
        """
        if not self._client:
            raise LibraryException(code=13)

        return AsyncMembersIterator(
            self._client, self, maximum=maximum, start_at=start_at, check=check
        )

    async def get_webhooks(self) -> List[Webhook]:
        """
        .. versionadded:: 4.3.0

        Get all webhooks of a guild.
        """
        if not self._client:
            raise LibraryException(code=13)

        res = await self._client.get_guild_webhooks(int(self.id))

        return [Webhook(**_, _client=self._client) for _ in res]

    async def list_auto_moderation_rules(self) -> List["AutoModerationRule"]:
        """
        .. versionadded:: 4.3.0

        Lists all AutoMod rules.
        """
        if not self._client:
            raise LibraryException(code=13)

        from .gw import AutoModerationRule

        res = await self._client.list_auto_moderation_rules(int(self.id))

        return [AutoModerationRule(**_) for _ in res]

    async def get_auto_moderation_rule(
        self, rule_id: Union[int, Snowflake]
    ) -> "AutoModerationRule":
        """
        .. versionadded:: 4.3.0

        Gets a AutoMod rule from its ID

        :param Union[int, Snowflake] rule_id: The ID of the rule to get
        :return: A AutoMod rule
        :rtype: AutoModerationRule
        """
        if not self._client:
            raise LibraryException(code=13)

        from .gw import AutoModerationRule

        res = await self._client.get_auto_moderation_rule(int(self.id), int(rule_id))

        return AutoModerationRule(**res)

    async def create_auto_moderation_rule(
        self,
        name: str,
        # event_type: int, # only 1 exists
        trigger_type: AutoModTriggerType,
        actions: List[AutoModAction],
        trigger_metadata: Optional[AutoModTriggerMetadata] = MISSING,
        enabled: Optional[bool] = False,
        exempt_roles: Optional[List[int]] = MISSING,
        exempt_channels: Optional[List[int]] = MISSING,
        reason: Optional[str] = None,
    ) -> "AutoModerationRule":
        """
        .. versionadded:: 4.3.0

        Creates an AutoMod rule

        :param str name: The name of the new rule.
        :param AutoModTriggerType trigger_type: The trigger type of the new rule.
        :param Optional[AutoModTriggerMetadata] trigger_metadata: The trigger metadata payload representation. This can be omitted based on the trigger type.
        :param List[AutoModAction] actions: The actions that will execute when the rule is triggered.
        :param Optional[bool] enabled: Whether the rule will be enabled upon creation. False by default.
        :param Optional[List[int]] exempt_roles: The role IDs that are whitelisted by the rule, if given. The maximum is 20.
        :param Optional[List[int]] exempt_channels: The channel IDs that are whitelisted by the rule, if given. The maximum is 20
        :param Optional[str] reason: The reason of the creation
        :return: The new AutoMod rule
        :rtype: AutoModerationRule
        """

        if not self._client:
            raise LibraryException(code=13)

        from .gw import AutoModerationRule

        event_type = 1
        _actions = None if actions is MISSING else [_._json for _ in actions]
        _trigger_metadata = None if trigger_metadata is MISSING else trigger_metadata._json
        _trigger_type = (
            None
            if trigger_type is MISSING
            else trigger_type
            if isinstance(trigger_type, int)
            else trigger_type.value
        )

        res = await self._client.create_auto_moderation_rule(
            guild_id=int(self.id),
            event_type=event_type,
            actions=_actions,
            trigger_type=_trigger_type,
            trigger_metadata=_trigger_metadata,
            name=name,
            enabled=enabled,
            exempt_roles=exempt_roles,
            exempt_channels=exempt_channels,
            reason=reason,
        )

        return AutoModerationRule(**res)

    async def modify_auto_moderation_rule(
        self,
        rule: Union[int, Snowflake, "AutoModerationRule"],
        name: str = MISSING,
        # event_type: int, # only 1 exists
        trigger_type: AutoModTriggerType = MISSING,
        actions: List[AutoModAction] = MISSING,
        trigger_metadata: Optional[AutoModTriggerMetadata] = MISSING,
        enabled: Optional[bool] = MISSING,
        exempt_roles: Optional[List[int]] = MISSING,
        exempt_channels: Optional[List[int]] = MISSING,
        reason: Optional[str] = None,
    ) -> "AutoModerationRule":  # noqa  # sourcery skip: compare-via-equals
        """
        .. versionadded:: 4.3.0

        Edits an AutoMod rule

        :param Union[int, Snowflake, AutoModerationRule] rule: The rule to modify
        :param str name: The name of the new rule.
        :param AutoModTriggerType trigger_type: The trigger type of the new rule.
        :param Optional[AutoModTriggerMetadata] trigger_metadata: The trigger metadata payload representation. This can be omitted based on the trigger type.
        :param List[AutoModAction] actions: The actions that will execute when the rule is triggered.
        :param Optional[bool] enabled: Whether the rule will be enabled upon creation. False by default.
        :param Optional[List[int]] exempt_roles: The role IDs that are whitelisted by the rule, if given. The maximum is 20.
        :param Optional[List[int]] exempt_channels: The channel IDs that are whitelisted by the rule, if given. The maximum is 20
        :param Optional[str] reason: The reason of the creation
        :return: The new AutoMod rule
        :rtype: AutoModerationRule
        """

        if not self._client:
            raise LibraryException(code=13)

        from .gw import AutoModerationRule

        if isinstance(rule, (int, Snowflake)):
            rule = await self.get_auto_moderation_rule(rule)

        event_type = 1

        _actions = actions if actions is not MISSING else [_._json for _ in rule.actions]
        _trigger_type = trigger_type if trigger_type is not MISSING else rule.trigger_type
        _trigger_metadata = (
            trigger_metadata if trigger_metadata is not MISSING else rule.trigger_metadata._json
        )
        _name = name if name is not MISSING else rule.name
        _enabled = enabled if enabled is not MISSING else rule.enabled
        _exempt_roles = exempt_roles if exempt_roles is not MISSING else rule.exempt_roles
        _exempt_channels = (
            exempt_channels if exempt_channels is not MISSING else rule.exempt_channels
        )

        res = await self._client.create_auto_moderation_rule(
            guild_id=int(self.id),
            event_type=event_type,
            actions=_actions,
            trigger_type=_trigger_type,
            trigger_metadata=_trigger_metadata,
            name=_name,
            enabled=_enabled,
            exempt_roles=_exempt_roles,
            exempt_channels=_exempt_channels,
            reason=reason,
        )
        return AutoModerationRule(**res)

    async def get_audit_logs(
        self,
        limit: Optional[int] = 100,
        user_id: Optional[Union[User, int, Snowflake]] = MISSING,
        action_type: Optional[Union[int, AuditLogEvents]] = MISSING,
        before: Optional[Union[int, Snowflake]] = MISSING,
    ) -> AuditLogs:
        """
        .. versionadded:: 4.3.0

        Gets the audit logs of the guild.

        :param Optional[int] limit: How many entries to get, default 100
        :param Optional[Union[User, int, Snowflake]] user_id: User ID snowflake. filter the log for actions made by a user.
        :param Optional[Union[int, AuditLogEvents]] action_type: The Type of the audit log action.
        :param Union[int, Snowflake] before: filter the log before a certain entry id.
        :return: The guild audit logs
        :rtype: AuditLogs
        """

        _user_id = (
            int(user_id.id if isinstance(user_id, User) else user_id)
            if user_id is not MISSING
            else None
        )
        _before = before if before is not MISSING else None
        _action_type = action_type if action_type is not MISSING else None

        res = await self._client.get_guild_auditlog(
            guild_id=int(self.id),
            limit=limit,
            before=_before,
            user_id=_user_id,
            action_type=_action_type,
        )
        return AuditLogs(**res)

    async def get_latest_audit_log_action(
        self,
        of: Union[
            User,
            Snowflake,
            AuditLogEvents,
            int,
            Member,
            Tuple[Union[User, Member, Snowflake, int], Union[AuditLogEvents, int]],
        ],
    ) -> AuditLogs:
        """
        .. versionadded:: 4.3.0

        Gets the latest audit log action of either a user or an action type

        :param Union[User, Snowflake, AuditLogEvents, int, Tuple[Union[User, Snowflake, int], Union[AuditLogEvents, int]]] of:
            The user/user ID or action type to look for.

            Detailed description:
                #.
                    :class:`.User` or :class:`.Member`, :class:`.Snowflake` or member or user ID as :class:`int`/:class:`str`:
                        :return: The latest audit log entry of this user.
                #.
                    :class:`.AuditLogEvents` or and AuditLogEvent as :class:`int` representation:
                        :return: The latest audit log entry of this type.
                #.
                     :class:`tuple` object:
                        - **Length 2!**
                        - First value of: :class:`.User` or :class:`.Member`, :class:`.Snowflake` or member or user ID as :class:`int`/:class:`str`
                        - Second value of: :class:`.AuditLogEvents` or and AuditLogEvent as :class:`int` representation.


                        :return: The latest audit log entry of this user AND this type combined


        :return: The latest AuditLog action that applies to the ``of`` parameter
        :rtype: AuditLogs
        """

        if isinstance(of, tuple):
            if len(of) != 2 or len(str(of[1])) > 3:
                raise LibraryException(
                    12,
                    "You specified invalid arguments in the tuple. Make sure the first argument"
                    "is the user ID and the second is the action type!",
                )

            _user = int(of[0].id if isinstance(of[0], (Member, User)) else of[0])
            res = await self._client.get_guild_auditlog(
                guild_id=int(self.id), user_id=_user, action_type=of[1]
            )

        elif isinstance(of, AuditLogEvents) or isinstance(of, int) and len(str(of)) <= 3:
            res = await self._client.get_guild_auditlog(
                guild_id=int(self.id), limit=1, action_type=of
            )

        else:
            if isinstance(of, (Member, User)):
                of = of.id
            res = await self._client.get_guild_auditlog(
                guild_id=int(self.id), user_id=int(of), limit=1
            )

        return AuditLogs(**res)

    async def get_full_audit_logs(
        self,
        user_id: Optional[Union[User, int, Snowflake]] = MISSING,
        action_type: Optional[Union[int, AuditLogEvents]] = MISSING,
    ) -> AuditLogs:
        """
        .. versionadded:: 4.3.0

        Gets the full audit log of the guild.

        :param Optional[Union[User, int, Snowflake]] user_id: User ID snowflake. filter the log for actions made by a user.
        :param Optional[Union[int, AuditLogEvents]] action_type: The type of the audit log action.
        :return: The full AuditLog of the guild
        :rtype: AuditLogs
        """
        double = False
        _action_type = action_type if action_type is not MISSING else None
        _user_id = (
            int(user_id.id if isinstance(user_id, User) else user_id)
            if user_id is not MISSING
            else None
        )
        _audit_log_dict: dict = {
            "audit_log_entries": [],
            "users": [],
            "integrations": [],
            "webhooks": [],
            "guild_scheduled_events": [],
            "threads": [],
            "application_commands": [],
            "auto_moderation_rules": [],
        }

        res = await self._client.get_guild_auditlog(
            guild_id=int(self.id), user_id=_user_id, action_type=_action_type, limit=100
        )

        if len(res["audit_log_entries"]) < 100:
            return AuditLogs(**res)

        while len(res["audit_log_entries"]) == 100:
            _before = res["audit_log_entries"][-1]["id"]

            double = False
            for key, values in res.items():
                for value in values:
                    if value not in _audit_log_dict[key]:
                        _audit_log_dict[key] = value
                    else:
                        double = True
                        # It is possible that an item is already present, however we should not break directly out
                        # in case other attributes are not present yet.
            if double:
                break

            res = await self._client.get_guild_auditlog(
                guild_id=int(self.id),
                user_id=_user_id,
                before=_before,
                action_type=_action_type,
                limit=100,
            )

        if not double:
            for key, values in res.items():
                for value in values:
                    if value not in _audit_log_dict[key]:
                        _audit_log_dict[key] = value

        return AuditLogs(**_audit_log_dict)

    async def get_invite(
        self,
        invite_code: str,
        with_counts: Optional[bool] = MISSING,
        with_expiration: Optional[bool] = MISSING,
        guild_scheduled_event_id: Optional[int] = MISSING,
    ) -> "Invite":
        """
        .. versionadded:: 4.3.4

        Gets the invite using its code.

        :param str invite_code: A string representing the invite code.
        :param Optional[bool] with_counts: Whether approximate_member_count and approximate_presence_count are returned.
        :param Optional[bool] with_expiration: Whether the invite's expiration date is returned.
        :param Optional[int] guild_scheduled_event_id: A guild scheduled event's ID.
        :return: An invite
        :rtype: Invite
        """
        if not self._client:
            raise LibraryException(code=13)

        _with_counts = with_counts if with_counts is not MISSING else None
        _with_expiration = with_expiration if with_expiration is not MISSING else None
        _guild_scheduled_event_id = (
            guild_scheduled_event_id if guild_scheduled_event_id is not MISSING else None
        )

        res = await self._client.get_invite(
            invite_code=invite_code,
            with_counts=_with_counts,
            with_expiration=_with_expiration,
            guild_scheduled_event_id=_guild_scheduled_event_id,
        )

        return Invite(**res, _client=self._client)

    async def delete_invite(self, invite_code: str, reason: Optional[str] = None) -> None:
        """
        .. versionadded:: 4.3.4

        Deletes the invite using its code.

        :param str invite_code: A string representing the invite code.
        :param Optional[str] reason: The reason of the deletion
        """
        if not self._client:
            raise LibraryException(code=13)

        await self._client.delete_invite(invite_code=invite_code, reason=reason)

    async def get_invites(self) -> List["Invite"]:
        """
        .. versionadded:: 4.3.4

        Gets invites of the guild.

        :return: A list of guild invites
        :rtype: List[Invite]
        """
        if not self._client:
            raise LibraryException(code=13)

        res = await self._client.get_guild_invites(guild_id=int(self.id))
        return [Invite(**_, _client=self._client) for _ in res]

    async def modify_bot_nick(self, new_nick: Optional[str] = MISSING) -> Member:
        """
        .. versionadded:: 4.4.0

        Changes a nickname of the current bot user in a guild.

        :param Optional[str] new_nick: The new nickname, if any.
        :return: The modified bot member object
        :rtype: Member
        """
        if not self._client:
            raise LibraryException(code=13)

        if new_nick is MISSING:
            raise LibraryException(code=12, message="new nick name must either a string or `None`")

        _member = Member(
            **await self._client.modify_self_nick_in_guild(int(self.id), new_nick),
            _client=self._client,
        )
        _member_id = int(_member.id)

        if self.members is None:
            self.members = []

        for index, member in enumerate(self.members):
            if int(member.id) == _member_id:
                self.members[index] = _member
                break
        else:
            self.members.append(_member)

        return _member

    @property
    def icon_url(self) -> Optional[str]:
        """
        .. versionadded:: 4.2.0

        Returns the URL of the guild's icon.

        :return: URL of the guild's icon (None will be returned if no icon is set)
        :rtype: str
        """
        if not self.icon:
            return None

        url = f"https://cdn.discordapp.com/icons/{int(self.id)}/{self.icon}"
        url += ".gif" if self.icon.startswith("a_") else ".png"
        return url

    @property
    def banner_url(self) -> Optional[str]:
        """
        .. versionadded:: 4.2.0

        Returns the URL of the guild's banner.

        :return: URL of the guild's banner (None will be returned if no banner is set)
        :rtype: str
        """
        if not self.banner:
            return None

        url = f"https://cdn.discordapp.com/banners/{int(self.id)}/{self.banner}"
        url += ".gif" if self.banner.startswith("a_") else ".png"
        return url

    @property
    def splash_url(self) -> Optional[str]:
        """
        .. versionadded:: 4.2.0

        Returns the URL of the guild's invite splash banner.

        :return: URL of the guild's invite splash banner (None will be returned if no banner is set)
        :rtype: str
        """
        return (
            f"https://cdn.discordapp.com/splashes/{int(self.id)}/{self.splash}.png"
            if self.banner
            else None
        )

    @property
    def discovery_splash_url(self) -> Optional[str]:
        """
        .. versionadded:: 4.2.0

        Returns the URL of the guild's discovery splash banner.

        :return: URL of the guild's discovery splash banner (None will be returned if no banner is set)
        :rtype: str
        """
        return (
            f"https://cdn.discordapp.com/discovery-splashes/{int(self.id)}/{self.discovery_splash}.png"
            if self.banner
            else None
        )


@define()
class GuildPreview(DictSerializerMixin, IDMixin):
    """
    A class object representing the preview of a guild.

    :ivar Snowflake id: The ID of the guild.
    :ivar str name: The name of the guild.
    :ivar Optional[str] icon: The icon of the guild.
    :ivar Optional[str] splash: The invite splash banner of the guild.
    :ivar Optional[str] discovery_splash: The discovery splash banner of the guild.
    :ivar List[Emoji] emojis: The list of emojis from the guild.
    :ivar List[GuildFeatures] features: The list of features of the guild.
    :ivar int approximate_member_count: The approximate amount of members in the guild.
    :ivar int approximate_presence_count: The approximate amount of presences in the guild.
    :ivar Optional[str] description: The description of the guild.
    """

    id: Snowflake = field(converter=Snowflake)
    emojis: Optional[List[Emoji]] = field(converter=convert_list(Emoji), default=None)
    name: str = field()
    icon: Optional[str] = field(default=None)
    splash: Optional[str] = field(default=None)
    discovery_splash: Optional[str] = field(default=None)
    features: Optional[List[str]] = field(default=None)
    approximate_member_count: int = field()
    approximate_presence_count: int = field()
    description: Optional[str] = field(default=None)


@define()
class Integration(DictSerializerMixin, IDMixin):
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

    id: Snowflake = field(converter=Snowflake)
    name: str = field()
    type: str = field()
    enabled: bool = field()
    syncing: bool = field()
    role_id: Snowflake = field(converter=Snowflake)
    enable_emoticons: bool = field()
    expire_behavior: int = field()
    expire_grace_period: int = field()
    user: User = field()
    account: Any = field()
    synced_at: datetime = field(converter=datetime.fromisoformat)
    subscriber_count: int = field()
    revoked: bool = field()
    application: Application = field()


@define()
class GuildTemplate(DictSerializerMixin):
    """
    An object representing the snapshot of an existing guild.

    :ivar str code: The code of the guild template.
    :ivar str name: The name of the guild template.
    :ivar Optional[str] description: The description of the guild template, if given.
    :ivar int usage_count: The amount of uses on the template.
    :ivar Snowflake creator_id: User ID of the creator of this template.
    :ivar User creator: The User object of the creator of this template.
    :ivar datetime created_at: The time when this template was created.
    :ivar datetime update_at: The time when this template was updated.
    :ivar Snowflake source_guild_id: The Guild ID that the template sourced from.
    :ivar Guild serialized_source_guild: A partial Guild object from the sourced template.
    :ivar Optional[bool] is_dirty: A status that denotes if the changes are unsynced.
    """

    code: str = field()
    name: str = field()
    description: Optional[str] = field(default=None)
    usage_count: int = field()
    creator_id: Snowflake = field(converter=Snowflake)
    creator: User = field(converter=User)
    created_at: datetime = field(converter=datetime.fromisoformat)
    updated_at: datetime = field(converter=datetime.fromisoformat)
    source_guild_id: Snowflake = field(converter=Snowflake)
    serialized_source_guild: Guild = field(converter=Guild)
    is_dirty: Optional[bool] = field(default=None)


@define()
class EventMetadata(DictSerializerMixin):
    """
    A class object representing the metadata of an event entity.

    :ivar Optional[str] location: The location of the event, if any.
    """

    location: Optional[str] = field(default=None)


@define()
class ScheduledEvents(DictSerializerMixin, IDMixin):
    """
    A class object representing the scheduled events of a guild.

    :ivar Snowflake id: The ID of the scheduled event.
    :ivar Snowflake guild_id: The ID of the guild that this scheduled event belongs to.
    :ivar Optional[Snowflake] channel_id: The channel ID in which the scheduled event belongs to, if any.
    :ivar Optional[Snowflake] creator_id: The ID of the user that created the scheduled event.
    :ivar str name: The name of the scheduled event.
    :ivar str description: The description of the scheduled event.
    :ivar datetime scheduled_start_time: The scheduled event start time.
    :ivar Optional[datetime] scheduled_end_time: The scheduled event end time, if any.
    :ivar int privacy_level: The privacy level of the scheduled event.
    :ivar int entity_type: The type of the scheduled event.
    :ivar Optional[Snowflake] entity_id: The ID of the entity associated with the scheduled event.
    :ivar Optional[EventMetadata] entity_metadata: Additional metadata associated with the scheduled event.
    :ivar Optional[User] creator: The user that created the scheduled event.
    :ivar Optional[int] user_count: The number of users subscribed to the scheduled event.
    :ivar int status: The status of the scheduled event
    :ivar Optional[str] image: The hash containing the image of an event, if applicable.
    """

    id: Snowflake = field(converter=Snowflake)
    guild_id: Snowflake = field(converter=Snowflake)
    channel_id: Optional[Snowflake] = field(converter=Snowflake, default=None)
    creator_id: Optional[Snowflake] = field(converter=Snowflake, default=None)
    name: str = field()
    description: str = field()
    scheduled_start_time: Optional[datetime] = field(converter=datetime.fromisoformat, default=None)
    scheduled_end_time: Optional[datetime] = field(converter=datetime.fromisoformat, default=None)
    privacy_level: int = field()
    entity_type: int = field()
    entity_id: Optional[Snowflake] = field(converter=Snowflake, default=None)
    entity_metadata: Optional[EventMetadata] = field(converter=EventMetadata, default=None)
    creator: Optional[User] = field(converter=User, default=None)
    user_count: Optional[int] = field(default=None)
    status: int = field()
    image: Optional[str] = field(default=None)


@define()
class Invite(ClientSerializerMixin):
    """
    The invite object.

    :ivar int uses: The amount of uses on this invite.
    :ivar int max_uses: The amount of maximum uses on this invite.
    :ivar int max_age: The maximum age of this invite, in seconds.
    :ivar bool temporary: A detection of whether this invite only grants temporary membership.
    :ivar datetime created_at: The time when this invite was created.
    :ivar datetime expires_at: The time when this invite will expire.
    :ivar int type: The type of this invite.
    :ivar User inviter: The user who created this invite.
    :ivar str code: The code of this invite.
    :ivar Optional[int] guild_id: The guild ID of this invite.
    :ivar Optional[int] channel_id: The channel ID of this invite.
    :ivar Optional[int] target_user_type: The type of the target user of this invite.
    :ivar Optional[User] target_user: The target user of this invite.
    :ivar Optional[int] target_type: The target type of this invite.
    :ivar Optional[Guild] guild: The guild of this invite.
    :ivar Optional[Channel] channel: The channel of this invite.
    :ivar Optional[int] approximate_member_count: The approximate amount of total members in a guild.
    :ivar Optional[int] approximate_presence_count: The aprpoximate amount of online members in a guild.
    :ivar Optional[ScheduledEvents] guild_scheduled_event: A scheduled guild event object included in the invite.

    """

    uses: int = field()
    max_uses: int = field()
    max_age: int = field()
    temporary: bool = field()
    created_at: datetime = field(converter=datetime.fromisoformat)
    expires_at: datetime = field(converter=datetime.fromisoformat)
    type: int = field()
    inviter: User = field(converter=User)
    code: str = field()
    guild_id: Optional[Snowflake] = field(converter=Snowflake, default=None)
    channel_id: Optional[Snowflake] = field(converter=Snowflake, default=None)
    target_user_type: Optional[int] = field(default=None)
    target_user: Optional[User] = field(converter=User, default=None)
    target_type: Optional[int] = field(default=None)
    guild: Optional[Guild] = field(converter=Guild, default=None, add_client=True)
    channel: Optional[Channel] = field(converter=Channel, default=None, add_client=True)
    approximate_member_count: Optional[int] = field(default=None)
    approximate_presence_count: Optional[int] = field(default=None)
    guild_scheduled_event: Optional[ScheduledEvents] = field(
        converter=ScheduledEvents, default=None
    )

    async def delete(self) -> None:
        """Deletes the invite"""

        if not self._client:
            raise LibraryException(code=13)

        await self._client.delete_invite(self.code)

    @property
    def url(self) -> str:
        """
        .. versionadded:: 4.3.0

        Returns the URL of the invite.
        """

        return f"https://discord.gg/{self.code}" if self.code else None
