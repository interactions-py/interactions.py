from datetime import datetime
from enum import IntEnum
from typing import List, Optional

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
        :type components: Optional[Union[ActionRow, Button, SelectMenu, List[Union[ActionRow, Button, SelectMenu]]]]
        :return: The sent message as an object.
        :rtype: Message
        """
        if not self._client:
            raise AttributeError("HTTPClient not found!")
        from ...models.component import ActionRow, Button, SelectMenu
        from .message import Message

        _content: str = "" if content is None else content
        _tts: bool = False if tts is None else tts
        # _file = None if file is None else file
        # _attachments = [] if attachments else None
        _embeds: list = []
        _allowed_mentions: dict = {} if allowed_mentions is None else allowed_mentions
        _components: List[dict] = [{"type": 1, "components": []}]
        if embeds:
            if isinstance(embeds, list):
                _embeds = [embed._json for embed in embeds]
            else:
                _embeds = [embeds._json]

        # TODO: Break this obfuscation pattern down to a "builder" method.
        if components:
            if isinstance(components, list) and all(
                isinstance(action_row, ActionRow) for action_row in components
            ):
                _components = [
                    {
                        "type": 1,
                        "components": [
                            (
                                component._json
                                if component._json.get("custom_id") or component._json.get("url")
                                else []
                            )
                            for component in action_row.components
                        ],
                    }
                    for action_row in components
                ]
            elif isinstance(components, list) and all(
                isinstance(component, (Button, SelectMenu)) for component in components
            ):
                for component in components:
                    if isinstance(component, SelectMenu):
                        component._json["options"] = [
                            options._json if not isinstance(options, dict) else options
                            for options in component._json["options"]
                        ]
                _components = [
                    {
                        "type": 1,
                        "components": [
                            (
                                component._json
                                if component._json.get("custom_id") or component._json.get("url")
                                else []
                            )
                            for component in components
                        ],
                    }
                ]
            elif isinstance(components, list) and all(
                isinstance(action_row, (list, ActionRow)) for action_row in components
            ):
                _components = []
                for action_row in components:
                    for component in (
                        action_row if isinstance(action_row, list) else action_row.components
                    ):
                        if isinstance(component, SelectMenu):
                            component._json["options"] = [
                                option._json for option in component.options
                            ]
                    _components.append(
                        {
                            "type": 1,
                            "components": [
                                (
                                    component._json
                                    if component._json.get("custom_id")
                                    or component._json.get("url")
                                    else []
                                )
                                for component in (
                                    action_row
                                    if isinstance(action_row, list)
                                    else action_row.components
                                )
                            ],
                        }
                    )
            elif isinstance(components, ActionRow):
                _components[0]["components"] = [
                    (
                        component._json
                        if component._json.get("custom_id") or component._json.get("url")
                        else []
                    )
                    for component in components.components
                ]
            elif isinstance(components, Button):
                _components[0]["components"] = (
                    [components._json]
                    if components._json.get("custom_id") or components._json.get("url")
                    else []
                )
            elif isinstance(components, SelectMenu):
                components._json["options"] = [
                    options._json if not isinstance(options, dict) else options
                    for options in components._json["options"]
                ]
                _components[0]["components"] = (
                    [components._json]
                    if components._json.get("custom_id") or components._json.get("url")
                    else []
                )
        else:
            _components = []

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
        name: Optional[str] = None,
        topic: Optional[str] = None,
        bitrate: Optional[int] = None,
        user_limit: Optional[int] = None,
        rate_limit_per_user: Optional[int] = None,
        position: Optional[int] = None,
        # permission_overwrites,
        parent_id: Optional[int] = None,
        nsfw: Optional[bool] = False,
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
        :param reason: The reason for the edit
        :type reason: Optional[str]
        :return: The modified channel as new object
        :rtype: Channel
        """
        if not self._client:
            raise AttributeError("HTTPClient not found!")
        _name = self.name if not name else name
        _topic = self.topic if not topic else topic
        _bitrate = self.bitrate if not bitrate else bitrate
        _user_limit = self.user_limit if not user_limit else user_limit
        _rate_limit_per_user = (
            self.rate_limit_per_user if not rate_limit_per_user else rate_limit_per_user
        )
        _position = self.position if not position else position
        _parent_id = self.parent_id if not parent_id else parent_id
        _nsfw = self.nsfw if not nsfw else nsfw
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
    ):
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

    async def get_pinned_messages(self):
        """
        Get all pinned messages from the channel.

        :return: A list of pinned message objects.
        :rtype: List[Message]
        """
        if not self._client:
            raise AttributeError("HTTPClient not found!")
        from .message import Message

        res = await self._client.get_pinned_messages(int(self.id))
        messages = [Message(**message, _client=self._client) for message in res]
        return messages


class Thread(Channel):
    """An object representing a thread.

    .. note::
        This is a derivation of the base Channel, since a
        thread can be its own event.
    """

    ...
