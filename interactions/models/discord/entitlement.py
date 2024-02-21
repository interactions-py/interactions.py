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
    application_id: Snowflake_Type = attrs.field(repr=False, converter=to_snowflake)
    type: EntitlementType = attrs.field(repr=False, converter=EntitlementType)
    deleted: bool = attrs.field(repr=False, converter=bool)
    subscription_id: Optional[Snowflake_Type] = attrs.field(repr=False, converter=to_optional_snowflake, default=None)
    starts_at: Optional[Timestamp] = attrs.field(repr=False, converter=optional_c(timestamp_converter), default=None)
    ends_at: Optional[Timestamp] = attrs.field(repr=False, converter=optional_c(timestamp_converter), default=None)
    _user_id: Optional[Snowflake_Type] = attrs.field(repr=False, converter=to_optional_snowflake, default=None)
    _guild_id: Optional[Snowflake_Type] = attrs.field(repr=False, converter=to_optional_snowflake, default=None)

    @property
    def user(self) -> "User | None":
        return self.client.cache.get_user(self._user_id)

    @property
    def guild(self) -> "Guild | None":
        return self.client.cache.get_guild(self._guild_id)
