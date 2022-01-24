from datetime import datetime
from typing import List, Optional, Union

from .flags import Permissions
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

        self.permissions = (
            Permissions(int(self._json.get("permissions")))
            if self._json.get("permissions")
            else None
        )

        if not self.avatar and self.user:
            self.avatar = self.user.avatar

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
        reason: Optional[str],
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
        reason: Optional[str],
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
        content: Optional[str] = None,
        *,
        components=None,
        tts: Optional[bool] = False,
        # attachments: Optional[List[Any]] = None,  # TODO: post-v4: Replace with own file type.
        embeds=None,
        allowed_mentions=None,
    ):
        """
        Sends a DM to the member.

        :param content?: The contents of the message as a string or string-converted value.
        :type content: Optional[str]
        :param components?: A component, or list of components for the message.
        :type components: Optional[Union[ActionRow, Button, SelectMenu, List[Union[ActionRow, Button, SelectMenu]]]]
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
        from ...models.component import ActionRow, Button, SelectMenu
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
            components=_components,
            allowed_mentions=_allowed_mentions,
        )

        channel = Channel(**await self._client.create_dm(recipient_id=int(self.user.id)))
        res = await self._client.create_message(channel_id=int(channel.id), payload=payload._json)

        return Message(**res, _client=self._client)

    async def modify(
        self,
        guild_id: int,
        nick: Optional[str] = None,
        roles: Optional[List[int]] = None,
        mute: Optional[bool] = None,
        deaf: Optional[bool] = None,
        channel_id: Optional[int] = None,
        communication_disabled_until: Optional[datetime.isoformat] = None,
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
        if nick:
            payload["nick"] = nick

        if roles:
            payload["roles"] = roles

        if channel_id:
            payload["channel_id"] = channel_id

        if mute:
            payload["mute"] = mute

        if deaf:
            payload["deaf"] = deaf

        if communication_disabled_until:
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
