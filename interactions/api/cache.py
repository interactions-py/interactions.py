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

import interactions

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

    def __init__(self, limit: Optional[int] = None) -> None:
        """
        :param Optional[int] limit: The maximum number of items to store
        """
        if not limit:
            limit = float("inf")
        self.values: interactions.LRUDict["Key", _T] = interactions.LRUDict(max_items=limit)

    def merge(self, item: _T, id: Optional["Key"] = None) -> None:
        """
        Merges new data of an item into an already present item of the cache

        :param Any item: The item to merge.
        :param Optional[Union[Snowflake, Tuple[Snowflake, Snowflake]]] id: The unique id of the item.
        """
        if not self.values.get(id or item.id):
            return self.add(item, id)

        _id = id or item.id
        old_item = self.values[_id]

        for attrib in item.__slots__:
            if getattr(old_item, attrib) and not getattr(item, attrib):
                continue
                # we can only assume that discord did not provide it, falsely deleting is worse than not deleting
            if getattr(old_item, attrib) != getattr(item, attrib):
                if isinstance(getattr(item, attrib), list) and not isinstance(
                    getattr(old_item, attrib), list
                ):  # could be None
                    setattr(old_item, attrib, [])
                if isinstance(getattr(old_item, attrib), list):
                    if _attrib := getattr(item, attrib):
                        for value in _attrib:
                            old_item_attrib = getattr(old_item, attrib)
                            if value not in old_item_attrib:
                                old_item_attrib.append(value)
                            setattr(old_item, attrib, old_item_attrib)
                else:
                    setattr(old_item, attrib, getattr(item, attrib))

        self.values[_id] = old_item

    def add(self, item: _T, id: Optional["Key"] = None) -> None:
        """
        Adds a new item to the storage.

        :param Any item: The item to add.
        :param Optional[Union[Snowflake, Tuple[Snowflake, Snowflake]]] id: The unique id of the item.
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

        :param Union[Snowflake, Tuple[Snowflake, Snowflake]] id: The ID of the item.
        :param Optional[Any] default: The default value to return if the item is not found.
        :return: The item from the storage if any.
        :rtype: Optional[Any]
        """
        return self.values.get(id, default)

    def update(self, data: Dict["Key", _T]):
        """
        Updates multiple items from the storage.

        :param dict data: The data to update with.
        """
        self.values.update(data)

    @overload
    def pop(self, key: "Key") -> Optional[_T]:
        ...

    @overload
    def pop(self, key: "Key", default: _P) -> Union[_T, _P]:
        ...

    def pop(self, key: "Key", default: Optional[_P] = None) -> Union[_T, _P, None]:
        return self.values.pop(key, default)

    @property
    def view(self) -> List[dict]:
        """Views all items from storage.

        :return: The items stored.
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

    :ivar defaultdict[Type, Storage] storages: A dictionary denoting the Type and the objects that correspond to the Type.
    """

    __slots__ = ("storages", "config")

    def __init__(self, config: Dict[Type[_T], int] = None) -> None:
        self.storages: Dict[Type[_T], Storage[_T]] = defaultdict(Storage)

        if config is not None:
            for type_, limit in config.items():
                self.storages[type_] = Storage(limit)

    def __getitem__(self, item: Type[_T]) -> Storage[_T]:
        return self.storages[item]
