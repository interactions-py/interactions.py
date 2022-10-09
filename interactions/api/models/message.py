import contextlib
from datetime import datetime
from enum import IntEnum
from io import BytesIO
from typing import TYPE_CHECKING, List, Optional, Union

from ...client.models.component import ActionRow, Button, SelectMenu
from ...utils.attrs_utils import (
    ClientSerializerMixin,
    DictSerializerMixin,
    convert_list,
    convert_type,
    deepcopy_kwargs,
    define,
    field,
)
from ...utils.missing import MISSING
from ..error import LibraryException
from .channel import Channel
from .emoji import Emoji
from .member import Member
from .misc import AllowedMentions, File, IDMixin, Snowflake
from .team import Application
from .user import User

if TYPE_CHECKING:
    from ..http import HTTPClient

__all__ = (
    "MessageType",
    "Message",
    "MessageReference",
    "MessageActivity",
    "MessageInteraction",
    "ChannelMention",
    "Embed",
    "EmbedAuthor",
    "EmbedProvider",
    "EmbedImageStruct",
    "EmbedField",
    "Attachment",
    "EmbedFooter",
    "ReactionObject",
    "PartialSticker",
    "Sticker",
    "StickerPack",
)


class MessageType(IntEnum):
    """An enumerable object representing the types of messages."""

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
    AUTO_MODERATION_ACTION = 24


@define()
class MessageActivity(DictSerializerMixin):
    """A class object representing the activity state of a message.

    .. note::
        ``party_id`` is ambiguous -- Discord poorly documented this. :)

        We assume it's for game rich presence invites?
        i.e. : Phasmophobia and Call of Duty.

    :ivar str type: The message activity type.
    :ivar Optional[Snowflake] party_id?: The party ID of the activity.
    """

    type: int = field()
    party_id: Optional[Snowflake] = field(converter=Snowflake, default=None)


@define()
class MessageReference(DictSerializerMixin):
    """
    A class object representing the "referenced"/replied message.

    .. note::
        All of the attributes in this class are optionals because
        a message can potentially never be referenced.

    :ivar Optional[Snowflake] message_id?: The ID of the referenced message.
    :ivar Optional[Snowflake] channel_id?: The channel ID of the referenced message.
    :ivar Optional[Snowflake] guild_id?: The guild ID of the referenced message.
    :ivar Optional[bool] fail_if_not_exists?: Whether the message reference exists.
    """

    message_id: Optional[Snowflake] = field(converter=Snowflake, default=None)
    channel_id: Optional[Snowflake] = field(converter=Snowflake, default=None)
    guild_id: Optional[Snowflake] = field(converter=Snowflake, default=None)
    fail_if_not_exists: Optional[bool] = field(default=None)


@define()
class Attachment(ClientSerializerMixin, IDMixin):
    """
    A class object representing an attachment in a message.

    .. note::
        ``height`` and ``width`` have values based off of ``content_type``,
        which requires it to be a media file with viewabiltity as a photo,
        animated photo, GIF and/or video.

        If `ephemeral` is given, the attachments will automatically be removed after a set period of time.
        In the case of regular messages, they're available as long as the message associated with the attachment exists.

    :ivar int id: The ID of the attachment.
    :ivar str filename: The name of the attachment file.
    :ivar Optional[str] description?: The description of the file.
    :ivar Optional[str] content_type?: The type of attachment file.
    :ivar int size: The size of the attachment file.
    :ivar str url: The CDN URL of the attachment file.
    :ivar str proxy_url: The proxied/cached CDN URL of the attachment file.
    :ivar Optional[int] height?: The height of the attachment file.
    :ivar Optional[int] width?: The width of the attachment file.
    :ivar Optional[bool] ephemeral: Whether the attachment is ephemeral.
    """

    id: Snowflake = field(converter=Snowflake)
    filename: str = field()
    content_type: Optional[str] = field(default=None)
    size: int = field()
    url: str = field()
    proxy_url: str = field()
    height: Optional[int] = field(default=None)
    width: Optional[int] = field(default=None)
    ephemeral: Optional[bool] = field(default=None)

    async def download(self) -> BytesIO:
        """
        Downloads the attachment.

        :returns: The attachment's bytes as BytesIO object
        :rtype: BytesIO
        """

        if not self._client:
            raise LibraryException(code=13)

        async with self._client._req._session.get(self.url) as response:
            _bytes: bytes = await response.content.read()

        return BytesIO(_bytes)


@define()
class MessageInteraction(ClientSerializerMixin, IDMixin):
    """
    A class object that resembles the interaction used to generate
    the associated message.

    :ivar Snowflake id: ID of the interaction.
    :ivar int type: Type of interaction.
    :ivar str name: Name of the application command.
    :ivar User user: The user who invoked the interaction.
    """

    # TODO: document member attr.
    id: Snowflake = field(converter=Snowflake)
    type: int = field()  # replace with Enum
    name: str = field()
    user: User = field(converter=User, add_client=True)


@define()
class ChannelMention(DictSerializerMixin, IDMixin):
    """
    A class object that resembles the mention of a channel
    in a guild.

    :ivar Snowflake id: The ID of the channel.
    :ivar Snowflake guild_id: The ID of the guild that contains the channel.
    :ivar int type: The channel type.
    :ivar str name: The name of the channel.
    """

    id: Snowflake = field(converter=Snowflake)
    guild_id: Snowflake = field(converter=Snowflake)
    type: int = field()  # Replace with enum from Channel Type, another PR
    name: str = field()


@define()
class EmbedImageStruct(DictSerializerMixin):
    """
    A class object representing the structure of an image in an embed.

    The structure of an embed image:

    .. code-block:: python

        interactions.EmbedImageStruct(
            url="https://example.com/",
            height=300,
            width=250,
        )

    :ivar str url: Source URL of the object.
    :ivar Optional[str] proxy_url?: Proxied url of the object.
    :ivar Optional[int] height?: Height of the object.
    :ivar Optional[int] width?: Width of the object.
    """

    url: str = field()
    proxy_url: Optional[str] = field(default=None)
    height: Optional[int] = field(default=None)
    width: Optional[int] = field(default=None)

    def __setattr__(self, key, value) -> None:
        super().__setattr__(key, value)
        if key not in {"_json", "_extras"} and (
            key not in self._json or value != self._json.get(key)
        ):
            if value is not None and value is not MISSING:
                self._json.update({key: value})

            elif value is None and key in self._json.keys():
                del self._json[key]


@define()
class EmbedProvider(DictSerializerMixin):
    """
    A class object representing the provider of an embed.

    :ivar Optional[str] name?: Name of provider
    :ivar Optional[str] url?: URL of provider
    """

    name: Optional[str] = field(default=None)
    url: Optional[str] = field(default=None)

    def __setattr__(self, key, value) -> None:
        super().__setattr__(key, value)
        if key not in {"_json", "_extras"} and (
            key not in self._json or value != self._json.get(key)
        ):
            if value is not None and value is not MISSING:
                self._json.update({key: value})

            elif value is None and key in self._json.keys():
                del self._json[key]


@define()
class EmbedAuthor(DictSerializerMixin):
    """
    A class object representing the author of an embed.

    The structure of an embed author:

    .. code-block:: python

        interactions.EmbedAuthor(
            name="fl0w#0001",
        )

    :ivar str name: Name of author
    :ivar Optional[str] url?: URL of author
    :ivar Optional[str] icon_url?: URL of author icon
    :ivar Optional[str] proxy_icon_url?: Proxied URL of author icon
    """

    name: str = field()
    url: Optional[str] = field(default=None)
    icon_url: Optional[str] = field(default=None)
    proxy_icon_url: Optional[str] = field(default=None)

    def __setattr__(self, key, value) -> None:
        super().__setattr__(key, value)
        if key not in {"_json", "_extras"} and (
            key not in self._json or value != self._json.get(key)
        ):
            if value is not None and value is not MISSING:
                self._json.update({key: value})

            elif value is None and key in self._json.keys():
                del self._json[key]


@define()
class EmbedFooter(DictSerializerMixin):
    """
    A class object representing the footer of an embed.

    The structure of an embed footer:

    .. code-block:: python

        interactions.EmbedFooter(
            text="yo mama so short, she can fit in here",
        )

    :ivar str text: Footer text
    :ivar Optional[str] icon_url?: URL of footer icon
    :ivar Optional[str] proxy_icon_url?: Proxied URL of footer icon
    """

    text: str = field()
    icon_url: Optional[str] = field(default=None)
    proxy_icon_url: Optional[str] = field(default=None)

    def __setattr__(self, key, value) -> None:
        super().__setattr__(key, value)
        if key not in {"_json", "_extras"} and (
            key not in self._json or value != self._json.get(key)
        ):
            if value is not None and value is not MISSING:
                self._json.update({key: value})

            elif value is None and key in self._json.keys():
                del self._json[key]


@define()
class EmbedField(DictSerializerMixin):
    """
    A class object representing the field of an embed.

    The structure of an embed field:

    .. code-block:: python

        interactions.EmbedField(
            name="field title",
            value="blah blah blah",
            inline=False,
        )

    :ivar str name: Name of the field.
    :ivar str value: Value of the field
    :ivar Optional[bool] inline?: A status denoting if the field should be displayed inline.
    """

    name: str = field()
    inline: Optional[bool] = field(default=None)
    value: str = field()

    def __setattr__(self, key, value) -> None:
        super().__setattr__(key, value)
        if key not in {"_json", "_extras"} and (
            key not in self._json or value != self._json.get(key)
        ):
            if value is not None and value is not MISSING:
                self._json.update({key: value})

            elif value is None and key in self._json.keys():
                del self._json[key]


@define()
@deepcopy_kwargs()
class Embed(DictSerializerMixin):
    """
    A class object representing an embed.

    .. note::
        The example provided below is for a very basic
        implementation of an embed. Embeds are more unique
        than what is being shown.

    The structure for an embed:

    .. code-block:: python

        interactions.Embed(
            title="Embed title",
            fields=[interaction.EmbedField(...)],
        )

    :ivar Optional[str] title?: Title of embed
    :ivar Optional[str] type?: Embed type, relevant by CDN file connected. This is only important to rendering.
    :ivar Optional[str] description?: Embed description
    :ivar Optional[str] url?: URL of embed
    :ivar Optional[datetime] timestamp?: Timestamp of embed content
    :ivar Optional[int] color?: Color code of embed
    :ivar Optional[EmbedFooter] footer?: Footer information
    :ivar Optional[EmbedImageStruct] image?: Image information
    :ivar Optional[EmbedImageStruct] thumbnail?: Thumbnail information
    :ivar Optional[EmbedImageStruct] video?: Video information
    :ivar Optional[EmbedProvider] provider?: Provider information
    :ivar Optional[EmbedAuthor] author?: Author information
    :ivar Optional[List[EmbedField]] fields?: A list of fields denoting field information
    """

    title: Optional[str] = field(default=None)
    type: Optional[str] = field(default=None)
    description: Optional[str] = field(default=None)
    url: Optional[str] = field(default=None)
    timestamp: Optional[datetime] = field(
        converter=convert_type(datetime, classmethod="fromisoformat"), default=None
    )
    color: Optional[int] = field(default=None)
    footer: Optional[EmbedFooter] = field(converter=EmbedFooter, default=None)
    image: Optional[EmbedImageStruct] = field(converter=EmbedImageStruct, default=None)
    thumbnail: Optional[EmbedImageStruct] = field(converter=EmbedImageStruct, default=None)
    video: Optional[EmbedImageStruct] = field(converter=EmbedImageStruct, default=None)
    provider: Optional[EmbedProvider] = field(converter=EmbedProvider, default=None)
    author: Optional[EmbedAuthor] = field(converter=EmbedAuthor, default=None)
    fields: Optional[List[EmbedField]] = field(converter=convert_list(EmbedField), default=None)

    def __setattr__(self, key, value) -> None:
        super().__setattr__(key, value)

        if key not in {"_json", "_extras"} and (
            key not in self._json
            or (
                value != self._json.get(key)
                or not isinstance(value, dict)
                # we don't need this instance check in components because serialisation works for them
            )
        ):
            if value is not None and value is not MISSING:
                try:
                    value = [val._json for val in value] if isinstance(value, list) else value._json
                except AttributeError:
                    if isinstance(value, datetime):
                        value = value.isoformat()
                self._json.update({key: value})

            elif value is None and key in self._json.keys():
                del self._json[key]

    def add_field(self, name: str, value: str, inline: Optional[bool] = False) -> None:
        """
        Adds a field to the embed

        :param name: The name of the field
        :type name: str
        :param value: The value of the field
        :type value: str
        :param inline?: if the field is in the same line as the previous one
        :type inline?: Optional[bool]
        """

        fields = self.fields or []
        fields.append(EmbedField(name=name, value=value, inline=inline))

        self.fields = fields
        # We must use "=" here to call __setattr__. Append does not call any magic, making it impossible to modify the
        # json when using it, so the object what would be sent wouldn't be modified.
        # Imo this is still better than doing a `self._json.update({"fields": [field._json for ...]})`

    def clear_fields(self) -> None:
        """
        Clears all the fields of the embed
        """

        self.fields = []

    def insert_field_at(
        self, index: int, name: str, value: str, inline: Optional[bool] = False
    ) -> None:
        """
        Inserts a field in the embed at the specified index

        :param index: The field's index to insert
        :type index: int
        :param name: The name of the field
        :type name: str
        :param value: The value of the field
        :type value: str
        :param inline?: if the field is in the same line as the previous one
        :type inline?: Optional[bool]
        """

        try:
            fields = self.fields
            fields.insert(index, EmbedField(name=name, value=value, inline=inline))
            self.fields = fields

        except AttributeError as e:
            raise AttributeError("No fields found in Embed") from e

    def set_field_at(
        self, index: int, name: str, value: str, inline: Optional[bool] = False
    ) -> None:
        """
        Overwrites the field in the embed at the specified index

        :param index: The field's index to overwrite
        :type index: int
        :param name: The name of the field
        :type name: str
        :param value: The value of the field
        :type value: str
        :param inline?: if the field is in the same line as the previous one
        :type inline?: Optional[bool]
        """

        try:
            fields = self.fields
            fields[index] = EmbedField(name=name, value=value, inline=inline)
            self.fields = fields

        except AttributeError as e:
            raise AttributeError("No fields found in Embed") from e

        except IndexError as e:
            raise IndexError("No fields at this index") from e

    def remove_field(self, index: int) -> None:
        """
        Remove field at the specified index

        :param index: The field's index to remove
        :type index: int
        """

        try:
            fields = self.fields
            fields.pop(index)
            self.fields = fields

        except AttributeError as e:
            raise AttributeError("No fields found in Embed") from e

        except IndexError as e:
            raise IndexError("Field not Found at index") from e

    def remove_author(self) -> None:
        """
        Removes the embed's author
        """

        with contextlib.suppress(AttributeError):
            del self.author

    def set_author(
        self,
        name: str,
        url: Optional[str] = None,
        icon_url: Optional[str] = None,
        proxy_icon_url: Optional[str] = None,
    ) -> None:
        """
        Sets the embed's author

        :param name: The name of the author
        :type name: str
        :param url?: Url of author
        :type url?: Optional[str]
        :param icon_url?: Url of author icon (only supports http(s) and attachments)
        :type icon_url?: Optional[str]
        :param proxy_icon_url?: A proxied url of author icon
        :type proxy_icon_url?: Optional[str]
        """

        self.author = EmbedAuthor(
            name=name, url=url, icon_url=icon_url, proxy_icon_url=proxy_icon_url
        )

    def set_footer(
        self, text: str, icon_url: Optional[str] = None, proxy_icon_url: Optional[str] = None
    ) -> None:
        """
        Sets the embed's footer

        :param text: The text of the footer
        :type text: str
        :param icon_url?: Url of footer icon (only supports http(s) and attachments)
        :type icon_url?: Optional[str]
        :param proxy_icon_url?: A proxied url of footer icon
        :type proxy_icon_url?: Optional[str]
        """

        self.footer = EmbedFooter(text=text, icon_url=icon_url, proxy_icon_url=proxy_icon_url)

    def set_image(
        self,
        url: str,
        proxy_url: Optional[str] = None,
        height: Optional[int] = None,
        width: Optional[int] = None,
    ) -> None:
        """
        Sets the embed's image

        :param url: Url of the image
        :type url: str
        :param proxy_url?: A proxied url of the image
        :type proxy_url?: Optional[str]
        :param height?: The image's height
        :type height?: Optional[int]
        :param width?: The image's width
        :type width?: Optional[int]
        """

        self.image = EmbedImageStruct(url=url, proxy_url=proxy_url, height=height, width=width)

    def set_video(
        self,
        url: str,
        proxy_url: Optional[str] = None,
        height: Optional[int] = None,
        width: Optional[int] = None,
    ) -> None:
        """
        Sets the embed's video

        :param url: Url of the video
        :type url: str
        :param proxy_url?: A proxied url of the video
        :type proxy_url?: Optional[str]
        :param height?: The video's height
        :type height?: Optional[int]
        :param width?: The video's width
        :type width?: Optional[int]
        """

        self.video = EmbedImageStruct(url=url, proxy_url=proxy_url, height=height, width=width)

    def set_thumbnail(
        self,
        url: str,
        proxy_url: Optional[str] = None,
        height: Optional[int] = None,
        width: Optional[int] = None,
    ) -> None:
        """
        Sets the embed's thumbnail

        :param url: Url of the thumbnail
        :type url: str
        :param proxy_url?: A proxied url of the thumbnail
        :type proxy_url?: Optional[str]
        :param height?: The thumbnail's height
        :type height?: Optional[int]
        :param width?: The thumbnail's width
        :type width?: Optional[int]
        """

        self.thumbnail = EmbedImageStruct(url=url, proxy_url=proxy_url, height=height, width=width)


@define()
class PartialSticker(DictSerializerMixin, IDMixin):
    """
    Partial object for a Sticker.

    :ivar Snowflake id: ID of the sticker
    :ivar str name: Name of the sticker
    :ivar int format_type: Type of sticker format
    """

    id: Snowflake = field(converter=Snowflake)
    name: str = field()
    format_type: int = field()


@define()
class Sticker(PartialSticker, IDMixin):
    """
    A class object representing a full sticker apart from a partial.

    :ivar Snowflake id: ID of the sticker
    :ivar Optional[Snowflake] pack_id?: ID of the pack the sticker is from.
    :ivar str name: Name of the sticker
    :ivar Optional[str] description?: Description of the sticker
    :ivar str tags: Autocomplete/suggestion tags for the sticker (max 200 characters)
    :ivar str asset: Previously a sticker asset hash, now an empty string.
    :ivar int type: Type of sticker
    :ivar int format_type: Type of sticker format
    :ivar Optional[bool] available?: Status denoting if this sticker can be used. (Can be false via server boosting)
    :ivar Optional[Snowflake] guild_id?: Guild ID that owns the sticker.
    :ivar Optional[User] user?: The user that uploaded the sticker.
    :ivar Optional[int] sort_value?: The standard sticker's sort order within its pack
    """

    id: Snowflake = field(converter=Snowflake)
    pack_id: Optional[Snowflake] = field(converter=Snowflake, default=None)
    name: str = field()
    description: Optional[str] = field(default=None)
    tags: str = field()
    asset: str = field()
    type: int = field()
    format_type: int = field()
    available: Optional[bool] = field(default=None)
    guild_id: Optional[Snowflake] = field(converter=Snowflake, default=None)
    user: Optional[User] = field(converter=User, default=None)
    sort_value: Optional[int] = field(default=None)


@define()
class StickerPack(DictSerializerMixin, IDMixin):
    """
    A class objects representing a pack of stickers.

    :ivar Snowflake id: ID of the sticker pack.
    :ivar List[Sticker] stickers: The stickers in the pack.
    :ivar str name: The name of sticker pack.
    :ivar Snowflake sku_id: ID of the pack's SKU.
    :ivar Optional[Snowflake] cover_sticker_id?: ID of a sticker in the pack which is shown as the pack's icon.
    :ivar str description: The description of sticker pack.
    :ivar Optional[Snowflake] banned_asset_id?: ID of the sticker pack's banner image.
    """

    id: Snowflake = field(converter=Snowflake)
    stickers: List[Sticker] = field(converter=convert_list(Sticker))
    name: str = field()
    sku_id: Snowflake = field(converter=Snowflake)
    cover_sticker_id: Optional[Snowflake] = field(converter=Snowflake, default=None)
    description: str = field()
    banned_asset_id: Optional[Snowflake] = field(converter=Snowflake, default=None)


@define()
class ReactionObject(DictSerializerMixin):
    """The reaction object.

    :ivar int count: The amount of times this emoji has been used to react
    :ivar bool me: A status denoting if the current user reacted using this emoji
    :ivar Emoji emoji: Emoji information
    """

    count: int = field()
    me: bool = field()
    emoji: Emoji = field(converter=Emoji)


@define()
class Message(ClientSerializerMixin, IDMixin):
    """
    A class object representing a message.

    :ivar Snowflake id: ID of the message.
    :ivar Snowflake channel_id: ID of the channel the message was sent in
    :ivar Optional[Snowflake] guild_id?: ID of the guild the message was sent in, if it exists.
    :ivar User author: The author of the message.
    :ivar Optional[Member] member?: The member object associated with the author, if any.
    :ivar str content: Message contents.
    :ivar datetime timestamp: Timestamp denoting when the message was sent.
    :ivar Optional[datetime] edited_timestamp?: Timestamp denoting when the message was edited, if any.
    :ivar bool tts: Status dictating if this was a TTS message or not.
    :ivar bool mention_everyone: Status dictating of this message mentions everyone
    :ivar Optional[List[Union[Member, User]]] mentions?: Array of user objects with an additional partial member field.
    :ivar Optional[List[str]] mention_roles?: Array of roles mentioned in this message
    :ivar Optional[List[ChannelMention]] mention_channels?: Channels mentioned in this message, if any.
    :ivar List[Attachment] attachments: An array of attachments
    :ivar List[Embed] embeds: An array of embeds
    :ivar Optional[List[ReactionObject]] reactions?: Reactions to the message.
    :ivar Union[int, str] nonce: Used for message validation
    :ivar bool pinned: Whether this message is pinned.
    :ivar Optional[Snowflake] webhook_id?: Webhook ID if the message is generated by a webhook.
    :ivar MessageType type: Type of message
    :ivar Optional[MessageActivity] activity?: Message activity object that's sent by Rich Presence
    :ivar Optional[Application] application?: Application object that's sent by Rich Presence
    :ivar Optional[MessageReference] message_reference?: Data showing the source of a message (crosspost, channel follow, add, pin, or replied message)
    :ivar int flags: Message flags
    :ivar Optional[MessageInteraction] interaction?: Message interaction object, if the message is sent by an interaction.
    :ivar Optional[Channel] thread?: The thread that started from this message, if any, with a thread member object embedded.
    :ivar Optional[List[ActionRow]] components?: Array of Action Rows associated with this message, if any.
    :ivar Optional[List[PartialSticker]] sticker_items?: An array of message sticker item objects, if sent with them.
    :ivar Optional[List[Sticker]] stickers?: Array of sticker objects sent with the message if any. Deprecated.
    :ivar Optional[int] position?: The approximate position of the message in a thread.
    """

    id: Snowflake = field(converter=Snowflake)
    channel_id: Snowflake = field(converter=Snowflake)
    guild_id: Optional[Snowflake] = field(converter=Snowflake, default=None)
    author: User = field(converter=User, add_client=True, default=None)
    member: Optional[Member] = field(converter=Member, default=None, add_client=True)
    content: str = field(default=None)
    timestamp: datetime = field(converter=datetime.fromisoformat, default=None)
    edited_timestamp: Optional[datetime] = field(converter=datetime.fromisoformat, default=None)
    tts: bool = field(default=None)
    mention_everyone: bool = field(default=None)
    # mentions: array of Users, and maybe partial members
    mentions: Optional[List[Union[Member, User]]] = field(
        default=None
    )  # todo convert to the right types
    mention_roles: Optional[List[str]] = field(default=None)
    mention_channels: Optional[List[ChannelMention]] = field(
        converter=convert_list(ChannelMention), default=None
    )
    attachments: List[Attachment] = field(converter=convert_list(Attachment), default=None)
    embeds: List[Embed] = field(converter=convert_list(Embed), default=None)
    reactions: Optional[List[ReactionObject]] = field(
        converter=convert_list(ReactionObject), default=None
    )
    nonce: Optional[Union[int, str]] = field(default=None, repr=False)
    pinned: bool = field(default=None)
    webhook_id: Optional[Snowflake] = field(converter=Snowflake, default=None)
    type: MessageType = field(converter=MessageType, default=None)
    activity: Optional[MessageActivity] = field(converter=MessageActivity, default=None)
    application: Optional[Application] = field(converter=Application, default=None)
    application_id: Optional[Snowflake] = field(converter=Snowflake, default=None)
    message_reference: Optional[MessageReference] = field(converter=MessageReference, default=None)
    flags: int = field(default=None)
    referenced_message: Optional[MessageReference] = field(converter=MessageReference, default=None)
    interaction: Optional[MessageInteraction] = field(
        converter=MessageInteraction, default=None, add_client=True, repr=False
    )
    thread: Optional[Channel] = field(converter=Channel, default=None, add_client=True)

    components: Optional[List["ActionRow"]] = field(converter=convert_list(ActionRow), default=None)
    sticker_items: Optional[List[PartialSticker]] = field(
        converter=convert_list(PartialSticker), default=None
    )
    stickers: Optional[List[Sticker]] = field(
        converter=convert_list(Sticker), default=None
    )  # deprecated
    position: Optional[int] = field(default=None, repr=False)

    def __attrs_post_init__(self):
        if self.member:
            if self.guild_id:
                self.member._extras["guild_id"] = self.guild_id

        if self.author and self.member:
            self.member.user = self.author

    async def get_channel(self) -> Channel:
        """
        Gets the channel where the message was sent.

        :rtype: Channel
        """
        if not self._client:
            raise LibraryException(code=13)
        res = await self._client.get_channel(channel_id=int(self.channel_id))
        return Channel(**res, _client=self._client)

    async def get_guild(self):
        """
        Gets the guild where the message was sent.

        :rtype: Guild
        """
        if not self._client:
            raise LibraryException(code=13)
        from .guild import Guild

        res = await self._client.get_guild(guild_id=int(self.guild_id))
        return Guild(**res, _client=self._client)

    async def delete(self, reason: Optional[str] = None) -> None:
        """
        Deletes the message.

        :param reason: Optional reason to show up in the audit log. Defaults to `None`.
        :type reason: Optional[str]
        """
        if not self._client:
            raise LibraryException(code=13)
        await self._client.delete_message(
            message_id=int(self.id), channel_id=int(self.channel_id), reason=reason
        )

    async def edit(
        self,
        content: Optional[str] = MISSING,
        *,
        tts: Optional[bool] = MISSING,
        files: Optional[Union[File, List[File]]] = MISSING,
        embeds: Optional[Union["Embed", List["Embed"]]] = MISSING,
        suppress_embeds: Optional[bool] = MISSING,
        allowed_mentions: Optional[Union[AllowedMentions, dict]] = MISSING,
        message_reference: Optional[MessageReference] = MISSING,
        attachments: Optional[List["Attachment"]] = MISSING,
        components: Optional[
            Union[
                "ActionRow",
                "Button",
                "SelectMenu",
                List["ActionRow"],
                List["Button"],
                List["SelectMenu"],
            ]
        ] = MISSING,
    ) -> "Message":
        """
        This method edits a message. Only available for messages sent by the bot.

        :param content?: The contents of the message as a string or string-converted value.
        :type content?: Optional[str]
        :param tts?: Whether the message utilizes the text-to-speech Discord programme or not.
        :type tts?: Optional[bool]
        :param files?: A file or list of files to be attached to the message.
        :type files?: Optional[Union[File, List[File]]]
        :param embeds?: An embed, or list of embeds for the message.
        :type embeds?: Optional[Union[Embed, List[Embed]]]
        :param suppress_embeds?: Whether to suppress embeds in the message.
        :type suppress_embeds?: Optional[bool]
        :param allowed_mentions?: The allowed mentions for the message.
        :type allowed_mentions?: Optional[Union[AllowedMentions, dict]]
        :param attachments?: The attachments to attach to the message. Needs to be uploaded to the CDN first
        :type attachments?: Optional[List[Attachment]]
        :param components?: A component, or list of components for the message. If `[]` the components will be removed
        :type components?: Optional[Union[ActionRow, Button, SelectMenu, List[ActionRow], List[Button], List[SelectMenu]]]
        :return: The edited message as an object.
        :rtype: Message
        """
        if not self._client:
            raise LibraryException(code=13)
        if self.flags == 64:
            raise LibraryException(message="You cannot edit a hidden message!", code=12)
        _flags = self.flags
        if suppress_embeds is not MISSING and suppress_embeds:
            _flags |= 1 << 2
        elif suppress_embeds is not MISSING:
            _flags &= ~1 << 2

        from ...client.models.component import _build_components

        _content: str = self.content if content is MISSING else content
        _tts: bool = False if tts is MISSING else tts

        if attachments is MISSING:
            _attachments = [a._json for a in self.attachments]
        elif not attachments:
            _attachments = []
        else:
            _attachments = [a._json for a in attachments]

        if not files or files is MISSING:
            _files = []
        elif isinstance(files, list):
            _files = [file._json_payload(id) for id, file in enumerate(files)]
        else:
            _files = [files._json_payload(0)]
            files = [files]

        _files.extend(_attachments)

        if embeds is MISSING:
            embeds = self.embeds
        _embeds: list = (
            ([embed._json for embed in embeds] if isinstance(embeds, list) else [embeds._json])
            if embeds
            else []
        )

        _allowed_mentions: dict = (
            {}
            if allowed_mentions is MISSING
            else allowed_mentions._json
            if isinstance(allowed_mentions, AllowedMentions)
            else allowed_mentions
        )
        _message_reference: dict = {} if message_reference is MISSING else message_reference._json
        if not components:
            _components = []
        elif components is MISSING:
            _components = _build_components(components=self.components)
        else:
            _components = _build_components(components=components)

        payload = dict(
            content=_content,
            tts=_tts,
            attachments=_files,
            embeds=_embeds,
            allowed_mentions=_allowed_mentions,
            message_reference=_message_reference,
            components=_components,
            flags=_flags,
        )

        _dct = await self._client.edit_message(
            channel_id=int(self.channel_id),
            message_id=int(self.id),
            payload=payload,
            files=files,
        )

        self.update(_dct)

        return self

    async def reply(
        self,
        content: Optional[str] = MISSING,
        *,
        tts: Optional[bool] = MISSING,
        embeds: Optional[Union["Embed", List["Embed"]]] = MISSING,
        files: Optional[Union[File, List[File]]] = MISSING,
        attachments: Optional[List["Attachment"]] = MISSING,
        allowed_mentions: Optional[Union[AllowedMentions, dict]] = MISSING,
        stickers: Optional[List["Sticker"]] = MISSING,
        components: Optional[
            Union[
                "ActionRow",
                "Button",
                "SelectMenu",
                List["ActionRow"],
                List["Button"],
                List["SelectMenu"],
            ]
        ] = MISSING,
    ) -> "Message":  # sourcery skip: dict-assign-update-to-union
        """
        Sends a new message replying to the old.

        :param content?: The contents of the message as a string or string-converted value.
        :type content?: Optional[str]
        :param tts?: Whether the message utilizes the text-to-speech Discord programme or not.
        :type tts?: Optional[bool]
        :param attachments?: The attachments to attach to the message. Needs to be uploaded to the CDN first
        :type attachments?: Optional[List[Attachment]]
        :param files?: A file or list of files to be attached to the message.
        :type files?: Optional[Union[File, List[File]]]
        :param embeds?: An embed, or list of embeds for the message.
        :type embeds?: Optional[Union[Embed, List[Embed]]]
        :param allowed_mentions?: The allowed mentions for the message.
        :type allowed_mentions?: Optional[Union[AllowedMentions, dict]]
        :param components?: A component, or list of components for the message.
        :type components?: Optional[Union[ActionRow, Button, SelectMenu, List[ActionRow], List[Button], List[SelectMenu]]]
        :param stickers?: A list of stickers to send with your message. You can send up to 3 stickers per message.
        :type stickers?: Optional[List[Sticker]]
        :return: The sent message as an object.
        :rtype: Message
        """
        if not self._client:
            raise LibraryException(code=13)
        from ...client.models.component import _build_components

        _content: str = "" if content is MISSING else content
        _tts: bool = False if tts is MISSING else tts
        # _file = None if file is None else file
        # _attachments = [] if attachments else None
        _embeds: list = (
            []
            if not embeds or embeds is MISSING
            else ([embed._json for embed in embeds] if isinstance(embeds, list) else [embeds._json])
        )
        _allowed_mentions: dict = (
            {}
            if allowed_mentions is MISSING
            else allowed_mentions._json
            if isinstance(allowed_mentions, AllowedMentions)
            else allowed_mentions
        )
        _message_reference = MessageReference(message_id=int(self.id))._json
        _attachments = [] if attachments is MISSING else [a._json for a in attachments]
        if not components or components is MISSING:
            _components = []
        else:
            _components = _build_components(components=components)

        if not files or files is MISSING:
            _files = []
        elif isinstance(files, list):
            _files = [file._json_payload(id) for id, file in enumerate(files)]
        else:
            _files = [files._json_payload(0)]
            files = [files]

        _files.extend(_attachments)
        _sticker_ids: list = (
            [] if stickers is MISSING else [str(sticker.id) for sticker in stickers]
        )

        payload = dict(
            content=_content,
            tts=_tts,
            attachments=_files,
            embeds=_embeds,
            message_reference=_message_reference,
            allowed_mentions=_allowed_mentions,
            components=_components,
            sticker_ids=_sticker_ids,
        )

        res = await self._client.create_message(
            channel_id=int(self.channel_id), payload=payload, files=files
        )

        author = {"id": None, "username": None, "discriminator": None}
        author.update(res["author"])
        res["author"] = author

        return Message(**res, _client=self._client)

    async def pin(self) -> None:
        """Pins the message to its channel"""
        if not self._client:
            raise LibraryException(code=13)
        await self._client.pin_message(channel_id=int(self.channel_id), message_id=int(self.id))

    async def unpin(self) -> None:
        """Unpins the message from its channel"""
        if not self._client:
            raise LibraryException(code=13)
        await self._client.unpin_message(channel_id=int(self.channel_id), message_id=int(self.id))

    async def publish(self) -> "Message":
        """Publishes (API calls it crossposts) the message in its channel to any that is followed by.

        :return: message object
        :rtype: Message
        """
        if not self._client:
            raise LibraryException(code=13)
        res = await self._client.publish_message(
            channel_id=int(self.channel_id), message_id=int(self.id)
        )
        return Message(**res, _client=self._client)

    async def create_thread(
        self,
        name: str,
        auto_archive_duration: Optional[int] = MISSING,
        invitable: Optional[bool] = MISSING,
        reason: Optional[str] = None,
    ) -> Channel:
        """
        Creates a thread from the message.

        :param name: The name of the thread
        :type name: str
        :param auto_archive_duration?: duration in minutes to automatically archive the thread after recent activity,
            can be set to: 60, 1440, 4320, 10080
        :type auto_archive_duration?: Optional[int]
        :param invitable?: Boolean to display if the Thread is open to join or private.
        :type invitable?: Optional[bool]
        :param reason?: An optional reason for the audit log
        :type reason?: Optional[str]
        :return: The created thread
        :rtype: Channel
        """
        if not self._client:
            raise LibraryException(code=13)
        _auto_archive_duration = None if auto_archive_duration is MISSING else auto_archive_duration
        _invitable = None if invitable is MISSING else invitable
        res = await self._client.create_thread(
            channel_id=int(self.channel_id),
            message_id=int(self.id),
            name=name,
            reason=reason,
            invitable=_invitable,
            auto_archive_duration=_auto_archive_duration,
        )
        return Channel(**res, _client=self._client)

    async def create_reaction(
        self,
        emoji: Union[str, "Emoji"],
    ) -> None:
        """
        Adds a reaction to the message.

        :param emoji: The Emoji as object or formatted as `name:id`
        :type emoji: Union[str, Emoji]
        """
        if not self._client:
            raise LibraryException(code=13)

        _emoji = (
            (f":{emoji.name.replace(':', '')}:{emoji.id or ''}" if emoji.id else emoji.name)
            if isinstance(emoji, Emoji)
            else emoji
        )

        return await self._client.create_reaction(
            channel_id=int(self.channel_id), message_id=int(self.id), emoji=_emoji
        )

    async def remove_all_reactions(self) -> None:
        """
        Removes all reactions of the message.
        """
        if not self._client:
            raise LibraryException(code=13)

        return await self._client.remove_all_reactions(
            channel_id=int(self.channel_id), message_id=int(self.id)
        )

    async def remove_all_reactions_of(
        self,
        emoji: Union[str, "Emoji"],
    ) -> None:
        """
        Removes all reactions of one emoji of the message.

        :param emoji: The Emoji as object or formatted as `name:id`
        :type emoji: Union[str, Emoji]
        """
        if not self._client:
            raise LibraryException(code=13)

        _emoji = (
            (f":{emoji.name.replace(':', '')}:{emoji.id or ''}" if emoji.id else emoji.name)
            if isinstance(emoji, Emoji)
            else emoji
        )

        return await self._client.remove_all_reactions_of_emoji(
            channel_id=int(self.channel_id), message_id=int(self.id), emoji=_emoji
        )

    async def remove_own_reaction_of(
        self,
        emoji: Union[str, "Emoji"],
    ) -> None:
        """
        Removes the own reaction of an emoji of the message.

        :param emoji: The Emoji as object or formatted as `name:id`
        :type emoji: Union[str, Emoji]
        """
        if not self._client:
            raise LibraryException(code=13)

        _emoji = (
            (f":{emoji.name.replace(':', '')}:{emoji.id or ''}" if emoji.id else emoji.name)
            if isinstance(emoji, Emoji)
            else emoji
        )

        return await self._client.remove_self_reaction(
            channel_id=int(self.channel_id), message_id=int(self.id), emoji=_emoji
        )

    async def remove_reaction_from(
        self, emoji: Union[str, "Emoji"], user: Union[Member, User, int]
    ) -> None:
        """
        Removes another reaction of an emoji of the message.

        :param emoji: The Emoji as object or formatted as `name:id`
        :type emoji: Union[str, Emoji]
        :param user: The user or user_id to remove the reaction of
        :type user: Union[Member, user, int]
        """
        _emoji = (
            (f":{emoji.name.replace(':', '')}:{emoji.id or ''}" if emoji.id else emoji.name)
            if isinstance(emoji, Emoji)
            else emoji
        )
        if not self._client:
            raise LibraryException(code=13)

        _user_id = user if isinstance(user, (int, Snowflake)) else user.id
        return await self._client.remove_user_reaction(
            channel_id=int(self.channel_id),
            message_id=int(self.id),
            user_id=int(_user_id),
            emoji=_emoji,
        )

    async def get_users_from_reaction(
        self,
        emoji: Union[str, "Emoji"],
    ) -> List[User]:
        """
        Retrieves all users that reacted to the message with the given emoji

        :param emoji: The Emoji as object or formatted as `name:id`
        :type emoji: Union[str, Emoji]
        :return: A list of user objects
        :rtype: List[User]
        """
        if not self._client:
            raise LibraryException(code=13)

        _all_users: List[User] = []

        _emoji = (
            (f":{emoji.name.replace(':', '')}:{emoji.id or ''}" if emoji.id else emoji.name)
            if isinstance(emoji, Emoji)
            else emoji
        )

        res: List[dict] = await self._client.get_reactions_of_emoji(
            channel_id=int(self.channel_id), message_id=int(self.id), emoji=_emoji, limit=100
        )

        while len(res) == 100:
            _after = int(res[-1]["id"])
            _all_users.extend(User(**_) for _ in res)
            res: List[dict] = await self._client.get_reactions_of_emoji(
                channel_id=int(self.channel_id),
                message_id=int(self.id),
                emoji=_emoji,
                limit=100,
                after=_after,
            )

        _all_users.extend(User(**_) for _ in res)

        return _all_users

    @classmethod
    async def get_from_url(cls, url: str, client: "HTTPClient") -> "Message":
        """
        Gets a Message based from its url.

        :param url: The full url of the message
        :type url: str
        :param client: The HTTPClient of your bot. Set ` _client=botvar._http``
        :type client: HTTPClient
        :return: The message the URL points to
        :rtype: Message
        """

        if "channels/" not in url:
            raise LibraryException(message="You provided an invalid URL!", code=12)
        _, _channel_id, _message_id = url.split("channels/")[1].split("/")
        _message = await client.get_message(
            channel_id=_channel_id,
            message_id=_message_id,
        )
        return cls(**_message, _client=client)

    @property
    def url(self) -> str:
        """
        Returns the URL of the message.

        :return: The URL of said message
        :rtype: str
        """
        guild = self.guild_id or "@me"
        return f"https://discord.com/channels/{guild}/{self.channel_id}/{self.id}"

    async def disable_all_components(self) -> "Message":
        """
        Sets all components to disabled on this message.

        :return: The modified message.
        :rtype: Message
        """
        if not self._client:
            raise LibraryException(code=13)

        if not self.components:
            return self

        for components in self.components:
            for component in components.components:
                component.disabled = True

        return Message(
            **await self._client.edit_message(
                int(self.channel_id),
                int(self.id),
                payload={"components": [component._json for component in self.components]},
            ),
            _client=self._client,
        )
