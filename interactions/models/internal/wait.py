from asyncio import Future, iscoroutinefunction
from typing import Callable, Optional, Union, Awaitable

__all__ = ("Wait",)


class Wait:
    """Class for waiting for a future event to happen. Internally used by wait_for."""

    def __init__(
        self, event: str, checks: Optional[Union[Callable[..., bool], Callable[..., Awaitable[bool]]]], future: Future
    ) -> None:
        self.event: str = event
        self.check: Optional[Union[Callable[..., bool], Callable[..., Awaitable[bool]]]] = checks
        self.future: Future = future

    async def __call__(self, *args, **kwargs) -> bool:
        if self.future.cancelled():
            return True

        if self.check:
            try:
                if iscoroutinefunction(self.check):
                    check_result = await self.check(*args, **kwargs)
                else:
                    check_result = self.check(*args, **kwargs)
            except Exception as exc:
                self.future.set_exception(exc)
                return True
        else:
            check_result = True

        if check_result:
            self.future.set_result(*args, **kwargs)
            return True

        return False
