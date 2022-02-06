from typing import TYPE_CHECKING, List, Optional, Union

from ..cache import Item
from .misc import MISSING, DictSerializerMixin, Snowflake

if TYPE_CHECKING:
    from ..http import HTTPClient


class RoleTags(DictSerializerMixin):
    """
    A class object representing the tags of a role.

    :ivar Optional[Snowflake] bot_id?: The id of the bot this role belongs to
    :ivar Optional[Snowflake] integration_id?: The id of the integration this role belongs to
    :ivar Optional[Any] premium_subscriber?: Whether if this is the guild's premium subscriber role
    """

    __slots__ = ("_json", "id", "bot_id", "integration_id", "premium_subscriber")

    # TODO: Figure out what actual type it returns, all it says is null.

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = Snowflake(self.id) if self._json.get("id") else None
        self.bot_id = Snowflake(self.bot_id) if self._json.get("bot_id") else None
        self.integration_id = (
            Snowflake(self.integration_id) if self._json.get("integration_id") else None
        )


class Role(DictSerializerMixin):
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

    __slots__ = (
        "_json",
        "id",
        "name",
        "color",
        "hoist",
        "icon",
        "unicode_emoji",
        "position",
        "managed",
        "mentionable",
        "tags",
        "permissions",
        "_client",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = Snowflake(self.id) if self._json.get("id") else None
        self.tags = RoleTags(**self.tags) if self._json.get("tags") else None

    @classmethod
    async def fetch(
        cls,
        guild_id: int,
        role_ids: Optional[Union[int, List[int]]] = None,
        *,
        cache: bool = True,
        http: "HTTPClient"
    ) -> "Role":
        """
        Fetches a role or roles from the cache or the Discord API.

        :param guild_id: The ID of the role's guild.
        :type guild_id: int
        :param role_ids?: The ID of the role to fetch.
        :type role_ids: int
        :param cache?: Whether to get from cache.
        :type cache: bool
        :param http: The HTTPClient to use to fetch the role(s).
        :type http: HTTPClient
        :return: The role(s).
        :rtype: Guild
        """
        if isinstance(role_ids, int):
            data = http.cache.roles.get(str(role_ids)) if cache else None
            if not data:
                roles = await http.get_all_roles(guild_id)
                for role in roles:
                    if int(role["id"]) == role_ids:
                        data = role
                        break
            if not data:
                return
            data = data if isinstance(data, dict) else data._json
            data["_client"] = http
            model = cls(**data)
            http.cache.roles.add(Item(str(role_ids), model))
            return model
        elif isinstance(role_ids, list):
            roles = []
            for role_id in role_ids:
                data = http.cache.roles.get(str(role_id)) if cache else None
                if not data:
                    roles_ = await http.get_all_roles(guild_id)
                    for role in roles_:
                        if int(role["id"]) == role_id:
                            data = role
                            break
                if not data:
                    continue
                data = data if isinstance(data, dict) else data._json
                data["_client"] = http
                model = cls(**data)
                http.cache.roles.add(Item(str(role_id), model))
                roles.append(model)
            return roles
        else:
            roles = [
                cls(**role, _client=http)
                for role in await http.get_all_roles(guild_id)
                if role.get("id")
            ]
            for role in roles:
                http.cache.roles.add(Item(str(role.id), role))

    async def delete(
        self,
        guild_id: int,
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
            raise AttributeError("HTTPClient not found!")
        await self._client.delete_guild_role(
            guild_id=guild_id, role_id=int(self.id), reason=reason
        ),

    async def modify(
        self,
        guild_id: int,
        name: Optional[str] = MISSING,
        # permissions,
        color: Optional[int] = MISSING,
        hoist: Optional[bool] = MISSING,
        # icon,
        # unicode_emoji,
        mentionable: Optional[bool] = MISSING,
        reason: Optional[str] = None,
    ) -> "Role":
        """
        Edits the role in a guild.

        :param guild_id: The id of the guild to edit the role on
        :type guild_id: int
        :param name?: The name of the role, defaults to the current value of the role
        :type name: Optional[str]
        :param color?: RGB color value as integer, defaults to the current value of the role
        :type color: Optional[int]
        :param hoist?: Whether the role should be displayed separately in the sidebar, defaults to the current value of the role
        :type hoist: Optional[bool]
        :param mentionable?: Whether the role should be mentionable, defaults to the current value of the role
        :type mentionable: Optional[bool]
        :param reason?: The reason why the role is edited, default ``None``
        :type reason: Optional[str]
        :return: The modified role object
        :rtype: Role
        """
        if not self._client:
            raise AttributeError("HTTPClient not found!")
        _name = self.name if name is MISSING else name
        _color = self.color if color is MISSING else color
        _hoist = self.hoist if hoist is MISSING else hoist
        _mentionable = self.mentionable if mentionable is MISSING else mentionable

        payload = Role(name=_name, color=_color, hoist=_hoist, mentionable=_mentionable)

        res = await self._client.modify_guild_role(
            guild_id=guild_id,
            role_id=int(self.id),
            data=payload._json,
            reason=reason,
        )
        model = Role(**res, _client=self._client)
        self._client.cache.roles.add(Item(str(self.id), model))
        return model

    async def modify_position(
        self,
        guild_id: int,
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
        :type reason: Optional[str]
        :return: List of guild roles with updated hierarchy
        :rtype: List[Role]
        """
        if not self._client:
            raise AttributeError("HTTPClient not found!")
        res = await self._client.modify_guild_role_position(
            guild_id=guild_id, position=position, role_id=int(self.id), reason=reason
        )
        roles = [Role(**role, _client=self._client) for role in res]
        for role in roles:
            self._client.cache.roles.add(Item(str(role.id), role))
        return roles
