import copy
from typing import TYPE_CHECKING

import interactions.api.events as events
from interactions.client.const import MISSING
from interactions.models import ScheduledEvent
from ._template import EventMixinTemplate, Processor

if TYPE_CHECKING:
    from interactions.api.events import RawGatewayEvent

__all__ = ("ScheduledEvents",)


class ScheduledEvents(EventMixinTemplate):
    @Processor.define()
    async def _on_raw_guild_scheduled_event_create(self, event: "RawGatewayEvent") -> None:
        scheduled_event = self.cache.place_scheduled_event_data(event.data)

        self.dispatch(events.GuildScheduledEventCreate(scheduled_event))

    @Processor.define()
    async def _on_raw_guild_scheduled_event_update(self, event: "RawGatewayEvent") -> None:
        before = copy.copy(self.cache.get_scheduled_event(event.data.get("id")))
        after = self.cache.place_scheduled_event_data(event.data)

        self.dispatch(events.GuildScheduledEventUpdate(before or MISSING, after))

    @Processor.define()
    async def _on_raw_guild_scheduled_event_delete(self, event: "RawGatewayEvent") -> None:
        # for some reason this event returns the deleted scheduled event data?
        # so we create an object from it
        scheduled_event = ScheduledEvent.from_dict(event.data, self)
        self.cache.delete_scheduled_event(event.data.get("id"))

        self.dispatch(events.GuildScheduledEventDelete(scheduled_event))

    @Processor.define()
    async def _on_raw_guild_scheduled_event_user_add(self, event: "RawGatewayEvent") -> None:
        self.dispatch(
            events.GuildScheduledEventUserAdd(
                event.data["guild_id"], event.data["guild_scheduled_event_id"], event.data["user_id"]
            )
        )

    @Processor.define()
    async def _on_raw_guild_scheduled_event_user_remove(self, event: "RawGatewayEvent") -> None:
        self.dispatch(
            events.GuildScheduledEventUserRemove(
                event.data["guild_id"], event.data["guild_scheduled_event_id"], event.data["user_id"]
            )
        )
