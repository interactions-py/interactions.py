from datetime import datetime
from enum import IntEnum

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

    .. note::
        ``party_id`` is ambigious -- Discord poorly documented this. :)

        We assume it's for game rich presence invites?
        i.e. : Phasmophobia, Call of Duty

    :ivar int type: The message activity type.
    :ivar typing.Optional[str] party_id: The party ID of the activity.
    """

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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Attachment(DictSerializerMixin):
    """
    A class object representing an attachment in a message.

    .. note::
        ``height`` and ``width`` have values based off of ``content_type``,
        which requires it to be a media file with viewabiltiy as a photo,
        animated photo, GIF and/or video.

    :ivar int id: The ID of the attachment.
    :ivar str filename: The name of the attachment file.
    :ivar typing.Optional[str] content_type: The type of attachment file.
    :ivar int size: The size of the attachment file.
    :ivar str url: The CDN URL of the attachment file.
    :ivar str proxy_url: The proxied/cached CDN URL of the attachment file.
    :ivar typing.Optional[int] height: The height of the attachment file.
    :ivar typing.Optional[int] width: The width of the attachment file.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class MessageInteraction(DictSerializerMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class ChannelMention(DictSerializerMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Message(DictSerializerMixin):
    """
    The big Message model.

    The purpose of this model is to be used as a base class, and
    is never needed to be used directly.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.timestamp = (
            datetime.fromisoformat(self._json.get("timestamp"))
            if self._json.get("timestamp")
            else datetime.utcnow()
        )
        self.author = (
            User(**self._json.get("author"))
            if self._json.get("author")
            else User(**self._json.get("user"))
        )  # interaction models are different for some reason


class Emoji(DictSerializerMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class ReactionObject(DictSerializerMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class PartialSticker(DictSerializerMixin):
    """Partial object for a Sticker."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Sticker(PartialSticker):
    """The full Sticker object."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class EmbedImageStruct(DictSerializerMixin):
    """This is the internal structure denoted for thumbnails, images or videos"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class EmbedProvider(DictSerializerMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class EmbedAuthor(DictSerializerMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class EmbedFooter(DictSerializerMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class EmbedField(DictSerializerMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Embed(DictSerializerMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
