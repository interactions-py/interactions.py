import copy
from typing import TYPE_CHECKING

import interactions.api.events as events
from interactions.client.const import MISSING
from ._template import EventMixinTemplate, Processor

if TYPE_CHECKING:
    from interactions.api.events import RawGatewayEvent

__all__ = ("RoleEvents",)


class RoleEvents(EventMixinTemplate):
    @Processor.define()
    async def _on_raw_guild_role_create(self, event: "RawGatewayEvent") -> None:
        g_id = int(event.data.get("guild_id"))
        r_id = int(event.data["role"]["id"])

        guild = self.cache.get_guild(g_id)
        guild._role_ids.add(r_id)

        role = self.cache.place_role_data(g_id, [event.data.get("role")])[r_id]
        self.dispatch(events.RoleCreate(g_id, role))

    @Processor.define()
    async def _on_raw_guild_role_update(self, event: "RawGatewayEvent") -> None:
        g_id = int(event.data.get("guild_id"))
        r_data = event.data.get("role")
        before = copy.copy(self.cache.get_role(r_data["id"]) or MISSING)

        after = self.cache.place_role_data(g_id, [r_data])
        after = after[int(event.data["role"]["id"])]

        self.dispatch(events.RoleUpdate(g_id, before, after))

    @Processor.define()
    async def _on_raw_guild_role_delete(self, event: "RawGatewayEvent") -> None:
        g_id = int(event.data.get("guild_id"))
        r_id = int(event.data.get("role_id"))

        guild = self.cache.get_guild(g_id)
        role = self.cache.get_role(r_id)

        self.cache.delete_role(r_id)

        role_members = (member for member in guild.members if member.has_role(r_id))
        for member in role_members:
            member._role_ids.remove(r_id)

        self.dispatch(events.RoleDelete(g_id, r_id, role))
