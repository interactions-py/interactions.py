from typing import TYPE_CHECKING, Any, List, Optional, Union

from ...utils.attrs_utils import ClientSerializerMixin, DictSerializerMixin, define, field
from ...utils.missing import MISSING
from ..error import LibraryException
from .misc import IDMixin, Image, Snowflake

if TYPE_CHECKING:
    from .guild import Guild

__all__ = (
    "Role",
    "RoleTags",
)


@define()
class RoleTags(DictSerializerMixin):
    """
    A class object representing the tags of a role.

    :ivar Optional[Snowflake] bot_id?: The id of the bot this role belongs to
    :ivar Optional[Snowflake] integration_id?: The id of the integration this role belongs to
    :ivar Optional[Any] premium_subscriber?: Whether if this is the guild's premium subscriber role
    """

    bot_id: Optional[Snowflake] = field(converter=Snowflake, default=None)
    integration_id: Optional[Snowflake] = field(converter=Snowflake, default=None)
    premium_subscriber: Optional[Any] = field(default=None)

    # TODO: Figure out what actual type it returns, all it says is null.


@define()
class Role(ClientSerializerMixin, IDMixin):
    """
    A class object representing a role.

    :ivar Snowflake id: Role ID
    :ivar str name: Role name
    :ivar int color: Role color in integer representation
    :ivar bool hoist: A status denoting if this role is hoisted
    :ivar Optional[str] icon?: Role icon hash, if any.
    :ivar Optional[str] unicode_emoji?: Role unicode emoji
    :ivar int position: Role position
    :ivar str permissions: Role permissions as a bit set
    :ivar bool managed: A status denoting if this role is managed by an integration
    :ivar bool mentionable: A status denoting if this role is mentionable
    :ivar Optional[RoleTags] tags?: The tags this role has
    """

    id: Snowflake = field(converter=Snowflake)
    name: str = field()
    color: int = field()
    hoist: bool = field()
    icon: Optional[str] = field(default=None, repr=False)
    unicode_emoji: Optional[str] = field(default=None)
    position: int = field()
    permissions: str = field()
    managed: bool = field()
    mentionable: bool = field()
    tags: Optional[RoleTags] = field(converter=RoleTags, default=None)

    @property
    def mention(self) -> str:
        """
        Returns a string that allows you to mention the given role.

        :return: The string of the mentioned role.
        :rtype: str
        """
        return f"<@&{self.id}>"

    async def delete(
        self,
        guild_id: Union[int, Snowflake, "Guild"],
        reason: Optional[str] = None,
    ) -> None:
        """
        Deletes the role from the guild.

        :param guild_id: The id of the guild to delete the role from
        :type guild_id: int
        :param reason: The reason for the deletion
        :type reason: Optional[str]
        """
        if not self._client:
            raise LibraryException(code=13)

        _guild_id = int(guild_id) if isinstance(guild_id, (int, Snowflake)) else int(guild_id.id)

        await self._client.delete_guild_role(
            guild_id=_guild_id, role_id=int(self.id), reason=reason
        )

    async def modify(
        self,
        guild_id: Union[int, Snowflake, "Guild"],
        name: Optional[str] = MISSING,
        permissions: Optional[int] = MISSING,
        color: Optional[int] = MISSING,
        hoist: Optional[bool] = MISSING,
        icon: Optional[Image] = MISSING,
        unicode_emoji: Optional[str] = MISSING,
        mentionable: Optional[bool] = MISSING,
        reason: Optional[str] = None,
    ) -> "Role":
        """
        Edits the role in a guild.

        :param guild_id: The id of the guild to edit the role on
        :type guild_id: int
        :param name?: The name of the role, defaults to the current value of the role
        :type name?: Optional[str]
        :param color?: RGB color value as integer, defaults to the current value of the role
        :type color?: Optional[int]
        :param permissions?: Bitwise value of the enabled/disabled permissions, defaults to the current value of the role
        :type permissions?: Optional[int]
        :param hoist?: Whether the role should be displayed separately in the sidebar, defaults to the current value of the role
        :type hoist?: Optional[bool]
        :param icon?: The role's icon image (if the guild has the ROLE_ICONS feature), defaults to the current value of the role
        :type icon?: Optional[Image]
        :param unicode_emoji?: The role's unicode emoji as a standard emoji (if the guild has the ROLE_ICONS feature), defaults to the current value of the role
        :type unicode_emoji?: Optional[str]
        :param mentionable?: Whether the role should be mentionable, defaults to the current value of the role
        :type mentionable?: Optional[bool]
        :param reason?: The reason why the role is edited, default ``None``
        :type reason?: Optional[str]
        :return: The modified role object
        :rtype: Role
        """
        if not self._client:
            raise LibraryException(code=13)
        _name = self.name if name is MISSING else name
        _color = self.color if color is MISSING else color
        _hoist = self.hoist if hoist is MISSING else hoist
        _mentionable = self.mentionable if mentionable is MISSING else mentionable
        _permissions = self.permissions if permissions is MISSING else permissions
        _icon = self.icon if icon is MISSING else icon
        _unicode_emoji = self.unicode_emoji if unicode_emoji is MISSING else unicode_emoji
        _guild_id = int(guild_id) if isinstance(guild_id, (int, Snowflake)) else int(guild_id.id)

        payload = dict(
            name=_name,
            color=_color,
            hoist=_hoist,
            mentionable=_mentionable,
            permissions=_permissions,
            icon=_icon,
            unicode_emoji=_unicode_emoji,
        )

        res = await self._client.modify_guild_role(
            guild_id=_guild_id,
            role_id=int(self.id),
            payload=payload,
            reason=reason,
        )

        self.update(res)

        return self

    async def modify_position(
        self,
        guild_id: Union[int, Snowflake, "Guild"],
        position: int,
        reason: Optional[str] = None,
    ) -> List["Role"]:
        """
        Modifies the position of a role in the guild.

        :param guild_id: The id of the guild to modify the role position on
        :type guild_id: int
        :param position: The new position of the role
        :type position: int
        :param reason?: The reason for the modifying
        :type reason?: Optional[str]
        :return: List of guild roles with updated hierarchy
        :rtype: List[Role]
        """
        if not self._client:
            raise LibraryException(code=13)

        _guild_id = int(guild_id) if isinstance(guild_id, (int, Snowflake)) else int(guild_id.id)

        res = await self._client.modify_guild_role_positions(
            guild_id=_guild_id,
            payload=[{"position": position, "id": int(self.id)}],
            reason=reason,
        )
        return [Role(**role, _client=self._client) for role in res]
