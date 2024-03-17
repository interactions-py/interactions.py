from typing import TYPE_CHECKING

from interactions.models.discord.entitlement import Entitlement
import interactions.api.events as events
from ._template import EventMixinTemplate, Processor

if TYPE_CHECKING:
    from interactions.api.events import RawGatewayEvent


class EntitlementEvents(EventMixinTemplate):
    @Processor.define()
    async def _on_raw_entitlement_create(self, event: "RawGatewayEvent") -> None:
        self.dispatch(events.EntitlementCreate(Entitlement.from_dict(event.data, self)))

    @Processor.define()
    async def _on_raw_entitlement_update(self, event: "RawGatewayEvent") -> None:
        self.dispatch(events.EntitlementUpdate(Entitlement.from_dict(event.data, self)))

    @Processor.define()
    async def _on_raw_entitlement_delete(self, event: "RawGatewayEvent") -> None:
        self.dispatch(events.EntitlementDelete(Entitlement.from_dict(event.data, self)))
