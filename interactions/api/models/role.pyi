from typing import Any, Optional, List

from .misc import DictSerializerMixin, MISSING, Snowflake
from ..http.client import HTTPClient

class RoleTags(DictSerializerMixin):
    _json: dict
    bot_id: Optional[Snowflake]
    integration_id: Optional[Snowflake]
    premium_subscriber: Optional[Any]
    def __init__(self, **kwargs): ...

class Role(DictSerializerMixin):
    _json: dict
    _client: HTTPClient
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
    def __init__(self, **kwargs): ...
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
        # permissions,
        color: Optional[int] = MISSING,
        hoist: Optional[bool] = MISSING,
        # icon,
        # unicode_emoji,
        mentionable: Optional[bool] = MISSING,
        reason: Optional[str] = None,
    ) -> "Role": ...
    async def modify_position(
        self,
        guild_id: int,
        position: int,
        reason: Optional[str] = None,
    ) -> List["Role"]: ...
