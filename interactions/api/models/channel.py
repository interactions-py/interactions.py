from asyncio import Task, create_task, get_running_loop, sleep
from datetime import datetime, timedelta, timezone
from inspect import isawaitable
from math import inf
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    ContextManager,
    Iterable,
    List,
    Literal,
    Optional,
    Union,
)
from warnings import warn

from ...client.enums import IntEnum
from ...utils.abc.base_context_managers import BaseAsyncContextManager
from ...utils.abc.base_iterators import DiscordPaginationIterator
from ...utils.attrs_utils import (
    ClientSerializerMixin,
    DictSerializerMixin,
    convert_int,
    convert_list,
    define,
    field,
)
from ...utils.missing import MISSING
from ...utils.utils import search_iterable
from ..error import LibraryException
from .emoji import Emoji
from .flags import MessageFlags, Permissions
from .misc import AllowedMentions, File, IDMixin, Overwrite, Snowflake
from .role import Role
from .user import User
from .webhook import Webhook

if TYPE_CHECKING:
    from ...client.models.component import ActionRow, Button, SelectMenu
    from ..http.client import HTTPClient
    from .guild import Guild, Invite, InviteTargetType
    from .gw import VoiceState
    from .member import Member
    from .message import Attachment, Embed, Message, Sticker

__all__ = (
    "ChannelType",
    "Thread",
    "Channel",
    "ThreadMember",
    "ThreadMetadata",
    "AsyncHistoryIterator",
    "AsyncTypingContextManager",
    "Tags",
)


class ChannelType(IntEnum):
    """An enumerable object representing the type of channels."""

    GUILD_TEXT = 0
    DM = 1
    GUILD_VOICE = 2
    GROUP_DM = 3
    GUILD_CATEGORY = 4
    GUILD_ANNOUNCEMENT = 5
    GUILD_STORE = 6
    ANNOUNCEMENT_THREAD = 10
    PUBLIC_THREAD = 11
    PRIVATE_THREAD = 12
    GUILD_STAGE_VOICE = 13
    GUILD_DIRECTORY = 14
    GUILD_FORUM = 15


@define()
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
    :ivar Optional[bool] invitable: The ability to invite users to the thread.
    """

    archived: bool = field()
    auto_archive_duration: int = field()
    archive_timestamp: datetime = field(converter=datetime.fromisoformat, repr=False)
    locked: bool = field()
    invitable: Optional[bool] = field(default=None)


@define()
class ThreadMember(ClientSerializerMixin):
    """
    A class object representing a member in a thread.

    .. note::
        ``id`` only shows if there are active intents involved with the member
        in the thread.

    :ivar Optional[Snowflake] id: The "ID" or intents of the member.
    :ivar Snowflake user_id: The user ID of the member.
    :ivar datetime join_timestamp: The timestamp of when the member joined the thread.
    :ivar int flags: The bitshift flags for the member in the thread.
    :ivar bool muted: Whether the member is muted or not.
    """

    id: Optional[Snowflake] = field(converter=Snowflake, default=None, repr=False)
    user_id: Optional[Snowflake] = field(converter=Snowflake, default=None)
    join_timestamp: datetime = field(converter=datetime.fromisoformat, repr=False)
    flags: int = field(repr=False)
    muted: bool = field()
    mute_config: Optional[Any] = field(
        default=None, repr=False
    )  # todo explore this, it isn't in the ddev docs


class AsyncHistoryIterator(DiscordPaginationIterator):
    """
    .. versionadded:: 4.3.2

    A class object that allows iterating through a channel's history.

    :param HTTPClient _client: The HTTPClient of the bot
    :param Union[int, str, Snowflake, Channel] obj: The channel to get the history from
    :param Optional[Union[int, str, Snowflake, Message]] start_at: The message to begin getting the history from
    :param Optional[bool] reverse: Whether to only get newer message. Default False
    :param Optional[Callable[[Message], Union[bool, Awaitable[bool]]]] check: A check to ignore certain messages
    :param Optional[int] maximum: A set maximum of messages to get before stopping the iteration
    """

    def __init__(
        self,
        _client: "HTTPClient",
        obj: Union[int, str, Snowflake, "Channel"],
        maximum: Optional[int] = inf,
        start_at: Optional[Union[int, str, Snowflake, "Message"]] = MISSING,
        check: Optional[Callable[["Message"], Union[bool, Awaitable[bool]]]] = None,
        reverse: Optional[bool] = False,
    ):
        super().__init__(obj, _client, maximum=maximum, start_at=start_at, check=check)

        self.__stop: bool = False

        from .message import Message

        if reverse and start_at is MISSING:
            raise LibraryException(
                code=12,
                message="A message to start from is required to go through the channel in reverse.",
            )

        if reverse:
            self.before = MISSING
            self.after = self.start_at
        else:
            self.before = self.start_at
            self.after = MISSING

        self.objects: Optional[List[Message]]

    async def get_first_objects(self) -> None:
        from .message import Message

        limit = min(self.maximum, 100)

        if self.maximum == limit:
            self.__stop = True

        if self.after is not MISSING:
            msgs = await self._client.get_channel_messages(
                channel_id=self.object_id, after=self.after, limit=limit
            )
            msgs.reverse()
            self.after = int(msgs[-1]["id"])
        else:
            msgs = await self._client.get_channel_messages(
                channel_id=self.object_id, before=self.before, limit=limit
            )
            self.before = int(msgs[-1]["id"])

        if len(msgs) < 100:
            # already all messages resolved with one operation
            self.__stop = True

        self.object_count += limit

        self.objects = [Message(**msg, _client=self._client) for msg in msgs]

    async def flatten(self) -> List["Message"]:
        """Returns all remaining items as list"""
        return [item async for item in self]

    async def get_objects(self) -> None:
        from .message import Message

        limit = min(50, self.maximum - self.object_count)

        if self.after is not MISSING:
            msgs = await self._client.get_channel_messages(
                channel_id=self.object_id, after=self.after, limit=limit
            )
            msgs.reverse()
            self.after = int(msgs[-1]["id"])
        else:
            msgs = await self._client.get_channel_messages(
                channel_id=self.object_id, before=self.before, limit=limit
            )
            self.before = int(msgs[-1]["id"])

        if len(msgs) < limit or limit == self.maximum - self.object_count:
            # end of messages reached again
            self.__stop = True

        self.object_count += limit

        self.objects.extend([Message(**msg, _client=self._client) for msg in msgs])

    async def __anext__(self) -> "Message":
        try:
            if self.objects is None:
                await self.get_first_objects()

            obj = self.objects.pop(0)

            if self.check:
                res = self.check(obj)
                _res = await res if isawaitable(res) else res
                while not _res:
                    if (
                        not self.__stop
                        and len(self.objects) < 5
                        and self.object_count >= self.maximum
                    ):
                        await self.get_objects()

                    self.object_count -= 1
                    obj = self.objects.pop(0)

                    _res = self.check(obj)

            if not self.__stop and len(self.objects) < 5 and self.object_count <= self.maximum:
                await self.get_objects()
        except IndexError as e:
            raise StopAsyncIteration from e
        else:
            return obj


class AsyncTypingContextManager(BaseAsyncContextManager):
    """
    .. versionadded:: 4.3.2

    An async context manager for triggering typing.

    :param Union[int, str, Snowflake, Channel] obj: The channel to trigger typing in.
    :param HTTPClient _client: The HTTPClient of the bot
    """

    def __init__(
        self,
        obj: Union[int, str, "Snowflake", "Channel"],
        _client: "HTTPClient",
    ):
        try:
            self.loop = get_running_loop()
        except RuntimeError as e:
            raise RuntimeError("No running event loop detected!") from e

        self.object_id = (int(obj.id) if hasattr(obj, "id") else int(obj)) if obj else None

        self._client = _client
        self.__task: Optional[Task] = None

    def __await__(self):
        return self._client.trigger_typing(self.object_id).__await__()

    async def do_action(self):
        while True:
            await self._client.trigger_typing(self.object_id)
            await sleep(8)

    async def __aenter__(self):
        self.__task = create_task(self.do_action())

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.__task.cancel()


@define()
class Tags(ClientSerializerMixin):
    """
    .. versionadded:: 4.3.2

    An object denoting a tag object within a forum channel.

    .. note::
        If the emoji is custom, it won't have name information.

    :ivar str name: Name of the tag. The limit is up to 20 characters.
    :ivar Snowflake id: ID of the tag. Can also be 0 if manually created.
    :ivar bool moderated: A boolean denoting whether this tag can be removed/added by moderators with the :attr:`.Permissions.MANAGE_THREADS` permission.
    :ivar Optional[str] emoji_name: The unicode character of the emoji.
    :ivar Optional[Snowflake] emoji_id: The id of a guild's custom emoji.
    """

    # TODO: Rename these to discord-docs
    name: str = field()
    id: Snowflake = field(converter=Snowflake)
    moderated: bool = field()
    emoji_name: Optional[str] = field(default=None)
    emoji_id: Optional[Snowflake] = field(converter=Snowflake, default=None)

    @property
    def emoji(self) -> Emoji:
        """
        Returns an emoji of tag.
        """
        return Emoji(name=self.emoji_name, id=self.emoji_id, _client=self._client)

    @property
    def created_at(self) -> datetime:
        """
        .. versionadded:: 4.4.0

        Returns when the tag was created.
        """
        return self.id.timestamp

    async def delete(
        self, channel_id: Union[int, str, Snowflake, "Channel"]  # discord, why :hollow:
    ) -> None:
        """
        Deletes this tag

        :param Union[int, str, Snowflake, Channel] channel_id: The ID of the channel where the tag belongs to
        """
        if isinstance(channel_id, Channel) and channel_id.type != ChannelType.GUILD_FORUM:
            raise LibraryException(code=14, message="Can only manage tags on a forum channel")

        if not self._client:
            raise LibraryException(code=13)

        _channel_id = int(channel_id.id) if isinstance(channel_id, Channel) else int(channel_id)

        return await self._client.delete_tag(_channel_id, int(self.id))

    async def edit(
        self,
        channel_id: Union[int, str, Snowflake, "Channel"],  # discord, why :hollow:
        name: str,
        emoji_name: Optional[str] = MISSING,
        emoji_id: Optional[int] = MISSING,
    ) -> "Tags":
        """
        Edits this tag

        .. note::
            Can either have an emoji_id or an emoji_name, but not both.
            emoji_id is meant for custom emojis, emoji_name is meant for unicode emojis.

        :param Union[int, str, Snowflake, Channel] channel_id: The ID of the channel where the tag belongs to
        :param str name: The new name of the tag
        :param Optional[int] emoji_id: The ID of the emoji to use for the tag
        :param Optional[int] emoji_name: The name of the emoji to use for the tag
        :return: The modified tag
        :rtype: Tags
        """

        if isinstance(channel_id, Channel) and channel_id.type != ChannelType.GUILD_FORUM:
            raise LibraryException(code=14, message="Can only manage tags on a forum channel")

        if not self._client:
            raise LibraryException(code=13)

        _channel_id = int(channel_id.id) if isinstance(channel_id, Channel) else int(channel_id)

        payload = {"name": name}

        if emoji_id is not MISSING and emoji_id and emoji_name and emoji_name is not MISSING:
            raise LibraryException(
                code=12, message="emoji_id and emoji_name are mutually exclusive"
            )

        if emoji_id is not MISSING:
            payload["emoji_id"] = emoji_id
        if emoji_name is not MISSING:
            payload["emoji_name"] = emoji_name

        data = await self._client.edit_tag(_channel_id, int(self.id), **payload)

        return Tags(**data)


@define()
class Channel(ClientSerializerMixin, IDMixin):
    """
    A class object representing all types of channels.

    :ivar Snowflake id: The (snowflake) ID of the channel.
    :ivar ChannelType type: The type of channel.
    :ivar Optional[Snowflake] guild_id: The ID of the guild if it is not a DM channel.
    :ivar Optional[int] position: The position of the channel.
    :ivar List[Overwrite] permission_overwrites: The non-synced permissions of the channel.
    :ivar str name: The name of the channel.
    :ivar Optional[str] topic: The description of the channel.
    :ivar Optional[bool] nsfw: Whether the channel is NSFW.
    :ivar Snowflake last_message_id: The ID of the last message sent.
    :ivar Optional[int] bitrate: The audio bitrate of the channel.
    :ivar Optional[int] user_limit: The maximum amount of users allowed in the channel.
    :ivar Optional[int] rate_limit_per_user: The concurrent ratelimit for users in the channel.
    :ivar Optional[List[User]] recipients: The recipients of the channel.
    :ivar Optional[str] icon: The icon of the channel.
    :ivar Optional[Snowflake] owner_id: The owner of the channel.
    :ivar Optional[Snowflake] application_id: The application of the channel.
    :ivar Optional[Snowflake] parent_id: The ID of the "parent"/main channel.
    :ivar Optional[datetime] last_pin_timestamp: The timestamp of the last pinned message in the channel.
    :ivar Optional[str] rtc_region: The region of the WebRTC connection for the channel.
    :ivar Optional[int] video_quality_mode: The set quality mode for video streaming in the channel.
    :ivar int message_count: The amount of messages in the channel.
    :ivar Optional[int] member_count: The amount of members in the channel.
    :ivar Optional[bool] newly_created: Boolean representing if a thread is created.
    :ivar Optional[ThreadMetadata] thread_metadata: The thread metadata of the channel.
    :ivar Optional[ThreadMember] member: The member of the thread in the channel.
    :ivar Optional[int] default_auto_archive_duration: The set auto-archive time for all threads to naturally follow in the channel.
    :ivar Optional[Permissions] permissions: The permissions of the channel.
    :ivar Optional[int] flags: The flags of the channel.
    :ivar Optional[int] total_message_sent: Number of messages ever sent in a thread.
    :ivar Optional[int] default_thread_slowmode_delay: The default slowmode delay in seconds for threads, if this channel is a forum.
    :ivar Optional[List[Tags]] available_tags: Tags in a forum channel, if any.
    :ivar Optional[List[Snowflake]] applied_tags: The IDs of tags that have been applied to a thread, if any.
    :ivar Optional[Emoji] default_reaction_emoji: Default reaction emoji for threads created in a forum, if any.
    """

    # Template attribute isn't live/documented, this line exists as a placeholder 'TODO' of sorts

    __slots__ = (
        # TODO: Document banner when Discord officially documents them.
        "banner",
        "guild_hashes",
    )

    type: ChannelType = field(converter=ChannelType)
    id: Snowflake = field(converter=Snowflake)
    _guild_id: Optional[Snowflake] = field(
        converter=Snowflake, default=None, discord_name="guild_id"
    )
    position: Optional[int] = field(default=None)
    permission_overwrites: Optional[List[Overwrite]] = field(
        converter=convert_list(Overwrite), factory=list
    )
    name: str = field(factory=str)
    topic: Optional[str] = field(default=None)
    nsfw: Optional[bool] = field(default=None)
    last_message_id: Optional[Snowflake] = field(converter=Snowflake, default=None, repr=False)
    bitrate: Optional[int] = field(default=None, repr=False)
    user_limit: Optional[int] = field(default=None)
    rate_limit_per_user: Optional[int] = field(default=None)
    recipients: Optional[List[User]] = field(converter=convert_list(User), default=None, repr=False)
    icon: Optional[str] = field(default=None, repr=False)
    owner_id: Optional[Snowflake] = field(converter=Snowflake, default=None)
    application_id: Optional[Snowflake] = field(converter=Snowflake, default=None, repr=False)
    parent_id: Optional[Snowflake] = field(converter=Snowflake, default=None)
    last_pin_timestamp: Optional[datetime] = field(
        converter=datetime.fromisoformat, default=None, repr=False
    )
    rtc_region: Optional[str] = field(default=None, repr=False)
    video_quality_mode: Optional[int] = field(default=None, repr=False)
    message_count: Optional[int] = field(default=None, repr=False)
    member_count: Optional[int] = field(default=None, repr=False)
    newly_created: Optional[int] = field(default=None, repr=False)
    thread_metadata: Optional[ThreadMetadata] = field(converter=ThreadMetadata, default=None)
    member: Optional[ThreadMember] = field(
        converter=ThreadMember, default=None, add_client=True, repr=False
    )
    default_auto_archive_duration: Optional[int] = field(default=None)
    permissions: Optional[Permissions] = field(
        converter=convert_int(Permissions), default=None, repr=False
    )
    flags: Optional[int] = field(default=None, repr=False)
    total_message_sent: Optional[int] = field(default=None, repr=False)
    default_thread_slowmode_delay: Optional[int] = field(default=None, repr=False)
    available_tags: Optional[List[Tags]] = field(
        converter=convert_list(Tags), default=None, add_client=True
    )
    applied_tags: Optional[List[Snowflake]] = field(converter=convert_list(Snowflake), default=None)
    default_reaction_emoji: Optional[Emoji] = field(converter=Emoji, default=None)

    def __attrs_post_init__(self):  # sourcery skip: last-if-guard
        if self._client:
            if channel := self._client.cache[Channel].get(self.id):
                if not self.recipients:
                    self.recipients = channel.recipients

    @property
    def guild_id(self) -> Optional[Snowflake]:
        """
        .. versionadded:: 4.4.0

        Attempts to get the guild ID the channel is in.

        :return: The ID of the guild this channel belongs to.
        :rtype: Optional[Snowflake]
        """

        if self._guild_id:
            return self._guild_id

        elif _id := self._extras.get("guild_id"):
            return Snowflake(_id)

        if not self._client:
            raise LibraryException(code=13)

        from .guild import Guild

        def check(channel: Channel):
            return self.id == channel.id

        for guild in self._client.cache[Guild].values.values():
            if len(search_iterable(guild.channels, check=check)) == 1:
                self._extras["guild_id"] = guild.id
                return guild.id

    @property
    def guild(self) -> Optional["Guild"]:
        """
        .. versionadded:: 4.4.0

        Attempts to get the guild the channel is in.

        :return: The guild this channel belongs to.
        :rtype: Guild
        """
        _id = self.guild_id
        from .guild import Guild

        return self._client.cache[Guild].get(_id, None) if _id else None

    @property
    def typing(self) -> Union[Awaitable, ContextManager]:
        """
        .. versionadded:: 4.3.2

        Manages the typing of the channel. Use with `await` or `async with`

        :return: A manager for typing
        :rtype: AsyncTypingContextManager
        """
        return AsyncTypingContextManager(self, self._client)

    @property
    def mention(self) -> str:
        """
        .. versionadded:: 4.1.0

        Returns a string that allows you to mention the given channel.

        :return: The string of the mentioned channel.
        :rtype: str
        """
        return f"<#{self.id}>"

    @property
    def voice_states(self) -> List["VoiceState"]:
        """
        .. versionadded:: 4.4.0

        Returns all voice states this channel has. Only applicable for voice channels.

        :rtype: List[VoiceState]
        """
        if self.type != ChannelType.GUILD_VOICE:
            raise LibraryException(
                code=14, message="Cannot only get voice states from a voice channel!"
            )

        if not self._client:
            raise LibraryException(code=13)

        from .gw import VoiceState

        states: List[VoiceState] = []

        data = self._client.cache[VoiceState].values.values()
        states.extend(state for state in data if state.channel_id == self.id)
        return states

    @property
    def created_at(self) -> datetime:
        """
        .. versionadded:: 4.4.0

        Returns when the channel was created.
        """
        return self.id.timestamp

    def history(
        self,
        start_at: Optional[Union[int, str, Snowflake, "Message"]] = MISSING,
        reverse: Optional[bool] = False,
        maximum: Optional[int] = inf,
        check: Optional[Callable[["Message"], Union[bool, Awaitable[bool]]]] = None,
    ) -> AsyncHistoryIterator:
        """
        .. versionadded:: 4.3.2

        :param Optional[Union[int, str, Snowflake, Message]] start_at: The message to begin getting the history from
        :param Optional[bool] reverse: Whether to only get newer message. Default False
        :param Optional[int] maximum: A set maximum of messages to get before stopping the iteration
        :param Optional[Callable[[Message], Union[bool, Awaitable[bool]]]] check: A custom check to ignore certain messages

        :return: An asynchronous iterator over the history of the channel
        :rtype: AsyncHistoryIterator
        """
        if not self._client:
            raise LibraryException(code=13)

        return AsyncHistoryIterator(
            self._client, self, start_at=start_at, reverse=reverse, maximum=maximum, check=check
        )

    async def send(
        self,
        content: Optional[str] = MISSING,
        *,
        tts: Optional[bool] = MISSING,
        attachments: Optional[List["Attachment"]] = MISSING,
        files: Optional[Union[File, List[File]]] = MISSING,
        embeds: Optional[Union["Embed", List["Embed"]]] = MISSING,
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
    ) -> "Message":  # noqa  # sourcery skip: dict-assign-update-to-union
        """
        .. versionadded:: 4.0.2

        Sends a message in the channel.

        :param Optional[str] content: The contents of the message as a string or string-converted value.
        :param Optional[bool] tts: Whether the message utilizes the text-to-speech Discord programme or not.
        :param Optional[Union[File, List[File]]] files:
            .. versionadded:: 4.2.0

            A file or list of files to be attached to the message.
        :param Optional[List[Attachment]] attachments:
            .. versionadded:: 4.3.0

            The attachments to attach to the message. Needs to be uploaded to the CDN first.
        :param Optional[Union[Embed, List[Embed]]] embeds: An embed, or list of embeds for the message.
        :param Optional[Union[AllowedMentions, dict]] allowed_mentions: The allowed mentions for the message.
        :param Optional[List[Sticker]] stickers:
            .. versionadded:: 4.3.0

            A list of stickers to send with your message. You can send up to 3 stickers per message.
        :param Optional[Union[ActionRow, Button, SelectMenu, List[Actionrow], List[Button], List[SelectMenu]]] components: A component, or list of components for the message.
        :return: The sent message as an object.
        :rtype: Message
        """

        if self.type == ChannelType.GUILD_FORUM:
            raise LibraryException(code=14, message="Cannot message a forum channel!")

        if not self._client:
            raise LibraryException(code=13)
        from ...client.models.component import _build_components
        from .message import Message

        _content: str = "" if content is MISSING else content
        _tts: bool = False if tts is MISSING else tts
        _attachments = [] if attachments is MISSING else [a._json for a in attachments]
        _allowed_mentions: dict = (
            {}
            if allowed_mentions is MISSING
            else allowed_mentions._json
            if isinstance(allowed_mentions, AllowedMentions)
            else allowed_mentions
        )
        _sticker_ids: list = (
            [] if stickers is MISSING else [str(sticker.id) for sticker in stickers]
        )
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

        if not files or files is MISSING:
            _files = []
        elif isinstance(files, list):
            _files = [file._json_payload(id) for id, file in enumerate(files)]
        else:
            _files = [files._json_payload(0)]
            files = [files]

        _files.extend(_attachments)

        payload = dict(
            content=_content,
            tts=_tts,
            attachments=_files,
            embeds=_embeds,
            allowed_mentions=_allowed_mentions,
            components=_components,
            sticker_ids=_sticker_ids,
        )

        res = await self._client.create_message(
            channel_id=int(self.id), payload=payload, files=files
        )

        # dumb hack, discord doesn't send the full author data
        author = {"id": None, "username": None, "discriminator": None}
        author.update(res["author"])
        res["author"] = author

        return Message(**res, _client=self._client)

    async def delete(self) -> None:
        """
        .. versionadded:: 4.0.2

        Deletes the channel.
        """
        if not self._client:
            raise LibraryException(code=13)
        await self._client.delete_channel(channel_id=int(self.id))

    async def modify(
        self,
        name: Optional[str] = MISSING,
        topic: Optional[str] = MISSING,
        bitrate: Optional[int] = MISSING,
        user_limit: Optional[int] = MISSING,
        rate_limit_per_user: Optional[int] = MISSING,
        position: Optional[int] = MISSING,
        permission_overwrites: Optional[List[Overwrite]] = MISSING,
        parent_id: Optional[int] = MISSING,
        nsfw: Optional[bool] = MISSING,
        archived: Optional[bool] = MISSING,
        auto_archive_duration: Optional[int] = MISSING,
        locked: Optional[bool] = MISSING,
        reason: Optional[str] = None,
    ) -> "Channel":  # sourcery skip: low-code-quality
        """
        .. versionadded:: 4.0.2

        Edits the channel.

        .. versionadded:: 4.2.0
            The fields ``archived``, ``auto_archive_duration`` and ``locked``.
            All require the provided channel to be a thread.

        :param Optional[str] name: The name of the channel, defaults to the current value of the channel
        :param Optional[str] topic: The topic of that channel, defaults to the current value of the channel
        :param Optional[int] bitrate: (voice channel only) The bitrate (in bits) of the voice channel, defaults to the current value of the channel
        :param Optional[int] user_limit: (voice channel only) Maximum amount of users in the channel, defaults to the current value of the channel
        :param Optional[int] rate_limit_per_user: Amount of seconds a user has to wait before sending another message (0-21600), defaults to the current value of the channel
        :param Optional[int] position: Sorting position of the channel, defaults to the current value of the channel
        :param Optional[int] parent_id: The id of the parent category for a channel, defaults to the current value of the channel
        :param Optional[bool] nsfw: Whether the channel is nsfw or not, defaults to the current value of the channel
        :param Optional[List[Overwrite]] permission_overwrites: The permission overwrites, if any
        :param Optional[bool] archived:
            .. versionadded:: 4.2.0

            Whether the thread is archived
        :param Optional[int] auto_archive_duration:
            .. versionadded:: 4.2.0

            The time after the thread is automatically archived. One of 60, 1440, 4320, 10080
        :param Optional[bool] locked:
            .. versionadded:: 4.2.0

            Whether the thread is locked
        :param Optional[str] reason: The reason for the edit
        :return: The modified channel as new object
        :rtype: Channel
        """
        if not self._client:
            raise LibraryException(code=13)
        _name = self.name if name is MISSING else name
        _topic = self.topic if topic is MISSING else topic
        _bitrate = self.bitrate if bitrate is MISSING else bitrate
        _user_limit = self.user_limit if user_limit is MISSING else user_limit
        _rate_limit_per_user = (
            self.rate_limit_per_user if rate_limit_per_user is MISSING else rate_limit_per_user
        )
        _position = self.position if position is MISSING else position
        _parent_id = (
            (int(self.parent_id) if self.parent_id else None)
            if parent_id is MISSING
            else int(parent_id)
        )
        _nsfw = self.nsfw if nsfw is MISSING else nsfw
        _permission_overwrites = (
            [overwrite._json for overwrite in permission_overwrites]
            if permission_overwrites is not MISSING
            else [overwrite._json for overwrite in self.permission_overwrites]
            if self.permission_overwrites
            else None
        )
        _type = self.type

        payload = dict(
            name=_name,
            type=_type,
            topic=_topic,
            bitrate=_bitrate,
            user_limit=_user_limit,
            rate_limit_per_user=_rate_limit_per_user,
            position=_position,
            parent_id=_parent_id,
            nsfw=_nsfw,
            permission_overwrites=_permission_overwrites,
        )

        if (
            archived is not MISSING or auto_archive_duration is not MISSING or locked is not MISSING
        ) and not self.thread_metadata:
            raise LibraryException(message="The specified channel is not a Thread!", code=12)

        if archived is not MISSING:
            payload["archived"] = archived
        if auto_archive_duration is not MISSING:
            payload["auto_archive_duration"] = auto_archive_duration
        if locked is not MISSING:
            payload["locked"] = locked

        res = await self._client.modify_channel(
            channel_id=int(self.id),
            reason=reason,
            payload=payload,
        )

        self.update(res)

        return self

    async def set_name(
        self,
        name: str,
        *,
        reason: Optional[str] = None,
    ) -> "Channel":
        """
        .. versionadded:: 4.1.0

        Sets the name of the channel.

        :param str name: The new name of the channel
        :param Optional[str] reason: The reason of the edit
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
        .. versionadded:: 4.1.0

        Sets the topic of the channel.

        :param str topic: The new topic of the channel
        :param Optional[str] reason: The reason of the edit
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
        .. versionadded:: 4.1.0

        Sets the bitrate of the channel.

        :param int bitrate: The new bitrate of the channel
        :param Optional[str] reason: The reason of the edit
        :return: The edited channel
        :rtype: Channel
        """

        if self.type != ChannelType.GUILD_VOICE:
            raise LibraryException(message="Bitrate is only available for VoiceChannels", code=12)

        return await self.modify(bitrate=bitrate, reason=reason)

    async def set_user_limit(
        self,
        user_limit: int,
        *,
        reason: Optional[str] = None,
    ) -> "Channel":
        """
        .. versionadded:: 4.1.0

        Sets the user_limit of the channel.

        :param int user_limit: The new user limit of the channel
        :param Optional[str] reason: The reason of the edit
        :return: The edited channel
        :rtype: Channel
        """

        if self.type != ChannelType.GUILD_VOICE:
            raise LibraryException(
                message="user_limit is only available for VoiceChannels", code=12
            )

        return await self.modify(user_limit=user_limit, reason=reason)

    async def set_rate_limit_per_user(
        self,
        rate_limit_per_user: int,
        *,
        reason: Optional[str] = None,
    ) -> "Channel":
        """
        .. versionadded:: 4.1.0

        Sets the amount of seconds a user has to wait before sending another message.

        :param int rate_limit_per_user: The new rate_limit_per_user of the channel (0-21600)
        :param Optional[str] reason: The reason of the edit
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
        .. versionadded:: 4.1.0

        Sets the position of the channel.

        :param int position: The new position of the channel
        :param Optional[str] reason: The reason of the edit
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
        .. versionadded:: 4.1.0

        Sets the parent_id of the channel.

        :param int parent_id: The new parent_id of the channel
        :param Optional[str] reason: The reason of the edit
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
        .. versionadded:: 4.1.0

        Sets the nsfw-flag of the channel.

        :param bool nsfw: The new nsfw-flag of the channel
        :param Optional[str] reason: The reason of the edit
        :return: The edited channel
        :rtype: Channel
        """

        return await self.modify(nsfw=nsfw, reason=reason)

    async def archive(
        self,
        archived: bool = True,
        *,
        reason: Optional[str] = None,
    ) -> "Channel":
        """
        .. versionadded:: 4.2.0

        Sets the archived state of the thread.

        :param bool archived: Whether the Thread is archived, defaults to True
        :param Optional[str] reason: The reason of the archiving
        :return: The edited channel
        :rtype: Channel
        """

        return await self.modify(archived=archived, reason=reason)

    async def set_auto_archive_duration(
        self,
        auto_archive_duration: int,
        *,
        reason: Optional[str] = None,
    ) -> "Channel":
        """
        .. versionadded:: 4.2.0

        Sets the time after the thread is automatically archived.

        :param int auto_archive_duration: The time after the thread is automatically archived. One of 60, 1440, 4320, 10080
        :param Optional[str] reason: The reason of the edit
        :return: The edited channel
        :rtype: Channel
        """

        return await self.modify(auto_archive_duration=auto_archive_duration, reason=reason)

    async def lock(
        self,
        locked: bool = True,
        *,
        reason: Optional[str] = None,
    ) -> "Channel":
        """
        .. versionadded:: 4.2.0

        Sets the locked state of the thread.

        :param bool locked: Whether the Thread is locked, defaults to True
        :param Optional[str] reason: The reason of the edit
        :return: The edited channel
        :rtype: Channel
        """

        return await self.modify(locked=locked, reason=reason)

    async def add_member(
        self,
        member_id: Union[int, Snowflake, "Member"],
    ) -> None:
        """
        .. versionadded:: 4.2.0

        This adds a member to the channel, if the channel is a thread.

        :param int member_id: The id of the member to add to the channel
        """
        if not self._client:
            raise LibraryException(code=13)
        if not self.thread_metadata:
            raise LibraryException(message="The Channel you specified is not a thread!", code=12)

        _member_id = (
            int(member_id) if isinstance(member_id, (int, Snowflake)) else int(member_id.id)
        )

        await self._client.add_member_to_thread(thread_id=int(self.id), user_id=_member_id)

    async def remove_member(
        self,
        member_id: Union[int, Snowflake, "Member"],
    ) -> None:
        """
        .. versionadded:: 4.3.0

        This removes a member of the channel, if the channel is a thread.

        :param int member_id: The id of the member to remove of the channel
        """
        if not self._client:
            raise LibraryException(code=13)
        if not self.thread_metadata:
            raise LibraryException(message="The Channel you specified is not a thread!", code=12)

        _member_id = (
            int(member_id) if isinstance(member_id, (int, Snowflake)) else int(member_id.id)
        )

        await self._client.remove_member_from_thread(thread_id=int(self.id), user_id=_member_id)

    async def pin_message(
        self,
        message_id: Union[int, Snowflake, "Message"],
    ) -> None:
        """
        .. versionadded:: 4.0.2

        Pins a message to the channel.

        :param Union[int, Snowflake, Message] message_id: The id of the message to pin
        """
        if not self._client:
            raise LibraryException(code=13)

        _message_id = (
            int(message_id) if isinstance(message_id, (int, Snowflake)) else int(message_id.id)
        )

        await self._client.pin_message(channel_id=int(self.id), message_id=_message_id)

    async def unpin_message(
        self,
        message_id: Union[int, Snowflake, "Message"],
    ) -> None:
        """
        .. versionadded:: 4.0.2

        Unpins a message from the channel.

        :param Union[int, Snowflake, Message] message_id: The id of the message to unpin
        """
        if not self._client:
            raise LibraryException(code=13)

        _message_id = (
            int(message_id) if isinstance(message_id, (int, Snowflake)) else int(message_id.id)
        )

        await self._client.unpin_message(channel_id=int(self.id), message_id=_message_id)

    async def publish_message(
        self,
        message_id: Union[int, Snowflake, "Message"],
    ) -> "Message":
        """
        .. versionadded:: 4.0.2

        Publishes (API calls it crossposts) a message in the channel to any that is followed by.

        :param Union[int, Snowflake, Message] message_id: The id of the message to publish
        :return: The message published
        :rtype: Message
        """
        if not self._client:
            raise LibraryException(code=13)
        from .message import Message

        _message_id = (
            int(message_id) if isinstance(message_id, (int, Snowflake)) else int(message_id.id)
        )

        res = await self._client.publish_message(channel_id=int(self.id), message_id=_message_id)

        return Message(**res, _client=self._client)

    async def get_pinned_messages(self) -> List["Message"]:
        """
        .. versionadded:: 4.0.2

        Get all pinned messages from the channel.

        :return: A list of pinned message objects.
        :rtype: List[Message]
        """
        if not self._client:
            raise LibraryException(code=13)
        from .message import Message

        res = await self._client.get_pinned_messages(int(self.id))
        return [Message(**message, _client=self._client) for message in res]

    async def get_message(
        self,
        message_id: Union[int, Snowflake],
    ) -> "Message":
        """
        .. versionadded:: 4.1.0

        Gets a message sent in that channel.

        :param Union[int, Snowflake] message_id: The ID of the message to get
        :return: The message as object
        :rtype: Message
        """
        res = await self._client.get_message(
            channel_id=int(self.id),
            message_id=int(message_id),
        )
        from .message import Message

        return Message(**res, _client=self._client)

    async def purge(
        self,
        amount: int,
        check: Optional[Callable[[Any], Union[bool, Awaitable[bool]]]] = MISSING,
        before: Optional[int] = MISSING,
        reason: Optional[str] = None,
        bulk: Optional[bool] = True,
        force_bulk: Optional[bool] = False,
    ) -> List["Message"]:
        """
        .. versionadded:: 4.1.0

        Purges a given amount of messages from a channel. You can specify a check function to exclude specific messages.

        .. warning:: Calling this method can lead to rate-limits when purging higher amounts of messages.

        .. code-block:: python

            def check_pinned(message):
                return not message.pinned  # This returns `True` only if the message is the message is not pinned
            await channel.purge(100, check=check_pinned)
            # This will delete the newest 100 messages that are not pinned in that channel

        :param int amount: The amount of messages to delete
        :param Optional[Callable[[Any], Union[bool, Awaitable[bool]]]] check:
            The function used to check if a message should be deleted.
            The message is only deleted if the check returns `True`
        :param Optional[int] before: An id of a message to purge only messages before that message
        :param Optional[bool] bulk:
            Whether to use the bulk delete endpoint for deleting messages. This only works for 14 days

            .. versionchanged:: 4.4.0
                Purge now automatically continues deleting messages even after the 14 days limit was hit. Check
                ``force_bulk`` for more information. If the 14 days span is exceeded the bot will encounter rate-limits
                more frequently.
        :param Optional[st] reason: The reason of the deletes
        :param Optional[bool] force_bulk:
            .. versionadded:: 4.4.0
                Whether to stop deleting messages when the 14 days bulk limit was hit, default ``False``
        :return: A list of the deleted messages
        :rtype: List[Message]
        """
        if not self._client:
            raise LibraryException(code=13)
        from .message import Message

        _before = None if before is MISSING else before
        _all = []

        async def normal_delete():
            nonlocal _before, _all, amount, check, reason
            while amount > 0:
                messages = [
                    Message(**res)
                    for res in await self._client.get_channel_messages(
                        channel_id=int(self.id),
                        limit=min(amount, 100),
                        before=_before,
                    )
                ]
                if not messages:
                    return _all

                amount -= min(amount, 100)
                messages2 = messages.copy()
                for message in messages2:
                    if (
                        message.flags & MessageFlags.EPHEMERAL
                        or message.flags & MessageFlags.LOADING
                        or not message.deletable
                    ):
                        messages.remove(message)
                        amount += 1
                        _before = int(message.id)
                    elif check is not MISSING:
                        _check = check(message)
                        if isawaitable(_check):
                            _check = await _check
                        if not _check:
                            messages.remove(message)
                            amount += 1
                            _before = int(message.id)

                for message in messages:  # show results faster
                    await self._client.delete_message(
                        channel_id=int(self.id),
                        message_id=int(message.id),
                        reason=reason,
                    )

                _all += messages

            return _all

        async def bulk_delete():
            nonlocal _before, _all, amount, check, reason

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
                if not messages:
                    return _all
                messages2 = messages.copy()
                for message in messages2:
                    if datetime.fromisoformat(str(message.timestamp)) < _allowed_time:
                        messages.remove(message)
                        _stop = True

                    elif (
                        message.flags & MessageFlags.EPHEMERAL
                        or message.flags & MessageFlags.LOADING
                        or not message.deletable
                    ):
                        messages.remove(message)
                        amount += 1
                        _before = int(message.id)
                    elif check is not MISSING:
                        _check = check(message)
                        if isawaitable(_check):
                            _check = await _check
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
                if not messages:
                    return _all
                amount -= amount
                messages2 = messages.copy()
                for message in messages2:
                    if datetime.fromisoformat(str(message.timestamp)) < _allowed_time:
                        messages.remove(message)
                        _stop = True
                    elif (
                        message.flags & MessageFlags.EPHEMERAL
                        or message.flags & MessageFlags.LOADING
                        or not message.deletable
                    ):
                        messages.remove(message)
                        amount += 1
                        _before = int(message.id)
                    elif check is not MISSING:
                        _check = check(message)
                        if isawaitable(_check):
                            _check = await _check
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
                if not messages:
                    return _all
                amount -= 1
                messages2 = messages.copy()
                for message in messages2:
                    if (
                        message.flags & MessageFlags.EPHEMERAL
                        or message.flags & MessageFlags.LOADING
                        or not message.deletable
                    ):
                        messages.remove(message)
                        amount += 1
                        _before = int(message.id)
                    elif check is not MISSING:
                        _check = check(message)
                        if isawaitable(_check):
                            _check = await _check
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
            return _all

        if bulk:
            await bulk_delete()
            if not force_bulk:
                await normal_delete()
            return _all

        await normal_delete()

        return _all

    async def create_thread(
        self,
        name: str,
        type: Optional[ChannelType] = ChannelType.PUBLIC_THREAD,
        auto_archive_duration: Optional[int] = MISSING,
        invitable: Optional[bool] = MISSING,
        message_id: Optional[Union[int, Snowflake, "Message"]] = MISSING,  # noqa
        reason: Optional[str] = None,
    ) -> "Channel":
        """
        .. versionadded:: 4.1.0

        Creates a thread in the Channel.

        :param str name: The name of the thread
        :param Optional[int] auto_archive_duration: duration in minutes to automatically archive the thread after recent activity, can be set to: 60, 1440, 4320, 10080
        :param Optional[ChannelType] type: The type of thread, defaults to public. ignored if creating thread from a message
        :param Optional[bool] invitable: Boolean to display if the Thread is open to join or private.
        :param Optional[Union[int, Snowflake, Message]] message_id: An optional message to create a thread from.
        :param Optional[str] reason: An optional reason for the audit log
        :return: The created thread
        :rtype: Channel
        """
        if not self._client:
            raise LibraryException(code=13)
        if type not in [
            ChannelType.ANNOUNCEMENT_THREAD,
            ChannelType.PUBLIC_THREAD,
            ChannelType.PRIVATE_THREAD,
        ]:
            raise LibraryException(message="type must be a thread type!", code=12)

        _auto_archive_duration = None if auto_archive_duration is MISSING else auto_archive_duration
        _invitable = None if invitable is MISSING else invitable
        _message_id = (
            None
            if message_id is MISSING
            else (
                int(message_id) if isinstance(message_id, (int, Snowflake)) else int(message_id.id)
            )
        )
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

    @property
    def url(self) -> str:
        """
        .. versionadded:: 4.2.0

        Returns the URL of the channel
        """
        _guild_id = self.guild_id if isinstance(self.guild_id, int) else "@me"
        return f"https://discord.com/channels/{_guild_id}/{self.id}"

    async def create_invite(
        self,
        max_age: Optional[int] = 86400,
        max_uses: Optional[int] = 0,
        temporary: Optional[bool] = False,
        unique: Optional[bool] = False,
        target_type: Optional["InviteTargetType"] = MISSING,
        target_user_id: Optional[int] = MISSING,
        target_application_id: Optional[int] = MISSING,
        reason: Optional[str] = None,
    ) -> "Invite":
        """
        Creates an invite for the channel

        :param Optional[int] max_age: Duration of invite in seconds before expiry, or 0 for never. between 0 and 604800 (7 days). Default 86400 (24h)
        :param Optional[int] max_uses: Max number of uses or 0 for unlimited. between 0 and 100. Default 0
        :param Optional[bool] temporary: Whether this invite only grants temporary membership. Default False
        :param Optional[bool] unique: If true, don't try to reuse a similar invite (useful for creating many unique one time use invites). Default False
        :param Optional[InviteTargetType] target_type: The type of target for this voice channel invite
        :param Optional[int] target_user_id: The id of the user whose stream to display for this invite, required if target_type is STREAM, the user must be streaming in the channel
        :param Optional[int] target_application_id: The id of the embedded application to open for this invite, required if target_type is EMBEDDED_APPLICATION, the application must have the EMBEDDED flag
        :param Optional[str] reason: The reason for the creation of the invite
        """

        if not self._client:
            raise LibraryException(code=13)

        payload = {
            "max_age": max_age,
            "max_uses": max_uses,
            "temporary": temporary,
            "unique": unique,
        }

        if (target_user_id is not MISSING and target_user_id) and (
            target_application_id is not MISSING and target_application_id
        ):
            raise LibraryException(
                message="target user id and target application are mutually exclusive!", code=12
            )

        elif (
            (target_user_id is not MISSING and target_user_id)
            or (target_application_id is not MISSING and target_application_id)
        ) and not target_type:
            raise LibraryException(
                message="you have to specify a target_type if you specify target_user-/target_application_id",
                code=12,
            )

        if target_user_id is not MISSING:
            payload["target_type"] = (
                target_type if isinstance(target_type, int) else target_type.value
            )
            payload["target_user_id"] = target_user_id

        if target_application_id is not MISSING:
            payload["target_type"] = (
                target_type if isinstance(target_type, int) else target_type.value
            )
            payload["target_application_id"] = target_application_id

        res = await self._client.create_channel_invite(
            channel_id=int(self.id),
            payload=payload,
            reason=reason,
        )

        from .guild import Invite

        return Invite(**res, _client=self._client)

    async def get_history(self, limit: int = 100) -> Optional[List["Message"]]:
        """
        .. versionadded:: 4.2.0

        .. deprecated:: 4.3.2
            Use the :meth:`.history` method instead

        Gets messages from the channel's history.

        :param int limit: The amount of messages to get. Default 100
        :return: A list of messages
        :rtype: List[Message]
        """

        warn(
            "This method has been deprecated in favour of the 'history' method.", DeprecationWarning
        )

        if not self._client:
            raise LibraryException(code=13)

        from .message import Message

        _messages: List[Message] = []
        _before: Optional[int] = None
        while limit > 100:
            _msgs = [
                Message(**res, _client=self._client)
                for res in await self._client.get_channel_messages(
                    channel_id=int(self.id),
                    limit=100,
                    before=_before,
                )
            ]
            limit -= 100
            if not _msgs:
                return _messages
            _before = int(_msgs[-1].id)

            for msg in _msgs:
                if msg in _messages:
                    return _messages
                else:
                    _messages.append(msg)

        if limit > 0:
            _msgs = [
                Message(**res, _client=self._client)
                for res in await self._client.get_channel_messages(
                    channel_id=int(self.id), limit=limit, before=_before
                )
            ]
            if not _msgs:
                return _messages
            for msg in _msgs:
                if msg in _messages:
                    return _messages
                else:
                    _messages.append(msg)

        return _messages

    async def get_webhooks(self) -> List[Webhook]:
        """
        .. versionadded:: 4.3.0

        Gets a list of webhooks of that channel
        """

        if not self._client:
            raise LibraryException(code=13)

        res = await self._client.get_channel_webhooks(int(self.id))
        return [Webhook(**_, _client=self._client) for _ in res]

    async def get_members(self) -> List[ThreadMember]:
        """
        .. versionadded:: 4.3.0

        Gets the list of thread members

        :return: The members of the thread.
        :rtype: List[ThreadMember]
        """
        if not self._client:
            raise LibraryException(code=13)
        if not self.thread_metadata:
            raise LibraryException(message="The Channel you specified is not a thread!", code=12)

        res = await self._client.list_thread_members(int(self.id))
        return [ThreadMember(**member, _client=self._client) for member in res]

    async def leave(self) -> None:
        """
        .. versionadded:: 4.3.0

        Removes the bot from the thread
        """
        if not self._client:
            raise LibraryException(code=13)
        if not self.thread_metadata:
            raise LibraryException(message="The Channel you specified is not a thread!", code=12)

        await self._client.leave_thread(int(self.id))

    async def join(self) -> None:
        """
        .. versionadded:: 4.3.0

        Add the bot to the thread
        """
        if not self._client:
            raise LibraryException(code=13)
        if not self.thread_metadata:
            raise LibraryException(message="The Channel you specified is not a thread!", code=12)

        await self._client.join_thread(int(self.id))

    async def create_tag(
        self,
        name: str,
        emoji_id: Optional[int] = MISSING,
        emoji_name: Optional[str] = MISSING,
    ) -> Tags:
        """
        .. versionadded:: 4.3.2

        Create a new tag.

        .. note::
            Can either have an emoji_id or an emoji_name, but not both.
            emoji_id is meant for custom emojis, emoji_name is meant for unicode emojis.

        :param str name: The name of the tag
        :param Optional[int] emoji_id: The ID of the emoji to use for the tag
        :param Optional[str] emoji_name: The name of the emoji to use for the tag
        :return: The create tag object
        :rtype: Tags
        """

        if not self._client:
            raise LibraryException(code=13)

        if self.type != ChannelType.GUILD_FORUM:
            raise LibraryException(code=14, message="Tags can only be created in forum channels!")

        if emoji_id is not MISSING and emoji_id and emoji_name and emoji_name is not MISSING:
            raise LibraryException(
                code=12, message="emoji_id and emoji_name are mutually exclusive"
            )

        payload = {"name": name}

        if emoji_id is not MISSING:
            payload["emoji_id"] = emoji_id
        if emoji_name is not MISSING:
            payload["emoji_name"] = emoji_name

        data = await self._client.create_tag(int(self.id), **payload)

        return Tags(**data)

    async def edit_tag(
        self,
        tag_id: Union[int, str, Snowflake, Tags],  # discord, why :hollow:
        name: str,
        emoji_name: Optional[str] = MISSING,
        emoji_id: Optional[int] = MISSING,
    ) -> "Tags":
        """
        .. versionadded:: 4.3.2

        Edits a tag

        .. note::
            Can either have an emoji_id or an emoji_name, but not both.
            emoji_id is meant for custom emojis, emoji_name is meant for unicode emojis.

        :param Union[int, str, Snowflake, Tags] tag_id: The ID of the tag to edit
        :param str name: The new name of the tag
        :param Optional[int] emoji_id: The ID of the emoji to use for the tag
        :param Optional[int] emoji_name: The name of the emoji to use for the tag
        :return: The modified tag
        :rtype: Tags
        """
        _tag_id = int(tag_id.id) if isinstance(tag_id, Tags) else int(tag_id)

        if emoji_id is not MISSING and emoji_id and emoji_name and emoji_name is not MISSING:
            raise LibraryException(
                code=12, message="emoji_id and emoji_name are mutually exclusive"
            )

        if self.type != ChannelType.GUILD_FORUM:
            raise LibraryException(code=14, message="Tags can only be created in forum channels!")

        payload = {"name": name}

        if emoji_id is not MISSING:
            payload["emoji_id"] = emoji_id
        if emoji_name is not MISSING:
            payload["emoji_name"] = emoji_name

        data = await self._client.edit_tag(int(self.id), _tag_id, **payload)

        return Tags(**data)

    async def delete_tag(
        self, tag_id: Union[int, str, Snowflake, Tags]  # discord, why :hollow:
    ) -> None:
        """
        .. versionadded:: 4.3.2

        Deletes a tag

        :param Union[int, str, Snowflake, Tags] tag_id: The ID of the Tag
        """
        if self.type != ChannelType.GUILD_FORUM:
            raise LibraryException(code=14, message="Tags can only be created in forum channels!")

        _tag_id = int(tag_id.id) if isinstance(tag_id, Tags) else int(tag_id)

        return await self._client.delete_tag(int(self.id), _tag_id)

    async def create_forum_post(
        self,
        name: str,
        content: Union[
            dict, "Message", str, "Attachment", List["Attachment"]
        ],  # overkill but why not
        auto_archive_duration: Optional[int] = MISSING,
        applied_tags: Union[List[str], List[int], List[Tags], int, str, Tags] = MISSING,
        files: Optional[List[File]] = MISSING,
        rate_limit_per_user: Optional[int] = MISSING,
        reason: Optional[str] = None,
    ) -> "Channel":  # sourcery skip: low-code-quality
        """
        .. versionadded:: 4.3.2

        Creates a new post inside a forum channel

        :param str name: The name of the thread
        :param Optional[int] auto_archive_duration: duration in minutes to automatically archive the thread after recent activity, can be set to: 60, 1440, 4320, 10080
        :param Union[dict, Message, str, Attachment, List[Attachment]] content: The content to send as first message.
        :param Union[List[str], List[int], List[Tags], int, str, Tags] applied_tags: Tags to give to the created thread
        :param Optional[List[File]] files: An optional list of files to send attached to the message.
        :param Optional[int] rate_limit_per_user: Seconds a user has to wait before sending another message (0 to 21600), if given.
        :param Optional[str] reason: An optional reason for the audit log
        :returns: A channel of type :attr:`ChannelType.PUBLIC_THREAD`
        :rtype: Channel
        """

        if self.type != ChannelType.GUILD_FORUM:
            raise LibraryException(code=14, message="Cannot create a post outside a forum channel")

        if not self._client:
            raise LibraryException(code=13)

        from .message import Attachment

        _top_payload: dict = {
            "name": name,
            "reason": reason,
            "rate_limit_per_user": rate_limit_per_user
            if rate_limit_per_user is not MISSING
            else None,
            "auto_archive_duration": auto_archive_duration
            if auto_archive_duration is not MISSING
            else None,
        }

        from .message import Message

        __files = [] if files is MISSING else files

        if isinstance(content, dict):  # just assume they know what they're doing
            _content = content

        elif isinstance(content, Message):
            _content = content._json
            if content.attachments and any(attach.id is None for attach in content.attachments):
                for attach in content.attachments:
                    _data = await attach.download()

                    __files.append(File(attach.filename, _data))

                if not __files or __files is MISSING:
                    _files = []
                elif isinstance(__files, list):
                    _files = [file._json_payload(id) for id, file in enumerate(__files)]
                else:
                    _files = [__files._json_payload(0)]
                    __files = [__files]

                _content["attachments"] = _files

        elif isinstance(content, Attachment):
            if content.id:
                _content: dict = {"attachments": [content._json]}
            else:
                data = await content.download()

                __files.append(File(content.name, data))

            if not __files or __files is MISSING:
                _files = []
            elif isinstance(__files, list):
                _files = [file._json_payload(id) for id, file in enumerate(__files)]
            else:
                _files = [__files._json_payload(0)]
                __files = [__files]

            _content: dict = {"attachments": [_files]}

        elif isinstance(content, list):
            _content = {"attachments": []}
            if any(not isinstance(item, Attachment) for item in content):
                raise LibraryException(code=12)

            attach: Attachment
            for attach in content:
                if attach.id:
                    _content["attachments"].append(attach._json)

                else:
                    _data = await attach.download()

                    __files.append(File(attach.filename, _data))

            if not __files or __files is MISSING:
                _files = []
            elif isinstance(__files, list):
                _files = [file._json_payload(id) for id, file in enumerate(__files)]
            else:
                _files = [__files._json_payload(0)]
                __files = [__files]

            _content["attachments"].extend(_files)

        else:
            _content: dict = {"content": content}

        _top_payload["files"] = __files
        _top_payload["message"] = _content

        if applied_tags is not MISSING:
            _tags = []
            if isinstance(applied_tags, list):
                for tag in applied_tags:
                    if isinstance(tag, Tags):
                        _tags.append(str(tag.id))
                    else:
                        _tags.append(str(tag))

            elif isinstance(applied_tags, Tags):
                _tags.append(str(applied_tags.id))
            else:
                _tags.append(str(applied_tags))
        else:
            _tags = []

        _top_payload["applied_tags"] = _tags

        data = await self._client.create_thread_in_forum(int(self.id), **_top_payload)

        return Channel(**data, _client=self._client)

    async def get_permissions_for(self, member: "Member") -> Permissions:
        """
        .. versionadded:: 4.3.2

        Returns the permissions of the member in this specific channel.

        .. note::
            The permissions returned by this function take into account role and
            user overwrites that can be assigned to channels or categories. If you
            don't need these overwrites, look into :meth:`.Member.get_guild_permissions`.

        :param Member member: The member to get the permissions from
        :return: Permissions of the member in this channel
        :rtype: Permissions
        """
        if not self.guild_id:
            return Permissions.DEFAULT

        permissions = await member.get_guild_permissions(self.guild_id)

        if Permissions.ADMINISTRATOR in permissions:
            return Permissions.ALL

        # @everyone role overwrites
        from interactions.utils.utils import search_iterable

        if overwrite_everyone := search_iterable(
            self.permission_overwrites, lambda overwrite: int(overwrite.id) == int(self.guild_id)
        ):
            permissions &= ~int(overwrite_everyone[0].deny)
            permissions |= int(overwrite_everyone[0].allow)

        # Apply role specific overwrites
        allow, deny = 0, 0
        for role_id in member.roles:
            if overwrite_role := search_iterable(
                self.permission_overwrites, lambda overwrite: int(overwrite.id) == int(role_id)
            ):
                allow |= int(overwrite_role[0].allow)
                deny |= int(overwrite_role[0].deny)

        if deny:
            permissions &= ~deny
        if allow:
            permissions |= allow

        # Apply member specific overwrites
        if overwrite_member := search_iterable(  # sourcery
            self.permission_overwrites, lambda overwrite: int(overwrite.id) == int(member.id)
        ):
            permissions &= ~int(overwrite_member[0].deny)
            permissions |= int(overwrite_member[0].allow)

        return Permissions(permissions)

    async def add_permission_overwrite(
        self,
        id: Union[int, str, Snowflake, User, Role],
        type: Optional[Literal[0, 1, "0", "1"]] = MISSING,
        allow: Optional[Union[int, Permissions, str]] = MISSING,
        deny: Optional[Union[int, Permissions, str]] = MISSING,
        reason: Optional[str] = None,
    ) -> "Channel":
        """
        .. versionadded:: 4.4.0

        Adds a permission overwrite to the channel.

        :param Union[int, str, Snowflake, User, Role] id: The ID of the User/Role to create the overwrite on.
        :param Optional[Literal[0, 1, "0", "1"]] type: The type of the overwrite. 0 for Role 1 for User.
        :param Optional[Union[int, Permissions, str]] allow: Permissions to allow
        :param Optional[Union[int, Permissions, str]] deny: Permissions to deny
        :param Optional[str] reason: The reason to be shown in the audit log
        :return: The updated channel
        :rtype: Channel
        """

        if not deny and not allow:
            raise LibraryException(message="Either allow or deny must be specified.", code=12)

        overwrites = self.permission_overwrites or []

        if isinstance(id, (User, Role)):
            _id = int(id.id)
            _type = 0 if isinstance(id, Role) else 1
        else:
            _id = int(id)
            _type = type

        if _type is MISSING:
            raise LibraryException(12, "Please set the type of the overwrite!")

        overwrites.append(Overwrite(id=_id, type=_type, allow=allow, deny=deny))

        return await self.modify(permission_overwrites=overwrites, reason=reason)

    async def add_permission_overwrites(
        self, overwrites: Iterable[Overwrite], reason: Optional[str] = None
    ) -> "Channel":
        """
        .. versionadded:: 4.4.0

        Add multiple overwrites to the channel.

        :param Iterable[Overwrite] overwrites: The overwrites to add to the channel.
        :param Optional[str] reason: The reason to be shown in the audit log
        :return: The updated channel
        :rtype: Channel
        """

        _overwrites = self.permission_overwrites or []
        _overwrites.extend(overwrites)
        return await self.modify(permission_overwrites=_overwrites, reason=reason)

    async def overwrite_permission_overwrites(
        self, overwrites: Iterable[Overwrite], reason: Optional[str] = None
    ) -> "Channel":
        """
        .. versionadded:: 4.4.0

        Overwrites the overwrites of the channel with new overwrites.

        :param Iterable[Overwrite] overwrites: The overwrites to add to the channel.
        :param Optional[str] reason: The reason to be shown in the audit log
        :return: The updated channel
        :rtype: Channel
        """

        return await self.modify(permission_overwrites=list(overwrites), reason=reason)

    async def remove_permission_overwrite_for(
        self,
        id: Union[int, str, Snowflake, User, Role, Overwrite],
        reason: Optional[str] = None,
    ) -> "Channel":
        """
        .. versionadded:: 4.4.0

        Removes the overwrite for the given ID.

        :param Union[int, str, Snowflake, User, Role, Overwrite] id: The ID of the User/Role to create the overwrite on.
        :param Optional[str] reason: The reason to be shown in the audit log
        :return: The updated channel
        :rtype: Channel
        """
        _id = int(id.id) if isinstance(id, (User, Role, Overwrite)) else int(id)

        if not self.permission_overwrites:
            raise LibraryException(12, message="There are no permission overwrites!")

        try:
            val = search_iterable(self.permission_overwrites, check=lambda o: o.id == _id)[0]
        except IndexError as e:
            raise LibraryException(12, "Could not find an overwrite with the given ID!") from e

        self.permission_overwrites.remove(val)
        return await self.modify(permission_overwrites=self.permission_overwrites, reason=reason)


@define()
class Thread(Channel):
    """
    .. versionadded:: 4.0.2

    An object representing a thread.

    .. note::
        This is a derivation of the base Channel, since a
        thread can be its own event.
    """

    ...
