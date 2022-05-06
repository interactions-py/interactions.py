from typing import List, Optional

from ...api.cache import Cache
from .request import _Request

class MemberRequest:

    __slots__ = ("_req", "cache")

    _req: _Request
    cache: Cache

    def __init__(self) -> None: ...
    async def get_member(self, guild_id: int, member_id: int) -> Optional[dict]: ...
    async def get_list_of_members(
        self, guild_id: int, limit: int = 1, after: Optional[int] = None
    ) -> List[dict]: ...
    async def search_guild_members(self, guild_id: int, query: str, limit: int = 1) -> List[dict]: ...
    async def add_member_role(
        self, guild_id: int, user_id: int, role_id: int, reason: Optional[str] = None
    ) -> None: ...
    async def remove_member_role(
        self, guild_id: int, user_id: int, role_id: int, reason: Optional[str] = None
    ) -> None: ...
    async def modify_member(
        self, user_id: int, guild_id: int, payload: dict, reason: Optional[str] = None
    ) -> dict: ...
