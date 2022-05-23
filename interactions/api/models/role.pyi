from typing import Any, List, Optional

from .attrs_utils import DictSerializerMixin, ClientSerializerMixin, define
from .misc import Snowflake


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
    async def delete(self, guild_id: int, reason: Optional[str] = ...) -> None: ...

    async def modify(self, guild_id: int, name: Optional[str] = ..., color: Optional[int] = ...,
                     hoist: Optional[bool] = ..., mentionable: Optional[bool] = ...,
                     reason: Optional[str] = ...) -> Role: ...

    async def modify_position(self, guild_id: int, position: int, reason: Optional[str] = ...) -> List[Role]: ...
