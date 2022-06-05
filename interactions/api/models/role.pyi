from typing import Any, List, Optional

from .attrs_utils import DictSerializerMixin, ClientSerializerMixin, define, MISSING
from .misc import Snowflake, Image
from ..http.client import HTTPClient


@define()
class RoleTags(DictSerializerMixin):
    bot_id: Optional[Snowflake]
    integration_id: Optional[Snowflake]
    premium_subscriber: Optional[Any]


@define()
class Role(ClientSerializerMixin):
    id: Snowflake
    name: str
    color: int
    hoist: bool
    icon: Optional[str]
    unicode_emoji: Optional[str]
    position: int
    permissions: str
    managed: bool
    mentionable: bool
    tags: Optional[RoleTags]
    @property
    def mention(self) -> str: ...
    async def delete(
        self,
        guild_id: int,
        reason: Optional[str] = None,
    ) -> None: ...
    async def modify(
        self,
        guild_id: int,
        name: Optional[str] = MISSING,
        permissions: Optional[int] = MISSING,
        color: Optional[int] = MISSING,
        hoist: Optional[bool] = MISSING,
        icon: Optional[Image] = MISSING,
        unicode_emoji: Optional[str] = MISSING,
        mentionable: Optional[bool] = MISSING,
        reason: Optional[str] = None,
    ) -> Role: ...
    async def modify_position(
        self,
        guild_id: int,
        position: int,
        reason: Optional[str] = None,
    ) -> List[Role]: ...
