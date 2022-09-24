from asyncio import Lock
from typing import Optional

from ...utils.missing import MISSING

__all__ = ("Limiter",)


class Limiter:
    """
    A class representing a limitation for an HTTP request.

    :ivar Lock lock: The "lock" or controller of the request.
    :ivar float reset_after: The remaining time before the request can be ran.
    """

    __slots__ = ("lock", "reset_after")

    lock: Lock
    reset_after: float

    def __init__(self, *, lock: Lock, reset_after: Optional[float] = MISSING) -> None:
        """
        :param lock: The asynchronous lock to control limits for.
        :type lock: Lock
        :param reset_after: The remaining time to run the limited lock on. Defaults to ``0``.
        :type reset_after: Optional[float]
        """
        self.lock = lock
        self.reset_after = 0 if reset_after is MISSING else reset_after

    async def __aenter__(self) -> "Limiter":
        await self.lock.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        return self.lock.release()

    def release_lock(self) -> None:
        # Releases the lock if its locked, overriding the traditional release() method.
        # Useful for per-route, not needed? for globals.

        # See #428.

        if self.lock.locked():
            self.lock.release()
