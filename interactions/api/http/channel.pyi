from typing import List, Optional

from ...api.cache import Cache
from .request import _Request


class ChannelRequest:

    _req: _Request
    cache: Cache

    def __init__(self) -> None: ...
    async def get_channel(self, channel_id: int) -> dict: ...
    async def delete_channel(self, channel_id: int) -> None: ...
    async def get_channel_messages(
        self,
        channel_id: int,
        limit: int = 50,
        around: Optional[int] = None,
        before: Optional[int] = None,
        after: Optional[int] = None,
    ) -> List[dict]: ...
    async def create_channel(
        self, guild_id: int, payload: dict, reason: Optional[str] = None
    ) -> dict: ...
    async def move_channel(
        self,
        guild_id: int,
        channel_id: int,
        new_pos: int,
        parent_id: Optional[int],
        lock_perms: bool = False,
        reason: Optional[str] = None,
    ) -> dict: ...
    async def modify_channel(
        self, channel_id: int, payload: dict, reason: Optional[str] = None
    ) -> dict: ...
    async def get_channel_invites(self, channel_id: int) -> List[dict]: ...
    async def create_channel_invite(
        self, channel_id: int, payload: dict, reason: Optional[str] = None
    ) -> dict: ...
    async def delete_invite(self, invite_code: str, reason: Optional[str] = None) -> dict: ...
    async def edit_channel_permission(
        self,
        channel_id: int,
        overwrite_id: int,
        allow: str,
        deny: str,
        perm_type: int,
        reason: Optional[str] = None,
    ) -> None: ...
    async def delete_channel_permission(
        self, channel_id: int, overwrite_id: int, reason: Optional[str] = None
    ) -> None: ...
    async def trigger_typing(self, channel_id: int) -> None: ...
    async def get_pinned_messages(self, channel_id: int) -> List[dict]: ...
    async def create_stage_instance(
        self, channel_id: int, topic: str, privacy_level: int = 1, reason: Optional[str] = None
    ) -> dict: ...
    async def get_stage_instance(self, channel_id: int) -> dict: ...
    async def modify_stage_instance(
        self,
        channel_id: int,
        topic: Optional[str] = None,
        privacy_level: Optional[int] = None,
        reason: Optional[str] = None,
    ) -> dict: ...
    async def delete_stage_instance(self, channel_id: int, reason: Optional[str] = None) -> None: ...
