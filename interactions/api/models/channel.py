from datetime import datetime, timedelta, timezone
from enum import IntEnum
from typing import Callable, List, Optional, Union

from .misc import MISSING, DictSerializerMixin, Snowflake


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

    __slots__ = (
        "_json",
        "id",
        "user_id",
        "join_timestamp",
        "flags",
        # TODO: Document below attributes.
        "user",
        "team_id",
        "membership_state",
        "permissions",
    )

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
        "_client",
        # TODO: Document banner when Discord officially documents them.
        "banner",
        "guild_hashes",
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

    @property
    def mention(self) -> str:
        """
        Returns a string that allows you to mention the given channel.

        :return: The string of the mentioned channel.
        :rtype: str
        """
        return f"<#{self.id}>"

    async def send(
        self,
        content: Optional[str] = MISSING,
        *,
        tts: Optional[bool] = MISSING,
        # attachments: Optional[List[Any]] = None,  # TODO: post-v4: Replace with own file type.
        embeds: Optional[Union["Embed", List["Embed"]]] = MISSING,  # noqa
        allowed_mentions: Optional["MessageInteraction"] = MISSING,  # noqa
        components: Optional[
            Union[
                "ActionRow",  # noqa
                "Button",  # noqa
                "SelectMenu",  # noqa
                List["ActionRow"],  # noqa
                List["Button"],  # noqa
                List["SelectMenu"],  # noqa
            ]
        ] = MISSING,
    ) -> "Message":  # noqa
        """
        Sends a message in the channel.

        :param content?: The contents of the message as a string or string-converted value.
        :type content: Optional[str]
        :param tts?: Whether the message utilizes the text-to-speech Discord programme or not.
        :type tts: Optional[bool]
        :param embeds?: An embed, or list of embeds for the message.
        :type embeds: Optional[Union[Embed, List[Embed]]]
        :param allowed_mentions?: The message interactions/mention limits that the message can refer to.
        :type allowed_mentions: Optional[MessageInteraction]
        :param components?: A component, or list of components for the message.
        :type components: Optional[Union[ActionRow, Button, SelectMenu, List[Actionrow], List[Button], List[SelectMenu]]]
        :return: The sent message as an object.
        :rtype: Message
        """
        if not self._client:
            raise AttributeError("HTTPClient not found!")
        from ...models.component import _build_components
        from .message import Message

        _content: str = "" if content is MISSING else content
        _tts: bool = False if tts is MISSING else tts
        # _file = None if file is None else file
        # _attachments = [] if attachments else None
        _allowed_mentions: dict = {} if allowed_mentions is MISSING else allowed_mentions
        if not embeds or embeds is MISSING:
            _embeds: list = []
        elif isinstance(embeds, list):
            _embeds = [embed._json for embed in embeds]
        else:
            _embeds = [embeds._json]

        if not components or components is MISSING:
            _components = []
        else:
            _components = _build_components(components=components)

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

        res = await self._client.create_message(channel_id=int(self.id), payload=payload._json)
        return Message(**res, _client=self._client)

    async def delete(self) -> None:
        """
        Deletes the channel.
        """
        if not self._client:
            raise AttributeError("HTTPClient not found!")
        await self._client.delete_channel(channel_id=int(self.id))

    async def modify(
        self,
        name: Optional[str] = MISSING,
        topic: Optional[str] = MISSING,
        bitrate: Optional[int] = MISSING,
        user_limit: Optional[int] = MISSING,
        rate_limit_per_user: Optional[int] = MISSING,
        position: Optional[int] = MISSING,
        # permission_overwrites,
        parent_id: Optional[int] = MISSING,
        nsfw: Optional[bool] = MISSING,
        reason: Optional[str] = None,
    ) -> "Channel":
        """
        Edits the channel.

        :param name?: The name of the channel, defaults to the current value of the channel
        :type name: str
        :param topic?: The topic of that channel, defaults to the current value of the channel
        :type topic: Optional[str]
        :param bitrate?: (voice channel only) The bitrate (in bits) of the voice channel, defaults to the current value of the channel
        :type bitrate Optional[int]
        :param user_limit?: (voice channel only) Maximum amount of users in the channel, defaults to the current value of the channel
        :type user_limit: Optional[int]
        :param rate_limit_per_use?: Amount of seconds a user has to wait before sending another message (0-21600), defaults to the current value of the channel
        :type rate_limit_per_user: Optional[int]
        :param position?: Sorting position of the channel, defaults to the current value of the channel
        :type position: Optional[int]
        :param parent_id?: The id of the parent category for a channel, defaults to the current value of the channel
        :type parent_id: Optional[int]
        :param nsfw?: Whether the channel is nsfw or not, defaults to the current value of the channel
        :type nsfw: Optional[bool]
        :param reason?: The reason for the edit
        :type reason: Optional[str]
        :return: The modified channel as new object
        :rtype: Channel
        """
        if not self._client:
            raise AttributeError("HTTPClient not found!")
        _name = self.name if name is MISSING else name
        _topic = self.topic if topic is MISSING else topic
        _bitrate = self.bitrate if bitrate is MISSING else bitrate
        _user_limit = self.user_limit if user_limit is MISSING else user_limit
        _rate_limit_per_user = (
            self.rate_limit_per_user if rate_limit_per_user is MISSING else rate_limit_per_user
        )
        _position = self.position if position is MISSING else position
        _parent_id = self.parent_id if parent_id is MISSING else parent_id
        _nsfw = self.nsfw if nsfw is MISSING else nsfw
        _type = self.type

        payload = Channel(
            name=_name,
            type=_type,
            topic=_topic,
            bitrate=_bitrate,
            user_limit=_user_limit,
            rate_limit_per_user=_rate_limit_per_user,
            position=_position,
            parent_id=_parent_id,
            nsfw=_nsfw,
        )
        res = await self._client.modify_channel(
            channel_id=int(self.id),
            reason=reason,
            data=payload._json,
        )
        return Channel(**res, _client=self._client)

    async def set_name(
        self,
        name: str,
        *,
        reason: Optional[str] = None,
    ) -> "Channel":
        """
        Sets the name of the channel.

        :param name: The new name of the channel
        :type name: str
        :param reason?: The reason of the edit
        :type reason: Optional[str]
        :return: The edited channel
        :rtype: Channel
        """

        return await self.modify(name=name, reason=reason)

    async def set_topic(
        self,
        topic: str,
        *,
        reason: Optional[str] = None,
    ) -> "Channel":
        """
        Sets the topic of the channel.

        :param topic: The new topic of the channel
        :type topic: str
        :param reason?: The reason of the edit
        :type reason: Optional[str]
        :return: The edited channel
        :rtype: Channel
        """

        return await self.modify(topic=topic, reason=reason)

    async def set_bitrate(
        self,
        bitrate: int,
        *,
        reason: Optional[str] = None,
    ) -> "Channel":
        """
        Sets the bitrate of the channel.

        :param bitrate: The new bitrate of the channel
        :type bitrate: int
        :param reason?: The reason of the edit
        :type reason: Optional[str]
        :return: The edited channel
        :rtype: Channel
        """

        if self.type != ChannelType.GUILD_VOICE:
            raise TypeError("Bitrate is only available for VoiceChannels")

        return await self.modify(bitrate=bitrate, reason=reason)

    async def set_user_limit(
        self,
        user_limit: int,
        *,
        reason: Optional[str] = None,
    ) -> "Channel":
        """
        Sets the user_limit of the channel.

        :param user_limit: The new user limit of the channel
        :type user_limit: int
        :param reason?: The reason of the edit
        :type reason: Optional[str]
        :return: The edited channel
        :rtype: Channel
        """

        if self.type != ChannelType.GUILD_VOICE:
            raise TypeError("user_limit is only available for VoiceChannels")

        return await self.modify(user_limit=user_limit, reason=reason)

    async def set_rate_limit_per_user(
        self,
        rate_limit_per_user: int,
        *,
        reason: Optional[str] = None,
    ) -> "Channel":
        """
        Sets the position of the channel.

        :param rate_limit_per_user: The new rate_limit_per_user of the channel (0-21600)
        :type rate_limit_per_user: int
        :param reason?: The reason of the edit
        :type reason: Optional[str]
        :return: The edited channel
        :rtype: Channel
        """

        return await self.modify(rate_limit_per_user=rate_limit_per_user, reason=reason)

    async def set_position(
        self,
        position: int,
        *,
        reason: Optional[str] = None,
    ) -> "Channel":
        """
        Sets the position of the channel.

        :param position: The new position of the channel
        :type position: int
        :param reason?: The reason of the edit
        :type reason: Optional[str]
        :return: The edited channel
        :rtype: Channel
        """

        return await self.modify(position=position, reason=reason)

    async def set_parent_id(
        self,
        parent_id: int,
        *,
        reason: Optional[str] = None,
    ) -> "Channel":
        """
        Sets the parent_id of the channel.

        :param parent_id: The new parent_id of the channel
        :type parent_id: int
        :param reason?: The reason of the edit
        :type reason: Optional[str]
        :return: The edited channel
        :rtype: Channel
        """

        return await self.modify(parent_id=parent_id, reason=reason)

    async def set_nsfw(
        self,
        nsfw: bool,
        *,
        reason: Optional[str] = None,
    ) -> "Channel":
        """
        Sets the nsfw-flag of the channel.

        :param nsfw: The new nsfw-flag of the channel
        :type nsfw: bool
        :param reason?: The reason of the edit
        :type reason: Optional[str]
        :return: The edited channel
        :rtype: Channel
        """

        return await self.modify(nsfw=nsfw, reason=reason)

    async def add_member(
        self,
        member_id: int,
    ) -> None:
        """
        This adds a member to the channel, if the channel is a thread.

        :param member_id: The id of the member to add to the channel
        :type member_id: int
        """
        if not self._client:
            raise AttributeError("HTTPClient not found!")
        if not self.thread_metadata:
            raise TypeError(
                "The Channel you specified is not a thread!"
            )  # TODO: Move to new error formatter.
        await self._client.add_member_to_thread(thread_id=int(self.id), user_id=member_id)

    async def pin_message(
        self,
        message_id: int,
    ) -> None:
        """
        Pins a message to the channel.

        :param message_id: The id of the message to pin
        :type message_id: int
        """
        if not self._client:
            raise AttributeError("HTTPClient not found!")

        await self._client.pin_message(channel_id=int(self.id), message_id=message_id)

    async def unpin_message(
        self,
        message_id: int,
    ) -> None:
        """
        Unpins a message from the channel.

        :param message_id: The id of the message to unpin
        :type message_id: int
        """
        if not self._client:
            raise AttributeError("HTTPClient not found!")

        await self._client.unpin_message(channel_id=int(self.id), message_id=message_id)

    async def publish_message(
        self,
        message_id: int,
    ) -> "Message":  # noqa
        """Publishes (API calls it crossposts) a message in the channel to any that is followed by.

        :param message_id: The id of the message to publish
        :type message_id: int
        :return: The message published
        :rtype: Message
        """
        if not self._client:
            raise AttributeError("HTTPClient not found!")
        from .message import Message

        res = await self._client.publish_message(
            channel_id=int(self.id), message_id=int(message_id)
        )
        return Message(**res, _client=self._client)

    async def get_pinned_messages(self) -> List["Message"]:  # noqa
        """
        Get all pinned messages from the channel.

        :return: A list of pinned message objects.
        :rtype: List[Message]
        """
        if not self._client:
            raise AttributeError("HTTPClient not found!")
        from .message import Message

        res = await self._client.get_pinned_messages(int(self.id))
        return [Message(**message, _client=self._client) for message in res]

    async def get_message(
        self,
        message_id: int,
    ) -> "Message":  # noqa
        """
        Gets a message sent in that channel.

        :return: The message as object
        :rtype: Message
        """
        res = await self._client.get_message(
            channel_id=int(self.id),
            message_id=message_id,
        )
        from .message import Message

        return Message(**res, _client=self._client)

    async def purge(
        self,
        amount: int,
        check: Callable = MISSING,
        before: Optional[int] = MISSING,
        reason: Optional[str] = None,
        bulk: Optional[bool] = True,
    ) -> List["Message"]:  # noqa
        """
        Purges a given amount of messages from a channel. You can specify a check function to exclude specific messages.
        .. code-block:: python
            def check_pinned(message):
                return not message.pinned  # This returns `True` only if the message is the message is not pinned
            await channel.purge(100, check=check_pinned)  # This will delete the newest 100 messages that are not pinned in that channel
        :param amount: The amount of messages to delete
        :type amount: int
        :param check?: The function used to check if a message should be deleted. The message is only deleted if the check returns `True`
        :type check: Callable[[Message], bool]
        :param before?: An id of a message to purge only messages before that message
        :type before: Optional[int]
        :param bulk?: Whether to bulk delete the messages (you cannot delete messages older than 14 days, default) or to delete every message seperately
        :param bulk: Optional[bool]
        :param reason?: The reason of the deletes
        :type reason: Optional[str]
        :return: A list of the deleted messages
        :rtype: List[Message]
        """
        if not self._client:
            raise AttributeError("HTTPClient not found!")
        from .message import Message

        _before = None if before is MISSING else before
        _all = []
        if bulk:
            _allowed_time = datetime.now(tz=timezone.utc) - timedelta(days=14)
            _stop = False
            while amount > 100:

                messages = [
                    Message(**res)
                    for res in await self._client.get_channel_messages(
                        channel_id=int(self.id),
                        limit=100,
                        before=_before,
                    )
                ]
                messages2 = messages.copy()
                for message in messages2:
                    if datetime.fromisoformat(str(message.timestamp)) < _allowed_time:
                        messages.remove(message)
                        _stop = True
                messages2 = messages.copy()
                for message in messages2:
                    if message.flags == (1 << 7):
                        messages.remove(message)
                        amount += 1
                        _before = int(message.id)
                    elif check is not MISSING:
                        _check = check(message)
                        if not _check:
                            messages.remove(message)
                            amount += 1
                            _before = int(message.id)
                _all += messages
                if len(messages) > 1:
                    await self._client.delete_messages(
                        channel_id=int(self.id),
                        message_ids=[int(message.id) for message in messages],
                        reason=reason,
                    )
                elif len(messages) == 1:
                    await self._client.delete_message(
                        channel_id=int(self.id),
                        message_id=int(messages[0].id),
                        reason=reason,
                    )
                elif _stop:
                    return _all
                else:
                    continue
                if _stop:
                    return _all

                amount -= 100

            while amount > 1:
                messages = [
                    Message(**res)
                    for res in await self._client.get_channel_messages(
                        channel_id=int(self.id),
                        limit=amount,
                        before=_before,
                    )
                ]
                messages2 = messages.copy()
                for message in messages2:
                    if datetime.fromisoformat(str(message.timestamp)) < _allowed_time:
                        messages.remove(message)
                        _stop = True
                amount -= amount
                messages2 = messages.copy()
                for message in messages2:
                    if message.flags == (1 << 7):
                        messages.remove(message)
                        amount += 1
                        _before = int(message.id)
                    elif check is not MISSING:
                        _check = check(message)
                        if not _check:
                            messages.remove(message)
                            amount += 1
                            _before = int(message.id)
                _all += messages
                if len(messages) > 1:
                    await self._client.delete_messages(
                        channel_id=int(self.id),
                        message_ids=[int(message.id) for message in messages],
                        reason=reason,
                    )
                elif len(messages) == 1:
                    await self._client.delete_message(
                        channel_id=int(self.id),
                        message_id=int(messages[0].id),
                        reason=reason,
                    )
                elif _stop:
                    return _all
                else:
                    continue
                if _stop:
                    return _all
            while amount == 1:
                messages = [
                    Message(**res)
                    for res in await self._client.get_channel_messages(
                        channel_id=int(self.id),
                        limit=amount,
                        before=_before,
                    )
                ]
                amount -= 1
                messages2 = messages.copy()
                for message in messages2:
                    if message.flags == (1 << 7):
                        messages.remove(message)
                        amount += 1
                        _before = int(message.id)
                    elif check is not MISSING:
                        _check = check(message)
                        if not _check:
                            messages.remove(message)
                            amount += 1
                            _before = int(message.id)
                _all += messages
                if not messages:
                    continue
                await self._client.delete_message(
                    channel_id=int(self.id),
                    message_id=int(messages[0].id),
                    reason=reason,
                )

        else:
            while amount > 0:
                messages = [
                    Message(**res)
                    for res in await self._client.get_channel_messages(
                        channel_id=int(self.id),
                        limit=min(amount, 100),
                        before=_before,
                    )
                ]

                amount -= min(amount, 100)
                messages2 = messages.copy()
                for message in messages2:
                    if message.flags == (1 << 7):
                        messages.remove(message)
                        amount += 1
                        _before = int(message.id)
                    elif check is not MISSING:
                        _check = check(message)
                        if not _check:
                            messages.remove(message)
                            amount += 1
                            _before = int(message.id)
                _all += messages

            for message in _all:
                await self._client.delete_message(
                    channel_id=int(self.id),
                    message_id=int(message.id),
                    reason=reason,
                )

        return _all

    async def create_thread(
        self,
        name: str,
        type: Optional[ChannelType] = ChannelType.GUILD_PUBLIC_THREAD,
        auto_archive_duration: Optional[int] = MISSING,
        invitable: Optional[bool] = MISSING,
        message_id: Optional[int] = MISSING,
        reason: Optional[str] = None,
    ) -> "Channel":
        """
        Creates a thread in the Channel.

        :param name: The name of the thread
        :type name: str
        :param auto_archive_duration?: duration in minutes to automatically archive the thread after recent activity,
            can be set to: 60, 1440, 4320, 10080
        :type auto_archive_duration: Optional[int]
        :param type?: The type of thread, defaults to public. ignored if creating thread from a message
        :type type: Optional[ChannelType]
        :param invitable?: Boolean to display if the Thread is open to join or private.
        :type invitable: Optional[bool]
        :param message_id?: An optional message to create a thread from.
        :type message_id: Optional[int]
        :param reason?: An optional reason for the audit log
        :type reason: Optional[str]
        :return: The created thread
        :rtype: Channel
        """
        if not self._client:
            raise AttributeError("HTTPClient not found!")
        if type not in [
            ChannelType.GUILD_NEWS_THREAD,
            ChannelType.GUILD_PUBLIC_THREAD,
            ChannelType.GUILD_PRIVATE_THREAD,
        ]:
            raise AttributeError("type must be a thread type!")

        _auto_archive_duration = None if auto_archive_duration is MISSING else auto_archive_duration
        _invitable = None if invitable is MISSING else invitable
        _message_id = None if message_id is MISSING else message_id
        res = await self._client.create_thread(
            channel_id=int(self.id),
            thread_type=type.value,
            name=name,
            auto_archive_duration=_auto_archive_duration,
            invitable=_invitable,
            message_id=_message_id,
            reason=reason,
        )

        return Channel(**res, _client=self._client)


class Thread(Channel):
    """An object representing a thread.

    .. note::
        This is a derivation of the base Channel, since a
        thread can be its own event.
    """

    ...
