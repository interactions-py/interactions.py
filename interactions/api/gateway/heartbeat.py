import contextlib
from asyncio import AbstractEventLoop, Event
from sys import version_info

__all__ = ("_Heartbeat",)


class _Heartbeat:
    """An internal class representing the heartbeat in a WebSocket connection."""

    event: Event
    delay: float

    def __init__(self, loop: AbstractEventLoop) -> None:
        """
        :param AbstractEventLoop loop: The event loop to base the asynchronous manager.
        """
        with contextlib.suppress(TypeError):
            self.event = Event(loop=loop) if version_info < (3, 10) else Event()
        self.delay = 0.0
