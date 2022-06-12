from datetime import datetime
from enum import IntEnum
from typing import List, Optional, Union

from ... import ActionRow, Button, Component, SelectMenu
from ..http.client import HTTPClient
from .attrs_utils import MISSING, ClientSerializerMixin, DictSerializerMixin, define
from .channel import Channel as Channel
from .guild import Guild
from .member import Member as Member
from .misc import File, Snowflake
from .role import Role as Role
from .team import Application as Application
from .user import User as User

class MessageType(IntEnum):
    DEFAULT: int
    RECIPIENT_ADD: int
    RECIPIENT_REMOVE: int
    CALL: int
    CHANNEL_NAME_CHANGE: int
    CHANNEL_ICON_CHANGE: int
    CHANNEL_PINNED_MESSAGE: int
    GUILD_MEMBER_JOIN: int
    USER_PREMIUM_GUILD_SUBSCRIPTION: int
    USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_1: int
    USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_2: int
    USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_3: int
    CHANNEL_FOLLOW_ADD: int
    GUILD_DISCOVERY_DISQUALIFIED: int
    GUILD_DISCOVERY_REQUALIFIED: int
    GUILD_DISCOVERY_GRACE_PERIOD_INITIAL_WARNING: int
    GUILD_DISCOVERY_GRACE_PERIOD_FINAL_WARNING: int
    THREAD_CREATED: int
    REPLY: int
    APPLICATION_COMMAND: int
    THREAD_STARTER_MESSAGE: int
    GUILD_INVITE_REMINDER: int
    CONTEXT_MENU_COMMAND: int

@define()
class MessageActivity(DictSerializerMixin):
    type: int
    party_id: Optional[Snowflake]

@define()
class MessageReference(DictSerializerMixin):
    message_id: Optional[Snowflake]
    channel_id: Optional[Snowflake]
    guild_id: Optional[Snowflake]
    fail_if_not_exists: Optional[bool]

@define()
class Attachment(DictSerializerMixin):
    id: Snowflake
    filename: str
    content_type: Optional[str]
    size: int
    url: str
    proxy_url: str
    height: Optional[int]
    width: Optional[int]
    ephemeral: Optional[bool]

@define()
class MessageInteraction(ClientSerializerMixin):
    id: Snowflake
    type: int
    name: str
    user: User

@define()
class ChannelMention(DictSerializerMixin):
    id: Snowflake
    guild_id: Snowflake
    type: int
    name: str

@define()
class Emoji(ClientSerializerMixin):
    id: Optional[Snowflake] = None
    name: Optional[str] = None
    roles: Optional[List[Role]] = None
    user: Optional[User] = None
    require_colons: Optional[bool] = None
    managed: Optional[bool] = None
    animated: Optional[bool] = None
    available: Optional[bool] = None
    @classmethod
    async def get(
        cls,
        guild_id: Union[int, Snowflake, Guild],
        emoji_id: Union[int, Snowflake],
        client: HTTPClient
    ) -> Emoji: ...
    @classmethod
    async def get_all_of_guild(cls, guild_id: Union[int, Snowflake, Guild], client: HTTPClient) -> List[Emoji]: ...
    async def delete(self, guild_id: Union[int, Snowflake, Guild], reason: Optional[str] = ...) -> None: ...
    @property
    def url(self) -> str: ...

@define()
class EmbedImageStruct(DictSerializerMixin):
    url: str
    proxy_url: Optional[str] = None
    height: Optional[int] = None
    width: Optional[int] = None
    def __setattr__(self, key, value) -> None: ...

@define()
class EmbedProvider(DictSerializerMixin):
    name: Optional[str] = None
    url: Optional[str] = None
    def __setattr__(self, key, value) -> None: ...

@define()
class EmbedAuthor(DictSerializerMixin):
    name: str
    url: Optional[str] = None
    icon_url: Optional[str] = None
    proxy_icon_url: Optional[str] = None
    def __setattr__(self, key, value) -> None: ...

@define()
class EmbedFooter(DictSerializerMixin):
    text: str
    icon_url: Optional[str] = None
    proxy_icon_url: Optional[str] = None
    def __setattr__(self, key, value) -> None: ...

@define()
class EmbedField(DictSerializerMixin):
    name: str
    inline: Optional[bool] = None
    value: str
    def __setattr__(self, key, value) -> None: ...

@define()
class Embed(DictSerializerMixin):
    title: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    timestamp: Optional[datetime] = None
    color: Optional[int] = None
    footer: Optional[EmbedFooter] = None
    image: Optional[EmbedImageStruct] = None
    thumbnail: Optional[EmbedImageStruct] = None
    video: Optional[EmbedImageStruct] = None
    provider: Optional[EmbedProvider] = None
    author: Optional[EmbedAuthor] = None
    fields: Optional[List[EmbedField]] = None
    def __setattr__(self, key, value) -> None: ...
    def add_field(self, name: str, value: str, inline: Optional[bool] = ...) -> None: ...
    def clear_fields(self) -> None: ...
    def insert_field_at(
        self, index: int, name: str = ..., value: str = ..., inline: Optional[bool] = ...
    ) -> None: ...
    def set_field_at(
        self, index: int, name: str, value: str, inline: Optional[bool] = ...
    ) -> None: ...
    def remove_field(self, index: int) -> None: ...
    def remove_author(self) -> None: ...
    def set_author(
        self,
        name: str,
        url: Optional[str] = ...,
        icon_url: Optional[str] = ...,
        proxy_icon_url: Optional[str] = ...,
    ) -> None: ...
    def set_footer(
        self, text: str, icon_url: Optional[str] = ..., proxy_icon_url: Optional[str] = ...
    ) -> None: ...
    def set_image(
        self,
        url: str,
        proxy_url: Optional[str] = ...,
        height: Optional[int] = ...,
        width: Optional[int] = ...,
    ) -> None: ...
    def set_video(
        self,
        url: str,
        proxy_url: Optional[str] = ...,
        height: Optional[int] = ...,
        width: Optional[int] = ...,
    ) -> None: ...
    def set_thumbnail(
        self,
        url: str,
        proxy_url: Optional[str] = ...,
        height: Optional[int] = ...,
        width: Optional[int] = ...,
    ) -> None: ...

@define()
class PartialSticker(DictSerializerMixin):
    id: Snowflake
    name: str
    format_type: int

@define()
class Sticker(PartialSticker):
    id: Snowflake
    pack_id: Optional[Snowflake]
    name: str
    description: Optional[str]
    tags: str
    asset: str
    type: int
    format_type: int
    available: Optional[bool]
    guild_id: Optional[Snowflake]
    user: Optional[User]
    sort_value: Optional[int]

@define()
class ReactionObject(DictSerializerMixin):
    count: int
    me: bool
    emoji: Emoji

@define()
class Message(ClientSerializerMixin):
    id: Snowflake
    channel_id: Snowflake
    guild_id: Optional[Snowflake]
    author: User
    member: Optional[Member]
    content: str
    timestamp: datetime
    edited_timestamp: Optional[datetime]
    tts: bool
    mention_everyone: bool
    mentions: Optional[List[Union[Member, User]]]
    mention_roles: Optional[List[str]]
    mention_channels: Optional[List[ChannelMention]]
    attachments: List[Attachment]
    embeds: List[Embed]
    reactions: Optional[List[ReactionObject]]
    nonce: Optional[Union[int, str]]
    pinned: bool
    webhook_id: Optional[Snowflake]
    type: int
    activity: Optional[MessageActivity]
    application: Optional[Application]
    application_id: Optional[Snowflake]
    message_reference: Optional[MessageReference]
    flags: int
    referenced_message: Optional[MessageReference]
    interaction: Optional[MessageInteraction]
    thread: Optional[Channel]
    components: Optional[Union[Component, List[Component]]]
    sticker_items: Optional[List[PartialSticker]]
    stickers: Optional[List[Sticker]]
    def __repr__(self) -> str: ...
    async def delete(self, reason: Optional[str] = None) -> None: ...
    async def edit(
        self,
        content: Optional[str] = MISSING,
        *,
        tts: Optional[bool] = MISSING,
        files: Optional[Union[File, List[File]]] = MISSING,
        embeds: Optional[Union[Embed, List[Embed]]] = MISSING,
        suppress_embeds: Optional[bool] = MISSING,
        allowed_mentions: Optional[MessageInteraction] = MISSING,
        message_reference: Optional[MessageReference] = MISSING,
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
    ) -> Message: ...
    async def reply(
        self,
        content: Optional[str] = MISSING,
        *,
        tts: Optional[bool] = MISSING,
        files: Optional[Union[File, List[File]]] = MISSING,
        embeds: Optional[Union[Embed, List[Embed]]] = MISSING,
        allowed_mentions: Optional[MessageInteraction] = MISSING,
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
    ) -> Message: ...
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
        emoji: Union[str, Emoji],
    ) -> None: ...
    async def remove_all_reactions(self) -> None: ...
    async def remove_all_reactions_of(
        self,
        emoji: Union[str, Emoji],
    ) -> None: ...
    async def remove_own_reaction_of(
        self,
        emoji: Union[str, Emoji],
    ) -> None: ...
    async def remove_reaction_from(
        self, emoji: Union[str, Emoji], user: Union[Member, User, int]
    ) -> None: ...
    async def get_users_from_reaction(
        self,
        emoji: Union[str, Emoji],
    ) -> List[User]: ...
    @classmethod
    async def get_from_url(
        cls,
        url: str,
        client: HTTPClient,
    ) -> Message: ...
    @property
    def url(self) -> str: ...
