from datetime import datetime
from typing import TYPE_CHECKING, Any, List, Optional, Union

from ...utils.attrs_utils import ClientSerializerMixin, convert_int, convert_list, define, field
from ...utils.missing import MISSING
from ...utils.utils import search_iterable
from ..error import LibraryException
from .channel import Channel
from .flags import MemberFlags, Permissions
from .misc import AllowedMentions, File, IDMixin, Snowflake
from .role import Role
from .user import User

if TYPE_CHECKING:
    from ...client.models.component import ActionRow, Button, SelectMenu
    from .guild import Guild
    from .gw import VoiceState
    from .message import Attachment, Embed, Message

__all__ = ("Member",)


@define()
class Member(ClientSerializerMixin, IDMixin):
    """
    A class object representing the user of a guild, known as a "member."

    .. note::
        ``pending`` and ``permissions`` only apply for members retroactively
        requiring to verify rules via. membership screening or lack permissions
        to speak.

    :ivar User user: The user of the guild.
    :ivar str nick: The nickname of the member.
    :ivar Optional[str] avatar: The hash containing the user's guild avatar, if applicable.
    :ivar List[int] roles: The list of roles of the member.
    :ivar datetime joined_at: The timestamp the member joined the guild at.
    :ivar datetime premium_since: The timestamp the member has been a server booster since.
    :ivar bool deaf: Whether the member is deafened.
    :ivar bool mute: Whether the member is muted.
    :ivar MemberFlags flags: The guild member flags. Default to 0.
    :ivar Optional[bool] pending: Whether the member is pending to pass membership screening.
    :ivar Optional[Permissions] permissions: Whether the member has permissions.
    :ivar Optional[str] communication_disabled_until: How long until they're unmuted, if any.
    """

    user: Optional[User] = field(converter=User, default=None, add_client=True)
    nick: Optional[str] = field(default=None)
    _avatar: Optional[str] = field(default=None, discord_name="avatar", repr=False)
    roles: List[int] = field(converter=convert_list(int))
    joined_at: datetime = field(converter=datetime.fromisoformat, repr=False)
    premium_since: Optional[datetime] = field(
        converter=datetime.fromisoformat, default=None, repr=False
    )
    deaf: bool = field()
    mute: bool = field()
    flags: MemberFlags = field(converter=convert_int(MemberFlags), repr=False)
    is_pending: Optional[bool] = field(default=None, repr=False)
    pending: Optional[bool] = field(default=None, repr=False)
    permissions: Optional[Permissions] = field(
        converter=convert_int(Permissions), default=None, repr=False
    )
    communication_disabled_until: Optional[datetime.isoformat] = field(
        converter=datetime.fromisoformat, default=None
    )
    hoisted_role: Optional[Any] = field(
        default=None, repr=False
    )  # TODO: Investigate what this is for when documented by Discord.

    def __getattr__(self, name):
        # Forward any attributes the user has to make it easier for devs
        try:
            return getattr(self.user, name)
        except AttributeError as e:
            raise AttributeError(f"Neither `User` nor `Member` have attribute {name}") from e

    @property
    def voice_state(self) -> Optional["VoiceState"]:
        """
        .. versionadded:: 4.4.0

        Returns the current voice state of the member, if any.

        :rtype: VoiceState
        """
        if not self._client:
            raise LibraryException(code=13)

        from .gw import VoiceState

        return self._client.cache[VoiceState].get(self.id)

    @property
    def guild(self) -> Optional["Guild"]:
        """
        .. versionadded:: 4.4.0

        Attempts to get the guild the member is in.
        Only works then roles or nick or joined at is present and the guild is cached.

        :return: The guild this member belongs to.
        :rtype: Guild
        """
        _id = self.guild_id
        from .guild import Guild

        if not _id or isinstance(_id, LibraryException):
            return

        return self._client.cache[Guild].get(_id, None)

    @property
    def guild_id(self) -> Optional[Union[Snowflake, LibraryException]]:
        """
        .. versionadded:: 4.3.2

        Attempts to get the guild ID the member is in.
        Only works when roles or nick or joined at is present and the guild is cached.

        :return: The ID of the guild this member belongs to.
        :rtype: Optional[Union[Snowflake, LibraryException]]
        """

        if hasattr(self, "_guild_id"):
            return self._guild_id

        elif _id := self._extras.get("guild_id"):
            return Snowflake(_id)

        if not self._client:
            raise LibraryException(code=13)

        from .guild import Guild

        if self.roles:
            for guild in self._client.cache[Guild].values.values():
                for role in guild.roles:
                    if role.id in self.roles:
                        self._extras["guild_id"] = int(guild.id)
                        return guild.id

        possible_guilds: List[Guild] = []

        if self.nick:

            def check(_member: Member):
                return _member.nick == self.nick and _member.id == self.id

            for guild in self._client.cache[Guild].values.values():
                if len(search_iterable(guild.members, check=check)) > 0:
                    possible_guilds.append(guild)

        if len(possible_guilds) == 1:
            self._extras["guild_id"] = int(possible_guilds[0].id)
            return possible_guilds[0].id

        elif not possible_guilds:
            possible_guilds = list(self._client.cache[Guild].values.values())

        for guild in possible_guilds:
            for member in guild.members:
                if member.joined_at == self.joined_at:
                    self._extras["guild_id"] = int(guild.id)
                    return guild.id

        else:
            return LibraryException(
                code=12, message="the guild_id could not be retrieved, please insert one!"
            )

    @property
    def avatar(self) -> Optional[str]:
        """Returns the user's avatar hash, if any."""
        return self._avatar or getattr(self.user, "avatar", None)

    @property
    def id(self) -> Snowflake:
        """
        .. versionadded:: 4.1.0

        Returns the ID of the user.

        :return: The ID of the user
        :rtype: Snowflake
        """
        return self.user.id if self.user else None

    @property
    def mention(self) -> str:
        """
        .. versionadded:: 4.1.0

        Returns a string that allows you to mention the given member.

        :return: The string of the mentioned member.
        :rtype: str
        """
        return f"<@{'!' if self.nick else ''}{self.id}>"

    @property
    def name(self) -> str:
        """
        .. versionadded:: 4.2.0

        Returns the string of either the user's nickname or username.

        :return: The name of the member
        :rtype: str
        """
        return self.nick or (self.user.username if self.user else None)

    async def ban(
        self,
        guild_id: Optional[Union[int, Snowflake, "Guild"]] = MISSING,
        seconds: Optional[int] = 0,
        minutes: Optional[int] = MISSING,
        hours: Optional[int] = MISSING,
        days: Optional[int] = MISSING,
        reason: Optional[str] = None,
    ) -> None:
        """
        .. versionadded:: 4.0.2

        .. versionchanged:: 4.3.2
            Method has been aligned to changes in the Discord API. You can now input days, hours, minutes and seconds,
            as long as it doesn't exceed 604800 seconds in total for deleting messages, instead of only days.

        .. versionchanged:: 4.3.2
            ``guild_id`` is no longer required

        Bans the member from a guild.

        :param Optional[Union[int, Snowflake, Guild]] guild_id: The id of the guild to ban the member from
        :param Optional[int] seconds: Number of seconds to delete messages, from 0 to 604800. Defaults to 0
        :param Optional[int] minutes: Number of minutes to delete messages, from 0 to 10080
        :param Optional[int] hours: Number of hours to delete messages, from 0 to 168
        :param Optional[int] days: Number of days to delete messages, from 0 to 7
        :param Optional[str] reason: The reason of the ban
        """

        if guild_id is MISSING:
            _guild_id = self.guild_id
            if isinstance(_guild_id, LibraryException):
                raise _guild_id

        else:
            _guild_id = (
                int(guild_id) if isinstance(guild_id, (Snowflake, int)) else int(guild_id.id)
            )

        if days is not MISSING:
            seconds += days * 24 * 3600
        if hours is not MISSING:
            seconds += hours * 3600
        if minutes is not MISSING:
            seconds += minutes * 60

        if seconds > 604800:
            raise LibraryException(
                code=12,
                message="The amount of total seconds to delete messages exceeds the limit Discord provides (604800)",
            )

        await self._client.create_guild_ban(
            guild_id=_guild_id,
            user_id=int(self.user.id),
            reason=reason,
            delete_message_seconds=seconds,
        )

    async def kick(
        self,
        guild_id: Optional[Union[int, Snowflake, "Guild"]] = MISSING,
        reason: Optional[str] = None,
    ) -> None:
        """
        .. versionadded:: 4.0.2

        .. versionchanged:: 4.3.2
            ``guild_id`` is no longer required.

        Kicks the member from a guild.

        :param Optional[Union[int, Snowflake, Guild]] guild_id: The id of the guild to kick the member from
        :param Optional[str] reason: The reason for the kick
        """
        if not self._client:
            raise LibraryException(code=13)

        if guild_id is MISSING:
            _guild_id = self.guild_id

            if isinstance(_guild_id, LibraryException):
                raise _guild_id

        else:
            _guild_id = (
                int(guild_id) if isinstance(guild_id, (Snowflake, int)) else int(guild_id.id)
            )

        await self._client.create_guild_kick(
            guild_id=_guild_id,
            user_id=int(self.user.id),
            reason=reason,
        )

    async def add_role(
        self,
        role: Union[Role, int, Snowflake],
        guild_id: Optional[Union[int, Snowflake, "Guild"]] = MISSING,
        reason: Optional[str] = None,
    ) -> None:
        """
        .. versionadded:: 4.0.2

        .. versionchanged:: 4.3.2
            ``guild_id`` is no longer required.

        This method adds a role to a member.

        :param Union[Role, int, Snowflake] role: The role to add. Either ``Role`` object or role_id
        :param Optional[Union[int, Snowflake, Guild]] guild_id: The id of the guild to add the roles to the member
        :param Optional[str] reason: The reason why the roles are added
        """
        if not self._client:
            raise LibraryException(code=13)

        _role = int(role.id) if isinstance(role, Role) else int(role)
        if guild_id is MISSING:
            _guild_id = self.guild_id
            if isinstance(_guild_id, LibraryException):
                raise _guild_id

        else:
            _guild_id = (
                int(guild_id) if isinstance(guild_id, (Snowflake, int)) else int(guild_id.id)
            )

        await self._client.add_member_role(
            guild_id=_guild_id,
            user_id=int(self.user.id),
            role_id=_role,
            reason=reason,
        )

    async def remove_role(
        self,
        role: Union[Role, int],
        guild_id: Optional[Union[int, Snowflake, "Guild"]] = MISSING,
        reason: Optional[str] = None,
    ) -> None:
        """
        .. versionadded:: 4.0.2

        .. versionchanged:: 4.3.2
            ``guild_id`` is no longer required.

        This method removes a role from a member.

        :param Union[Role, int] role: The role to remove. Either ``Role`` object or role_id
        :param Optional[Union[int, Snowflake, Guild]] guild_id: The id of the guild to remove the roles of the member
        :param Optional[str] reason: The reason why the roles are removed
        """
        if not self._client:
            raise LibraryException(code=13)

        if guild_id is MISSING:
            _guild_id = self.guild_id
            if isinstance(_guild_id, LibraryException):
                raise _guild_id

        else:
            _guild_id = (
                int(guild_id) if isinstance(guild_id, (Snowflake, int)) else int(guild_id.id)
            )
        _role = int(role.id) if isinstance(role, Role) else int(role)

        await self._client.remove_member_role(
            guild_id=_guild_id,
            user_id=int(self.user.id),
            role_id=_role,
            reason=reason,
        )

    async def send(
        self,
        content: Optional[str] = MISSING,
        *,
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
        tts: Optional[bool] = MISSING,
        attachments: Optional[List["Attachment"]] = MISSING,
        files: Optional[Union[File, List[File]]] = MISSING,
        embeds: Optional[Union["Embed", List["Embed"]]] = MISSING,
        allowed_mentions: Optional[Union[AllowedMentions, dict]] = MISSING,
    ) -> "Message":
        """
        .. versionadded:: 4.0.2

        Sends a DM to the member.

        :param Optional[str] content: The contents of the message as a string or string-converted value.
        :param Optional[Union[ActionRow, Button, SelectMenu, List[ActionRow], List[Button], List[SelectMenu]]] components: A component, or list of components for the message.
        :param Optional[bool] tts: Whether the message utilizes the text-to-speech Discord programme or not.
        :param Optional[List[Attachment]] attachments:
            .. versionadded:: 4.3.0

            The attachments to attach to the message. Needs to be uploaded to the CDN first
        :param Optional[Union[File, List[File]]] files:
            .. versionadded:: 4.2.0

            A file or list of files to be attached to the message.
        :param Optional[Union[Embed, List[Embed]]] embeds: An embed, or list of embeds for the message.
        :param Optional[Union[AllowedMentions, dict]] allowed_mentions: The allowed mentions for the message.
        :return: The sent message as an object.
        :rtype: Message
        """
        if not self._client:
            raise LibraryException(code=13)
        from ...client.models.component import _build_components
        from .message import Message

        _content: str = "" if content is MISSING else content
        _tts: bool = False if tts is MISSING else tts
        _attachments = [] if attachments is MISSING else [a._json for a in attachments]
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
            components=_components,
            allowed_mentions=_allowed_mentions,
        )
        channel = Channel(**await self._client.create_dm(recipient_id=int(self.user.id)))
        res = await self._client.create_message(
            channel_id=int(channel.id), payload=payload, files=files
        )

        return Message(**res, _client=self._client)

    async def modify(
        self,
        guild_id: Optional[Union[int, Snowflake, "Guild"]] = MISSING,
        nick: Optional[str] = MISSING,
        roles: Optional[List[int]] = MISSING,
        mute: Optional[bool] = MISSING,
        deaf: Optional[bool] = MISSING,
        channel_id: Optional[Union[Channel, int, Snowflake]] = MISSING,
        communication_disabled_until: Optional[datetime.isoformat] = MISSING,
        reason: Optional[str] = None,
    ) -> "Member":
        """
        .. versionadded:: 4.0.2

        .. versionchanged:: 4.3.2
            ``guild_id`` is no longer required.

        Modifies the member of a guild.

        :param Optional[Union[int, Snowflake, Guild]] guild_id: The id of the guild to modify the member on
        :param Optional[str] nick: The nickname of the member
        :param Optional[List[int]] roles: A list of all role ids the member has
        :param Optional[bool] mute: whether the user is muted in voice channels
        :param Optional[bool] deaf: whether the user is deafened in voice channels
        :param Optional[Union[Channel, int, Snowflake]] channel_id: id of channel to move user to (if they are connected to voice)
        :param Optional[datetime.isoformat] communication_disabled_until: when the user's timeout will expire and the user will be able to communicate in the guild again (up to 28 days in the future)
        :param Optional[str] reason: The reason of the modifying
        :return: The modified member object
        :rtype: Member
        """
        if not self._client:
            raise LibraryException(code=13)

        if guild_id is MISSING:
            _guild_id = self.guild_id
            if isinstance(_guild_id, LibraryException):
                raise _guild_id

        else:
            _guild_id = (
                int(guild_id) if isinstance(guild_id, (int, Snowflake)) else int(guild_id.id)
            )

        payload = {}
        if nick is not MISSING:
            payload["nick"] = nick

        if roles is not MISSING:
            payload["roles"] = roles

        if channel_id is not MISSING:
            payload["channel_id"] = (
                int(channel_id.id)
                if isinstance(channel_id, Channel)
                else (int(channel_id) if channel_id is not None else None)
            )

        if mute is not MISSING:
            payload["mute"] = mute

        if deaf is not MISSING:
            payload["deaf"] = deaf

        if communication_disabled_until is not MISSING:
            payload["communication_disabled_until"] = communication_disabled_until

        res = await self._client.modify_member(
            user_id=int(self.user.id),
            guild_id=_guild_id,
            payload=payload,
            reason=reason,
        )

        self.update(res)
        return self

    async def add_to_thread(
        self,
        thread_id: Union[int, Snowflake, Channel],
    ) -> None:
        """
        .. versionadded:: 4.0.2

        Adds the member to a thread.

        :param Union[int, Snowflake, Channel] thread_id: The id of the thread to add the member to
        """
        if not self._client:
            raise LibraryException(code=13)

        _thread_id = int(thread_id.id) if isinstance(thread_id, Channel) else int(thread_id)

        await self._client.add_member_to_thread(
            user_id=int(self.user.id),
            thread_id=_thread_id,
        )

    def get_avatar_url(
        self, guild_id: Optional[Union[int, Snowflake, "Guild"]] = MISSING
    ) -> Optional[str]:
        """
        .. versionadded:: 4.2.0

        .. versionchanged:: 4.3.0
            Has been renamed to `get_avatar_url` instead of `get_member_avatar_url`

        .. versionchanged:: 4.3.2
            ``guild_id`` is no longer required.

        Returns the URL of the member's avatar for the specified guild.

        :param Optional[Union[int, Snowflake, Guild]] guild_id: The id of the guild to get the member's avatar from
        :return: URL of the members's avatar (None will be returned if no avatar is set)
        :rtype: str
        """
        if not self.avatar or self.avatar == self.user.avatar:
            return None

        if guild_id is MISSING:
            _guild_id = self.guild_id
            if isinstance(_guild_id, LibraryException):
                raise _guild_id

        else:
            _guild_id = (
                int(guild_id) if isinstance(guild_id, (int, Snowflake)) else int(guild_id.id)
            )

        url = f"https://cdn.discordapp.com/guilds/{_guild_id}/users/{int(self.user.id)}/avatars/{self.avatar}"
        url += ".gif" if self.avatar.startswith("a_") else ".png"
        return url

    async def get_guild_permissions(
        self, guild_id: Optional[Union[int, Snowflake, "Guild"]] = MISSING
    ) -> Permissions:
        """
        .. versionadded:: 4.3.2

        Returns the permissions of the member for the specified guild.

        .. note::
            The permissions returned by this function will not take into account role and
            user overwrites that can be assigned to channels or categories. If you need
            these overwrites, look into :meth:`.Channel.get_permissions_for`.

        :param Guild guild: The guild of the member
        :return: Base permissions of the member in the specified guild
        :rtype: Permissions
        """
        from .guild import Guild

        if guild_id is MISSING:
            _guild_id = self.guild_id
            if isinstance(_guild_id, LibraryException):
                raise _guild_id

        else:
            _guild_id = int(guild_id.id) if isinstance(guild_id, Guild) else int(guild_id)

        guild = Guild(**await self._client.get_guild(int(_guild_id)), _client=self._client)

        if int(guild.owner_id) == int(self.id):
            return Permissions.ALL

        role_everyone = await guild.get_role(int(guild.id))
        permissions = int(role_everyone.permissions)

        for role_id in self.roles:
            role = await guild.get_role(role_id)
            permissions |= int(role.permissions)

        if Permissions.ADMINISTRATOR in Permissions(permissions):
            return Permissions.ALL

        return Permissions(permissions)

    async def has_permissions(
        self,
        *permissions: Union[int, Permissions],
        channel: Optional[Channel] = MISSING,
        guild_id: Optional[Union[int, Snowflake, "Guild"]] = MISSING,
        operator: str = "and",
    ) -> bool:
        r"""
        .. versionadded:: 4.3.2

        Returns whether the member has the permissions passed.

        .. note::
            If the channel argument is present, the function will look if the member has the permissions in the specified channel.
            If the argument is missing, then it will only consider the member's guild permissions.

        :param Union[int, Permissions] \*permissions: The list of permissions
        :param Channel channel: The channel where to check for permissions
        :param Optional[Union[int, Snowflake, Guild]] guild_id: The id of the guild
        :param Optional[str] operator: The operator to use to calculate permissions. Possible values: `and`, `or`. Defaults to `and`.
        :return: Whether the member has the permissions
        :rtype: bool
        """
        perms = (
            await self.get_guild_permissions(guild_id)
            if channel is MISSING
            else await channel.get_permissions_for(self)
        )

        if operator == "and":
            return all(perm in perms for perm in permissions)
        else:
            return any(perm in perms for perm in permissions)
