from datetime import datetime
from enum import IntEnum
from typing import Optional

from .misc import DictSerializerMixin, Snowflake


class ChannelType(IntEnum):
    """An enumerable object representing the type of channels."""

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


class ThreadMetadata(DictSerializerMixin):
    """
    A class object representing the metadata of a thread.

    .. note::
        ``invitable`` will only show if the thread can have an invited created with the
        current cached permissions.

    :ivar bool archived: The current thread accessibility state.
    :ivar int auto_archive_duration: The auto-archive time.
    :ivar datetime archive_timestamp: The timestamp that the thread will be/has been closed at.
    :ivar bool locked: The current message state of the thread.
    :ivar Optional[bool] invitable?: The ability to invite users to the thread.
    """

    __slots__ = (
        "_json",
        "archived",
        "auto_archive_duration",
        "archive_timestamp",
        "locked",
        "invitable",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.archive_timestamp = (
            datetime.fromisoformat(self._json.get("archive_timestamp"))
            if self._json.get("archive_timestamp")
            else datetime.utcnow()
        )


class ThreadMember(DictSerializerMixin):
    """
    A class object representing a member in a thread.

    .. note::
        ``id`` only shows if there are active intents involved with the member
        in the thread.

    :ivar Optional[Snowflake] id?: The "ID" or intents of the member.
    :ivar Snowflake user_id: The user ID of the member.
    :ivar datetime join_timestamp: The timestamp of when the member joined the thread.
    :ivar int flags: The bitshift flags for the member in the thread.
    """

    __slots__ = ("_json", "id", "user_id", "join_timestamp", "flags")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = Snowflake(self.id) if self._json.get("id") else None
        self.user_id = Snowflake(self.user_id) if self._json.get("user_id") else None
        self.join_timestamp = (
            datetime.fromisoformat(self._json.get("join_timestamp"))
            if self._json.get("join_timestamp")
            else None
        )


class Channel(DictSerializerMixin):
    """
    A class object representing all types of channels.

    .. note::
        The purpose of this model is to be used as a base class, and
        is never needed to be used directly.

    :ivar Snowflake id: The (snowflake) ID of the channel.
    :ivar ChannelType type: The type of channel.
    :ivar Optional[Snowflake] guild_id?: The ID of the guild if it is not a DM channel.
    :ivar Optional[int] position?: The position of the channel.
    :ivar List[Overwrite] permission_overwrites: The non-synced permissions of the channel.
    :ivar str name: The name of the channel.
    :ivar Optional[str] topic?: The description of the channel.
    :ivar Optional[bool] nsfw?: Whether the channel is NSFW.
    :ivar Snowflake last_message_id: The ID of the last message sent.
    :ivar Optional[int] bitrate?: The audio bitrate of the channel.
    :ivar Optional[int] user_limit?: The maximum amount of users allowed in the channel.
    :ivar Optional[int] rate_limit_per_user?: The concurrent ratelimit for users in the channel.
    :ivar Optional[List[User]] recipients?: The recipients of the channel.
    :ivar Optional[str] icon?: The icon of the channel.
    :ivar Optional[Snowflake] owner_id?: The owner of the channel.
    :ivar Optional[Snowflake] application_id?: The application of the channel.
    :ivar Optional[Snowflake] parent_id?: The ID of the "parent"/main channel.
    :ivar Optional[datetime] last_pin_timestamp?: The timestamp of the last pinned message in the channel.
    :ivar Optional[str] rtc_region?: The region of the WebRTC connection for the channel.
    :ivar Optional[int] video_quality_mode?: The set quality mode for video streaming in the channel.
    :ivar int message_count: The amount of messages in the channel.
    :ivar Optional[int] member_count?: The amount of members in the channel.
    :ivar Optional[ThreadMetadata] thread_metadata?: The thread metadata of the channel.
    :ivar Optional[ThreadMember] member?: The member of the thread in the channel.
    :ivar Optional[int] default_auto_archive_duration?: The set auto-archive time for all threads to naturally follow in the channel.
    :ivar Optional[str] permissions?: The permissions of the channel.
    """

    __slots__ = (
        "_json",
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
        "client",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = ChannelType(self.type)
        self.id = Snowflake(self.id) if self._json.get("id") else None
        self.guild_id = Snowflake(self.guild_id) if self._json.get("guild_id") else None
        self.last_message_id = (
            Snowflake(self.last_message_id) if self._json.get("last_message_id") else None
        )
        self.owner_id = Snowflake(self.owner_id) if self._json.get("owner_id") else None
        self.application_id = (
            Snowflake(self.application_id) if self._json.get("application_id") else None
        )
        self.parent_id = Snowflake(self.parent_id) if self._json.get("parent_id") else None
        self.last_pin_timestamp = (
            datetime.fromisoformat(self._json.get("last_pin_timestamp"))
            if self._json.get("last_pin_timestamp")
            else None
        )
        self.client = self.client if self.client else None

    async def send(
        self,
        content: Optional[str] = None,
        *,
        tts: Optional[bool] = False,
        # attachments: Optional[List[Any]] = None,  # TODO: post-v4: Replace with own file type.
        embeds=None,
        allowed_mentions=None,
        components=None,
    ):
        """
        Sends a message in the channel

        :param content?: The contents of the message as a string or string-converted value.
        :type content: Optional[str]
        :param tts?: Whether the message utilizes the text-to-speech Discord programme or not.
        :type tts: Optional[bool]
        :param embeds?: An embed, or list of embeds for the message.
        :type embeds: Optional[Union[Embed, List[Embed]]]
        :param allowed_mentions?: The message interactions/mention limits that the message can refer to.
        :type allowed_mentions: Optional[MessageInteraction]
        :param components?: A component, or list of components for the message.
        :type components: Optional[Union[Component, List[Component]]]
        :return: The sent message as an object.
        :rtype: Message
        """
        from ...models.component import ActionRow, Button, SelectMenu
        from .message import Message

        _content: str = "" if content is None else content
        _tts: bool = False if tts is None else tts
        # _file = None if file is None else file
        # _attachments = [] if attachments else None
        _embeds: list = (
            []
            if embeds is None
            else ([embed._json for embed in embeds] if isinstance(embeds, list) else [embeds._json])
        )
        _allowed_mentions: dict = {} if allowed_mentions is None else allowed_mentions
        _components: list = [{"type": 1, "components": []}]

        if isinstance(components, ActionRow):
            _components[0]["components"] = [component._json for component in components.components]
        elif isinstance(components, Button):
            _components[0]["components"] = [] if components is None else [components._json]
        elif isinstance(components, SelectMenu):
            components._json["options"] = [option._json for option in components.options]
            _components[0]["components"] = [] if components is None else [components._json]
        else:
            _components = [] if components is None else [components]

        # TODO: post-v4: Add attachments into Message obj.
        payload = Message(
            content=_content,
            tts=_tts,
            # file=file,
            # attachments=_attachments,
            embeds=_embeds,
            allowed_mentions=_allowed_mentions,
            components=_components,
        )

        res = await self.client.create_message(channel_id=int(self.id), payload=payload._json)
        message = Message(**res, client=self.client)
        return message

    async def delete(self) -> None:
        """
        Deletes the channel.
        """
        await self.client.delete_channel(channel_id=int(self.id))
