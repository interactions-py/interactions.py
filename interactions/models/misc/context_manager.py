from asyncio import sleep, Task, create_task
from typing import TYPE_CHECKING

from interactions.client.const import Absent, MISSING

if TYPE_CHECKING:
    from interactions import MessageableMixin

__all__ = ("Typing",)


class Typing:
    """
    A context manager to send a typing state to a given channel as long as long as the wrapped operation takes.

    Args:
        channel: The channel to send the typing state to
    """

    def __init__(self, channel: "MessageableMixin") -> None:
        self._task: Absent[Task] = MISSING
        self.channel: "MessageableMixin" = channel
        self._stop: bool = False

    async def _typing_task(self) -> None:
        while not self._stop:
            await self.channel.trigger_typing()
            await sleep(5)

    async def __aenter__(self) -> None:
        self.task = create_task(self._typing_task())

    async def __aexit__(self, *_) -> None:
        self._stop = True
        self.task.cancel()
