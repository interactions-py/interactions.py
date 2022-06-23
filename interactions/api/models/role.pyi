from typing import Any, List, Optional, Union

from .attrs_utils import ClientSerializerMixin, DictSerializerMixin, define
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
    async def delete(self, guild_id: Union[int, Snowflake, "Guild"], reason: Optional[str] = ...) -> None: ...  # noqa
    async def modify(
        self,
        guild_id: Union[int, Snowflake, "Guild"],  # noqa
        name: Optional[str] = ...,
        color: Optional[int] = ...,
        hoist: Optional[bool] = ...,
        mentionable: Optional[bool] = ...,
        reason: Optional[str] = ...,
    ) -> Role: ...
    async def modify_position(
        self, guild_id: Union[int, Snowflake, "Guild"], position: int, reason: Optional[str] = ...  # noqa
    ) -> List[Role]: ...
