from typing import List


from ...api.cache import Cache
from ..models import Snowflake
from .request import _Request


class ScheduledEventRequest:

    __slots__ = ("_req", "cache")

    _req: _Request
    cache: Cache

    def __init__(self) -> None: ...
    async def create_scheduled_event(self, guild_id: Snowflake, payload: dict) -> dict: ...
    async def get_scheduled_event(
        self, guild_id: Snowflake, guild_scheduled_event_id: Snowflake, with_user_count: bool
    ) -> dict: ...
    async def get_scheduled_events(self, guild_id: Snowflake, with_user_count: bool) -> List[dict]: ...
    async def modify_scheduled_event(
        self, guild_id: Snowflake, guild_scheduled_event_id: Snowflake, payload: dict
    ) -> dict: ...
    async def delete_scheduled_event(
        self, guild_id: Snowflake, guild_scheduled_event_id: Snowflake
    ) -> None: ...
    async def get_scheduled_event_users(
        self,
        guild_id: Snowflake,
        guild_scheduled_event_id: Snowflake,
        limit: int = 100,
        with_member: bool = False,
        before: Snowflake = None,
        after: Snowflake = None,
    ) -> dict: ...
