from datetime import datetime
from typing import Optional, Union

from .misc import DictSerializerMixin
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
    :ivar Optional[str] permissions?: Whether the member has permissions.
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

    async def ban(
        self,
        guild_id: int,
        reason: Optional[str] = None,
        delete_message_days: Optional[int] = 0,
    ) -> None:
        """
        Bans the member from a guild
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
        Kicks the member from a guild
        :param guild_id: The id of the guild to kick the member from
        :type guild_id: int
        :param reason?: The reason for the kick
        :type reason: Optional[str]
        """
        await self._client.create_guild_kick(
            guild_id=guild_id,
            user_id=int(self.user.id),
            reason=reason,
        )

    async def add_role(
        self,
        role: Union[Role, int],
        guild_id: int,
        reason: Optional[str],
    ) -> None:
        """
        This method adds a role to a member
        :param role: The role to add. Either ``Role`` object or role_id
        :type role: Union[Role, int]
        :param guild_id: The id of the guild to add the roles to the member
        :type guild_id: int
        :param reason?: The reason why the roles are added
        :type reason: Optional[str]
        """
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
        reason: Optional[str],
    ) -> None:
        """
        This method removes a role from a member
        :param role: The role to remove. Either ``Role`` object or role_id
        :type role: Union[Role, int]
        :param guild_id: The id of the guild to remove the roles of the member
        :type guild_id: int
        :param reason?: The reason why the roles are removed
        :type reason: Optional[str]
        """
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
        content: Optional[str] = None,
        *,
        tts: Optional[bool] = False,
        # attachments: Optional[List[Any]] = None,  # TODO: post-v4: Replace with own file type.
        embeds=None,
        allowed_mentions=None,
    ):
        """
        Sends a DM to the member

        :param content?: The contents of the message as a string or string-converted value.
        :type content: Optional[str]
        :param tts?: Whether the message utilizes the text-to-speech Discord programme or not.
        :type tts: Optional[bool]
        :param embeds?: An embed, or list of embeds for the message.
        :type embeds: Optional[Union[Embed, List[Embed]]]
        :param allowed_mentions?: The message interactions/mention limits that the message can refer to.
        :type allowed_mentions: Optional[MessageInteraction]
        :return: The sent message as an object.
        :rtype: Message
        """
        from .channel import Channel
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

        # TODO: post-v4: Add attachments into Message obj.
        payload = Message(
            content=_content,
            tts=_tts,
            # file=file,
            # attachments=_attachments,
            embeds=_embeds,
            allowed_mentions=_allowed_mentions,
        )

        channel = Channel(**await self._client.create_dm(recipient_id=int(self.user.id)))
        res = await self._client.create_message(channel_id=int(channel.id), payload=payload._json)

        message = Message(**res, _client=self._client)
        return message
