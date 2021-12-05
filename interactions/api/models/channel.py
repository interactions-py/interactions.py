from enum import IntEnum

from .misc import DictSerializerMixin, Snowflake


class ChannelType(IntEnum):
    """
    An enumerable object representing the type of channels.

    ..note::
        While all of them are listed, not all of them will be used at this library's scope.
    """

    ...


class ThreadMetadata(DictSerializerMixin):
    """
    A class object representing the metadata of a thread.

    .. note::
        ``invitable`` will only show if the thread can have an invited created with the
        current cached permissions.

    :ivar bool archived: The current thread accessibility state.
    :ivar int auto_archive_duration: The auto-archive time.
    :ivar datetime.datetime.timestamp archive_timestamp: The timestamp that the thread will be/has been closed at.
    :ivar bool locked: The current message state of the thread.
    :ivar typing.Optional[bool] invitable: The ability to invite users to the thread.
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


class ThreadMember(DictSerializerMixin):
    """
    A class object representing a member in a thread.

    .. note::
        ``id`` only shows if there are active intents involved with the member
        in the thread.

    :ivar typing.Optional[int] id: The "ID" or intents of the member.
    :ivar int user_id: The user ID of the member.
    :ivar datetime.datetime.timestamp join_timestamp: The timestamp of when the member joined the thread.
    :ivar int flags: The bitshift flags for the member in the thread.
    """

    __slots__ = ("_json", "id", "user_id", "join_timestamp", "flags")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = Snowflake(self.id) if self._json.get("id") else None
        self.user_id = Snowflake(self.user_id) if self._json.get("user_id") else None


class ThreadList(DictSerializerMixin):
    __slots__ = ("_json", "guild_id", "channel_ids", "threads", "members")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.guild_id = Snowflake(self.guild_id) if self._json.get("guild_id") else None
        self.channel_ids = (
            [Snowflake(channel_id) for channel_id in self.channel_ids]
            if self._json.get("channel_id")
            else None
        )


class Channel(DictSerializerMixin):
    """
    A class object representing all types of channels.

    .. note::
        The purpose of this model is to be used as a base class, and
        is never needed to be used directly.

    :ivar int id: The (snowflake) ID of the channel.
    :ivar int type: The type of channel.
    :ivar typing.Optional[int] guild_id: The ID of the guild if it is not a DM channel.
    :ivar typing.Optional[int] position: The position of the channel.
    :ivar typing.List[interactions.api.models.misc.Overwrite] permission_overwrites: The non-synced permissions of the channel.
    :ivar str name: The name of the channel.
    :ivar typing.Optional[str] topic: The description of the channel.
    :ivar typing.Optional[bool] nsfw: Whether the channel is NSFW.
    :ivar int last_message_id: The ID of the last message sent.
    :ivar typing.Optional[int] bitrate: The audio bitrate of the channel.
    :ivar typing.Optional[int] user_limit: The maximum amount of users allowed in the channel.
    :ivar typing.Optional[int] rate_limit_per_user: The concurrent ratelimit for users in the channel.
    :ivar typing.Optional[typing.List[interactions.api.models.user.User]] recipients: The recipients of the channel.
    :ivar typing.Optional[str] icon: The icon of the channel.
    :ivar typing.Optional[int] owner_id: The owner of the channel.
    :ivar typing.optional[int] application_id: The application of the channel.
    :ivar typing.Optional[int] parent_id: The ID of the "parent"/main channel.
    :ivar typing.Optional[datetime.datetime] last_pin_timestamp: The timestamp of the last pinned message in the channel.
    :ivar typing.Optional[str] rtc_region: The region of the WebRTC connection for the channel.
    :ivar typing.Optional[int] video_quality_mode: The set quality mode for video streaming in the channel.
    :ivar int message_count: The amount of messages in the channel.
    :ivar typing.Optional[int] member_count: The amount of members in the channel.
    :ivar typing.Optional[interactions.api.models.channel.ThreadMetadata] thread_metadata: The thread metadata of the channel.
    :ivar typing.Optional[interactions.api.models.channel.ThreadMember] member: The member of the thread in the channel.
    :ivar typing.Optional[int] default_auto_archive_duration: The set auto-archive time for all threads to naturally follow in the channel.
    :ivar typing.Optional[str] permissions: The permissions of the channel.
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
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
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


class ChannelPins(DictSerializerMixin):
    __slots__ = ("_json", "guild_id", "channel_id", "last_pin_timestamp")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.guild_id = Snowflake(self.guild_id) if self._json.get("guild_id") else None
        self.guild_id = Snowflake(self.channel_id) if self._json.get("channel_id") else None
