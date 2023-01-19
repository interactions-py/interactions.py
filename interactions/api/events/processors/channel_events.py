import copy
from typing import TYPE_CHECKING

import interactions.api.events as events
from interactions.client.const import MISSING
from interactions.models.discord.channel import BaseChannel
from interactions.models.discord.invite import Invite
from ._template import EventMixinTemplate, Processor

if TYPE_CHECKING:
    from interactions.api.events import RawGatewayEvent

__all__ = ("ChannelEvents",)


class ChannelEvents(EventMixinTemplate):
    @Processor.define()
    async def _on_raw_channel_create(self, event: "RawGatewayEvent") -> None:
        channel = self.cache.place_channel_data(event.data)
        self.dispatch(events.ChannelCreate(channel))

    @Processor.define()
    async def _on_raw_channel_delete(self, event: "RawGatewayEvent") -> None:
        # for some reason this event returns the deleted channel data?
        # so we create an object from it
        channel = BaseChannel.from_dict_factory(event.data, self)
        self.cache.delete_channel(event.data.get("id"))
        self.dispatch(events.ChannelDelete(channel))

    @Processor.define()
    async def _on_raw_channel_update(self, event: "RawGatewayEvent") -> None:
        before = copy.copy(self.cache.get_channel(event.data.get("id")))
        self.dispatch(events.ChannelUpdate(before=before or MISSING, after=self.cache.place_channel_data(event.data)))

    @Processor.define()
    async def _on_raw_channel_pins_update(self, event: "RawGatewayEvent") -> None:
        channel = await self.cache.fetch_channel(event.data.get("channel_id"))
        channel.last_pin_timestamp = event.data.get("last_pin_timestamp")
        self.dispatch(events.ChannelPinsUpdate(channel, channel.last_pin_timestamp))

    @Processor.define()
    async def _on_raw_invite_create(self, event: "RawGatewayEvent") -> None:
        self.dispatch(events.InviteCreate(Invite.from_dict(event.data, self)))  # type: ignore

    @Processor.define()
    async def _on_raw_invite_delete(self, event: "RawGatewayEvent") -> None:
        self.dispatch(events.InviteDelete(Invite.from_dict(event.data, self)))  # type: ignore
