from datetime import datetime
from typing import List, Optional, Union

from .channel import Channel
from .member import Member
from .misc import DictSerializerMixin, MISSING, Snowflake, File
from .role import Role
from .team import Application
from .user import User
from ..http.client import HTTPClient
from ...models.component import ActionRow, Button, SelectMenu
from .guild import Guild


class MessageActivity(DictSerializerMixin):
    _json: dict
    type: int
    party_id: Optional[Snowflake]
    def __init__(self, **kwargs): ...

class MessageReference(DictSerializerMixin):
    _json: dict
    message_id: Optional[Snowflake]
    channel_id: Optional[Snowflake]
    guild_id: Optional[Snowflake]
    fail_if_not_exists: Optional[bool]
    def __init__(self, **kwargs): ...

class Attachment(DictSerializerMixin):
    _json: dict
    id: Snowflake
    filename: str
    content_type: Optional[str]
    size: int
    url: str
    proxy_url: str
    height: Optional[int]
    width: Optional[int]
    ephemeral: Optional[bool]
    def __init__(self, **kwargs): ...

class MessageInteraction(DictSerializerMixin):
    _json: dict
    id: Snowflake
    type: int  # replace with Enum
    name: str
    user: User
    def __init__(self, **kwargs): ...

class ChannelMention(DictSerializerMixin):
    _json: dict
    id: Snowflake
    guild_id: Snowflake
    type: int  # Replace with enum from Channel Type, another PR
    name: str
    def __init__(self, **kwargs): ...

class Message(DictSerializerMixin):
    _client: HTTPClient
    _json: dict
    id: Snowflake
    channel_id: Snowflake
    guild_id: Optional[Snowflake]
    author: User
    member: Optional[Member]
    content: str
    timestamp: datetime.timestamp
    edited_timestamp: Optional[datetime]
    tts: bool
    mention_everyone: bool
    # mentions: array of Users, and maybe partial members
    mentions: Optional[List[Union[Member, User]]]
    mention_roles: Optional[List[str]]
    mention_channels: Optional[List["ChannelMention"]]
    attachments: List[Attachment]
    embeds: List["Embed"]
    reactions: Optional[List["ReactionObject"]]
    nonce: Union[int, str]
    pinned: bool
    webhook_id: Optional[Snowflake]
    type: int
    activity: Optional[MessageActivity]
    application: Optional[Application]
    application_id: Snowflake
    message_reference: Optional[MessageReference]
    flags: int
    referenced_message: Optional["Message"]  # pycharm says it works, idk
    interaction: Optional[MessageInteraction]
    thread: Optional[Channel]

    components: Optional[Union["Component", List["Component"]]]  # noqa: F821
    sticker_items: Optional[List["PartialSticker"]]
    stickers: Optional[List["Sticker"]]  # deprecated
    def __init__(self, **kwargs): ...
    def __repr__(self) -> str: ...
    async def delete(self, reason: Optional[str] = None) -> None: ...
    async def edit(
        self,
        content: Optional[str] = MISSING,
        *,
        tts: Optional[bool] = MISSING,
        files: Optional[Union[File, List[File]]] = MISSING,
        embeds: Optional[Union["Embed", List["Embed"]]] = MISSING,
        allowed_mentions: Optional["MessageInteraction"] = MISSING,
        message_reference: Optional["MessageReference"] = MISSING,
        components: Optional[
            Union[
                ActionRow,
                Button,
                SelectMenu,
                List[ActionRow],
                List[Button],
                List[SelectMenu],
            ]
        ] = MISSING,
    ) -> "Message": ...

    async def reply(
        self,
        content: Optional[str] = MISSING,
        *,
        tts: Optional[bool] = MISSING,
        files: Optional[Union[File, List[File]]] = MISSING,
        embeds: Optional[Union["Embed", List["Embed"]]] = MISSING,
        allowed_mentions: Optional["MessageInteraction"] = MISSING,
        components: Optional[
            Union[
                ActionRow,
                Button,
                SelectMenu,
                List[ActionRow],
                List[Button],
                List[SelectMenu],
            ]
        ] = MISSING,
    ) -> "Message": ...
    async def get_channel(self) -> Channel: ...
    async def get_guild(self) -> Guild: ...
    async def pin(self) -> None: ...
    async def unpin(self) -> None: ...
    async def publish(self) -> "Message": ...
    async def create_thread(
        self,
        name: str,
        auto_archive_duration: Optional[int] = MISSING,
        invitable: Optional[bool] = MISSING,
        reason: Optional[str] = None,
    ) -> Channel: ...
    async def create_reaction(
        self,
        emoji: Union[str, "Emoji"],
    ) -> None: ...
    async def remove_all_reactions(self) -> None: ...
    async def remove_all_reactions_of(
        self,
        emoji: Union[str, "Emoji"],
    ) -> None: ...
    async def remove_own_reaction_of(
        self,
        emoji: Union[str, "Emoji"],
    ) -> None: ...
    async def remove_reaction_from(
        self,
        emoji: Union[str, "Emoji"],
        user: Union[Member, User, int]
    ) -> None: ...
    @classmethod
    async def get_from_url(
        cls,
        url: str,
        client: HTTPClient,
    ) -> "Message": ...
    @property
    def url(self) -> str: ...

class Emoji(DictSerializerMixin):
    _client: HTTPClient
    _json: dict
    id: Optional[Snowflake]
    name: Optional[str]
    roles: Optional[List[Role]]
    user: Optional[User]
    require_colons: Optional[bool]
    managed: Optional[bool]
    animated: Optional[bool]
    available: Optional[bool]
    def __init__(self, **kwargs): ...
    @classmethod
    async def get(
        cls,
        guild_id: int,
        emoji_id: int,
        client: "HTTPClient",  # noqa
    ) -> "Emoji": ...
    @classmethod
    async def get_all_of_guild(
        cls,
        guild_id: int,
        client: "HTTPClient",  # noqa
    ) -> List["Emoji"]: ...
    async def delete(
        self,
        guild_id: int,
        reason: Optional[str] = None,
    ) -> None: ...

class ReactionObject(DictSerializerMixin):
    _json: dict
    count: int
    me: bool
    emoji: Emoji
    def __init__(self, **kwargs): ...

class PartialSticker(DictSerializerMixin):
    _json: dict
    id: Snowflake
    name: str
    format_type: int
    def __init__(self, **kwargs): ...

class Sticker(PartialSticker):
    _json: dict
    pack_id: Optional[Snowflake]
    description: Optional[str]
    tags: str
    asset: str  # deprecated
    type: int  # has its own dedicated enum
    available: Optional[bool]
    guild_id: Optional[Snowflake]
    user: Optional[User]
    sort_value: Optional[int]
    def __init__(self, **kwargs): ...

class EmbedImageStruct(DictSerializerMixin):
    _json: dict
    url: Optional[str]
    proxy_url: Optional[str]
    height: Optional[str]
    width: Optional[str]
    def __init__(self, **kwargs): ...
    def __setattr__(self, key, value) -> None: ...

class EmbedProvider(DictSerializerMixin):
    _json: dict
    name: Optional[str]
    url: Optional[str]
    def __init__(self, **kwargs): ...
    def __setattr__(self, key, value) -> None: ...

class EmbedAuthor(DictSerializerMixin):
    _json: dict
    name: str
    url: Optional[str]
    icon_url: Optional[str]
    proxy_icon_url: Optional[str]
    def __init__(self, **kwargs): ...
    def __setattr__(self, key, value) -> None: ...

class EmbedFooter(DictSerializerMixin):
    _json: dict
    text: str
    icon_url: Optional[str]
    proxy_icon_url: Optional[str]
    def __init__(self, **kwargs): ...
    def __setattr__(self, key, value) -> None: ...

class EmbedField(DictSerializerMixin):
    _json: dict
    name: str
    inline: Optional[bool]
    value: str
    def __init__(self, **kwargs): ...
    def __setattr__(self, key, value) -> None: ...

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
    def __init__(self, **kwargs): ...
    def __setattr__(self, key, value) -> None: ...
    def add_field(self, name: str, value: str, inline: Optional[bool] = False) -> None: ...
    def clear_fields(self) -> None: ...
    def insert_field_at(self, index: int,  name: str, value: str, inline: Optional[bool] = False) -> None: ...
    def set_field_at(self, index: int, name: str, value: str, inline: Optional[bool] = False) -> None: ...
    def remove_field(self, index: int) -> None: ...
    def remove_author(self) -> None: ...
    def set_author(self, name: str, url: Optional[str] = None, icon_url: Optional[str] = None, proxy_icon_url: Optional[str] = None) -> None: ...
    def set_footer(self, text: str, icon_url: Optional[str] = None, proxy_icon_url: Optional[str] = None) -> None: ...
    def set_image(self, url: str, proxy_url: Optional[str] = None, height: Optional[int] = None, width: Optional[int] = None) -> None: ...
    def set_video(self, url: str, proxy_url: Optional[str] = None, height: Optional[int] = None, width: Optional[int] = None) -> None: ...
    def set_thumbnail(self, url: str, proxy_url: Optional[str] = None, height: Optional[int] = None, width: Optional[int] = None) -> None: ...
