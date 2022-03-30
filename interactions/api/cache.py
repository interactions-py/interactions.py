from collections import OrderedDict
from typing import Any, List, Optional, Type, TypeVar, Union

_T = TypeVar("_T")


class Item(object):
    """
    A class representing the defined item in a stored dataset.

    :ivar str id: The ID of the item.
    :ivar Any value: The item itself.
    :ivar Type type: The ID type representation.
    """

    __slots__ = ("id", "value", "type")

    def __init__(self, id: str, value: Any) -> None:
        """
        :param id: The item's ID.
        :type id: str
        :param value: The item itself.
        :type value: Any
        """
        self.id: str = id
        self.value: Any = value
        self.type: str = type(value)


class Cache:
    """
    A class representing the cache.
    This cache collects all of the HTTP requests made for
    the represented instances of the class.

    """

    __slots__ = ("values",)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} object containing {len(self.values)} items.>"

    def __init__(self) -> None:
        self.values: OrderedDict[str, Item] = OrderedDict()

    def add(self, item: Item) -> OrderedDict:
        """
        Adds a new item to the storage.

        :param item: The item to add.
        :type item: Item
        :return: The new storage.
        :rtype: OrderedDict
        """
        self.values.update({item.id: item})
        return self.values

    def get(self, id: str, default: _T = None) -> Union[Item, _T]:
        """
        Gets an item from the storage.

        :param id: The ID of the item.
        :type id: str
        :param default: The value to return if no matches were found
        :type default: Any
        :return: The item from the storage if any.
        :rtype: Optional[Item]
        """
        return self.values.get(id, default)

    def update(self, item: Item) -> Optional[Item]:
        """
        Updates an item from the storage.

        :param item: The item to update.
        :return: The updated item, if stored.
        :rtype: Optional[Item]
        """
        self.values[item.id] = item.value
        return self.values[
            item.id
        ]  # fetches from cache to see if its saved properly, instead of returning input.

    def get_types(self, type: Type[_T]) -> List[_T]:
        return [item.value for item in self.values.values() if issubclass(item.type, type)]


ref_cache: Cache = Cache()  # noqa
