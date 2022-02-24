from datetime import datetime
from typing import List, Optional, Union

from .channel import Channel
from .flags import Permissions
from .misc import MISSING, DictSerializerMixin, Snowflake
from .role import Role
from .user import User


class Member(DictSerializerMixin):
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

    __slots__ = (
        "_json",
        "user",
        "nick",
        "avatar",
        "roles",
        "joined_at",
        "premium_since",
        "deaf",
        "mute",
        "is_pending",
        "pending",
        "permissions",
        "communication_disabled_until",
        "hoisted_role",
        "_client",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user = (
            self.user
            if isinstance(self.user, User)
            else (User(**self.user) if self._json.get("user") else None)
        )
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

        self.permissions = (
            Permissions(int(self._json.get("permissions")))
            if self._json.get("permissions")
            else None
        )

        self.roles = [
            role_id if isinstance(role_id, int) else int(role_id) for role_id in self.roles
        ]

        if not self.avatar and self.user:
            self.avatar = self.user.avatar

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
        guild_id: int,
        reason: Optional[str] = None,
        delete_message_days: Optional[int] = 0,
    ) -> None:
        """
        Bans the member from a guild.

        :param guild_id: The id of the guild to ban the member from
        :type guild_id: int
        :param reason?: The reason of the ban
        :type reason: Optional[str]
        :param delete_message_days?: Number of days to delete messages, from 0 to 7. Defaults to 0
        :type delete_message_days: Optional[int]
        """
        await self._client.create_guild_ban(
            guild_id=guild_id,
            user_id=int(self.user.id),
            reason=reason,
            delete_message_days=delete_message_days,
        )

    async def kick(
        self,
        guild_id: int,
        reason: Optional[str] = None,
    ) -> None:
        """
        Kicks the member from a guild.

        :param guild_id: The id of the guild to kick the member from
        :type guild_id: int
        :param reason?: The reason for the kick
        :type reason: Optional[str]
        """
        if not self._client:
            raise AttributeError("HTTPClient not found!")
        await self._client.create_guild_kick(
            guild_id=guild_id,
            user_id=int(self.user.id),
            reason=reason,
        )

    async def add_role(
        self,
        role: Union[Role, int],
        guild_id: int,
        reason: Optional[str] = None,
    ) -> None:
        """
        This method adds a role to a member.

        :param role: The role to add. Either ``Role`` object or role_id
        :type role: Union[Role, int]
        :param guild_id: The id of the guild to add the roles to the member
        :type guild_id: int
        :param reason?: The reason why the roles are added
        :type reason: Optional[str]
        """
        if not self._client:
            raise AttributeError("HTTPClient not found!")
        if isinstance(role, Role):
            await self._client.add_member_role(
                guild_id=guild_id,
                user_id=int(self.user.id),
                role_id=int(role.id),
                reason=reason,
            )
        else:
            await self._client.add_member_role(
                guild_id=guild_id,
                user_id=int(self.user.id),
                role_id=role,
                reason=reason,
            )

    async def remove_role(
        self,
        role: Union[Role, int],
        guild_id: int,
        reason: Optional[str] = None,
    ) -> None:
        """
        This method removes a role from a member.

        :param role: The role to remove. Either ``Role`` object or role_id
        :type role: Union[Role, int]
        :param guild_id: The id of the guild to remove the roles of the member
        :type guild_id: int
        :param reason?: The reason why the roles are removed
        :type reason: Optional[str]
        """
        if not self._client:
            raise AttributeError("HTTPClient not found!")
        if isinstance(role, Role):
            await self._client.remove_member_role(
                guild_id=guild_id,
                user_id=int(self.user.id),
                role_id=int(role.id),
                reason=reason,
            )
        else:
            await self._client.remove_member_role(
                guild_id=guild_id,
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
                "ActionRow",  # noqa
                "Button",  # noqa
                "SelectMenu",  # noqa
                List["ActionRow"],  # noqa
                List["Button"],  # noqa
                List["SelectMenu"],  # noqa
            ]
        ] = MISSING,
        tts: Optional[bool] = MISSING,
        # attachments: Optional[List[Any]] = None,  # TODO: post-v4: Replace with own file type.
        embeds: Optional[Union["Embed", List["Embed"]]] = MISSING,  # noqa
        allowed_mentions: Optional["MessageInteraction"] = MISSING,  # noqa
    ):
        """
        Sends a DM to the member.

        :param content?: The contents of the message as a string or string-converted value.
        :type content: Optional[str]
        :param components?: A component, or list of components for the message.
        :type components: Optional[Union[ActionRow, Button, SelectMenu, List[Actionrow], List[Button], List[SelectMenu]]]
        :param tts?: Whether the message utilizes the text-to-speech Discord programme or not.
        :type tts: Optional[bool]
        :param embeds?: An embed, or list of embeds for the message.
        :type embeds: Optional[Union[Embed, List[Embed]]]
        :param allowed_mentions?: The message interactions/mention limits that the message can refer to.
        :type allowed_mentions: Optional[MessageInteraction]
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

        # TODO: post-v4: Add attachments into Message obj.
        payload = Message(
            content=_content,
            tts=_tts,
            # file=file,
            # attachments=_attachments,
            embeds=_embeds,
            components=_components,
            allowed_mentions=_allowed_mentions,
        )

        channel = Channel(**await self._client.create_dm(recipient_id=int(self.user.id)))
        res = await self._client.create_message(channel_id=int(channel.id), payload=payload._json)

        return Message(**res, _client=self._client)

    async def modify(
        self,
        guild_id: int,
        nick: Optional[str] = MISSING,
        roles: Optional[List[int]] = MISSING,
        mute: Optional[bool] = MISSING,
        deaf: Optional[bool] = MISSING,
        channel_id: Optional[int] = MISSING,
        communication_disabled_until: Optional[datetime.isoformat] = MISSING,
        reason: Optional[str] = None,
    ) -> "Member":
        """
        Modifies the member of a guild.

        :param guild_id: The id of the guild to modify the member on
        :type guild_id: int
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
            guild_id=guild_id,
            payload=payload,
            reason=reason,
        )
        return Member(**res, _client=self._client)

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
