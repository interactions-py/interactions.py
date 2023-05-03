from functools import partial, total_ordering
from typing import Any, TYPE_CHECKING

import attrs

from interactions.client.const import MISSING, T, Missing
from interactions.client.utils import nulled_boolean_get
from interactions.client.utils.attr_converters import optional as optional_c
from interactions.client.utils.serializer import dict_filter
from interactions.models.discord.asset import Asset
from interactions.models.discord.color import COLOR_TYPES, Color, process_color
from interactions.models.discord.emoji import PartialEmoji
from interactions.models.discord.enums import Permissions
from .base import DiscordObject

if TYPE_CHECKING:
    from interactions.client import Client
    from interactions.models.discord.guild import Guild
    from interactions.models.discord.user import Member
    from interactions.models.discord.snowflake import Snowflake_Type

__all__ = ("Role",)


def sentinel_converter(value: bool | T | None, sentinel: T = attrs.NOTHING) -> bool | T:
    if value is sentinel:
        return False
    return True if value is None else value


@attrs.define(eq=False, order=False, hash=False, kw_only=True)
@total_ordering
class Role(DiscordObject):
    _sentinel = object()

    name: str = attrs.field(repr=True)
    color: "Color" = attrs.field(repr=False, converter=Color)
    hoist: bool = attrs.field(repr=False, default=False)
    position: int = attrs.field(repr=True)
    permissions: "Permissions" = attrs.field(repr=False, converter=Permissions)
    managed: bool = attrs.field(repr=False, default=False)
    mentionable: bool = attrs.field(repr=False, default=True)
    premium_subscriber: bool = attrs.field(
        repr=False, default=_sentinel, converter=partial(sentinel_converter, sentinel=_sentinel)
    )
    subscription_listing_id: "Snowflake_Type | None" = attrs.field(default=None, repr=False)
    purchasable_or_has_subscribers: bool = attrs.field(default=False)
    _icon: Asset | None = attrs.field(repr=False, default=None)
    _unicode_emoji: PartialEmoji | None = attrs.field(
        repr=False, default=None, converter=optional_c(PartialEmoji.from_str)
    )
    _guild_id: "Snowflake_Type" = attrs.field(
        repr=False,
    )
    _bot_id: "Snowflake_Type | None" = attrs.field(repr=False, default=None)
    _integration_id: "Snowflake_Type | None" = attrs.field(repr=False, default=None)  # todo integration object?
    _guild_connections: bool = attrs.field(repr=False, default=False)

    def __lt__(self: "Role", other: "Role") -> bool:
        if not isinstance(self, Role) or not isinstance(other, Role):
            return NotImplemented

        if self._guild_id != other._guild_id:
            raise RuntimeError("Unable to compare Roles from different guilds.")

        if self.id == self._guild_id:  # everyone role
            # everyone role is on the bottom, so check if the other role is, well, not it
            # because then it must be higher than it
            return other.id != self.id

        if self.position < other.position:
            return True

        return self.id < other.id if self.position == other.position else False

    @classmethod
    def _process_dict(cls, data: dict[str, Any], client: "Client") -> dict[str, Any]:
        data |= data.pop("tags", {})

        if icon_hash := data.get("icon"):
            data["icon"] = Asset.from_path_hash(client, f"role-icons/{data['id']}/{{}}", icon_hash)

        data["premium_subscriber"] = nulled_boolean_get(data, "premium_subscriber")
        data["guild_connections"] = nulled_boolean_get(data, "guild_connections")
        data["available_for_purchase"] = nulled_boolean_get(data, "available_for_purchase")

        return data

    async def fetch_bot(self, *, force: bool = False) -> "Member | None":
        """
        Fetch the bot associated with this role if any.

        Args:
            force: Whether to force fetch the bot from the API.

        Returns:
            Member object if any

        """
        if self._bot_id is None:
            return None
        return await self._client.cache.fetch_member(self._guild_id, self._bot_id, force=force)

    def get_bot(self) -> "Member | None":
        """
        Get the bot associated with this role if any.

        Returns:
            Member object if any

        """
        if self._bot_id is None:
            return None
        return self._client.cache.get_member(self._guild_id, self._bot_id)

    @property
    def guild(self) -> "Guild":
        """The guild object this role is from."""
        return self._client.cache.get_guild(self._guild_id)  # pyright: ignore [reportGeneralTypeIssues]

    @property
    def default(self) -> bool:
        """Is this the `@everyone` role."""
        return self.id == self._guild_id

    @property
    def bot_managed(self) -> bool:
        """Is this role owned/managed by a bot."""
        return self._bot_id is not None

    @property
    def is_linked_role(self) -> bool:
        """Is this role a linked role."""
        return self._guild_connections

    @property
    def mention(self) -> str:
        """Returns a string that would mention the role."""
        return f"<@&{self.id}>" if self.id != self._guild_id else "@everyone"

    @property
    def integration(self) -> bool:
        """Is this role owned/managed by an integration."""
        return self._integration_id is not None

    @property
    def members(self) -> list["Member"]:
        """List of members with this role"""
        return [member for member in self.guild.members if member.has_role(self)]

    @property
    def icon(self) -> Asset | PartialEmoji | None:
        """
        The icon of this role

        !!! note
            You have to use this method instead of the `_icon` attribute, because the first does account for unicode emojis
        """
        return self._icon or self._unicode_emoji

    @property
    def is_assignable(self) -> bool:
        """
        Can this role be assigned or removed by this bot?

        !!! note
            This does not account for permissions, only the role hierarchy

        """
        return (self.default or self.guild.me.top_role > self) and not self.managed

    async def delete(self, reason: str | Missing = MISSING) -> None:
        """
        Delete this role.

        Args:
            reason: An optional reason for this deletion

        """
        await self._client.http.delete_guild_role(self._guild_id, self.id, reason)

    async def edit(
        self,
        *,
        name: str | None = None,
        permissions: str | None = None,
        color: Color | COLOR_TYPES | None = None,
        hoist: bool | None = None,
        mentionable: bool | None = None,
    ) -> "Role":
        """
        Edit this role, all arguments are optional.

        Args:
            name: name of the role
            permissions: New permissions to use
            color: The color of the role
            hoist: whether the role should be displayed separately in the sidebar
            mentionable: whether the role should be mentionable

        Returns:
            Role with updated information

        """
        color = process_color(color)

        payload = dict_filter(
            {
                "name": name,
                "permissions": permissions,
                "color": color,
                "hoist": hoist,
                "mentionable": mentionable,
            }
        )

        r_data = await self._client.http.modify_guild_role(self._guild_id, self.id, payload)
        r_data = dict(r_data)  # to convert typed dict to regular dict
        r_data["guild_id"] = self._guild_id
        return self.from_dict(r_data, self._client)

    async def move(self, position: int, reason: str | Missing = MISSING) -> "Role":
        """
        Move this role to a new position.

        Args:
            position: The new position of the role
            reason: An optional reason for this move

        Returns:
            The role object

        """
        await self._client.http.modify_guild_role_positions(
            self._guild_id, [{"id": self.id, "position": position}], reason
        )
        return self
