import asyncio
import logging
from sys import version_info
from time import time
from typing import Optional

log = logging.getLogger("gateway.ratelimit")

__all__ = ("WSRateLimit",)


class WSRateLimit:
    """
    A class that controls Gateway ratelimits using locking and a timer.

    .. note ::
        While the docs state that the Gateway ratelimits are 120/60 (120 requests per 60 seconds),
        this ratelimit offsets to 115 instead of 120 for room.

    :ivar Lock lock: The gateway Lock object.
    :ivar int max: The upper limit of the ratelimit in seconds. Defaults to `115`.
    :ivar int remaining: How many requests are left per ``per_second``. This is automatically decremented and reset.
    :ivar float current_limit: When this cooldown session began. This is defined automatically.
    :ivar float per_second: A constant denoting how many requests can be done per unit of seconds. (i.e., per 60 seconds, per 45, etc.)
    """

    def __init__(self, loop: Optional[asyncio.AbstractEventLoop] = None):
        self.lock = asyncio.Lock(loop=loop) if version_info < (3, 10) else asyncio.Lock()
        # To conserve timings, we need to do 115/60
        # Also, credit to d.py for their ratelimiter inspiration

        self.max = self.remaining = 115
        self.per_second = 60.0
        self.current_limit = 0.0

    @property
    def ratelimited(self) -> bool:
        """
        An attribute that reflects whenever the websocket ratelimiter is rate-limited.

        :return: Whether it's rate-limited or not.
        :rtype: bool
        """
        current = time()
        if current > self.current_limit + self.per_second:
            return False
        return self.remaining == 0

    @property
    def delay(self) -> float:
        """
        An attribute that reflects how long we need to wait for ratelimit to pass, if any.

        :return: How long to wait in seconds, if any. Defaults to ``0.0``.
        :rtype: float
        """
        current = time()

        if current > self.current_limit + self.per_second:
            self.remaining = self.max

        if self.remaining == self.max:
            self.current_limit = current

        if self.remaining == 0:
            return self.per_second - (current - self.current_limit)

        self.remaining -= 1
        if self.remaining == 0:
            self.current_limit = current

        return 0.0

    async def block(self) -> None:
        """
        A function that uses the internal Lock to check for rate-limits and cooldown whenever necessary.
        """
        async with self.lock:
            if delta := self.delay:
                log.warning(f"We are rate-limited. Please wait {round(delta, 2)} seconds...")
                await asyncio.sleep(delta)
