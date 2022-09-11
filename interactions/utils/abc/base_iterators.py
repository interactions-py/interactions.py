from abc import ABCMeta, abstractmethod
from math import inf
from typing import TYPE_CHECKING, Callable, List, Optional, TypeVar, Union

from ...api.models.misc import IDMixin, Snowflake
from ..missing import MISSING, DefaultMissing

_T = TypeVar("_T", bound=IDMixin)
_O = TypeVar("_O", bound=IDMixin)

__all__ = ("BaseAsyncIterator", "BaseIterator", "DiscordPaginationIterator")

if TYPE_CHECKING:
    from ...api.http.client import HTTPClient


class BaseAsyncIterator(metaclass=ABCMeta):
    """A base class for async iterators."""

    # I don't want to make it subclass the BaseIterator since it forces implementation of __next__ and __iter__

    @abstractmethod
    def __init__(self):
        raise NotImplementedError

    def __aiter__(self):
        return self

    async def flatten(self):
        return [item async for item in self]

    @abstractmethod
    async def __anext__(self) -> _O:
        raise NotImplementedError


class DiscordPaginationIterator(BaseAsyncIterator, metaclass=ABCMeta):
    def __init__(
        self,
        obj: Union[int, str, Snowflake, _T] = None,
        _client: Optional["HTTPClient"] = None,
        maximum: Union[int, float] = inf,
        start_at: DefaultMissing[Union[int, str, Snowflake, _O]] = MISSING,
        check: Optional[Callable[[_O], bool]] = None,
    ):

        self.object_id = (int(obj.id) if isinstance(obj, IDMixin) else int(obj)) if obj else None  # type: ignore

        self.maximum = maximum
        self.check = check
        self._client = _client
        self.object_count: int = 0
        self.start_at = (
            None
            if start_at is MISSING
            else int(start_at.id)  # type: ignore
            if isinstance(start_at, IDMixin)
            else int(start_at)  # type: ignore
        )

        self.__stop: bool = False
        self.objects: Optional[List[_O]] = None


class BaseIterator(metaclass=ABCMeta):
    """A base class for iterators"""

    @abstractmethod
    def __init__(self):
        raise NotImplementedError

    def __iter__(self):
        return self

    def flatten(self):
        return [item for item in self]

    @abstractmethod
    def __next__(self) -> _O:
        raise NotImplementedError
