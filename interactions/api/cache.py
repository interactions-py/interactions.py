from collections import OrderedDict
from typing import Any, Dict, List, Optional, Tuple, TypeVar, Union

_T = TypeVar("_T")
key = Union[str, Tuple[str, str]]


class Storage:
    """
    A class representing a set of items stored as a cache state.

    :ivar List[Item] values: The list of items stored.
    """

    __slots__ = "values"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} object containing {len(self.values)} items.>"

    def __init__(self) -> None:
        self.values: OrderedDict = OrderedDict()

    def add(self, id: key, value: Any) -> OrderedDict:
        """
        Adds a new item to the storage.

        :param id: The id of the item
        :type id: str
        :param value: The item to add.
        :type value: Any
        :return: The new storage.
        :rtype: OrderedDict[str, _T]
        """
        id = str(id)

        self.values.update({id: value})
        return self.values

    def get(self, id: key, default: Any = None) -> Optional[Any]:
        """
        Gets an item from the storage.

        :param id: The ID of the item.
        :type id: str
        :param default: The value to return if the item was not found
        :type default: Any
        :return: The item from the storage if any.
        :rtype: Optional[Item]
        """
        return self.values.get(str(id), default)

    def update(self, items: Dict[key, _T]) -> Dict[key, _T]:
        """
        Updates an item from the storage.

        :param items: The dict to update from
        :type items: Dict[str, Any]
        """
        self.values.update(items)

        # mimicking what was done in the previous design of the cache
        return {key: self.values[key] for key in items}

    @property
    def view(self) -> List[dict]:
        """Views all items from storage.

        :return The items stored.
        :rtype: List[dict]
        """
        return [v._json for v in self.values.values()]


class Cache:
    """
    A class representing the cache.
    This cache collects all of the HTTP requests made for
    the represented instances of the class.

    :ivar Cache dms: The cached Direct Messages.
    :ivar Cache guilds: The cached guilds after ready.
    :ivar Cache channels: The cached channels of guilds.
    :ivar Cache roles: The cached roles of guilds.
    :ivar Cache members: The cached members of guilds and threads.
    :ivar Cache messages: The cached messages of DMs and channels.
    :ivar Cache interactions: The cached interactions upon interaction.
    """

    __slots__ = (
        "dms",
        "guilds",
        "channels",
        "roles",
        "members",
        "messages",
        "users",
        "interactions",
    )

    def __init__(self) -> None:
        self.dms: Storage = Storage()
        self.guilds: Storage = Storage()
        self.channels: Storage = Storage()
        self.roles: Storage = Storage()
        self.members: Storage = Storage()
        self.messages: Storage = Storage()
        self.users: Storage = Storage()
        self.interactions: Storage = Storage()


ref_cache = Cache()  # noqa
