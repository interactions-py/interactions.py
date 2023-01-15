from typing import TYPE_CHECKING

import interactions.api.events as events
from interactions.models import StageInstance
from ._template import EventMixinTemplate, Processor

if TYPE_CHECKING:
    from interactions.api.events import RawGatewayEvent

__all__ = ("StageEvents",)


class StageEvents(EventMixinTemplate):
    @Processor.define()
    async def _on_raw_stage_instance_create(self, event: "RawGatewayEvent") -> None:
        self.dispatch(events.StageInstanceCreate(StageInstance.from_dict(event.data, self)))  # type: ignore

    @Processor.define()
    async def _on_raw_stage_instance_update(self, event: "RawGatewayEvent") -> None:
        self.dispatch(events.StageInstanceUpdate(StageInstance.from_dict(event.data, self)))  # type: ignore

    @Processor.define()
    async def _on_raw_stage_instance_delete(self, event: "RawGatewayEvent") -> None:
        self.dispatch(events.StageInstanceDelete(StageInstance.from_dict(event.data, self)))  # type: ignore
