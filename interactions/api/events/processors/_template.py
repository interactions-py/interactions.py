import asyncio
import functools
import inspect
from typing import TYPE_CHECKING, Callable, Coroutine

from interactions.client.const import Absent, MISSING
from interactions.models.discord.user import NaffUser

if TYPE_CHECKING:
    from interactions.client.smart_cache import GlobalCache
    from interactions.api.events.internal import BaseEvent

__all__ = ("Processor", "EventMixinTemplate")


class Processor:

    callback: Coroutine
    event_name: str

    def __init__(self, callback: Coroutine, name: str) -> None:
        self.callback = callback
        self.event_name = name

    @classmethod
    def define(cls, event_name: Absent[str] = MISSING) -> Callable[[Coroutine], "Processor"]:
        def wrapper(coro: Coroutine) -> "Processor":
            name = event_name
            if name is MISSING:
                name = coro.__name__
            name = name.lstrip("_")
            name = name.removeprefix("on_")

            return cls(coro, name)

        return wrapper


class EventMixinTemplate:
    """All event mixins inherit from this to keep them uniform."""

    cache: "GlobalCache"
    dispatch: Callable[["BaseEvent"], None]
    _init_interactions: Callable[[], Coroutine]
    synchronise_interactions: Callable[[], Coroutine]
    _user: NaffUser
    _guild_event: asyncio.Event

    def __init__(self) -> None:
        for call in inspect.getmembers(self):
            if isinstance(call[1], Processor):
                self.add_event_processor(call[1].event_name)(
                    functools.partial(call[1].callback, self)
                )
