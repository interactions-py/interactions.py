from collections import OrderedDict
from typing import Any, List, Optional


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
        self.id = id
        self.value = value
        self.type = type(value)


class Storage:
    """
    A class representing a set of items stored as a cache state.

    :ivar List[Item] values: The list of items stored.
    """

    __slots__ = "values"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} object containing {len(self.values)} items.>"

    def __init__(self) -> None:
        self.values = OrderedDict()

    def add(self, item: Item) -> OrderedDict:
        """
        Adds a new item to the storage.

        :param item: The item to add.
        :type item: Item
        :return: The new storage.
        :rtype: OrderedDict
        """
        self.values.update({item.id: item.value})
        return self.values

    def get(self, id: str) -> Optional[Item]:
        """
        Gets an item from the storage.

        :param id: The ID of the item.
        :type id: str
        :return: The item from the storage if any.
        :rtype: Optional[Item]
        """
        if id in self.values.keys():
            return self.values[id]

    def update(self, item: Item) -> Optional[Item]:
        """
        Updates an item from the storage.

        :param item: The item to update.
        :return: The updated item, if stored.
        :rtype: Optional[Item]
        """
        if item.id in self.values.keys():
            self.values[item.id] = item.value
            return self.values[
                id
            ]  # fetches from cache to see if its saved properly, instead of returning input.

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
    :ivar Cache self_guilds: The cached guilds upon gateway connection.
    :ivar Cache guilds: The cached guilds after ready.
    :ivar Cache channels: The cached channels of guilds.
    :ivar Cache roles: The cached roles of guilds.
    :ivar Cache members: The cached members of guilds and threads.
    :ivar Cache messages: The cached messages of DMs and channels.
    :ivar Cache interactions: The cached interactions upon interaction.
    """

    __slots__ = (
        "dms",
        "self_guilds",
        "guilds",
        "channels",
        "roles",
        "members",
        "messages",
        "users",
        "interactions",
    )

    def __init__(self) -> None:
        self.dms = Storage()
        self.self_guilds = Storage()
        self.guilds = Storage()
        self.channels = Storage()
        self.roles = Storage()
        self.members = Storage()
        self.messages = Storage()
        self.users = Storage()
        self.interactions = Storage()


ref_cache = Cache()  # noqa
