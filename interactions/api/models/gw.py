from datetime import datetime
from typing import List, Optional, Union

from ...client.models.component import ActionRow, Button, SelectMenu, _build_components
from .channel import Channel, ThreadMember
from .member import Member
from .message import Embed, Emoji, Message, MessageInteraction, Sticker
from .misc import MISSING, ClientStatus, DictSerializerMixin, File, Snowflake
from .presence import PresenceActivity
from .role import Role
from .user import User


class ApplicationCommandPermissions(DictSerializerMixin):
    """
    A class object representing the gateway event ``APPLICATION_COMMAND_PERMISSIONS_UPDATE``.

    .. note:: This is undocumented by the Discord API, so these attribute docs may or may not be finalised.

    :ivar Snowflake application_id: The application ID associated with the event.
    :ivar Snowflake guild_id: The guild ID associated with the event.
    :ivar Snowflake id: The ID of the command associated with the event. (?)
    :ivar List[Permission] permissions: The updated permissions of the associated command/event.
    """

    __slots__ = ("_json", "application_id", "guild_id", "id", "permissions", "_client")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.application_id = (
            Snowflake(self.application_id) if self._json.get("application_id") else None
        )
        self.guild_id = Snowflake(self.guild_id) if self._json.get("guild_id") else None
        self.id = Snowflake(self.id) if self._json.get("id") else None
        # TODO: fix the circular import hell from this.
        # self.permissions = (
        #     [
        #         Permission(**_permission) if isinstance(_permission, dict) else _permission
        #         for _permission in self._json.get("permissions")
        #     ]
        #     if self._json.get("permissions")
        #     else None
        # )


class ChannelPins(DictSerializerMixin):
    """
    A class object representing the gateway event ``CHANNEL_PINS_UPDATE``.

    :ivar Snowflake guild_id: The guild ID of the event.
    :ivar Snowflake channel_id: The channel ID of the event.
    :ivar datetime last_pin_timestamp: The time that the event took place.
    """

    __slots__ = ("_json", "guild_id", "channel_id", "last_pin_timestamp")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.guild_id = Snowflake(self.guild_id) if self._json.get("guild_id") else None
        self.channel_id = Snowflake(self.channel_id) if self._json.get("channel_id") else None
        self.last_pin_timestamp = (
            datetime.fromisoformat(self._json.get("last_pin_timestamp"))
            if self._json.get("last_pin_timestamp")
            else None
        )


class EmbeddedActivity(DictSerializerMixin):
    """
    A class object representing the event ``EMBEDDED_ACTIVITY_UPDATE``.

    .. note::
        This is entirely undocumented by the API.

    :ivar List[Snowflake] users: The list of users of the event.
    :ivar Snowflake guild_id: The guild ID of the event.
    :ivar PresenceActivity embedded_activity: The embedded presence activity of the associated event.
    :ivar Snowflake channel_id: The channel ID of the event.
    """

    __slots__ = ("_json", "users", "guild_id", "embedded_activity", "channel_id")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.users = (
            [Snowflake(user) for user in self._json.get("users")]
            if self._json.get("users")
            else None
        )
        self.guild_id = Snowflake(self.guild_id) if self._json.get("guild_id") else None
        self.embedded_activity = (
            PresenceActivity(**self.embedded_activity)
            if self._json.get("embedded_activity")
            else None
        )
        self.channel_id = Snowflake(self.channel_id) if self._json.get("channel_id") else None


class GuildBan(DictSerializerMixin):
    """
    A class object representing the gateway event ``GUILD_BAN_ADD``.

    :ivar Snowflake guild_id: The guild ID of the event.
    :ivar User user: The user of the event.
    """

    __slots__ = ("_json", "guild_id", "user", "_client")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.guild_id = Snowflake(self.guild_id) if self._json.get("guild_id") else None
        self.user = User(**self.user) if self._json.get("user") else None


class GuildEmojis(DictSerializerMixin):
    """
    A class object representing the gateway event ``GUILD_EMOJIS_UPDATE``.

    :ivar Snowflake guild_id: The guild ID of the event.
    :ivar List[Emoji] emojis: The emojis of the event.
    """

    __slots__ = ("_json", "guild_id", "emojis")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.guild_id = Snowflake(self.guild_id) if self._json.get("guild_id") else None
        self.emojis = (
            [Emoji(**emoji) for emoji in self.emojis] if self._json.get("emojis") else None
        )


class GuildIntegrations(DictSerializerMixin):
    """
    A class object representing the gateway event ``GUILD_INTEGRATIONS_UPDATE``.

    :ivar Snowflake guild_id: The guild ID of the event.
    """

    __slots__ = ("_json", "guild_id")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.guild_id = Snowflake(self.guild_id) if self._json.get("guild_id") else None


class GuildJoinRequest(DictSerializerMixin):
    """
    A class object representing the gateway events ``GUILD_JOIN_REQUEST_CREATE``, ``GUILD_JOIN_REQUEST_UPDATE``, and ``GUILD_JOIN_REQUEST_DELETE``

    .. note::
        This is entirely undocumented by the API.

    :ivar Snowflake user_id: The user ID of the event.
    :ivar Snowflake guild_id: The guild ID of the event.
    """

    __slots__ = ("_json", "user_id", "guild_id")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_id = Snowflake(self.user_id) if self._json.get("user_id") else None
        self.guild_id = Snowflake(self.guild_id) if self._json.get("guild_id") else None


class GuildMember(DictSerializerMixin):
    """
    A class object representing the gateway events ``GUILD_MEMBER_ADD``, ``GUILD_MEMBER_UPDATE`` and ``GUILD_MEMBER_REMOVE``.

    :ivar Snowflake guild_id: The guild ID of the event.
    :ivar Optional[List[Role]] roles?: The roles of the event.
    :ivar Optional[User] user?: The user of the event.
    :ivar Optional[str] nick?: The nickname of the user of the event.
    :ivar Optional[str] avatar?: The avatar URL of the user of the event.
    :ivar Optional[datetime] joined_at?: The time that the user of the event joined at.
    :ivar Optional[datetime] premium_since?: The time that the user of the event has since had "premium."
    :ivar Optional[bool] deaf?: Whether the member of the event is deafened or not.
    :ivar Optional[bool] mute?: Whether the member of the event is muted or not.
    :ivar Optional[bool] pending?: Whether the member of the event is still pending -- pass membership screening -- or not.
    """

    __slots__ = (
        "_json",
        "_client",
        "guild_id",
        "roles",
        "user",
        "nick",
        "avatar",
        "joined_at",
        "premium_since",
        "is_pending",  # TODO: investigate what this is.
        "communication_disabled_until",  # TODO: investigate what this is.
        "deaf",
        "mute",
        "pending",
        "hoisted_role",  # TODO: investigate what this is.
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.guild_id = Snowflake(self.guild_id) if self._json.get("guild_id") else None
        self.user = User(**self.user) if self._json.get("user") else None
        self.joined_at = (
            datetime.fromisoformat(self._json.get("joined_at"))
            if self._json.get("joined_at")
            else None
        )
        self.premium_since = (
            datetime.fromisoformat(self._json.get("premium_since"))
            if self._json.get("premium_since")
            else None
        )

    @property
    def id(self) -> Snowflake:
        """
        Returns the ID of the user.

        :return: The ID of the user
        :rtype: Snowflake
        """
        return self.user.id if self.user else None

    @property
    def mention(self) -> str:
        """
        Returns a string that allows you to mention the given member.

        :return: The string of the mentioned member.
        :rtype: str
        """
        return f"<@!{self.user.id}>" if self.nick else f"<@{self.user.id}>"

    async def ban(
        self,
        reason: Optional[str] = None,
        delete_message_days: Optional[int] = 0,
    ) -> None:
        """
        Bans the member from a guild.

        :param reason?: The reason of the ban
        :type reason: Optional[str]
        :param delete_message_days?: Number of days to delete messages, from 0 to 7. Defaults to 0
        :type delete_message_days: Optional[int]
        """
        await self._client.create_guild_ban(
            guild_id=int(self.guild_id),
            user_id=int(self.user.id),
            reason=reason,
            delete_message_days=delete_message_days,
        )

    async def kick(
        self,
        reason: Optional[str] = None,
    ) -> None:
        """
        Kicks the member from a guild.

        :param reason?: The reason for the kick
        :type reason: Optional[str]
        """
        if not self._client:
            raise AttributeError("HTTPClient not found!")
        await self._client.create_guild_kick(
            guild_id=int(self.guild_id),
            user_id=int(self.user.id),
            reason=reason,
        )

    async def add_role(
        self,
        role: Union[Role, int],
        reason: Optional[str],
    ) -> None:
        """
        This method adds a role to a member.

        :param role: The role to add. Either ``Role`` object or role_id
        :type role: Union[Role, int]
        :param reason?: The reason why the roles are added
        :type reason: Optional[str]
        """
        if not self._client:
            raise AttributeError("HTTPClient not found!")
        if isinstance(role, Role):
            await self._client.add_member_role(
                guild_id=int(self.guild_id),
                user_id=int(self.user.id),
                role_id=int(role.id),
                reason=reason,
            )
        else:
            await self._client.add_member_role(
                guild_id=int(self.guild_id),
                user_id=int(self.user.id),
                role_id=role,
                reason=reason,
            )

    async def remove_role(
        self,
        role: Union[Role, int],
        reason: Optional[str],
    ) -> None:
        """
        This method removes a role from a member.

        :param role: The role to remove. Either ``Role`` object or role_id
        :type role: Union[Role, int]
        :param reason?: The reason why the roles are removed
        :type reason: Optional[str]
        """
        if not self._client:
            raise AttributeError("HTTPClient not found!")
        if isinstance(role, Role):
            await self._client.remove_member_role(
                guild_id=int(self.guild_id),
                user_id=int(self.user.id),
                role_id=int(role.id),
                reason=reason,
            )
        else:
            await self._client.remove_member_role(
                guild_id=int(self.guild_id),
                user_id=int(self.user.id),
                role_id=role,
                reason=reason,
            )

    async def send(
        self,
        content: Optional[str] = MISSING,
        *,
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
        tts: Optional[bool] = MISSING,
        files: Optional[Union[File, List[File]]] = MISSING,
        embeds: Optional[Union[Embed, List[Embed]]] = MISSING,
        allowed_mentions: Optional[MessageInteraction] = MISSING,
    ) -> Message:
        """
        Sends a DM to the member.

        :param content?: The contents of the message as a string or string-converted value.
        :type content: Optional[str]
        :param components?: A component, or list of components for the message.
        :type components: Optional[Union[ActionRow, Button, SelectMenu, List[Actionrow], List[Button], List[SelectMenu]]]
        :param tts?: Whether the message utilizes the text-to-speech Discord programme or not.
        :type tts: Optional[bool]
        :param files?: A file or list of files to be attached to the message.
        :type files: Optional[Union[File, List[File]]]
        :param embeds?: An embed, or list of embeds for the message.
        :type embeds: Optional[Union[Embed, List[Embed]]]
        :param allowed_mentions?: The message interactions/mention limits that the message can refer to.
        :type allowed_mentions: Optional[MessageInteraction]
        :return: The sent message as an object.
        :rtype: Message
        """
        if not self._client:
            raise AttributeError("HTTPClient not found!")

        _content: str = "" if content is MISSING else content
        _tts: bool = False if tts is MISSING else tts
        # _file = None if file is None else file
        # _attachments = [] if attachments else None
        _embeds: list = (
            []
            if not embeds or embeds is MISSING
            else ([embed._json for embed in embeds] if isinstance(embeds, list) else [embeds._json])
        )
        _allowed_mentions: dict = {} if allowed_mentions is MISSING else allowed_mentions

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

        payload = Message(
            content=_content,
            tts=_tts,
            attachments=_files,
            embeds=_embeds,
            components=_components,
            allowed_mentions=_allowed_mentions,
        )

        channel = Channel(**await self._client.create_dm(recipient_id=int(self.user.id)))
        res = await self._client.create_message(
            channel_id=int(channel.id), payload=payload._json, files=files
        )

        return Message(**res, _client=self._client)

    async def modify(
        self,
        nick: Optional[str] = MISSING,
        roles: Optional[List[int]] = MISSING,
        mute: Optional[bool] = MISSING,
        deaf: Optional[bool] = MISSING,
        channel_id: Optional[int] = MISSING,
        communication_disabled_until: Optional[datetime.isoformat] = MISSING,
        reason: Optional[str] = None,
    ) -> "GuildMember":
        """
        Modifies the member of a guild.

        :param nick?: The nickname of the member
        :type nick: Optional[str]
        :param roles?: A list of all role ids the member has
        :type roles: Optional[List[int]]
        :param mute?: whether the user is muted in voice channels
        :type mute: Optional[bool]
        :param deaf?: whether the user is deafened in voice channels
        :type deaf: Optional[bool]
        :param channel_id?: id of channel to move user to (if they are connected to voice)
        :type channel_id: Optional[int]
        :param communication_disabled_until?: when the user's timeout will expire and the user will be able to communicate in the guild again (up to 28 days in the future)
        :type communication_disabled_until: Optional[datetime.isoformat]
        :param reason?: The reason of the modifying
        :type reason: Optional[str]
        :return: The modified member object
        :rtype: Member
        """
        if not self._client:
            raise AttributeError("HTTPClient not found!")
        payload = {}
        if nick is not MISSING:
            payload["nick"] = nick

        if roles is not MISSING:
            payload["roles"] = roles

        if channel_id is not MISSING:
            payload["channel_id"] = channel_id

        if mute is not MISSING:
            payload["mute"] = mute

        if deaf is not MISSING:
            payload["deaf"] = deaf

        if communication_disabled_until is not MISSING:
            payload["communication_disabled_until"] = communication_disabled_until

        res = await self._client.modify_member(
            user_id=int(self.user.id),
            guild_id=int(self.guild_id),
            payload=payload,
            reason=reason,
        )
        return GuildMember(**res, _client=self._client, guild_id=self.guild_id)

    async def add_to_thread(
        self,
        thread_id: int,
    ) -> None:
        """
        Adds the member to a thread.

        :param thread_id: The id of the thread to add the member to
        :type thread_id: int
        """
        if not self._client:
            raise AttributeError("HTTPClient not found!")
        await self._client.add_member_to_thread(
            user_id=int(self.user.id),
            thread_id=thread_id,
        )


class GuildMembers(DictSerializerMixin):
    """
    A class object representing the gateway event ``GUILD_MEMBERS_CHUNK``.

    :ivar Snowflake guild_id: The guild ID of the event.
    :ivar List[GuildMember] members: The members of the event.
    :ivar int chunk_index: The current chunk index of the event.
    :ivar int chunk_count: The total chunk count of the event.
    :ivar list not_found: A list of not found members in the event if an invalid request was made.
    :ivar List[PresenceActivity] presences: A list of presences in the event.
    :ivar str nonce: The "nonce" of the event.
    """

    __slots__ = (
        "_json",
        "guild_id",
        "members",
        "chunk_index",
        "chunk_count",
        "not_found",
        "presences",
        "nonce",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.guild_id = Snowflake(self.guild_id) if self._json.get("guild_id") else None
        self.members = (
            [GuildMember(**member, guild_id=self.guild_id) for member in self.members]
            if self._json.get("members")
            else None
        )
        self.presences = (
            [PresenceActivity(**presence) for presence in self.presences]
            if self._json.get("presences")
            else None
        )


class GuildRole(DictSerializerMixin):
    """
    A class object representing the gateway events ``GUILD_ROLE_CREATE``, ``GUILD_ROLE_UPDATE`` and ``GUILD_ROLE_DELETE``.

    :ivar Snowflake guild_id: The guild ID of the event.
    :ivar Role role: The role of the event.
    :ivar Optional[Snowflake] role_id?: The role ID of the event.
    """

    __slots__ = (
        "_json",
        "guild_id",
        "role",
        "role_id",
        "_client",
        "guild_hashes",  # TODO: investigate what this is.
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.guild_id = Snowflake(self.guild_id) if self._json.get("guild_id") else None
        self.role_id = Snowflake(self.role_id) if self._json.get("role_id") else None
        self.role = Role(**self.role) if self._json.get("role") else None


class GuildStickers(DictSerializerMixin):
    """
    A class object representing the gateway event ``GUILD_STICKERS_UPDATE``.

    :ivar Snowflake guild_id: The guild ID of the event.
    :ivar List[Sticker] stickers: The stickers of the event.
    """

    __slots__ = ("_json", "guild_id", "stickers")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.guild_id = Snowflake(self.guild_id) if self._json.get("guild_id") else None
        self.stickers = (
            [Sticker(**sticker) for sticker in self.stickers]
            if self._json.get("stickers")
            else None
        )


class Integration(DictSerializerMixin):
    """
    A class object representing the gateway events ``INTEGRATION_CREATE``, ``INTEGRATION_UPDATE`` and ``INTEGRATION_DELETE``.

    .. note::
        The documentation of this event is the same as :class:`interactions.api.models.guild.Guild`.
        The only key missing attribute is ``guild_id``. Likewise, the documentation
        below reflects this.

    :ivar Snowflake id: The ID of the event.
    :ivar str name: The name of the event.
    :ivar str type: The type of integration in the event.
    :ivar bool enabled: Whether the integration of the event is enabled or not.
    :ivar bool syncing: Whether the integration of the event is syncing or not.
    :ivar Snowflake role_id: The role ID that the integration in the event uses for "subscribed" users.
    :ivar bool enable_emoticons: Whether emoticons of the integration's event should be enabled or not.
    :ivar int expire_behavior: The expiration behavior of the integration of the event.
    :ivar int expire_grace_period: The "grace period" of the integration of the event when expired -- how long it can still be used.
    :ivar User user: The user of the event.
    :ivar Any account: The account of the event.
    :ivar datetime synced_at: The time that the integration of the event was last synced.
    :ivar int subscriber_count: The current subscriber count of the event.
    :ivar bool revoked: Whether the integration of the event was revoked for use or not.
    :ivar Application application: The application used for the integration of the event.
    :ivar Snowflake guild_id: The guild ID of the event.
    """

    __slots__ = (
        "_json",
        "id",
        "name",
        "type",
        "enabled",
        "syncing",
        "role_id",
        "enable_emoticons",
        "expire_behavior",
        "expire_grace_period",
        "user",
        "account",
        "synced_at",
        "subscriber_count",
        "revoked",
        "application",
        "guild_id",
        # TODO: Document these when Discord does.
        "guild_hashes",
        "application_id",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = Snowflake(self.id) if self._json.get("id") else None
        self.role_id = Snowflake(self.role_id) if self._json.get("role_id") else None
        self.guild_id = Snowflake(self.guild_id) if self._json.get("guild_id") else None


class Presence(DictSerializerMixin):
    """
    A class object representing the gateway event ``PRESENCE_UPDATE``.

    :ivar User user: The user of the event.
    :ivar Snowflake guild_id: The guild ID of the event.
    :ivar str status: The status of the event.
    :ivar List[PresenceActivity] activities: The activities of the event.
    :ivar ClientStatus client_status: The client status across platforms in the event.
    """

    __slots__ = ("_json", "user", "guild_id", "status", "activities", "client_status", "_client")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.guild_id = Snowflake(self.guild_id) if self._json.get("guild_id") else None
        self.user = User(**self.user) if self._json.get("user") else None
        self.activities = (
            [PresenceActivity(**activity) for activity in self.activities]
            if self._json.get("activities")
            else None
        )
        self.client_status = (
            ClientStatus(**self.client_status) if self._json.get("client_status") else None
        )


class MessageReaction(DictSerializerMixin):
    """
    A class object representing the gateway event ``MESSAGE_REACTION_ADD``.

    :ivar Optional[Snowflake] user_id?: The user ID of the event.
    :ivar Snowflake channel_id: The channel ID of the event.
    :ivar Snowflake message_id: The message ID of the event.
    :ivar Optional[Snowflake] guild_id?: The guild ID of the event.
    :ivar Optional[Member] member?: The member of the event.
    :ivar Optional[Emoji] emoji?: The emoji of the event.
    """

    __slots__ = (
        "_json",
        "_client",
        "user_id",
        "channel_id",
        "message_id",
        "guild_id",
        "member",
        "emoji",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_id = Snowflake(self.user_id) if self._json.get("user_id") else None
        self.channel_id = Snowflake(self.channel_id) if self._json.get("channel_id") else None
        self.message_id = Snowflake(self.message_id) if self._json.get("message_id") else None
        self.guild_id = Snowflake(self.guild_id) if self._json.get("guild_id") else None
        self.member = Member(**self.member) if self._json.get("member") else None
        self.emoji = Emoji(**self.emoji) if self._json.get("emoji") else None


class ReactionRemove(MessageReaction):
    """
    A class object representing the gateway events ``MESSAGE_REACTION_REMOVE``, ``MESSAGE_REACTION_REMOVE_ALL`` and ``MESSAGE_REACTION_REMOVE_EMOJI``.

    .. note::
        This class inherits the already existing attributes of :class:`interactions.api.models.gw.Reaction`.
        The main missing attribute is ``member``.

    :ivar Optional[Snowflake] user_id?: The user ID of the event.
    :ivar Snowflake channel_id: The channel ID of the event.
    :ivar Snowflake message_id: The message ID of the event.
    :ivar Optional[Snowflake] guild_id?: The guild ID of the event.
    :ivar Optional[Emoji] emoji?: The emoji of the event.
    """

    __slots__ = ("_json", "_client", "user_id", "channel_id", "message_id", "guild_id", "emoji")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_id = Snowflake(self.user_id) if self.user_id else None
        self.channel_id = Snowflake(self.channel_id)
        self.message_id = Snowflake(self.message_id)
        self.guild_id = Snowflake(self.guild_id) if self.guild_id else None
        self.emoji = Emoji(**self.emoji) if self._json.get("emoji") else None


class ThreadList(DictSerializerMixin):
    """
    A class object representing the gateway event ``THREAD_LIST_SYNC``.

    :ivar Snowflake guild_id: The guild ID of the event.
    :ivar Optional[List[Snowflake]] channel_ids?: The channel IDs of the event.
    :ivar List[Channel] threads: The threads of the event.
    :ivar List[ThreadMember] members: The members of the thread of the event.
    """

    __slots__ = ("_json", "guild_id", "channel_ids", "threads", "members")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.guild_id = Snowflake(self.guild_id) if self._json.get("guild_id") else None
        self.channel_ids = (
            [Snowflake(channel_id) for channel_id in self.channel_ids]
            if self._json.get("channel_ids")
            else None
        )
        self.threads = (
            [Channel(**channel) for channel in self.threads] if self._json.get("threads") else None
        )
        self.members = (
            [ThreadMember(**member) for member in self.members]
            if self._json.get("members")
            else None
        )


class ThreadMembers(DictSerializerMixin):
    """
    A class object representing the gateway event ``THREAD_MEMBERS_UPDATE``.

    :ivar Snowflake id: The ID of the event.
    :ivar Snowflake guild_id: The guild ID of the event.
    :ivar int member_count: The member count of the event.
    :ivar Optional[List[ThreadMember]] added_members?: The added members of the thread of the event.
    :ivar Optional[List[Snowflake]] removed_member_ids?: The removed IDs of members of the thread of the event.
    """

    __slots__ = ("_json", "id", "guild_id", "member_count", "added_members", "removed_member_ids")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = Snowflake(self.id) if self._json.get("id") else None
        self.guild_id = Snowflake(self.guild_id) if self._json.get("guild_id") else None
        self.removed_member_ids = (
            [Snowflake(removed_member_id) for removed_member_id in self.removed_member_ids]
            if self._json.get("removed_member_ids")
            else None
        )
        self.added_members = (
            [ThreadMember(**member) for member in self.added_members]
            if self._json.get("added_members")
            else None
        )


class Webhooks(DictSerializerMixin):
    """
    A class object representing the gateway event ``WEBHOOKS_UPDATE``.

    :ivar Snowflake channel_id: The channel ID of the associated event.
    :ivar Snowflake guild_id: The guild ID of the associated event.
    """

    __slots__ = ("_json", "channel_id", "guild_id")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.channel_id = Snowflake(self.channel_id) if self._json.get("channel_id") else None
        self.guild_id = Snowflake(self.guild_id) if self._json.get("guild_id") else None
