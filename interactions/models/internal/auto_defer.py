import asyncio
import contextlib
from typing import TYPE_CHECKING

import attrs

from interactions.client.errors import AlreadyDeferred, NotFound, BadRequest, HTTPException

if TYPE_CHECKING:
    from interactions.models.internal.context import InteractionContext

__all__ = ("AutoDefer",)


@attrs.define(eq=False, order=False, hash=False, kw_only=True)
class AutoDefer:
    """Automatically defer application commands for you!"""

    enabled: bool = attrs.field(repr=False, default=False)
    """Whether or not auto-defer is enabled"""

    ephemeral: bool = attrs.field(repr=False, default=False)
    """Should the command be deferred as ephemeral or not"""

    time_until_defer: float = attrs.field(repr=False, default=1.5)
    """How long to wait before automatically deferring"""

    async def __call__(self, ctx: "InteractionContext") -> None:
        if self.enabled:
            if self.time_until_defer > 0:
                loop = asyncio.get_event_loop()
                loop.call_later(self.time_until_defer, loop.create_task, self.defer(ctx))
            else:
                await ctx.defer(ephemeral=self.ephemeral)

    async def defer(self, ctx: "InteractionContext") -> None:
        """Defer the command"""
        if not ctx.responded or not ctx.deferred:
            with contextlib.suppress(AlreadyDeferred, NotFound, BadRequest, HTTPException):
                await ctx.defer(ephemeral=self.ephemeral)
