from abc import ABCMeta, abstractmethod
from math import inf
from typing import TYPE_CHECKING, Callable, List, Optional, TypeVar, Union

from ..utils.missing import MISSING

_T = TypeVar("_T")
_O = TypeVar("_O")

__all__ = ("BaseAsyncIterator", "BaseIterator")

if TYPE_CHECKING:
    from ...api.http.client import HTTPClient
    from ...api.models.misc import Snowflake


class BaseAsyncIterator(metaclass=ABCMeta):
    """A base class for async iterators."""

    # I don't want to make it subclass the BaseIterator since it forces implementation of __next__ and __iter__

    @abstractmethod
    def __init__(
        self,
        obj: Union[int, str, "Snowflake", _T],
        _client: Optional["HTTPClient"] = None,
        maximum: Optional[int] = inf,
        start_at: Optional[Union[int, str, "Snowflake", _O]] = MISSING,
        check: Optional[Callable[[_O], bool]] = None,
    ):

        self.object_id = int(obj) if not hasattr(obj, "id") else int(obj.id)
        self.maximum = maximum
        self.check = check
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
    async def __anext__(self) -> _O:
        raise NotImplementedError


class BaseIterator(metaclass=ABCMeta):
    """A base class for iterators"""

    @abstractmethod
    def __init__(
        self,
        obj: Union[int, str, "Snowflake", _T],
        maximum: Optional[int] = inf,
        start_at: Optional[Union[int, str, "Snowflake", _O]] = MISSING,
        check: Optional[Callable[[_O], bool]] = None,
    ):
        self.object_id = int(obj) if not hasattr(obj, "id") else int(obj.id)
        self.maximum = maximum
        self.check = check
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

    def __iter__(self):
        return self

    @abstractmethod
    def get_objects(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def __next__(self) -> _O:
        raise NotImplementedError
