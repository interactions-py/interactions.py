from typing import cast

import discord_typings

from interactions.models.internal.protocols import CanRequest
from ..route import Route

__all__ = ("BotRequests",)


class BotRequests(CanRequest):
    async def get_current_bot_information(self) -> discord_typings.ApplicationData:
        """
        Gets the bot's application object without flags.

        Returns:
            application object

        """
        result = await self.request(Route("GET", "/oauth2/applications/@me"))
        return cast(discord_typings.ApplicationData, result)

    async def get_current_authorisation_information(self) -> dict:  # todo typing?
        """
        Gets info about the current authorization.

        Returns:
            Authorisation information

        """
        result = await self.request(Route("GET", "/oauth2/@me"))
        return cast(dict, result)

    async def list_voice_regions(self) -> list[discord_typings.VoiceRegionData]:
        """
        Gets an array of voice region objects that can be used when setting a voice or stage channel's `rtc_region`.

        Returns:
            an array of voice region objects

        """
        result = await self.request(Route("GET", "/voice/regions"))
        return cast(list[discord_typings.VoiceRegionData], result)
