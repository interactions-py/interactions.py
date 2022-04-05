from asyncio import AbstractEventLoop, Event

class _Heartbeat():
    event: Event
    delay: float
    def __init__(self, loop: AbstractEventLoop) -> None: ...
