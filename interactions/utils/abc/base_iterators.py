from abc import ABC, ABCMeta, abstractmethod
from math import inf
from typing import TYPE_CHECKING, Awaitable, Callable, List, Optional, TypeVar, Union

from ..missing import MISSING

_T = TypeVar("_T")
_O = TypeVar("_O")

__all__ = ("BaseAsyncIterator", "BaseIterator", "DiscordPaginationIterator")

if TYPE_CHECKING:
    from ...api.http.client import HTTPClient
    from ...api.models.misc import Snowflake


class BaseAsyncIterator(ABC):
    """
    .. versionadded:: 4.3.2

    A base class for async iterators.
    """

    @abstractmethod
    def __init__(self):
        """Initialise the iterator"""
        raise NotImplementedError

    def __aiter__(self):
        return self

    async def flatten(self):
        """
        Returns all items of the iterator as list
        """
        return [item async for item in self]

    @abstractmethod
    async def __anext__(self) -> _O:
        """Return the next object"""
        raise NotImplementedError


class DiscordPaginationIterator(BaseAsyncIterator, metaclass=ABCMeta):
    """
    .. versionadded:: 4.3.2

    A base class for Discord Pagination Iterators.
    """

    def __init__(
        self,
        obj: Union[int, str, "Snowflake", _T] = None,
        _client: Optional["HTTPClient"] = None,
        maximum: Optional[int] = inf,
        start_at: Optional[Union[int, str, "Snowflake", _O]] = MISSING,
        check: Optional[Callable[[_O], Union[bool, Awaitable[bool]]]] = None,
    ):
        """
        Create a Discord Pagination iterator. All attributes are optional but may be useful for getting Discord objects.
        Check usages in the :class:`.AsyncMembersIterator` and :class:`.AsyncHistoryIterator` or
        :meth:`.Guild.get_members` and :meth:`.Channel.history`
        for more information about the arguments.

        :param Union[int, str, "Snowflake", _T] obj:
        :param Optional["HTTPClient"] _client:
        :param Optional[int] maximum:
        :param Optional[Union[int, str, "Snowflake", _O]] start_at:
        :param Optional[Callable[[_O], Union[bool, Awaitable[bool]]]] check:
        """

        self.object_id = (int(obj.id) if hasattr(obj, "id") else int(obj)) if obj else None

        self.maximum = maximum
        self.check = check
        self._client = _client
        self.object_count: int = 0
        self.start_at = (
            None
            if start_at is MISSING
            else int(start_at.id)
            if hasattr(start_at, "id")
            else int(start_at)
        )

        self.objects: Optional[List[_O]] = None


class BaseIterator(ABC):
    """
    .. versionadded:: 4.3.2

    A base class for iterators.
    """

    @abstractmethod
    def __init__(self):
        """Initialise the iterator"""
        raise NotImplementedError

    def __iter__(self):
        return self

    def flatten(self):
        """
        Returns all items of the iterator as list
        """
        return [item for item in self]

    @abstractmethod
    def __next__(self) -> _O:
        """Return the next object"""
        raise NotImplementedError
