# versionadded declared in docs gen file

from typing import TYPE_CHECKING, List, Optional, TypeVar

from ...client.enums import IntEnum
from ...utils.attrs_utils import DictSerializerMixin, convert_list, define, field
from .channel import Channel
from .misc import Snowflake
from .user import User
from .webhook import Webhook

__all__ = (
    "AuditLogEntry",
    "AuditLogEvents",
    "AuditLogs",
    "AuditLogChange",
    "OptionalAuditEntryInfo",
)

_T = TypeVar("_T")


if TYPE_CHECKING:
    from .guild import Integration, ScheduledEvents
    from .gw import AutoModerationRule


class AuditLogEvents(IntEnum):
    """
    A class object representing the different types of AuditLogEvents.

    .. note::
        There is no official name for AuditLogEvents type 151, however it does represent the server owner sets up the guild for monetization/server subscriptions.

    :ivar int GUILD_UPDATE: 1 - Server settings were updated
    :ivar int CHANNEL_CREATE: 10 - Channel was created
    :ivar int CHANNEL_UPDATE: 11 - Channel settings were updated
    :ivar int CHANNEL_DELETE: 12 - Channel was deleted
    :ivar int CHANNEL_OVERWRITE_CREATE: 13 - Permission overwrite was added to a channel
    :ivar int CHANNEL_OVERWRITE_UPDATE: 14 - Permission overwrite was updated for a channel
    :ivar int CHANNEL_OVERWRITE_DELETE: 15 - Permission overwrite was deleted from a channel
    :ivar int MEMBER_KICK: 20 - Member was removed from server
    :ivar int MEMBER_PRUNE: 21 - Members were pruned from server
    :ivar int MEMBER_BAN_ADD: 22 - Member was banned from server
    :ivar int MEMBER_BAN_REMOVE: 23 - Server ban was lifted for a member
    :ivar int MEMBER_UPDATE: 24 - Member was updated in server
    :ivar int MEMBER_ROLE_UPDATE: 25 - Member was added or removed from a role
    :ivar int MEMBER_MOVE: 26 - Member was moved to a different voice channel
    :ivar int MEMBER_DISCONNECT: 27 - Member was disconnected from a voice channel
    :ivar int BOT_ADD: 28 - Bot user was added to server
    :ivar int ROLE_CREATE: 30 - Role was created
    :ivar int ROLE_UPDATE: 31 - Role was updated
    :ivar int ROLE_DELETE: 32 - Role was deleted
    :ivar int INVITE_CREATE: 40 - Server invite was created
    :ivar int INVITE_UPDATE: 41 - Server invite was updated
    :ivar int INVITE_DELETE: 42 - Server invite was deleted
    :ivar int WEBHOOK_CREATE: 50 - Webhook was created
    :ivar int WEBHOOK_UPDATE: 51 - Webhook properties or channel were updated
    :ivar int WEBHOOK_DELETE: 52 - Webhook was deleted
    :ivar int EMOJI_CREATE: 60 - Emoji was created
    :ivar int EMOJI_UPDATE: 61 - Emoji name was updated
    :ivar int EMOJI_DELETE: 62 - Emoji was deleted
    :ivar int MESSAGE_DELETE: 72 - Single message was deleted
    :ivar int MESSAGE_BULK_DELETE: 73 - Multiple messages were deleted
    :ivar int MESSAGE_PIN: 74 - Message was pinned to a channel
    :ivar int MESSAGE_UNPIN: 75 - Message was unpinned from a channel
    :ivar int INTEGRATION_CREATE: 80 - App was added to server
    :ivar int INTEGRATION_UPDATE: 81 - App was updated (as an example, its scopes were updated)
    :ivar int INTEGRATION_DELETE: 82 - App was removed from server
    :ivar int STAGE_INSTANCE_CREATE: 83 - Stage instance was created (stage channel becomes live)
    :ivar int STAGE_INSTANCE_UPDATE: 84 - Stage instance details were updated
    :ivar int STAGE_INSTANCE_DELETE: 85 - Stage instance was deleted (stage channel no longer live)
    :ivar int STICKER_CREATE: 90 - Sticker was created
    :ivar int STICKER_UPDATE: 91 - Sticker details were updated
    :ivar int STICKER_DELETE: 92 - Sticker was deleted
    :ivar int GUILD_SCHEDULED_EVENT_CREATE: 100 - Event was created
    :ivar int GUILD_SCHEDULED_EVENT_UPDATE: 101 - Event was updated
    :ivar int GUILD_SCHEDULED_EVENT_DELETE: 102 - Event was cancelled
    :ivar int THREAD_CREATE: 110 - Thread was created in a channel
    :ivar int THREAD_UPDATE: 111 - Thread was updated
    :ivar int THREAD_DELETE: 112 - Thread was deleted
    :ivar int APPLICATION_COMMAND_PERMISSION_UPDATE: 121 - Permissions were updated for a command
    :ivar int AUTO_MODERATION_RULE_CREATE: 140 - Auto Moderation rule was created
    :ivar int AUTO_MODERATION_RULE_UPDATE: 141 - Auto Moderation rule was updated
    :ivar int AUTO_MODERATION_RULE_DELETE: 142 - Auto Moderation rule was deleted
    :ivar int AUTO_MODERATION_BLOCK_MESSAGE: 143 - Message was blocked by AutoMod (according to a rule)
    :ivar int AUTO_MODERATION_FLAG_TO_CHANNEL: 144 - Message was flagged by AutoMod (according to a rule)
    :ivar int AUTO_MODERATION_USER_COMMUNICATION_DISABLED: 145 - Member was timed out by AutoMod (according to a rule)
    :ivar int GUILD_MONETIZATION_SETUP: 151 - Monetization was set up in the server.
    """

    # guild related
    GUILD_UPDATE = 1

    # channel related
    CHANNEL_CREATE = 10
    CHANNEL_UPDATE = 11
    CHANNEL_DELETE = 12
    CHANNEL_OVERWRITE_CREATE = 13
    CHANNEL_OVERWRITE_UPDATE = 14
    CHANNEL_OVERWRITE_DELETE = 15

    # member related
    MEMBER_KICK = 20
    MEMBER_PRUNE = 21
    MEMBER_BAN_ADD = 22
    MEMBER_BAN_REMOVE = 23
    MEMBER_UPDATE = 24
    MEMBER_ROLE_UPDATE = 25
    MEMBER_MOVE = 26
    MEMBER_DISCONNECT = 27
    BOT_ADD = 28

    # role related
    ROLE_CREATE = 30
    ROLE_UPDATE = 31
    ROLE_DELETE = 32

    # invite related
    INVITE_CREATE = 40
    INVITE_UPDATE = 41
    INVITE_DELETE = 42

    # webhook related
    WEBHOOK_CREATE = 50
    WEBHOOK_UPDATE = 51
    WEBHOOK_DELETE = 52

    # emoji related
    EMOJI_CREATE = 60
    EMOJI_UPDATE = 61
    EMOJI_DELETE = 62

    # message related
    MESSAGE_DELETE = 72
    MESSAGE_BULK_DELETE = 73
    MESSAGE_PIN = 74
    MESSAGE_UNPIN = 75

    # integration related
    INTEGRATION_CREATE = 80
    INTEGRATION_UPDATE = 81
    INTEGRATION_DELETE = 82

    # stage instance related
    STAGE_INSTANCE_CREATE = 83
    STAGE_INSTANCE_UPDATE = 84
    STAGE_INSTANCE_DELETE = 85

    # sticker related
    STICKER_CREATE = 90
    STICKER_UPDATE = 91
    STICKER_DELETE = 92

    # guild scheduled event related
    GUILD_SCHEDULED_EVENT_CREATE = 100
    GUILD_SCHEDULED_EVENT_UPDATE = 101
    GUILD_SCHEDULED_EVENT_DELETE = 102

    # thread related
    THREAD_CREATE = 110
    THREAD_UPDATE = 111
    THREAD_DELETE = 112

    # app-command permissions related
    APPLICATION_COMMAND_PERMISSION_UPDATE = 121

    # auto mod related
    AUTO_MODERATION_RULE_CREATE = 140
    AUTO_MODERATION_RULE_UPDATE = 141
    AUTO_MODERATION_RULE_DELETE = 142
    AUTO_MODERATION_BLOCK_MESSAGE = 143
    AUTO_MODERATION_FLAG_TO_CHANNEL = 144
    AUTO_MODERATION_USER_COMMUNICATION_DISABLED = 145

    # monetization related

    GUILD_MONETIZATION_SETUP = 151


@define()
class AuditLogChange(DictSerializerMixin):
    """
    A class object representing an AuditLogChange.

    :ivar Optional[_T] new_value: New value of the key
    :ivar Optional[_T] old_value: Old value of the key
    :ivar str key: Name of the changed entity, with a few `exceptions <https://discord.com/developers/docs/resources/audit-log#audit-log-change-object-audit-log-change-exceptions>`_
    """

    new_value: Optional[_T] = field(default=None)
    old_value: Optional[_T] = field(default=None)
    key: str = field()


@define()
class OptionalAuditEntryInfo(DictSerializerMixin):
    """
    A class object representing OptionalAuditEntryInfo.

    :ivar Snowflake application_id: ID of the app whose permissions were targeted. Used in event :attr:`AuditLogEvents.APPLICATION_COMMAND_PERMISSION_UPDATE`.
    :ivar str auto_moderation_rule_name: Name of the Auto Moderation rule that was triggered. Used in events :attr:`AuditLogEvents.AUTO_MODERATION_BLOCK_MESSAGE`, :attr:`AuditLogEvents.AUTO_MODERATION_FLAG_TO_CHANNEL` & :attr:`AuditLogEvents.AUTO_MODERATION_USER_COMMUNICATION_DISABLED`.
    :ivar str auto_moderation_rule_trigger_type: Trigger type of the Auto Moderation rule that was triggered. Used in events :attr:`AuditLogEvents.AUTO_MODERATION_BLOCK_MESSAGE`, :attr:`AuditLogEvents.AUTO_MODERATION_FLAG_TO_CHANNEL` & :attr:`AuditLogEvents.AUTO_MODERATION_USER_COMMUNICATION_DISABLED`.
    :ivar Snowflake channel_id: Channel in which the entities were targeted. Used in events :attr:`AuditLogEvents.MEMBER_MOVE`, :attr:`AuditLogEvents.MESSAGE_PIN`, :attr:`AuditLogEvents.MESSAGE_UNPIN`, :attr:`AuditLogEvents.MESSAGE_DELETE`, :attr:`AuditLogEvents.STAGE_INSTANCE_CREATE`, :attr:`AuditLogEvents.STAGE_INSTANCE_UPDATE`, :attr:`AuditLogEvents.STAGE_INSTANCE_DELETE`, :attr:`AuditLogEvents.AUTO_MODERATION_BLOCK_MESSAGE`, :attr:`AuditLogEvents.AUTO_MODERATION_FLAG_TO_CHANNEL` & :attr:`AuditLogEvents.AUTO_MODERATION_USER_COMMUNICATION_DISABLED`.
    :ivar str count: Number of entities that were targeted. Used in events :attr:`AuditLogEvents.MESSAGE_DELETE`, :attr:`AuditLogEvents.MESSAGE_BULK_DELETE`, :attr:`AuditLogEvents.MEMBER_DISCONNECT` & :attr:`AuditLogEvents.MEMBER_MOVE`
    :ivar str delete_member_days: Number of days after which inactive members were kicked. Used in event :attr:`AuditLogEvents.MEMBER_PRUNE`
    :ivar Snowflake id: ID of the overwritten entity. Used in events :attr:`AuditLogEvents.CHANNEL_OVERWRITE_CREATE`, :attr:`AuditLogEvents.CHANNEL_OVERWRITE_UPDATE` & :attr:`AuditLogEvents.CHANNEL_OVERWRITE_DELETE`
    :ivar str members_removed: Number of members removed by the prune. Used in event :attr:`AuditLogEvents.MEMBER_PRUNE`
    :ivar Snowflake message_id: ID of the message that was targeted. Used in events :attr:`AuditLogEvents.MESSAGE_PIN` & :attr:`AuditLogEvents.MESSAGE_UNPIN`
    :ivar Optional[str] role_name: Name of the role if type is "0" (not present if type is "1"). Used in events :attr:`AuditLogEvents.CHANNEL_OVERWRITE_CREATE`, :attr:`AuditLogEvents.CHANNEL_OVERWRITE_UPDATE` & :attr:`AuditLogEvents.CHANNEL_OVERWRITE_DELETE`
    :ivar str type: Type of overwritten entity - role ("0") or member ("1"). Used in events :attr:`AuditLogEvents.CHANNEL_OVERWRITE_CREATE`, :attr:`AuditLogEvents.CHANNEL_OVERWRITE_UPDATE` & :attr:`AuditLogEvents.CHANNEL_OVERWRITE_DELETE`
    """

    application_id: Snowflake = field(converter=Snowflake)
    channel_id: Snowflake = field(converter=Snowflake)
    auto_moderation_rule_name: str = field()
    auto_moderation_rule_trigger_type: str = field()
    count: str = field()
    delete_member_days: str = field()
    id: Snowflake = field(converter=Snowflake)
    members_removed: str = field()
    message_id: Snowflake = field(converter=Snowflake)
    role_name: Optional[str] = field(default=None)
    type: str = field()


@define()
class AuditLogEntry(DictSerializerMixin):
    """
    A class object representing an AuditLogEntry.

    :ivar Optional[str] target_id: ID of the affected entity (webhook, user, role, etc.)
    :ivar Optional[List[AuditLogChange]] changes: Changes made to the target_id
    :ivar Optional[Snowflake] user_id: User or app that made the changes
    :ivar Snowflake id: ID of the entry
    :ivar AuditLogEvents action_type: Type of action that occurred
    :ivar OptionalAuditEntryInfo options: Additional info for certain event types
    :ivar Optional[str] reason: Reason for the change (1-512 characters)
    """

    target_id: Optional[str] = field(default=None)
    changes: Optional[List[AuditLogChange]] = field(
        converter=convert_list(AuditLogChange), default=None
    )
    user_id: Optional[Snowflake] = field(converter=Snowflake, default=None)
    id: Snowflake = field(converter=Snowflake)
    action_type: AuditLogEvents = field(converter=AuditLogEvents)
    options: Optional[OptionalAuditEntryInfo] = field(
        converter=OptionalAuditEntryInfo, default=None
    )
    reason: Optional[str] = field(default=None)


@define()
class AuditLogs(DictSerializerMixin):
    """
    A class object representing the audit logs of a guild.

    :ivar List[AuditLogEntry] audit_log_entries: List of audit log entries, sorted from most to least recent.
    :ivar List[AutoModerationRule] auto_moderation_rules: List of auto moderation rules referenced in the audit log.
    :ivar List[ScheduledEvents] guild_scheduled_events: List of guild scheduled events referenced in the audit log
    :ivar List[Integration] integrations: List of partial integration objects
    :ivar List[Channel] threads: List of threads referenced in the audit log
    :ivar List[User] users: List of users referenced in the audit log
    :ivar List[Webhook] webhooks: List of webhooks referenced in the audit log
    """

    audit_log_entries: List[AuditLogEntry] = field(
        converter=convert_list(AuditLogEntry), default=None
    )
    auto_moderation_rules: List["AutoModerationRule"] = field(default=None)
    guild_scheduled_events: List["ScheduledEvents"] = field(default=None)
    integrations: List["Integration"] = field(default=None)
    threads: List[Channel] = field(converter=convert_list(Channel), default=None)
    users: List[User] = field(converter=convert_list(User), default=None)
    webhooks: List[Webhook] = field(converter=convert_list(Webhook), default=None)

    def __attrs_post__init(self):
        if self.guild_scheduled_events:
            from .guild import ScheduledEvents

            self.guild_scheduled_events = [
                ScheduledEvents(**event) for event in self.guild_scheduled_events
            ]
        if self.integrations:
            from .guild import Integration

            self.integrations = [Integration(**integration) for integration in self.integrations]

        if self.auto_moderation_rules:
            from .gw import AutoModerationRule

            self.auto_moderation_rules = [
                AutoModerationRule(**rule) for rule in self.auto_moderation_rules
            ]
