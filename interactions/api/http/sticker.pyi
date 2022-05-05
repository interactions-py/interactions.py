from typing import List, Optional

from aiohttp import FormData

from ...api.cache import Cache
from .request import _Request


class StickerRequest:

    _req: _Request
    cache: Cache

    def __init__(self) -> None: ...
    async def get_sticker(self, sticker_id: int) -> dict: ...
    async def list_nitro_sticker_packs(self) -> List[dict]: ...
    async def list_guild_stickers(self, guild_id: int) -> List[dict]: ...
    async def get_guild_sticker(self, guild_id: int, sticker_id: int) -> dict: ...
    async def create_guild_sticker(
        self, payload: FormData, guild_id: int, reason: Optional[str] = None
    ) -> dict: ...
    async def modify_guild_sticker(
        self, payload: dict, guild_id: int, sticker_id: int, reason: Optional[str] = None
    ) -> dict: ...
    async def delete_guild_sticker(
        self, guild_id: int, sticker_id: int, reason: Optional[str] = None
    ) -> None: ...
