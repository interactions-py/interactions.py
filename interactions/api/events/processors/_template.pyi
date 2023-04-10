from typing import Callable

from interactions import Client
from interactions.client.const import Absent, AsyncCallable

class Processor:
    callback: AsyncCallable
    event_name: str
    def __init__(self, callback: AsyncCallable, name: str) -> None: ...
    @classmethod
    def define(cls, event_name: Absent[str] = ...) -> Callable[[AsyncCallable], "Processor"]: ...

class EventMixinTemplate(Client):
    def __init__(self) -> None: ...
