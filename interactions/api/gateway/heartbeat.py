from asyncio import Event

__all__ = ("_Heartbeat",)


class _Heartbeat:
    """An internal class representing the heartbeat in a WebSocket connection."""

    event: Event
    delay: float

    def __init__(self) -> None:
        self.event = Event()
        self.delay = 0.0
