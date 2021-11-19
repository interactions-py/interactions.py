from datetime import datetime
from enum import IntEnum
from typing import List, Optional, Union

from .channel import Channel
from .member import Member
from .misc import DictSerializerMixin
from .team import Application
from .user import User

class MessageType(IntEnum):
    DEFAULT = 0
    RECIPIENT_ADD = 1
    RECIPIENT_REMOVE = 2
    CALL = 3
    CHANNEL_NAME_CHANGE = 4
    CHANNEL_ICON_CHANGE = 5
    CHANNEL_PINNED_MESSAGE = 6
    GUILD_MEMBER_JOIN = 7
    USER_PREMIUM_GUILD_SUBSCRIPTION = 8
    USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_1 = 9
    USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_2 = 10
    USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_3 = 11
    CHANNEL_FOLLOW_ADD = 12
    GUILD_DISCOVERY_DISQUALIFIED = 14
    GUILD_DISCOVERY_REQUALIFIED = 15
    GUILD_DISCOVERY_GRACE_PERIOD_INITIAL_WARNING = 16
    GUILD_DISCOVERY_GRACE_PERIOD_FINAL_WARNING = 17
    THREAD_CREATED = 18
    REPLY = 19
    APPLICATION_COMMAND = 20
    THREAD_STARTER_MESSAGE = 21
    GUILD_INVITE_REMINDER = 22
    CONTEXT_MENU_COMMAND = 23

class MessageActivity(DictSerializerMixin):
    _json: dict
    type: int
    party_id: Optional[str]

    __slots__ = ("_json", "type", "party_id")
    def __init__(self, **kwargs): ...

class MessageReference(DictSerializerMixin):
    _json: dict
    message_id: Optional[int]
    channel_id: Optional[int]
    guild_id: Optional[int]
    fail_if_not_exists: Optional[bool]

    __slots__ = ("_json", "message_id", "channel_id", "guild_id", "fail_if_not_exists")
    def __init__(self, **kwargs): ...

class Attachment(DictSerializerMixin):
    _json: dict
    id: int
    filename: str
    content_type: Optional[str]
    size: int
    url: str
    proxy_url: str
    height: Optional[int]
    width: Optional[int]

    __slots__ = (
        "_json",
        "id",
        "filename",
        "description",
        "content_type",
        "size",
        "url",
        "proxy_url",
        "height",
        "width",
    )
    def __init__(self, **kwargs): ...

class MessageInteraction(DictSerializerMixin):
    _json: dict
    id: int
    type: int  # replace with Enum
    name: str
    user: User

    __slots__ = ("_json", "id", "type", "name", "user")
    def __init__(self, **kwargs): ...

class ChannelMention(DictSerializerMixin):
    _json: dict
    id: int
    guild_id: int
    type: int  # Replace with enum from Channel Type, another PR
    name: str

    __slots__ = ("_json", "id", "type", "name", "guild_id")
    def __init__(self, **kwargs): ...

class Message(DictSerializerMixin):
    _json: dict
    id: int
    channel_id: int
    guild_id: Optional[int]
    author: User
    member: Optional[Member]
    content: str
    timestamp: datetime.timestamp
    edited_timestamp: Optional[datetime]
    tts: bool
    mention_everyone: bool
    mentions: Optional[List[Union[Member, User]]]
    mention_roles: Optional[List[str]]
    mention_channels: Optional[List["ChannelMention"]]
    attachments: List[Attachment]
    embeds: List["Embed"]
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

    components: Optional[Union["Component", List["Component"]]]  # noqa: F821
    sticker_items: Optional[List["PartialSticker"]]
    stickers: Optional[List["Sticker"]]  # deprecated

    __slots__ = (
        "_json",
        "id",
        "channel_id",
        "guild_id",
        "author",
        "member",
        "content",
        "timestamp",
        "edited_timestamp",
        "tts",
        "mention_everyone",
        "mentions",
        "mention_roles",
        "mention_channels",
        "attachments",
        "embeds",
        "reactions",
        "nonce",
        "pinned",
        "webhook_id",
        "type",
        "activity",
        "application",
        "application_id",
        "message_reference",
        "flags",
        "referenced_message",
        "interaction",
        "thread",
        "components",
        "sticker_items",
        "stickers",
    )
    def __init__(self, **kwargs): ...

class Emoji(DictSerializerMixin):
    _json: dict
    id: Optional[int]
    name: Optional[str]
    roles: Optional[List[str]]
    user: Optional[User]
    require_colons: Optional[bool]
    managed: Optional[bool]
    animated: Optional[bool]
    available: Optional[bool]

    __slots__ = (
        "_json",
        "id",
        "name",
        "roles",
        "user",
        "require_colons",
        "managed",
        "animated",
        "available",
    )
    def __init__(self, **kwargs): ...

class ReactionObject(DictSerializerMixin):
    _json: dict
    count: int
    me: bool
    emoji: Emoji

    __slots__ = ("_json", "count", "me", "bool")
    def __init__(self, **kwargs): ...

class PartialSticker(DictSerializerMixin):
    _json: dict
    id: int
    name: str
    format_type: int

    __slots__ = ("_json", "id", "name", "format_type")
    def __init__(self, **kwargs): ...

class Sticker(PartialSticker):
    _json: dict
    pack_id: Optional[int]
    description: Optional[str]
    tags: str
    asset: str  # deprecated
    type: int  # has its own dedicated enum
    available: Optional[bool]
    guild_id: Optional[int]
    user: Optional[User]
    sort_value: Optional[int]

    __slots__ = (
        "_json",
        "id",
        "pack_id",
        "name",
        "description",
        "tags",
        "asset",
        "type",
        "format_type",
        "available",
        "guild_id",
        "user",
        "sort_value",
    )
    def __init__(self, **kwargs): ...

class EmbedImageStruct(DictSerializerMixin):
    _json: dict
    url: Optional[str]
    proxy_url: Optional[str]
    height: Optional[str]
    width: Optional[str]

    __slots__ = ("_json", "url", "proxy_url", "height", "width")
    def __init__(self, **kwargs): ...

class EmbedProvider(DictSerializerMixin):
    _json: dict
    name: Optional[str]
    url: Optional[str]

    __slots__ = ("_json", "url", "name")
    def __init__(self, **kwargs): ...

class EmbedAuthor(DictSerializerMixin):
    _json: dict
    name: str
    url: Optional[str]
    icon_url: Optional[str]
    proxy_icon_url: Optional[str]

    __slots__ = ("_json", "url", "proxy_icon_url", "icon_url", "name")
    def __init__(self, **kwargs): ...

class EmbedFooter(DictSerializerMixin):
    _json: dict
    text: str
    icon_url: Optional[str]
    proxy_icon_url: Optional[str]

    __slots__ = ("_json", "text", "proxy_icon_url", "icon_url")
    def __init__(self, **kwargs): ...

class EmbedField(DictSerializerMixin):
    _json: dict
    name: str
    inline: Optional[bool]
    value: str

    __slots__ = ("_json", "name", "inline", "value")
    def __init__(self, **kwargs): ...

class Embed(DictSerializerMixin):
    _json: dict
    title: Optional[str]
    type: Optional[str]
    description: Optional[str]
    url: Optional[str]
    timestamp: Optional[datetime]
    color: Optional[int]
    footer: Optional[EmbedFooter]
    image: Optional[EmbedImageStruct]
    thumbnail: Optional[EmbedImageStruct]
    video: Optional[EmbedImageStruct]
    provider: Optional[EmbedProvider]
    author: Optional[EmbedAuthor]
    fields: Optional[List[EmbedField]]

    __slots__ = (
        "_json",
        "title",
        "type",
        "description",
        "url",
        "timestamp",
        "color",
        "footer",
        "image",
        "thumbnail",
        "video",
        "provider",
        "author",
        "fields",
    )
    def __init__(self, **kwargs): ...
