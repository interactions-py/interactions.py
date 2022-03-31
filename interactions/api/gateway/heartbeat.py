from asyncio import AbstractEventLoop, Event
from sys import version_info


class _Heartbeat:
    """An internal class representing the heartbeat in a WebSocket connection."""

    event: Event
    delay: float

    def __init__(self, loop: AbstractEventLoop) -> None:
        """
        :param loop: The event loop to base the asynchronous manager.
        :type loop: AbstractEventLoop
        """
        try:
            self.event = Event(loop=loop) if version_info < (3, 10) else Event()
        except TypeError:
            pass
        self.delay = 0.0
