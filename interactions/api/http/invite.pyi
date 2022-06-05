from typing import Optional

from ...api.cache import Cache
from .request import _Request

class InviteRequest:

    _req: _Request
    cache: Cache
    def __init__(self) -> None: ...
    async def get_invite(
        self,
        invite_code: str,
        with_counts: bool = None,
        with_expiration: bool = None,
        guild_scheduled_event_id: int = None,
    ) -> dict: ...
    async def delete_invite(self, invite_code: str, reason: Optional[str] = None) -> dict: ...
