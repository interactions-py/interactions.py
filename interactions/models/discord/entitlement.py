from typing import Optional, TYPE_CHECKING

import attrs

from interactions.models.discord.timestamp import Timestamp
from interactions.models.discord.enums import EntitlementType
from interactions.models.discord.base import DiscordObject
from interactions.client.utils.attr_converters import optional as optional_c
from interactions.client.utils.attr_converters import timestamp_converter
from interactions.models.discord.snowflake import to_snowflake, to_optional_snowflake, Snowflake_Type

if TYPE_CHECKING:
    from interactions.models.discord.guild import Guild
    from interactions.models.discord.user import User

__all__ = ("Entitlement",)


@attrs.define(eq=False, order=False, hash=False, kw_only=False)
class Entitlement(DiscordObject):
    sku_id: Snowflake_Type = attrs.field(repr=False, converter=to_snowflake)
    """ID of the SKU."""
    application_id: Snowflake_Type = attrs.field(repr=False, converter=to_snowflake)
    """ID of the parent application."""
    type: EntitlementType = attrs.field(repr=False, converter=EntitlementType)
    """The type of entitlement."""
    deleted: bool = attrs.field(repr=False, converter=bool)
    """Whether the entitlement is deleted."""
    subscription_id: Optional[Snowflake_Type] = attrs.field(repr=False, converter=to_optional_snowflake, default=None)
    """The ID of the subscription plan. Not present when using test entitlements."""
    starts_at: Optional[Timestamp] = attrs.field(repr=False, converter=optional_c(timestamp_converter), default=None)
    """Start date at which the entitlement is valid. Not present when using test entitlements."""
    ends_at: Optional[Timestamp] = attrs.field(repr=False, converter=optional_c(timestamp_converter), default=None)
    """Date at which the entitlement is no longer valid. Not present when using test entitlements."""
    _user_id: Optional[Snowflake_Type] = attrs.field(repr=False, converter=to_optional_snowflake, default=None)
    """The ID of the user that is granted access to the entitlement's SKU."""
    _guild_id: Optional[Snowflake_Type] = attrs.field(repr=False, converter=to_optional_snowflake, default=None)
    """The ID of the guild that is granted access to the entitlement's SKU."""

    @property
    def user(self) -> "Optional[User]":
        """The user that is granted access to the entitlement's SKU, if applicable."""
        return self.client.cache.get_user(self._user_id)

    @property
    def guild(self) -> "Optional[Guild]":
        """The guild that is granted access to the entitlement's SKU, if applicable."""
        return self.client.cache.get_guild(self._guild_id)
