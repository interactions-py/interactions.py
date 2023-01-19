import copy
from typing import TYPE_CHECKING

import interactions.api.events as events
from interactions.client.const import MISSING
from ._template import EventMixinTemplate, Processor

if TYPE_CHECKING:
    from interactions.api.events import RawGatewayEvent

__all__ = ("MemberEvents",)


class MemberEvents(EventMixinTemplate):
    @Processor.define()
    async def _on_raw_guild_member_add(self, event: "RawGatewayEvent") -> None:
        g_id = event.data.pop("guild_id")
        member = self.cache.place_member_data(g_id, event.data)
        if guild := self.cache.get_guild(g_id):
            guild.member_count += 1
        self.dispatch(events.MemberAdd(g_id, member))

    @Processor.define()
    async def _on_raw_guild_member_remove(self, event: "RawGatewayEvent") -> None:
        g_id = event.data.pop("guild_id")
        user = self.cache.place_user_data(event.data["user"])
        member = self.cache.get_member(g_id, user.id)

        self.cache.delete_member(g_id, user.id)
        if guild := self.cache.get_guild(g_id):
            guild.member_count -= 1

        self.dispatch(events.MemberRemove(g_id, member or user))

    @Processor.define()
    async def _on_raw_guild_member_update(self, event: "RawGatewayEvent") -> None:
        g_id = event.data.pop("guild_id")
        before = copy.copy(self.cache.get_member(g_id, event.data["user"]["id"])) or MISSING
        self.dispatch(events.MemberUpdate(g_id, before, self.cache.place_member_data(g_id, event.data)))
