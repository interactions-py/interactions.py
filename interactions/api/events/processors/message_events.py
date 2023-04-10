import copy
from typing import TYPE_CHECKING

import interactions.api.events as events
from interactions.models import to_snowflake, BaseMessage
from ._template import EventMixinTemplate, Processor

if TYPE_CHECKING:
    from interactions.api.events import RawGatewayEvent

__all__ = ("MessageEvents",)


class MessageEvents(EventMixinTemplate):
    @Processor.define()
    async def _on_raw_message_create(self, event: "RawGatewayEvent") -> None:
        """
        Automatically convert MESSAGE_CREATE event data to the object.

        Args:
            event: raw message event

        """
        msg = self.cache.place_message_data(event.data)
        if not msg._guild_id and event.data.get("guild_id"):
            msg._guild_id = event.data["guild_id"]

        if msg._guild_id and not msg.guild:
            await self.cache.fetch_guild(msg._guild_id)

        if not msg.channel:
            await self.cache.fetch_channel(to_snowflake(msg._channel_id))

        self.dispatch(events.MessageCreate(msg))

    @Processor.define()
    async def _on_raw_message_delete(self, event: "RawGatewayEvent") -> None:
        """
        Process raw deletions and dispatch a processed deletion event.

        Args:
            event: raw message deletion event

        """
        message = self.cache.get_message(
            event.data.get("channel_id"),
            event.data.get("id"),
        )

        if not message:
            message = BaseMessage.from_dict(event.data, self)
        self.cache.delete_message(event.data["channel_id"], event.data["id"])
        self.logger.debug(f"Dispatching Event: {event.resolved_name}")
        self.dispatch(events.MessageDelete(message))

    @Processor.define()
    async def _on_raw_message_update(self, event: "RawGatewayEvent") -> None:
        """
        Process raw message update event and dispatch a processed update event.

        Args:
            event: raw message update event

        """
        # a copy is made because the cache will update the original object in memory
        before = copy.copy(self.cache.get_message(event.data.get("channel_id"), event.data.get("id")))
        after = self.cache.place_message_data(event.data)
        self.dispatch(events.MessageUpdate(before=before, after=after))

    @Processor.define()
    async def _on_raw_message_delete_bulk(self, event: "RawGatewayEvent") -> None:
        """
        Process raw bulk message deletion event and dispatch a processed bulk deletion event.

        Args:
            event: raw bulk message deletion event

        """
        self.dispatch(
            events.MessageDeleteBulk(
                event.data.get("guild_id", None),
                event.data.get("channel_id"),
                event.data.get("ids"),
            )
        )
