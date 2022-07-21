from enum import IntEnum
from typing import TYPE_CHECKING, List, Optional, TypeVar

from .attrs_utils import DictSerializerMixin, convert_list, define, field
from .channel import Channel
from .gw import AutoModerationRule
from .misc import Snowflake
from .user import User
from .webhook import Webhook

__all__ = (
    "AuditLogEntry",
    "AuditLogEvents",
    "AuditLogs",
)
_T = TypeVar("_T")


if TYPE_CHECKING:
    from .guild import Integration, ScheduledEvents


class AuditLogEvents(IntEnum):
    """
    A class object representing the different types of AuditLogEvents.
    """

    ...


@define()
class AuditLogChange(DictSerializerMixin):
    """
    A class object representing an AuditLogChange.

    :ivar Optional[_T] new_value?: New value of the key
    :ivar Optional[_T] old_value?: Old value of the key
    :ivar str key: Name of the changed entity, with a few [exceptions](https://discord.com/developers/docs/resources/audit-log#audit-log-change-object-audit-log-change-exceptions)
    """

    new_value: Optional[_T] = field(default=None)
    old_value: Optional[_T] = field(default=None)
    key: str = field()


@define()
class OptionalAuditEntryInfo(DictSerializerMixin):
    """
    A class object representing OptionalAuditEntryInfo
    """

    ...


@define()
class AuditLogEntry(DictSerializerMixin):
    """
    A class object representing an AuditLogEntry.

    :ivar Optional[str] target_id?: ID of the affected entity (webhook, user, role, etc.)
    :ivar Optional[List[AuditLogChange]] changes?: Changes made to the target_id
    :ivar Optional[Snowflake] user_id?: User or app that made the changes
    :ivar Snowflake id: ID of the entry
    :ivar AuditLogEvents action_type: Type of action that occurred
    :ivar OptionalAuditEntryInfo options?: Additional info for certain event types
    :ivar str reason?: Reason for the change (1-512 characters)
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
    :ivar List[AutoModerationRule] auto_moderation_rules:
    :ivar List[ScheduledEvents] guild_scheduled_events: List of guild scheduled events referenced in the audit log
    :ivar List[Integration] integrations: List of partial integration objects
    :ivar List[Channel] threads: List of threads referenced in the audit log
    :ivar List[User] users: List of users referenced in the audit log
    :ivar List[Webhook] webhooks: List of webhooks referenced in the audit log
    """

    audit_log_entries: List[AuditLogEntry] = field(
        converter=convert_list(AuditLogEntry), default=None
    )
    auto_moderation_rules: List[AutoModerationRule] = field(
        converter=convert_list(AutoModerationRule), default=None
    )
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
