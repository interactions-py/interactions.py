from datetime import datetime
from typing import Any, List, Optional, Union

from ...client.enums import PermissionType
from ...utils.attrs_utils import (
    ClientSerializerMixin,
    DictSerializerMixin,
    convert_list,
    define,
    field,
)
from .audit_log import AuditLogEntry
from .channel import Channel, ThreadMember
from .emoji import Emoji
from .guild import EventMetadata, Guild
from .member import Member
from .message import Sticker
from .misc import (
    AutoModAction,
    AutoModTriggerMetadata,
    AutoModTriggerType,
    ClientStatus,
    IDMixin,
    Snowflake,
)
from .presence import PresenceActivity
from .role import Role
from .team import Application
from .user import User

__all__ = (
    "AutoModerationAction",
    "AutoModerationRule",
    "ApplicationCommandPermission",
    "ApplicationCommandPermissions",
    "EmbeddedActivity",
    "Integration",
    "ChannelPins",
    "ThreadMembers",
    "ThreadList",
    "MessageDelete",
    "MessageReactionRemove",
    "MessageReaction",
    "GuildAuditLogEntry",
    "GuildIntegrations",
    "GuildBan",
    "Webhooks",
    "GuildMembers",
    "GuildMember",
    "GuildStickers",
    "GuildScheduledEventUser",
    "GuildScheduledEvent",
    "Presence",
    "GuildJoinRequest",
    "GuildEmojis",
    "GuildRole",
    "VoiceState",
)


@define()
class AutoModerationAction(DictSerializerMixin):
    """
    .. versionadded:: 4.3.0

    A class object representing the gateway event ``AUTO_MODERATION_ACTION_EXECUTION``.

    :ivar Snowflake guild_id: The ID of the guild in which the action was executed.
    :ivar AutoModAction action: The action which was executed.
    :ivar Snowflake rule_id: The rule ID that the action belongs to.
    :ivar int rule_trigger_type: The trigger rule type.
    :ivar Optional[Snowflake] channel_id: The id of the channel in which user content was posted.
    :ivar Optional[Snowflake] message_id: The id of any user message which content belongs to.
    :ivar Optional[Snowflake] alert_system_message_id: The id of any system automoderation messages posted as a result of this action.
    :ivar str content: The user-generated text content in question.
    :ivar Optional[str] matched_keyword: The word/phrase configured in rule that triggered rule.
    :ivar Optional[str] matched_content: The substring in content that triggered rule.
    """

    guild_id: Snowflake = field(converter=Snowflake)
    action: AutoModAction = field(converter=AutoModAction)
    rule_id: Snowflake = field(converter=Snowflake)
    rule_trigger_type: int = field()
    channel_id: Optional[Snowflake] = field(converter=Snowflake, default=None)
    message_id: Optional[Snowflake] = field(converter=Snowflake, default=None)
    alert_system_message_id: Optional[Snowflake] = field(converter=Snowflake, default=None)
    content: str = field()
    matched_keyword: Optional[str] = field(default=None)
    matched_content: Optional[str] = field(default=None)


@define()
class AutoModerationRule(DictSerializerMixin, IDMixin):
    """
    .. versionadded:: 4.3.0

    A class object representing the gateway events ``AUTO_MODERATION_RULE_CREATE``, ``AUTO_MODERATION_RULE_UPDATE``, and ``AUTO_MODERATION_RULE_DELETE``

    .. note::
        ``event_type`` at the moment can only be ``1``, which represents message sending.

    :ivar Snowflake id: The ID of the rule.
    :ivar Snowflake guild_id: The guild ID associated with the rule.
    :ivar str name: The rule name.
    :ivar Snowflake creator_id: The user ID that first created this rule.
    :ivar int event_type: The rule type in which automod checks.
    :ivar AutoModTriggerType trigger_type: The automod type. It characterises what type of information that is checked.
    :ivar AutoModTriggerMetadata trigger_metadata: Additional data needed to figure out whether this rule should be triggered.
    :ivar List[AutoModerationAction] actions: The actions that will be executed when the rule is triggered.
    :ivar bool enabled: Whether the rule is enabled.
    :ivar List[Snowflake] exempt_roles: The role IDs that should not be affected by this rule. (Max 20)
    :ivar List[Snowflake] exempt_channels: The channel IDs that should not be affected by this rule. (Max 20)
    """

    id: Snowflake = field(converter=Snowflake)
    guild_id: Snowflake = field(converter=Snowflake)
    name: str = field()
    creator_id: Snowflake = field(converter=Snowflake)
    event_type: int = field()
    trigger_type: int = field(converter=AutoModTriggerType)
    trigger_metadata: AutoModTriggerMetadata = field(converter=AutoModTriggerMetadata)
    actions: List[AutoModAction] = field(converter=convert_list(AutoModAction))
    enabled: bool = field()
    exempt_roles: List[Snowflake] = field(converter=convert_list(Snowflake))
    exempt_channels: List[Snowflake] = field(converter=convert_list(Snowflake))


@define()
class ApplicationCommandPermission(DictSerializerMixin):
    """
    A class object representing the permission of an application command.

    The structure for a permission:

    .. code-block:: python

        interactions.ApplicationCommandPermission(
            id=1234567890,
            type=interactions.PermissionType.USER,
            permission=True,
        )

    :ivar int id: The ID of the permission.
    :ivar PermissionType type: The type of permission.
    :ivar bool permission: The permission state. ``True`` for allow, ``False`` for disallow.
    """

    id: int = field()
    type: PermissionType = field(converter=PermissionType)
    permission: bool = field()


@define()
class ApplicationCommandPermissions(ClientSerializerMixin, IDMixin):
    """
    .. versionadded:: 4.1.0

    A class object representing the gateway event ``APPLICATION_COMMAND_PERMISSIONS_UPDATE``.

    :ivar Snowflake id: ID of the command or the application ID
    :ivar Snowflake application_id: ID of the application the command belongs to
    :ivar Snowflake guild_id: ID of the guild
    :ivar List[ApplicationCommandPermission] permissions: Permissions for the command in the guild, max of 100
    """

    application_id: Snowflake = field(converter=Snowflake)
    guild_id: Snowflake = field(converter=Snowflake)
    id: Snowflake = field(converter=Snowflake)
    permissions: List[ApplicationCommandPermission] = field(
        converter=convert_list(ApplicationCommandPermission)
    )


@define()
class ChannelPins(DictSerializerMixin):
    """
    A class object representing the gateway event ``CHANNEL_PINS_UPDATE``.

    :ivar Snowflake guild_id: The guild ID of the event.
    :ivar Snowflake channel_id: The channel ID of the event.
    :ivar datetime last_pin_timestamp: The time that the event took place.
    """

    guild_id: Optional[Snowflake] = field(converter=Snowflake, default=None)
    channel_id: Snowflake = field(converter=Snowflake)
    last_pin_timestamp: Optional[datetime] = field(converter=datetime.fromisoformat, default=None)


@define()
class EmbeddedActivity(DictSerializerMixin):
    """
    .. versionadded:: 4.0.2

    A class object representing the event ``EMBEDDED_ACTIVITY_UPDATE``.

    .. note::
        This is entirely undocumented by the API.

    :ivar List[Snowflake] users: The list of users of the event.
    :ivar Snowflake guild_id: The guild ID of the event.
    :ivar PresenceActivity embedded_activity: The embedded presence activity of the associated event.
    :ivar Snowflake channel_id: The channel ID of the event.
    """

    users: List[Snowflake] = field(converter=convert_list(Snowflake))
    guild_id: Snowflake = field(converter=Snowflake)
    embedded_activity: PresenceActivity = field(converter=PresenceActivity)
    channel_id: Snowflake = field(converter=Snowflake)


@define()
class GuildAuditLogEntry(AuditLogEntry):
    """
    .. versionadded:: 4.4.0

    A class object representing the event ``GUILD_AUDIT_LOG_ENTRY_CREATE``.
    A derivation of :class:`.AuditLogEntry`.

    :ivar Snowflake guild_id: The guild ID of event.
    :ivar Optional[str] target_id: ID of the affected entity (webhook, user, role, etc.)
    :ivar Optional[List[AuditLogChange]] changes: Changes made to the target_id
    :ivar Optional[Snowflake] user_id: User or app that made the changes
    :ivar Snowflake id: ID of the entry
    :ivar AuditLogEvents action_type: Type of action that occurred
    :ivar OptionalAuditEntryInfo options: Additional info for certain event types
    :ivar Optional[str] reason: Reason for the change (1-512 characters)
    """

    guild_id: Snowflake = field(converter=Snowflake)


@define()
class GuildBan(ClientSerializerMixin):
    """
    A class object representing the gateway event ``GUILD_BAN_ADD``.

    :ivar Snowflake guild_id: The guild ID of the event.
    :ivar User user: The user of the event.
    """

    guild_id: Snowflake = field(converter=Snowflake)
    user: User = field(converter=User, add_client=True)


@define()
class GuildEmojis(ClientSerializerMixin):
    """
    A class object representing the gateway event ``GUILD_EMOJIS_UPDATE``.

    :ivar Snowflake guild_id: The guild ID of the event.
    :ivar List[Emoji] emojis: The emojis of the event.
    """

    guild_id: Snowflake = field(converter=Snowflake)
    emojis: List[Emoji] = field(converter=convert_list(Emoji), add_client=True)


@define()
class GuildIntegrations(DictSerializerMixin):
    """
    A class object representing the gateway event ``GUILD_INTEGRATIONS_UPDATE``.

    :ivar Snowflake guild_id: The guild ID of the event.
    """

    guild_id: Snowflake = field(converter=Snowflake)


@define()
class GuildJoinRequest(DictSerializerMixin):
    """
    .. versionadded:: 4.0.2

    A class object representing the gateway events ``GUILD_JOIN_REQUEST_CREATE``, ``GUILD_JOIN_REQUEST_UPDATE``, and ``GUILD_JOIN_REQUEST_DELETE``

    .. note::
        This is entirely undocumented by the API.

    :ivar Snowflake user_id: The user ID of the event.
    :ivar Snowflake guild_id: The guild ID of the event.
    :ivar Optional[Any] request: The actual request representing the event. This pertains primarily to _CREATE, but maybe _UPDATE as well.
    :ivar Optional[str] status: The status of the event, which pertains to _CREATE.
    """

    user_id: Snowflake = field(converter=Snowflake)
    guild_id: Snowflake = field(converter=Snowflake)
    request: Optional[Any] = field(default=None)
    status: Optional[str] = field(default=None)


@define()
class GuildMember(Member):
    """
    A class object representing the gateway events ``GUILD_MEMBER_ADD``, ``GUILD_MEMBER_UPDATE`` and ``GUILD_MEMBER_REMOVE``.

    .. versionchanged:: 4.3.2
        GuildMember now subclasses :class:`.Member`.

    .. note::
        ``pending`` and ``permissions`` only apply for members retroactively
        requiring to verify rules via. membership screening or lack permissions
        to speak.

    :ivar Snowflake guild_id: The guild ID.
    :ivar User user: The user of the guild.
    :ivar str nick: The nickname of the member.
    :ivar Optional[str] avatar: The hash containing the user's guild avatar, if applicable.
    :ivar List[int] roles: The list of roles of the member.
    :ivar datetime joined_at: The timestamp the member joined the guild at.
    :ivar datetime premium_since: The timestamp the member has been a server booster since.
    :ivar bool deaf: Whether the member is deafened.
    :ivar bool mute: Whether the member is muted.
    :ivar Optional[bool] pending: Whether the member is pending to pass membership screening.
    :ivar Optional[Permissions] permissions: Whether the member has permissions.
    :ivar Optional[str] communication_disabled_until: How long until they're unmuted, if any.
    """

    _guild_id: Snowflake = field(converter=Snowflake, discord_name="guild_id")


@define()
class GuildMembers(DictSerializerMixin):
    """
    A class object representing the gateway event ``GUILD_MEMBERS_CHUNK``.

    :ivar Snowflake guild_id: The guild ID of the event.
    :ivar List[Member] members: The members of the event.
    :ivar int chunk_index: The current chunk index of the event.
    :ivar int chunk_count: The total chunk count of the event.
    :ivar list not_found: A list of not found members in the event if an invalid request was made.
    :ivar List[PresenceActivity] presences: A list of presences in the event.
    :ivar str nonce: The "nonce" of the event.
    """

    guild_id: Snowflake = field(converter=Snowflake)
    members: List[Member] = field(converter=convert_list(Member), add_client=True)
    chunk_index: int = field()
    chunk_count: int = field()
    not_found: Optional[list] = field(default=None)
    presences: Optional[List[PresenceActivity]] = field(
        converter=convert_list(PresenceActivity), default=None
    )
    nonce: Optional[str] = field(default=None)


@define()
class GuildRole(ClientSerializerMixin):
    """
    A class object representing the gateway events ``GUILD_ROLE_CREATE``, ``GUILD_ROLE_UPDATE`` and ``GUILD_ROLE_DELETE``.

    :ivar Snowflake guild_id: The guild ID of the event.
    :ivar Optional[Role] role: The role of the event.
    :ivar Optional[Snowflake] role_id: The role ID of the event.
    """

    guild_id: Snowflake = field(converter=Snowflake)
    role: Optional[Role] = field(converter=Role, add_client=True, default=None)
    role_id: Optional[Snowflake] = field(converter=Snowflake, default=None)


@define()
class GuildStickers(DictSerializerMixin):
    """
    A class object representing the gateway event ``GUILD_STICKERS_UPDATE``.

    :ivar Snowflake guild_id: The guild ID of the event.
    :ivar List[Sticker] stickers: The stickers of the event.
    """

    guild_id: Snowflake = field(converter=Snowflake)
    stickers: List[Sticker] = field(converter=convert_list(Sticker))


@define()
class GuildScheduledEvent(ClientSerializerMixin, IDMixin):
    """
    .. versionadded:: 4.3.0

    A class object representing gateway events ``GUILD_SCHEDULED_EVENT_CREATE``, ``GUILD_SCHEDULED_EVENT_UPDATE``, ``GUILD_SCHEDULED_EVENT_DELETE``.

    .. note::
        Some attributes are optional via creator_id/creator implementation by the API:
        "``creator_id`` will be null and ``creator`` will not be included for events created before October 25th, 2021, when the concept of ``creator_id`` was introduced and tracked."

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
    scheduled_start_time: datetime = field(converter=datetime.fromisoformat)
    scheduled_end_time: Optional[datetime] = field(converter=datetime.fromisoformat, default=None)
    privacy_level: int = field()
    entity_type: int = field()
    entity_id: Optional[Snowflake] = field(converter=Snowflake, default=None)
    entity_metadata: Optional[EventMetadata] = field(converter=EventMetadata, default=None)
    creator: Optional[User] = field(converter=User, default=None, add_client=True)
    user_count: Optional[int] = field(default=None)
    status: int = field()
    image: Optional[str] = field(default=None)


@define()
class GuildScheduledEventUser(DictSerializerMixin):
    """
    .. versionadded:: 4.3.0

    A class object representing the gateway events ``GUILD_SCHEDULED_EVENT_USER_ADD`` and ``GUILD_SCHEDULED_EVENT_USER_REMOVE``

    :ivar Snowflake guild_scheduled_event_id: The ID of the guild scheduled event.
    :ivar Snowflake guild_id: The ID of the guild associated with this event.
    :ivar Snowflake user_id: The ID of the user associated with this event.
    """

    guild_scheduled_event_id: Snowflake = field(converter=Snowflake, default=None)
    guild_id: Snowflake = field(converter=Snowflake, default=None)
    user_id: Snowflake = field(converter=Snowflake, default=None)


@define()
class Integration(DictSerializerMixin, IDMixin):
    """
    A class object representing the gateway events ``INTEGRATION_CREATE``, ``INTEGRATION_UPDATE`` and ``INTEGRATION_DELETE``.

    .. note::
        The documentation of this event is the same as :class:`.Guild`.

    :ivar Snowflake id: The ID of the event.
    :ivar str name: The name of the event.
    :ivar str type: The type of integration in the event.
    :ivar bool enabled: Whether the integration of the event is enabled or not.
    :ivar bool syncing: Whether the integration of the event is syncing or not.
    :ivar Snowflake role_id: The role ID that the integration in the event uses for "subscribed" users.
    :ivar bool enable_emoticons: Whether emoticons of the integration's event should be enabled or not.
    :ivar int expire_behavior: The expiration behavior of the integration of the event.
    :ivar int expire_grace_period: The "grace period" of the integration of the event when expired -- how long it can still be used.
    :ivar User user: The user of the event.
    :ivar Any account: The account of the event.
    :ivar datetime synced_at: The time that the integration of the event was last synced.
    :ivar int subscriber_count: The current subscriber count of the event.
    :ivar bool revoked: Whether the integration of the event was revoked for use or not.
    :ivar Application application: The application used for the integration of the event.
    :ivar Snowflake guild_id: The guild ID of the event.
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
    user: User = field(converter=User)
    account: Any = field()
    synced_at: datetime = field(converter=datetime.fromisoformat)
    subscriber_count: int = field()
    revoked: bool = field()
    application: Application = field(converter=Application)
    guild_id: Snowflake = field(converter=Snowflake)


@define()
class Presence(ClientSerializerMixin):
    """
    A class object representing the gateway event ``PRESENCE_UPDATE``.

    :ivar User user: The user of the event.
    :ivar Snowflake guild_id: The guild ID of the event.
    :ivar str status: The status of the event.
    :ivar List[PresenceActivity] activities: The activities of the event.
    :ivar ClientStatus client_status: The client status across platforms in the event.
    """

    user: User = field(converter=User)
    guild_id: Snowflake = field(converter=Snowflake)
    status: str = field()
    activities: List[PresenceActivity] = field(converter=convert_list(PresenceActivity))
    client_status: ClientStatus = field(converter=ClientStatus)


@define()
class MessageDelete(DictSerializerMixin):
    """
    .. versionadded:: 4.3.1

    A class object representing the gateway event ``MESSAGE_DELETE_BULK``.

    :ivar List[Snowflake] ids: The message IDs of the event.
    :ivar Snowflake channel_id: The channel ID of the event.
    :ivar Optional[Snowflake] guild_id: The guild ID of the event.
    """

    ids: List[Snowflake] = field(converter=convert_list(Snowflake))
    channel_id: Snowflake = field(converter=Snowflake)
    guild_id: Optional[Snowflake] = field(converter=Snowflake, default=None)


@define()
class MessageReaction(ClientSerializerMixin):
    """
    A class object representing the gateway event ``MESSAGE_REACTION_ADD`` and ``MESSAGE_REACTION_REMOVE``.

    :ivar Optional[Snowflake] user_id: The user ID of the event.
    :ivar Snowflake channel_id: The channel ID of the event.
    :ivar Snowflake message_id: The message ID of the event.
    :ivar Optional[Snowflake] guild_id: The guild ID of the event.
    :ivar Optional[Member] member: The member of the event.
    :ivar Optional[Emoji] emoji: The emoji of the event.
    """

    user_id: Optional[Snowflake] = field(converter=Snowflake, default=None)
    channel_id: Snowflake = field(converter=Snowflake)
    message_id: Snowflake = field(converter=Snowflake)
    guild_id: Optional[Snowflake] = field(converter=Snowflake, default=None)
    member: Optional[Member] = field(converter=Member, default=None, add_client=True)
    emoji: Optional[Emoji] = field(converter=Emoji, default=None)

    def __attrs_post_init__(self):
        if self.member and self.guild_id:
            self.member._extras["guild_id"] = self.guild_id


class MessageReactionRemove(MessageReaction):
    """
    A class object representing the gateway events ``MESSAGE_REACTION_REMOVE_ALL`` and ``MESSAGE_REACTION_REMOVE_EMOJI``.

    .. note::
        This class inherits the already existing attributes of :class:`.MessageReaction`.
        The main missing attribute is ``member``.

    :ivar Optional[Snowflake] user_id: The user ID of the event.
    :ivar Snowflake channel_id: The channel ID of the event.
    :ivar Snowflake message_id: The message ID of the event.
    :ivar Optional[Snowflake] guild_id: The guild ID of the event.
    :ivar Optional[Emoji] emoji: The emoji of the event.
    """

    # todo see if the missing member attribute affects anything


# Thread object typically used for ``THREAD_X`` is found in the channel models instead, as its identical.
# and all attributes of Thread are in Channel.


@define()
class ThreadList(DictSerializerMixin):
    """
    A class object representing the gateway event ``THREAD_LIST_SYNC``.

    :ivar Snowflake guild_id: The guild ID of the event.
    :ivar Optional[List[Snowflake]] channel_ids: The channel IDs of the event.
    :ivar List[Channel] threads: The threads of the event.
    :ivar List[ThreadMember] members: The members of the thread of the event.
    """

    guild_id: Snowflake = field(converter=Snowflake)
    channel_ids: Optional[List[Snowflake]] = field(converter=convert_list(Snowflake), default=None)
    threads: List[Channel] = field(converter=convert_list(Channel))
    members: List[ThreadMember] = field(converter=convert_list(ThreadMember))


@define()
class ThreadMembers(DictSerializerMixin, IDMixin):
    """
    A class object representing the gateway event ``THREAD_MEMBERS_UPDATE``.

    :ivar Snowflake id: The ID of the event.
    :ivar Snowflake guild_id: The guild ID of the event.
    :ivar int member_count: The member count of the event.
    :ivar Optional[List[ThreadMember]] added_members: The added members of the thread of the event.
    :ivar Optional[List[Snowflake]] removed_member_ids: The removed IDs of members of the thread of the event.
    """

    id: Snowflake = field(converter=Snowflake)
    guild_id: Snowflake = field(converter=Snowflake)
    member_count: int = field()
    added_members: Optional[List[ThreadMember]] = field(
        converter=convert_list(ThreadMember), default=None
    )
    removed_member_ids: Optional[List[Snowflake]] = field(
        converter=convert_list(Snowflake), default=None
    )


@define()
class Webhooks(DictSerializerMixin):
    """
    .. versionadded:: 4.1.0

    A class object representing the gateway event ``WEBHOOKS_UPDATE``.

    :ivar Snowflake channel_id: The channel ID of the associated event.
    :ivar Snowflake guild_id: The guild ID of the associated event.
    """

    channel_id: Snowflake = field(converter=Snowflake)
    guild_id: Snowflake = field(converter=Snowflake)


@define()
class VoiceState(ClientSerializerMixin):
    """
    .. versionadded:: 4.4.0

    A class object representing the gateway event ``VOICE_STATE_UPDATE``.
    This class creates an object every time the event ``VOICE_STATE_UPDATE`` is received from the discord API.
    It contains information about the user's update voice information. Additionally, the last voice state is cached,
    allowing you to see, what attributes of the user's voice information change.

    :ivar Member member: The member whose VoiceState was updated
    :ivar Snowflake user_id: The id of the user whose VoiceState was updated. This is technically the same as the "member id", but it is called `user_id` because of API terminology.
    :ivar bool suppress: Whether the user is muted by the current user(-> bot)
    :ivar int session_id: The id of the session
    :ivar bool self_video: Whether the user's camera is enabled.
    :ivar bool self_mute: Whether the user is muted by themselves
    :ivar bool self_deaf: Whether the user is deafened by themselves
    :ivar bool self_stream: Whether the user is streaming in the current channel
    :ivar datetime request_to_speak_timestamp: Only for stage-channels; when the user requested permissions to speak in the stage channel
    :ivar bool mute: Whether the user's microphone is muted by the server
    :ivar Snowflake guild_id: The id of the guild in what the update took action
    :ivar bool deaf: Whether the user is deafened by the guild
    :ivar Snowflake channel_id: The id of the channel the update took action
    """

    channel_id: Optional[Snowflake] = field(converter=Snowflake, default=None)
    guild_id: Optional[Snowflake] = field(converter=Snowflake, default=None)
    user_id: Optional[Snowflake] = field(converter=Snowflake, default=None)
    member: Optional[Member] = field(converter=Member, default=None, add_client=True)
    request_to_speak_timestamp: Optional[datetime] = field(
        converter=datetime.fromisoformat, default=None
    )
    suppress: bool = field()
    session_id: int = field()
    self_video: bool = field()
    self_mute: bool = field()
    self_deaf: bool = field()
    self_stream: Optional[bool] = field(default=None)
    mute: bool = field()
    deaf: bool = field()

    def __attrs_post_init__(self):
        if self.member:
            self.member._extras["guild_id"] = self.guild_id

    @property
    def joined(self) -> bool:
        """
        Whether the user joined the channel.

        :rtype: bool
        """
        return self.channel_id is not None

    @property
    def channel(self) -> Optional[Channel]:
        """
        Returns the current channel, if cached.
        """
        return self._client.cache[Channel].get(self.channel_id)

    @property
    def guild(self) -> Optional[Guild]:
        """
        Returns the current guild, if cached.
        """

        return self._client.cache[Guild].get(self.guild_id)

    async def mute_member(self, reason: Optional[str] = None) -> Member:
        """
        Mutes the current member.

        :param Optional[str] reason: The reason of the muting, optional
        :return: The modified member object
        :rtype: Member
        """
        return await self.member.modify(guild_id=int(self.guild_id), mute=True, reason=reason)

    async def deafen_member(self, reason: Optional[str] = None) -> Member:
        """
        Deafens the current member.

        :param Optional[str] reason: The reason of the deafening, optional
        :return: The modified member object
        :rtype: Member
        """
        return await self.member.modify(guild_id=int(self.guild_id), deaf=True, reason=reason)

    async def move_member(
        self, channel_id: Union[int, str, Snowflake], *, reason: Optional[str] = None
    ) -> Member:
        """
        Moves the member to another channel.

        :param Union[int, str, Snowflake] channel_id: The ID of the channel to move the user to
        :param Optional[str] reason: The reason of the move
        :return: The modified member object
        :rtype: Member
        """
        return await self.member.modify(
            guild_id=int(self.guild_id), channel_id=channel_id, reason=reason
        )

    async def get_channel(self) -> Channel:
        """
        Gets the channel in what the update took place.

        :rtype: Channel
        """
        if channel := self.channel:
            return channel

        res = await self._client.get_channel(int(self.channel_id))
        return Channel(**res, _client=self._client)

    async def get_guild(self) -> Guild:
        """
        Gets the guild in what the update took place.

        :rtype: Guild
        """

        if guild := self.guild:
            return guild

        res = await self._client.get_guild(int(self.guild_id))
        return Guild(**res, _client=self._client)
