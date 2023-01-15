from typing import TYPE_CHECKING, Optional

import attrs

from interactions.client.const import MISSING, Absent
from interactions.models.discord.enums import StagePrivacyLevel
from interactions.models.discord.snowflake import to_snowflake
from .base import DiscordObject

if TYPE_CHECKING:
    from interactions.models import Guild, GuildStageVoice, Snowflake_Type

__all__ = ("StageInstance",)


@attrs.define(eq=False, order=False, hash=False, kw_only=True)
class StageInstance(DiscordObject):
    topic: str = attrs.field(
        repr=False,
    )
    privacy_level: StagePrivacyLevel = attrs.field(
        repr=False,
    )
    discoverable_disabled: bool = attrs.field(
        repr=False,
    )

    _guild_id: "Snowflake_Type" = attrs.field(repr=False, converter=to_snowflake)
    _channel_id: "Snowflake_Type" = attrs.field(repr=False, converter=to_snowflake)

    @property
    def guild(self) -> "Guild":
        return self._client.cache.get_guild(self._guild_id)

    @property
    def channel(self) -> "GuildStageVoice":
        return self._client.cache.get_channel(self._channel_id)

    async def delete(self, reason: Absent[Optional[str]] = MISSING) -> None:
        """
        Delete this stage instance. Effectively closes the stage.

        Args:
            reason: The reason for this deletion, for the audit log

        """
        await self._client.http.delete_stage_instance(self._channel_id, reason)
