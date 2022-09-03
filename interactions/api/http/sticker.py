from typing import List, Optional

from aiohttp import FormData

from ...api.cache import Cache
from ..models.misc import File
from .request import _Request
from .route import Route

__all__ = ("StickerRequest",)


class StickerRequest:

    _req: _Request
    cache: Cache

    def __init__(self) -> None:
        pass

    async def get_sticker(self, sticker_id: int) -> dict:
        """
        Get a specific sticker.

        :param sticker_id: The id of the sticker
        :return: Sticker or None
        """
        return await self._req.request(Route("GET", f"/stickers/{sticker_id}"))

    async def list_nitro_sticker_packs(self) -> List[dict]:
        """
        Gets the list of sticker packs available to Nitro subscribers.

        :return: List of sticker packs
        """
        return await self._req.request(Route("GET", "/sticker-packs"))

    async def list_guild_stickers(self, guild_id: int) -> List[dict]:
        """
        Get the stickers for a guild.

        :param guild_id: The guild to get stickers from
        :return: List of Stickers or None
        """
        return await self._req.request(Route("GET", f"/guilds/{guild_id}/stickers"))

    async def get_guild_sticker(self, guild_id: int, sticker_id: int) -> dict:
        """
        Get a sticker from a guild.

        :param guild_id: The guild to get stickers from
        :param sticker_id: The sticker to get from the guild
        :return: Sticker or None
        """
        return await self._req.request(Route("GET", f"/guilds/{guild_id}/stickers/{sticker_id}"))

    async def create_guild_sticker(
        self, payload: dict, file: File, guild_id: int, reason: Optional[str] = None
    ) -> dict:
        """
        Create a new sticker for the guild. Requires the MANAGE_EMOJIS_AND_STICKERS permission.

        :param payload: The payload to send.
        :param file: The file to send.
        :param guild_id: The guild to create sticker at.
        :param reason: The reason for this action.
        :return: The new sticker data on success.
        """
        data = FormData()
        data.add_field("file", file._fp, filename=file._filename)
        for key, value in payload.items():
            data.add_field(key, value)

        return await self._req.request(
            Route("POST", f"/guilds/{guild_id}/stickers"), data=data, reason=reason
        )

    async def modify_guild_sticker(
        self, payload: dict, guild_id: int, sticker_id: int, reason: Optional[str] = None
    ) -> dict:
        """
        Modify the given sticker. Requires the MANAGE_EMOJIS_AND_STICKERS permission.

        :param payload: the payload to send.
        :param guild_id: The guild of the target sticker.
        :param sticker_id:  The sticker to modify.
        :param reason: The reason for this action.
        :return: The updated sticker data on success.
        """
        return await self._req.request(
            Route("PATCH", f"/guilds/{guild_id}/stickers/{sticker_id}"), json=payload, reason=reason
        )

    async def delete_guild_sticker(
        self, guild_id: int, sticker_id: int, reason: Optional[str] = None
    ) -> None:
        """
        Delete the given sticker. Requires the MANAGE_EMOJIS_AND_STICKERS permission.

        :param guild_id: The guild of the target sticker.
        :param sticker_id:  The sticker to delete.
        :param reason: The reason for this action.
        :return: Returns 204 No Content on success.
        """
        return await self._req.request(
            Route("DELETE", f"/guilds/{guild_id}/stickers/{sticker_id}"), reason=reason
        )
