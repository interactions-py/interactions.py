from abc import ABCMeta, abstractmethod
from math import inf
from typing import TYPE_CHECKING, List, Optional, TypeVar, Union

from .missing import MISSING

_T = TypeVar("_T")
_O = TypeVar("_O")

if TYPE_CHECKING:
    from ..api.http.client import HTTPClient
    from ..api.models.misc import Snowflake


class BaseAsyncIterator(metaclass=ABCMeta):
    """A base class for async iterators."""

    @abstractmethod
    def __init__(
        self,
        _client: "HTTPClient",
        obj: Union[int, str, "Snowflake", _T],
        maximum: Optional[int] = inf,
        start_at: Optional[Union[int, str, "Snowflake", _O]] = MISSING,
    ):

        self.object_id = int(obj) if not hasattr(obj, "id") else int(obj.id)
        self.maximum = maximum
        self._client = _client
        self.object_count: int = 0
        self.start_at = (
            None
            if start_at is MISSING
            else int(start_at)
            if not hasattr(start_at, "id")
            else int(start_at.id)
        )
        self.__stop: bool = False
        self.objects: Optional[List[_O]] = None

    @abstractmethod
    async def get_first_objects(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_objects(self) -> None:
        raise NotImplementedError

    def __aiter__(self):
        return self

    @abstractmethod
    async def __anext__(self):
        if self.objects is None:
            await self.get_first_objects()
