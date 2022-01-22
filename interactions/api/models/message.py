from datetime import datetime
from enum import IntEnum
from typing import List, Optional, Union

from .channel import Channel, ChannelType
from .member import Member
from .misc import DictSerializerMixin, Snowflake
from .team import Application
from .user import User


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


class MessageActivity(DictSerializerMixin):
    """A class object representing the activity state of a message.

    .. note::
        ``party_id`` is ambiguous -- Discord poorly documented this. :)

        We assume it's for game rich presence invites?
        i.e. : Phasmophobia and Call of Duty.

    :ivar str type: The message activity type.
    :ivar Optional[Snowflake] party_id?: The party ID of the activity.
    """

    __slots__ = ("_json", "type", "party_id")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.party_id = Snowflake(self.party_id) if self._json.get("party_id") else None


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

    __slots__ = ("_json", "message_id", "channel_id", "guild_id", "fail_if_not_exists")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.message_id = Snowflake(self.message_id) if self._json.get("message_id") else None
        self.channel_id = Snowflake(self.channel_id) if self._json.get("channel_id") else None
        self.guild_id = Snowflake(self.guild_id) if self._json.get("guild_id") else None


class Attachment(DictSerializerMixin):
    """
    A class object representing an attachment in a message.

    .. note::
        ``height`` and ``width`` have values based off of ``content_type``,
        which requires it to be a media file with viewabiltity as a photo,
        animated photo, GIF and/or video.

    :ivar int id: The ID of the attachment.
    :ivar str filename: The name of the attachment file.
    :ivar Optional[str] description?: The description of the file.
    :ivar Optional[str] content_type?: The type of attachment file.
    :ivar int size: The size of the attachment file.
    :ivar str url: The CDN URL of the attachment file.
    :ivar str proxy_url: The proxied/cached CDN URL of the attachment file.
    :ivar Optional[int] height?: The height of the attachment file.
    :ivar Optional[int] width?: The width of the attachment file.
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
        self.id = Snowflake(self.id) if self._json.get("id") else None


class MessageInteraction(DictSerializerMixin):
    """
    A class object that resembles the interaction used to generate
    the associated message.

    :ivar Snowflake id: ID of the interaction.
    :ivar int type: Type of interaction.
    :ivar str name: Name of the application command.
    :ivar User user: The user who invoked the interaction.
    """

    # TODO: document member attr.
    __slots__ = ("_json", "id", "type", "name", "user", "member")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = Snowflake(self.id) if self._json.get("id") else None
        self.user = User(**self.user) if self._json.get("user") else None


class ChannelMention(DictSerializerMixin):
    """
    A class object that resembles the mention of a channel
    in a guild.

    :ivar Snowflake id: The ID of the channel.
    :ivar Snowflake guild_id: The ID of the guild that contains the channel.
    :ivar int type: The channel type.
    :ivar str name: The name of the channel.
    """

    __slots__ = ("_json", "id", "type", "name", "guild_id")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = Snowflake(self.id) if self._json.get("id") else None
        self.guild_id = Snowflake(self.guild_id) if self._json.get("guild_id") else None
        self.type = ChannelType(self.type)


class Message(DictSerializerMixin):
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
    :ivar int type: Type of message
    :ivar Optional[MessageActivity] activity?: Message activity object that's sent by Rich Presence
    :ivar Optional[Application] application?: Application object that's sent by Rich Presence
    :ivar Optional[MessageReference] message_reference?: Data showing the source of a message (crosspost, channel follow, add, pin, or replied message)
    :ivar Optional[Any] allowed_mentions: The allowed mentions of roles attached in the message.
    :ivar int flags: Message flags
    :ivar Optional[MessageInteraction] interaction?: Message interaction object, if the message is sent by an interaction.
    :ivar Optional[Channel] thread?: The thread that started from this message, if any, with a thread member object embedded.
    :ivar Optional[Union[Component, List[Component]]] components?: Components associated with this message, if any.
    :ivar Optional[List[PartialSticker]] sticker_items?: An array of message sticker item objects, if sent with them.
    :ivar Optional[List[Sticker]] stickers?: Array of sticker objects sent with the message if any. Deprecated.
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
        "allowed_mentions",
        "flags",
        "referenced_message",
        "interaction",
        "thread",
        "components",
        "sticker_items",
        "stickers",
        "_client",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.id = Snowflake(self.id) if self._json.get("id") else None
        self.channel_id = Snowflake(self.channel_id) if self._json.get("channel_id") else None
        self.guild_id = Snowflake(self.guild_id) if self._json.get("guild_id") else None
        self.webhook_id = Snowflake(self.webhook_id) if self._json.get("webhook_id") else None
        self.application_id = (
            Snowflake(self.application_id) if self._json.get("application_id") else None
        )
        self.timestamp = (
            datetime.fromisoformat(self._json.get("timestamp"))
            if self._json.get("timestamp")
            else datetime.utcnow()
        )
        self.author = User(**self._json.get("author")) if self._json.get("author") else None
        self.member = Member(**self._json.get("member")) if self._json.get("member") else None
        self.type = MessageType(self.type) if self._json.get("type") else None
        self.edited_timestamp = (
            datetime.fromisoformat(self._json.get("edited_timestamp"))
            if self._json.get("edited_timestamp")
            else datetime.utcnow()
        )
        self.mention_channels = (
            [ChannelMention(**mention) for mention in self.mention_channels]
            if self._json.get("mention_channels")
            else None
        )
        self.attachments = (
            [Attachment(**attachment) for attachment in self.attachments]
            if self._json.get("attachments")
            else None
        )
        self.embeds = (
            [Embed(**embed) for embed in self.embeds] if self._json.get("embeds") else None
        )
        self.activity = MessageActivity(**self.activity) if self._json.get("activity") else None
        self.application = (
            Application(**self.application) if self._json.get("application") else None
        )
        self.message_reference = (
            MessageReference(**self.message_reference)
            if self._json.get("message_reference")
            else None
        )
        self.interaction = (
            MessageInteraction(**self.interaction) if self._json.get("interaction") else None
        )
        self.thread = Channel(**self.thread) if self._json.get("thread") else None

    async def get_channel(self) -> Channel:
        """
        Gets the channel where the message was sent.

        :rtype: Channel
        """
        if not self._client:
            raise AttributeError("HTTPClient not found!")
        res = await self._client.get_channel(channel_id=int(self.channel_id))
        return Channel(**res, _client=self._client)

    async def get_guild(self):
        """
        Gets the guild where the message was sent.

        :rtype: Guild
        """
        if not self._client:
            raise AttributeError("HTTPClient not found!")
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
            raise AttributeError("HTTPClient not found!")
        await self._client.delete_message(
            message_id=int(self.id), channel_id=int(self.channel_id), reason=reason
        )

    async def edit(
        self,
        content: Optional[str] = None,
        *,
        tts: Optional[bool] = False,
        # file: Optional[FileIO] = None,
        embeds: Optional[Union["Embed", List["Embed"]]] = None,
        allowed_mentions: Optional["MessageInteraction"] = None,
        message_reference: Optional["MessageReference"] = None,
        components=None,
    ) -> "Message":
        """
        This method edits a message. Only available for messages sent by the bot.

        :param content?: The contents of the message as a string or string-converted value.
        :type content: Optional[str]
        :param tts?: Whether the message utilizes the text-to-speech Discord programme or not.
        :type tts: Optional[bool]
        :param embeds?: An embed, or list of embeds for the message.
        :type embeds: Optional[Union[Embed, List[Embed]]]
        :param allowed_mentions?: The message interactions/mention limits that the message can refer to.
        :type allowed_mentions: Optional[MessageInteraction]
        :param components?: A component, or list of components for the message. If `[]` the components will be removed
        :type components: Optional[Union[ActionRow, Button, SelectMenu, List[Union[ActionRow, Button, SelectMenu]]]]
        :return: The edited message as an object.
        :rtype: Message
        """
        if not self._client:
            raise AttributeError("HTTPClient not found!")
        from ...models.component import ActionRow, Button, SelectMenu

        _content: str = self.content if content is None else content
        _tts: bool = True if bool(tts) else tts
        # _file = None if file is None else file

        if embeds is None:
            _embeds = self.embeds
        else:
            _embeds: list = (
                []
                if embeds is None
                else (
                    [embed._json for embed in embeds]
                    if isinstance(embeds, list)
                    else [embeds._json]
                )
            )
        _allowed_mentions: dict = {} if allowed_mentions is None else allowed_mentions
        _message_reference: dict = {} if message_reference is None else message_reference._json
        if components == []:
            _components = []
        # TODO: Break this obfuscation pattern down to a "builder" method.
        elif components is not None and components != []:
            _components = []
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
            _components = self.components

        payload: Message = Message(
            content=_content,
            tts=_tts,
            # file=file,
            embeds=_embeds,
            allowed_mentions=_allowed_mentions,
            message_reference=_message_reference,
            components=_components,
        )

        await self._client.edit_message(
            channel_id=int(self.channel_id),
            message_id=int(self.id),
            payload=payload._json,
        )
        return payload

    async def reply(
        self,
        content: Optional[str] = None,
        *,
        tts: Optional[bool] = False,
        # attachments: Optional[List[Any]] = None
        embeds: Optional[Union["Embed", List["Embed"]]] = None,
        allowed_mentions: Optional["MessageInteraction"] = None,
        components=None,
    ) -> "Message":
        """
        Sends a new message replying to the old.

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

        _content: str = "" if content is None else content
        _tts: bool = True if bool(tts) else tts
        # _file = None if file is None else file
        # _attachments = [] if attachments else None
        _embeds: list = (
            []
            if embeds is None
            else ([embed._json for embed in embeds] if isinstance(embeds, list) else [embeds._json])
        )
        _allowed_mentions: dict = {} if allowed_mentions is None else allowed_mentions
        _message_reference = MessageReference(message_id=int(self.id))._json
        _components: List[dict] = [{"type": 1, "components": []}]

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
            message_reference=_message_reference,
            allowed_mentions=_allowed_mentions,
            components=_components,
        )

        res = await self._client.create_message(
            channel_id=int(self.channel_id), payload=payload._json
        )
        return Message(**res, _client=self._client)

    async def pin(self) -> None:
        """Pins the message to its channel"""
        if not self._client:
            raise AttributeError("HTTPClient not found!")
        await self._client.pin_message(channel_id=int(self.channel_id), message_id=int(self.id))

    async def unpin(self) -> None:
        """Unpins the message from its channel"""
        if not self._client:
            raise AttributeError("HTTPClient not found!")
        await self._client.unpin_message(channel_id=int(self.channel_id), message_id=int(self.id))

    async def publish(self) -> "Message":
        """Publishes (API calls it crossposts) the message in its channel to any that is followed by.

        :return: message object
        :rtype: Message
        """
        if not self._client:
            raise AttributeError("HTTPClient not found!")
        res = await self._client.publish_message(
            channel_id=int(self.channel_id), message_id=int(self.id)
        )
        return Message(**res, _client=self._client)


class Emoji(DictSerializerMixin):
    """
    A class objecting representing an emoji.

    :ivar Optional[Snowflake] id?: Emoji id
    :ivar Optional[str] name?: Emoji name.
    :ivar Optional[List[Role]] roles?: Roles allowed to use this emoji
    :ivar Optional[User] user?: User that created this emoji
    :ivar Optional[bool] require_colons?: Status denoting of this emoji must be wrapped in colons
    :ivar Optional[bool] managed?: Status denoting if this emoji is managed (by an integration)
    :ivar Optional[bool] animated?: Status denoting if this emoji is animated
    :ivar Optional[bool] available?: Status denoting if this emoji can be used. (Can be false via server boosting)
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
        self.id = Snowflake(self.id) if self._json.get("id") else None


class ReactionObject(DictSerializerMixin):
    """The reaction object.

    :ivar int count: The amount of times this emoji has been used to react
    :ivar bool me: A status denoting if the current user reacted using this emoji
    :ivar Emoji emoji: Emoji information
    """

    __slots__ = ("_json", "count", "me", "bool")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.emoji = Emoji(**self.emoji) if self._json.get("emoji") else None


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
        self.id = Snowflake(self.id) if self._json.get("id") else None


class Sticker(PartialSticker):
    """
    A class object representing a full sticker apart from a partial.

    :ivar int id: ID of the sticker
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
        self.id = Snowflake(self.id) if self._json.get("id") else None
        self.pack_id = Snowflake(self.pack_id) if self._json.get("pack_id") else None
        self.user = User(**self.user) if self._json.get("user") else None


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

    __slots__ = ("_json", "url", "proxy_url", "height", "width")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class EmbedProvider(DictSerializerMixin):
    """
    A class object representing the provider of an embed.

    :ivar Optional[str] name?: Name of provider
    :ivar Optional[str] name?: URL of provider
    """

    __slots__ = ("_json", "url", "name")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


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

    __slots__ = ("_json", "url", "proxy_icon_url", "icon_url", "name")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


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

    __slots__ = ("_json", "text", "proxy_icon_url", "icon_url")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


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

    __slots__ = ("_json", "name", "inline", "value")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


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
        self.timestamp = (
            datetime.fromisoformat(self._json.get("timestamp"))
            if self._json.get("timestamp")
            else datetime.utcnow()
        )
        self.footer = (
            EmbedFooter(**self.footer)
            if isinstance(self._json.get("footer"), dict)
            else self._json.get("footer")
        )
        self.image = (
            EmbedImageStruct(**self.image)
            if isinstance(self._json.get("image"), dict)
            else self._json.get("image")
        )
        self.thumbnail = (
            EmbedImageStruct(**self.thumbnail)
            if isinstance(self._json.get("thumbnail"), dict)
            else self._json.get("thumbnail")
        )
        self.video = (
            EmbedImageStruct(**self.video)
            if isinstance(self._json.get("video"), dict)
            else self._json.get("video")
        )
        self.provider = (
            EmbedProvider(**self.provider)
            if isinstance(self._json.get("provider"), dict)
            else self._json.get("provider")
        )
        self.author = (
            EmbedAuthor(**self.author)
            if isinstance(self._json.get("author"), dict)
            else self._json.get("author")
        )
        self.fields = (
            [
                EmbedField(**field) if isinstance(field, dict) else field
                for field in self._json["fields"]
            ]
            if self._json.get("fields")
            else None
        )

        # TODO: Complete partial fix.
        # The issue seems to be that this itself is not updating
        # JSON result correctly. After numerous attempts I seem to
        # have the attribute to do it, but _json won't budge at all.
        # a genexpr is a poor way to go about this, but I know later
        # on we'll be refactoring this anyhow. What the fuck is breaking
        # it?
        if self.fields:
            self._json.update({"fields": [field._json for field in self.fields]})

        if self.author:
            self._json.update({"author": self.author._json})

        if self.footer:
            self._json.update({"footer": self.footer._json})
