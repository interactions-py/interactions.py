from collections import defaultdict
from typing import (
    TYPE_CHECKING,
    Dict,
    Generic,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    overload,
)

if TYPE_CHECKING:
    from .models import Snowflake

    Key = TypeVar("Key", Snowflake, Tuple[Snowflake, Snowflake])

__all__ = (
    "Storage",
    "Cache",
)

_T = TypeVar("_T")
_P = TypeVar("_P")


class Storage(Generic[_T]):
    """
    A class representing a set of items stored as a cache state.

    :ivar Dict[Union[Snowflake, Tuple[Snowflake, Snowflake]], Any] values: The list of items stored.
    """

    __slots__ = ("values",)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} object containing {len(self.values)} items.>"

    def __init__(self) -> None:
        self.values: Dict["Key", _T] = {}

    def add(self, item: _T, id: Optional["Key"] = None) -> None:
        """
        Adds a new item to the storage.

        :param item: The item to add.
        :type item: Any
        :param id: The unique id of the item.
        :type id: Optional[Union[Snowflake, Tuple[Snowflake, Snowflake]]]
        """
        self.values[id or item.id] = item

    @overload
    def get(self, id: "Key") -> Optional[_T]:
        ...

    @overload
    def get(self, id: "Key", default: _P) -> Union[_T, _P]:
        ...

    def get(self, id: "Key", default: Optional[_P] = None) -> Union[_T, _P, None]:
        """
        Gets an item from the storage.

        :param id: The ID of the item.
        :type id: Union[Snowflake, Tuple[Snowflake, Snowflake]]
        :param default: The default value to return if the item is not found.
        :type default: Optional[Any]
        :return: The item from the storage if any.
        :rtype: Optional[Any]
        """
        return self.values.get(id, default)

    def update(self, data: Dict["Key", _T]):
        """
        Updates multiple items from the storage.

        :param data: The data to update with.
        :type data: dict
        """
        self.values.update(data)

    @overload
    def pop(self, key: "Key") -> Optional[_T]:
        ...

    @overload
    def pop(self, key: "Key", default: _P) -> Union[_T, _P]:
        ...

    def pop(self, key: "Key", default: Optional[_P] = None) -> Union[_T, _P, None]:
        try:
            return self.values.pop(key)
        except KeyError:
            return default

    @property
    def view(self) -> List[dict]:
        """Views all items from storage.

        :return The items stored.
        :rtype: List[dict]
        """
        return [v._json for v in self.values.values()]

    def __getitem__(self, item: "Key") -> _T:
        return self.values.__getitem__(item)

    def __setitem__(self, key: "Key", value: _T) -> None:
        return self.values.__setitem__(key, value)

    def __delitem__(self, key: "Key") -> None:
        return self.values.__delitem__(key)


class Cache:
    """
    A class representing the cache.
    This cache collects all of the HTTP requests made for
    the represented instances of the class.

    :ivar defaultdict[Type, Storage] storages:
    """

    __slots__ = "storages"

    def __init__(self) -> None:
        self.storages: defaultdict[Type[_T], Storage[_T]] = defaultdict(Storage)

    def __getitem__(self, item: Type[_T]) -> Storage[_T]:
        return self.storages[item]


ref_cache = Cache()  # noqa
