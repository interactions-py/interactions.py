import datetime
from typing import Optional, Union, List


# TODO: Reorganise these models based on which big obj uses little obj
# TODO: Figure out ? placements.


class MessageActivity(object):
    type: int
    party_id: Optional[str]


class MessageReference(object):
    message_id: Optional[int]
    channel_id: Optional[int]
    guild_id: Optional[int]
    fail_if_not_exists: Optional[bool]


class ThreadMetadata(object):
    archived: bool
    auto_archive_duration: int
    archive_timestamp: datetime.datetime.timestamp
    locked: bool
    invitable: Optional[bool]


class ThreadMember(object):
    id: Optional[int]  # intents
    user_id: Optional[int]
    join_timestamp: datetime.datetime.timestamp
    flags: int


class User(object):
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
    """Also, the guild member obj (Or partial.)"""

    user: Optional[User]
    nick: Optional[str]
    roles: List[str]
    joined_at: datetime.datetime.timestamp
    premium_since: Optional[datetime.datetime.timestamp]
    deaf: bool
    mute: bool
    pending: Optional[bool]
    permissions: Optional[str]


class Overwrite(object):
    """This is used for the PermissionOverride obj"""

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
    last_pin_timestamp: Optional[datetime.datetime.timestamp]
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


class Attachment(object):
    id: int
    filename: str
    content_type: Optional[str]
    size: int
    url: str
    proxy_url: str
    height: Optional[int]
    width: Optional[int]


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
    edited_timestamp: Optional[datetime.datetime.timestamp]
    tts: bool
    mention_everyone: bool
    # mentions: array of Users, and maybe partial members
    mentions = Optional[List[Union[Member, User]]]
    mention_roles: Optional[List[str]]
    mention_channels: Optional[List["ChannelMention"]]
    attachments: Optional[List[Attachment]]
    # embeds
    reactions: Optional[List["ReactionObject"]]
    nonce: Union[int, str]
    pinned: bool
    webhook_id: Optional[int]
    type: int
    activity: Optional[MessageActivity]
    # application
    application_id: int
    message_reference: Optional[MessageReference]
    flags: int
    referenced_message: Optional["Message"]  # pycharm says it works, idk
    # interaction
    thread: Optional[Channel]

    # components
    # s sticker items
    # stickers

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
