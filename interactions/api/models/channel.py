from datetime import datetime
from enum import IntEnum
from typing import List, Optional

from .misc import Overwrite
from .user import User


class ChannelType(IntEnum):
    """
    Types of channels.

    ..note::
        While all of them are listed, not all of them would be used at this lib's scope.
    """

    GUILD_TEXT = 0
    DM = 1
    GUILD_VOICE = 2
    GROUP_DM = 3
    GUILD_CATEGORY = 4
    GUILD_NEWS = 5
    GUILD_STORE = 6
    GUILD_NEWS_THREAD = 10
    GUILD_PUBLIC_THREAD = 11
    GUILD_PRIVATE_THREAD = 12
    GUILD_STAGE_VOICE = 13


class ThreadMetadata(object):
    __slots__ = ("archived", "auto_archive_duration", "archive_timestamp", "locked", "invitable")
    archived: bool
    auto_archive_duration: int
    archive_timestamp: datetime.timestamp
    locked: bool
    invitable: Optional[bool]


class ThreadMember(object):
    __slots__ = ("id", "user_id", "join_timestamp", "flags")
    id: Optional[int]  # intents
    user_id: Optional[int]
    join_timestamp: datetime.timestamp
    flags: int


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
    last_pin_timestamp: Optional[datetime]
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
    ...


class DMChannel(Channel):
    ...


class ThreadChannel(Channel):
    ...
