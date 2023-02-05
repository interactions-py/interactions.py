import asyncio
import functools
import time
from abc import abstractmethod
from typing import TypeVar

import interactions
from interactions import BaseComponent

T = TypeVar("T", bound="BaseUI")


class BaseUI:
    def __new__(cls, client: interactions.Client, *, timeout: float = 120) -> T:
        instance = super().__new__(cls)
        instance._client = client
        instance._logger = interactions.get_logger()

        instance._timeout = timeout
        instance._start_time = 0
        instance.__stop_event = asyncio.Event()

        instance.types = (BaseComponent,)

        return instance

    @abstractmethod
    def _gather_callbacks(self) -> None:
        raise NotImplementedError()

    def start_timeout(self) -> None:
        """Start the timeout for the UI."""
        self.__stop_event.set()
        asyncio.create_task(self.__timeout_task())

    async def __timeout_task(self) -> None:
        if self._timeout:
            self.__stop_event.clear()
            self._start_time = time.monotonic()
            future = asyncio.create_task(self.__stop_event.wait())
            done, _ = await asyncio.wait([future], timeout=self._timeout)
            if future in done:
                return
            self._logger.debug("UI timed out")
            await self.on_timeout()
        self.__stop_event.set()

    async def on_timeout(self) -> None:
        """Called when the UI times out."""
        ...

    @property
    def timeout(self) -> float:
        """The timeout for the UI."""
        return self._timeout

    @timeout.setter
    def timeout(self, value) -> None:
        """Set the timeout for the UI."""
        self.__stop_event.set()
        self._timeout = value

    @property
    def remaining_time(self) -> float:
        """The remaining time for the UI."""
        return self._timeout - (time.monotonic() - self._start_time)

    @property
    def timed_out(self) -> bool:
        return self.__stop_event.is_set()

    @functools.cached_property
    def _ordered_(self) -> list[str]:
        # depending on how the class was defined, components may be in self.__dict__ or __class__.__dict__ or both
        return [key for key, val in (self.__dict__ | self.__class__.__dict__).items() if isinstance(val, self.types)]
