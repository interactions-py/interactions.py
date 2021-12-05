from datetime import datetime
from enum import IntEnum

from .member import Member
from .misc import DictSerializerMixin
from .user import User


class MessageType(IntEnum):
    """
    An enumerable object representing the types of messages.

    ..note::
        While all of them are listed, not all of them would be used at this lib's scope.
    """

    ...


class MessageActivity(DictSerializerMixin):
    """
        A class object representing the activity state of a message.
    ~
        .. note::
            ``party_id`` is ambiguous -- Discord poorly documented this. :)

            We assume it's for game rich presence invites?
            i.e. : Phasmophobia, Call of Duty

        :ivar int type: The message activity type.
        :ivar typing.Optional[str] party_id: The party ID of the activity.
    """

    __slots__ = ("_json", "type", "party_id")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class MessageReference(DictSerializerMixin):
    """
    A class object representing the "referenced"/replied message.

    .. note::
        All of the class instances are optionals because a message
        can entirely never be referenced.

    :ivar typing.Optional[int] message_id: The ID of the referenced message.
    :ivar typing.Optional[int] channel_id: The channel ID of the referenced message.
    :ivar typing.Optional[int] guild_id: The guild ID of the referenced message.
    :ivar typing.Optional[bool] fail_if_not_exists: Whether the message reference exists.
    """

    __slots__ = ("_json", "message_id", "channel_id", "guild_id", "fail_if_not_exists")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Attachment(DictSerializerMixin):
    """
    A class object representing an attachment in a message.

    .. note::
        ``height`` and ``width`` have values based off of ``content_type``,
        which requires it to be a media file with viewabiltity as a photo,
        animated photo, GIF and/or video.

    :ivar int id: The ID of the attachment.
    :ivar str filename: The name of the attachment file.
    :ivar typing.Optional[str] description: The description of the file.
    :ivar typing.Optional[str] content_type: The type of attachment file.
    :ivar int size: The size of the attachment file.
    :ivar str url: The CDN URL of the attachment file.
    :ivar str proxy_url: The proxied/cached CDN URL of the attachment file.
    :ivar typing.Optional[int] height: The height of the attachment file.
    :ivar typing.Optional[int] width: The width of the attachment file.
    """

    __slots__ = (
        "_json",
        "id",
        "filename",
        "content_type",
        "size",
        "url",
        "proxy_url",
        "height",
        "width",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class MessageInteraction(DictSerializerMixin):
    """
    A class object that resembles the interaction used to generate
    the associated message.

    :ivar int id: ID of the interaction.
    :ivar int type: Type of interaction.
    :ivar str name: Name of the application command.
    :ivar User user: The user who invoked the interaction.
    """

    __slots__ = ("_json", "id", "type", "name", "user")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class ChannelMention(DictSerializerMixin):
    """
    A class object that resembles the mention of a channel
    in a guild.

    :ivar int id: The ID of the channel.
    :ivar int guild_id: The ID of the guild that contains the channel.
    :ivar int type: The channel type.
    :ivar str name: The name of the channel.
    """

    __slots__ = ("_json", "id", "type", "name", "guild_id")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Message(DictSerializerMixin):
    """
    The big Message model.

    The purpose of this model is to be used as a base class, and
    is never needed to be used directly.

    :ivar int id: ID of the message.
    :ivar int channel_id: ID of the channel the message was sent in
    :ivar typing.Optional[int] guild_id: ID of the guild the message was sent in, if it exists.
    :ivar User author: The author of the message.
    :ivar typing.Optional[Member] member: The member object associated with the author, if any.
    :ivar str content: Message contents.
    :ivar datetime.timestamp timestamp: Timestamp denoting when the message was sent.
    :ivar typing.Optional[datetime.timestamp] edited_timestamp: Timestamp denoting when the message was edited, if any.
    :ivar bool tts: Status dictating if this was a TTS message or not.
    :ivar bool mention_everyone: Status dictating of this message mentions everyone
    :ivar Optional[List[Union[Member, User]]] mentions: Array of user objects with an addictional partial member field.
    :ivar Optional[List[str]] mention_roles: Array of roles mentioned in this message
    :ivar Optional[List["ChannelMention"]] mention_channels: Channels mentioned in this message, if any.
    :ivar List[Attachment] attachments: An array of attachments
    :ivar List["Embed"] embeds: An array of embeds
    :ivar Optional[List["ReactionObject"]] reactions: Reactions to the message.
    :ivar Union[int, str] nonce: Used for message validation
    :ivar bool pinned: Whether this message is pinned.
    :ivar Optional[int] webhook_id: Webhook ID if the message is generated by a webhook.
    :ivar int type: Type of message
    :ivar Optional[MessageActivity] activity: Message activity object that's sent by Rich Presence
    :ivar Optional[Application] application: Application object that's sent by Rich Presence
    :ivar Optional[MessageReference] message_reference: Data showing the source of a message (crosspost, channel follow, add, pin, or replied message)
    :ivar int flags: Message flags
    :ivar Optional[MessageInteraction] interaction: Message interaction object, if the message is sent by an interaction.
    :ivar Optional[Channel] thread: The thread that started from this message, if any, with a thread member object embedded.
    :ivar Optional[Union["Component", List["Component"]]]  components: Components associated with this message, if any.
    :ivar Optional[List["PartialSticker"]] sticker_items: An array of message sticker item objects, if sent with them.
    :ivar Optional[List["Sticker"]] stickers: Array of sticker objects sent with the message if any. Deprecated.
    """

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
        "allowed_mentions",  # todo, add to documentation
        "flags",
        "referenced_message",
        "interaction",
        "thread",
        "components",
        "sticker_items",
        "stickers",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.timestamp = (
            datetime.fromisoformat(self._json.get("timestamp"))
            if self._json.get("timestamp")
            else datetime.utcnow()
        )
        self.author = User(**self._json.get("author")) if self._json.get("author") else None
        self.member = Member(**self._json.get("member")) if self._json.get("member") else None


class Emoji(DictSerializerMixin):
    """The emoji object.

    :ivar typing.Optional[int] id: Emoji id
    :ivar Optional[str] name: Emoji name.
    :ivar Optional[List[str]] roles: Roles allowed to use this emoji
    :ivar Optional[User] user: User that created this emoji
    :ivar Optional[bool] require_colons: Status denoting of this emoji must be wrapped in colons
    :ivar Optional[bool] managed: Status denoting if this emoji is managed (by an integration)
    :ivar Optional[bool] animated: Status denoting if this emoji is animated
    :ivar Optional[bool] available: Status denoting if this emoji can be used. (Can be false via server boosting)
    """

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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class ReactionObject(DictSerializerMixin):
    """The reaction object.

    :ivar int count: The amount of times this emoji has been used to react
    :ivar bool me: A status denoting if the current user reacted using this emoji
    :ivar Emoji emoji: Emoji information
    """

    __slots__ = ("_json", "count", "me", "bool")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class PartialSticker(DictSerializerMixin):
    """
    Partial object for a Sticker.

    :ivar int id: ID of the sticker
    :ivar str name: Name of the sticker
    :ivar int format_type: Type of sticker format
    """

    __slots__ = ("_json", "id", "name", "format_type")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Sticker(PartialSticker):
    """
    The full Sticker object.

    :ivar int id: ID of the sticker
    :ivar Optional[int] pack_id: ID of the pack the sticker is from.
    :ivar str name: Name of the sticker
    :ivar Optional[str] description: Description of the sticker
    :ivar str tags: Autocomplete/suggestion tags for the sticker (max 200 characters)
    :ivar str asset: Previously a sticker asset hash, now an empty string.
    :ivar int type: Type of sticker
    :ivar int format_type: Type of sticker format
    :ivar Optional[bool] available: Status denoting if this sticker can be used. (Can be false via server boosting)
    :ivar Optional[int] guild_id: Guild ID that owns the sticker.
    :ivar Optional[User] user: The user that uploaded the sticker.
    :ivar Optional[int] sort_value: The standard sticker's sort order within its pack
    """

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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class EmbedImageStruct(DictSerializerMixin):
    """
    This is the internal structure denoted for thumbnails, images or videos

    :ivar str url: Source URL of the object.
    :ivar typing.Optional[str] proxy_url: Proxied url of the object.
    :ivar typing.Optional[int] height: Height of the object.
    :ivar typing.Optional[int] width: Width of the object.
    """

    __slots__ = ("_json", "url", "proxy_url", "height", "width")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class EmbedProvider(DictSerializerMixin):
    """
    :ivar typing.Optional[str] name: Name of provider
    :ivar typing.Optional[str] name: URL of provider
    """

    __slots__ = ("_json", "url", "name")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class EmbedAuthor(DictSerializerMixin):
    """
    :ivar str name: Name of author
    :ivar typing.Optional[str] url: URL of author
    :ivar typing.Optional[str] icon_url: URL of author icon
    :ivar typing.Optional[str] proxy_icon_url: Proxied URL of author icon
    """

    __slots__ = ("_json", "url", "proxy_icon_url", "icon_url", "name")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class EmbedFooter(DictSerializerMixin):
    """
    :ivar str text: Footer text
    :ivar typing.Optional[str] icon_url: URL of footer icon
    :ivar typing.Optional[str] proxy_icon_url: Proxied URL of footer icon
    """

    __slots__ = ("_json", "text", "proxy_icon_url", "icon_url")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class EmbedField(DictSerializerMixin):
    """
    :ivar str name: Name of the field.
    :ivar str value: Value of the field
    :ivar typing.Optional[bool] inline: A status denoting if the field should be displayed inline.
    """

    __slots__ = ("_json", "name", "inline", "value")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Embed(DictSerializerMixin):
    """
    The embed object.

    :ivar typing.Optional[str] title: Title of embed
    :ivar typing.Optional[str] type: Embed type
    :ivar typing.Optional[str] description: Embed description
    :ivar typing.Optional[str] url: URL of embed
    :ivar typing.Optional[datetime.Timestamp] timestamp: Timestamp of embed content
    :ivar typing.Optional[int] color: Color code of embed
    :ivar typing.Optional[EmbedFooter] footer: Footer information
    :ivar typing.Optional[EmbedImageStruct] image: Image information
    :ivar typing.Optional[EmbedImageStruct] thumbnail: Thumbnail information
    :ivar typing.Optional[EmbedImageStruct] video: Video information
    :ivar typing.Optional[EmbedProvider] provider: Provider information
    :ivar typing.Optional[EmbedAuthor] author: Author information
    :ivar typing.Optional[EmbedField] fields: A list of fields denoting field information
    """

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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
