from asyncio import get_event_loop
from logging import basicConfig, getLogger
from typing import Coroutine, Optional

from ..base import Data

basicConfig(level=Data.LOGGER)
log = getLogger("dispatch")


class Listener:
    """
    A class representing how events become dispatched and listened to.

    :ivar asyncio.AbstractEventLoop loop: The coroutine event loop established on.
    :ivar dict events: A list of events being dispatched.
    """

    __slots__ = ("loop", "events")

    def __init__(self) -> None:
        self.loop = get_event_loop()
        self.events = {}

    def dispatch(self, name: str, *args, **kwargs) -> None:
        r"""
        Dispatches an event given out by the gateway.

        :param name: The name of the event to dispatch.
        :type name: str
        :param \*args: Multiple arguments of the coroutine.
        :type \*args: typing.list[typing.Any]
        :param \**kwargs: Keyword-only arguments of the coroutine.
        :type \**kwargs: dict
        :return: None
        """
        for event in self.events.get(name, []):
            self.loop.create_task(event(*args, **kwargs))
            log.debug(f"DISPATCH: {event}")

    def register(self, coro: Coroutine, name: Optional[str] = None) -> None:
        """
        Registers a given coroutine as an event to be listened to.
        If the name of the event is not given, it will then be
        determined by the coroutine's name.

        i.e. : async def on_guild_create -> "ON_GUILD_CREATE" dispatch.

        :param coro: The coroutine to register as an event.
        :type coro: typing.Coroutine
        :param name: The name to associate the coroutine with. Defaults to None.
        :type name: typing.Optional[str]
        :return: None
        """
        _name: str = coro.__name__ if name is None else name
        event = self.events.get(_name, [])
        event.append(coro)

        self.events[_name] = event
        log.debug(f"REGISTER: {self.events[_name]}")
