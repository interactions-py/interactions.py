from typing import Callable, Coroutine

from interactions import Client
from interactions.client.const import Absent

class Processor:
    callback: Coroutine
    event_name: str
    def __init__(self, callback: Coroutine, name: str) -> None: ...
    @classmethod
    def define(cls, event_name: Absent[str] = ...) -> Callable[[Coroutine], "Processor"]: ...

class EventMixinTemplate(Client):
    def __init__(self) -> None: ...
