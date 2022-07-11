from datetime import datetime
from typing import TYPE_CHECKING, Any, List, Optional, Union

from ..error import LibraryException
from .attrs_utils import MISSING, ClientSerializerMixin, convert_int, define, field
from .channel import Channel
from .flags import Permissions
from .misc import File, IDMixin, Snowflake
from .role import Role
from .user import User

if TYPE_CHECKING:
    from ...client.models.component import ActionRow, Button, SelectMenu
    from .guild import Guild
    from .message import Attachment, Embed, Message, MessageInteraction

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
    :ivar Optional[str] avatar?: The hash containing the user's guild avatar, if applicable.
    :ivar List[Role] roles: The list of roles of the member.
    :ivar datetime joined_at: The timestamp the member joined the guild at.
    :ivar datetime premium_since: The timestamp the member has been a server booster since.
    :ivar bool deaf: Whether the member is deafened.
    :ivar bool mute: Whether the member is muted.
    :ivar Optional[bool] pending?: Whether the member is pending to pass membership screening.
    :ivar Optional[Permissions] permissions?: Whether the member has permissions.
    :ivar Optional[str] communication_disabled_until?: How long until they're unmuted, if any.
    """

    user: Optional[User] = field(converter=User, default=None, add_client=True, repr=True)
    nick: Optional[str] = field(default=None, repr=True)
    _avatar: Optional[str] = field(default=None, discord_name="avatar")
    roles: List[int] = field()
    joined_at: datetime = field(converter=datetime.fromisoformat)
    premium_since: Optional[datetime] = field(converter=datetime.fromisoformat, default=None)
    deaf: bool = field()
    mute: bool = field()
    is_pending: Optional[bool] = field(default=None)
    pending: Optional[bool] = field(default=None)
    permissions: Optional[Permissions] = field(converter=convert_int(Permissions), default=None)
    communication_disabled_until: Optional[datetime.isoformat] = field(
        converter=datetime.fromisoformat, default=None
    )
    hoisted_role: Optional[Any] = field(
        default=None
    )  # TODO: Investigate what this is for when documented by Discord.
    flags: int = field()  # TODO: Investigate what this is for when documented by Discord.

    def __str__(self) -> str:
        return self.name or ""

    @property
    def avatar(self) -> Optional[str]:
        return self._avatar or getattr(self.user, "avatar", None)

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

    @property
    def name(self) -> str:
        """
        Returns the string of either the user's nickname or username.

        :return: The name of the member
        :rtype: str
        """
        return self.nick or (self.user.username if self.user else None)

    async def ban(
        self,
        guild_id: Union[int, Snowflake, "Guild"],
        reason: Optional[str] = None,
        delete_message_days: Optional[int] = 0,
    ) -> None:
        """
        Bans the member from a guild.

        :param guild_id: The id of the guild to ban the member from
        :type guild_id: Union[int, Snowflake, "Guild"]
        :param reason?: The reason of the ban
        :type reason: Optional[str]
        :param delete_message_days?: Number of days to delete messages, from 0 to 7. Defaults to 0
        :type delete_message_days: Optional[int]
        """

        _guild_id = int(guild_id) if isinstance(guild_id, (Snowflake, int)) else int(guild_id.id)

        await self._client.create_guild_ban(
            guild_id=_guild_id,
            user_id=int(self.user.id),
            reason=reason,
            delete_message_days=delete_message_days,
        )

    async def kick(
        self,
        guild_id: Union[int, Snowflake, "Guild"],
        reason: Optional[str] = None,
    ) -> None:
        """
        Kicks the member from a guild.

        :param guild_id: The id of the guild to kick the member from
        :type guild_id: Union[int, Snowflake, "Guild"]
        :param reason?: The reason for the kick
        :type reason: Optional[str]
        """
        if not self._client:
            raise LibraryException(code=13)

        _guild_id = int(guild_id) if isinstance(guild_id, (Snowflake, int)) else int(guild_id.id)

        await self._client.create_guild_kick(
            guild_id=_guild_id,
            user_id=int(self.user.id),
            reason=reason,
        )

    async def add_role(
        self,
        role: Union[Role, int, Snowflake],
        guild_id: Union[int, Snowflake, "Guild"],
        reason: Optional[str] = None,
    ) -> None:
        """
        This method adds a role to a member.

        :param role: The role to add. Either ``Role`` object or role_id
        :type role: Union[Role, int, Snowflake]
        :param guild_id: The id of the guild to add the roles to the member
        :type guild_id: Union[int, Snowflake, "Guild"]
        :param reason?: The reason why the roles are added
        :type reason: Optional[str]
        """
        if not self._client:
            raise LibraryException(code=13)

        _role = int(role.id) if isinstance(role, Role) else int(role)
        _guild_id = int(guild_id) if isinstance(guild_id, (Snowflake, int)) else int(guild_id.id)

        await self._client.add_member_role(
            guild_id=_guild_id,
            user_id=int(self.user.id),
            role_id=_role,
            reason=reason,
        )

    async def remove_role(
        self,
        role: Union[Role, int],
        guild_id: Union[int, Snowflake, "Guild"],
        reason: Optional[str] = None,
    ) -> None:
        """
        This method removes a role from a member.

        :param role: The role to remove. Either ``Role`` object or role_id
        :type role: Union[Role, int]
        :param guild_id: The id of the guild to remove the roles of the member
        :type guild_id: Union[int, Snowflake, "Guild"]
        :param reason?: The reason why the roles are removed
        :type reason: Optional[str]
        """
        if not self._client:
            raise LibraryException(code=13)

        _guild_id = int(guild_id) if isinstance(guild_id, (Snowflake, int)) else int(guild_id.id)
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
        allowed_mentions: Optional["MessageInteraction"] = MISSING,
    ) -> "Message":
        """
        Sends a DM to the member.

        :param content?: The contents of the message as a string or string-converted value.
        :type content: Optional[str]
        :param components?: A component, or list of components for the message.
        :type components: Optional[Union[ActionRow, Button, SelectMenu, List[ActionRow], List[Button], List[SelectMenu]]]
        :param tts?: Whether the message utilizes the text-to-speech Discord programme or not.
        :type tts: Optional[bool]
        :param attachments?: The attachments to attach to the message. Needs to be uploaded to the CDN first
        :type attachments: Optional[List[Attachment]]
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
        guild_id: Union[int, Snowflake, "Guild"],
        nick: Optional[str] = MISSING,
        roles: Optional[List[int]] = MISSING,
        mute: Optional[bool] = MISSING,
        deaf: Optional[bool] = MISSING,
        channel_id: Optional[Union[Channel, int, Snowflake]] = MISSING,
        communication_disabled_until: Optional[datetime.isoformat] = MISSING,
        reason: Optional[str] = None,
    ) -> "Member":
        """
        Modifies the member of a guild.

        :param guild_id: The id of the guild to modify the member on
        :type guild_id: Union[int, Snowflake, "Guild"]
        :param nick?: The nickname of the member
        :type nick: Optional[str]
        :param roles?: A list of all role ids the member has
        :type roles: Optional[List[int]]
        :param mute?: whether the user is muted in voice channels
        :type mute: Optional[bool]
        :param deaf?: whether the user is deafened in voice channels
        :type deaf: Optional[bool]
        :param channel_id?: id of channel to move user to (if they are connected to voice)
        :type channel_id: Optional[Union[Channel, int, Snowflake]]
        :param communication_disabled_until?: when the user's timeout will expire and the user will be able to communicate in the guild again (up to 28 days in the future)
        :type communication_disabled_until: Optional[datetime.isoformat]
        :param reason?: The reason of the modifying
        :type reason: Optional[str]
        :return: The modified member object
        :rtype: Member
        """
        if not self._client:
            raise LibraryException(code=13)

        _guild_id = int(guild_id) if isinstance(guild_id, (int, Snowflake)) else int(guild_id.id)

        payload = {}
        if nick is not MISSING:
            payload["nick"] = nick

        if roles is not MISSING:
            payload["roles"] = roles

        if channel_id is not MISSING:
            payload["channel_id"] = (
                int(channel_id.id) if isinstance(channel_id, Channel) else int(channel_id)
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
        Adds the member to a thread.

        :param thread_id: The id of the thread to add the member to
        :type thread_id: Union[int, Snowflake, Channel]
        """
        if not self._client:
            raise LibraryException(code=13)

        _thread_id = int(thread_id.id) if isinstance(thread_id, Channel) else int(thread_id)

        await self._client.add_member_to_thread(
            user_id=int(self.user.id),
            thread_id=_thread_id,
        )

    def get_avatar_url(self, guild_id: Union[int, Snowflake, "Guild"]) -> Optional[str]:
        """
        Returns the URL of the member's avatar for the specified guild.
        :param guild_id: The id of the guild to get the member's avatar from
        :type guild_id: Union[int, Snowflake, "Guild"]
        :return: URL of the members's avatar (None will be returned if no avatar is set)
        :rtype: str
        """
        if not self.avatar:
            return None

        _guild_id = int(guild_id) if isinstance(guild_id, (int, Snowflake)) else int(guild_id.id)

        url = f"https://cdn.discordapp.com/guilds/{_guild_id}/users/{int(self.user.id)}/avatars/{self.avatar}"
        url += ".gif" if self.avatar.startswith("a_") else ".png"
        return url
