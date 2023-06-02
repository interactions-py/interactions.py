import copy
from typing import TYPE_CHECKING

import interactions.api.events as events
from interactions.api.events.discord import (
    BanCreate,
    BanRemove,
    GuildAuditLogEntryCreate,
    GuildEmojisUpdate,
    IntegrationCreate,
    IntegrationUpdate,
    IntegrationDelete,
    GuildStickersUpdate,
    WebhooksUpdate,
)
from interactions.client.const import MISSING
from interactions.models import AuditLogEntry, GuildIntegration, Sticker, to_snowflake
from ._template import EventMixinTemplate, Processor

if TYPE_CHECKING:
    from interactions.api.events import RawGatewayEvent

__all__ = ("GuildEvents",)


class GuildEvents(EventMixinTemplate):
    @Processor.define()
    async def _on_raw_guild_create(self, event: "RawGatewayEvent") -> None:
        """
        Automatically cache a guild upon GUILD_CREATE event from gateway.

        Args:
            event: raw guild create event

        """
        new_guild = not self.cache.get_guild(event.data["id"])
        guild = self.cache.place_guild_data(event.data)

        self._user._guild_ids.add(to_snowflake(event.data.get("id")))

        self._guild_event.set()

        if self.fetch_members and not guild.chunked.is_set():
            # delays events until chunking has completed
            await guild.chunk()

        if new_guild:
            self.dispatch(events.GuildJoin(guild.id))
        else:
            self.dispatch(events.GuildAvailable(guild.id))

    @Processor.define()
    async def _on_raw_guild_update(self, event: "RawGatewayEvent") -> None:
        before = copy.copy(await self.cache.fetch_guild(event.data.get("id")))
        self.dispatch(events.GuildUpdate(before or MISSING, self.cache.place_guild_data(event.data)))

    @Processor.define()
    async def _on_raw_guild_delete(self, event: "RawGatewayEvent") -> None:
        guild_id = int(event.data.get("id"))
        if event.data.get("unavailable", False):
            self.dispatch(events.GuildUnavailable(guild_id))
        else:
            # noinspection PyProtectedMember
            if guild_id in self._user._guild_ids:
                # noinspection PyProtectedMember
                self._user._guild_ids.remove(guild_id)

            # get the guild right before deleting it
            guild = self.cache.get_guild(guild_id)
            self.cache.delete_guild(guild_id)

            self.dispatch(events.GuildLeft(guild_id, guild))

    @Processor.define()
    async def _on_raw_guild_ban_add(self, event: "RawGatewayEvent") -> None:
        self.dispatch(BanCreate(event.data.get("guild_id"), self.cache.place_user_data(event.data.get("user"))))

    @Processor.define()
    async def _on_raw_guild_ban_remove(self, event: "RawGatewayEvent") -> None:
        self.dispatch(BanRemove(event.data.get("guild_id"), self.cache.place_user_data(event.data.get("user"))))

    @Processor.define()
    async def _on_raw_integration_create(self, event: "RawGatewayEvent") -> None:
        self.dispatch(IntegrationCreate(GuildIntegration.from_dict(event.data, self)))  # type: ignore

    @Processor.define()
    async def _on_raw_integration_update(self, event: "RawGatewayEvent") -> None:
        self.dispatch(IntegrationUpdate(GuildIntegration.from_dict(event.data, self)))  # type: ignore

    @Processor.define()
    async def _on_raw_integration_delete(self, event: "RawGatewayEvent") -> None:
        self.dispatch(
            IntegrationDelete(event.data.get("guild_id"), event.data.get("id"), event.data.get("application_id"))
        )

    @Processor.define()
    async def _on_raw_guild_emojis_update(self, event: "RawGatewayEvent") -> None:
        guild_id = event.data.get("guild_id")
        emojis = event.data.get("emojis")

        if self.cache.emoji_cache:
            before = [copy.copy(self.cache.get_emoji(emoji["id"])) for emoji in emojis]
        else:
            before = []

        after = [self.cache.place_emoji_data(guild_id, emoji) for emoji in emojis]

        self.dispatch(
            GuildEmojisUpdate(
                guild_id=guild_id,
                before=before,
                after=after,
            )
        )

    @Processor.define()
    async def _on_raw_guild_stickers_update(self, event: "RawGatewayEvent") -> None:
        self.dispatch(
            GuildStickersUpdate(event.data.get("guild_id"), Sticker.from_list(event.data.get("stickers", []), self))
        )

    @Processor.define()
    async def _on_raw_webhook_update(self, event: "RawGatewayEvent") -> None:
        self.dispatch(WebhooksUpdate(event.data.get("guild_id"), event.data.get("channel_id")))

    @Processor.define()
    async def _on_raw_guild_audit_log_entry_create(self, event: "RawGatewayEvent") -> None:
        self.dispatch(GuildAuditLogEntryCreate(event.data.get("guild_id"), AuditLogEntry.from_dict(event.data, self)))
