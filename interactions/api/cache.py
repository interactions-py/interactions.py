from collections import OrderedDict
from typing import Any, Optional


class Item(object):
    """
    A class representing the defined item in a stored dataset.

    :ivar str id: The ID of the item.
    :ivar typing.Any value: The item itself.
    :ivar typing.Type type: The ID type representation.
    """

    __slots__ = ("id", "value", "type")

    def __init__(self, id: str, value: Any) -> None:
        """
        :param id: The item's ID.
        :type id: str
        :param value: The item itself.
        :type value: typing.Any
        :return: None
        """
        self.id = id
        self.value = value
        self.type = type(value)


class Storage:
    """
    A class representing a set of items stored as a cache state.

    :ivar typing.List[interactions.api.cache.Item] values: The list of items stored.
    """

    __slots__ = "values"

    def __init__(self) -> None:
        self.values = OrderedDict()

    def add(self, item: Item) -> OrderedDict:
        """
        Adds a new item to the storage.

        :param item: The item to add.
        :type item: interactions.api.cache.Item
        :return: typing.List[interactions.api.cache.Item]
        """
        self.values.update({item.id: item.value})
        return self.values

    def get(self, id: str) -> Optional[Item]:
        """
        Gets an item from the storage.

        :param id: The ID of the item.
        :type id: str
        :return: typing.Optional[interactions.api.cache.Item]
        """
        if id in self.values.keys():
            return self.values[id]


class Cache:
    """
    A class representing the cache.
    This cache collects all of the HTTP requests made for
    the represented instances of the class.

    :ivar interactions.api.cache.Cache dms: The cached Direct Messages.
    :ivar interactions.api.cache.Cache self_guilds: The cached guilds upon gateway connection.
    :ivar interactions.api.cache.Cache guilds: The cached guilds after ready.
    :ivar interactions.api.cache.Cache channels: The cached channels of guilds.
    :ivar interactions.api.cache.Cache roles: The cached roles of guilds.
    :ivar interactions.api.cache.Cache members: The cached members of guilds and threads.
    :ivar interactions.api.cache.Cache messages: The cached messages of DMs and channels.
    :ivar interactions.api.cache.Cache interactions: The cached interactions upon interaction.
    """

    def __init__(self) -> None:
        # TODO: Look into a better solution that handles duplication of data
        # in a storage.
        self.dms = Storage()
        self.self_guilds = Storage()
        self.guilds = Storage()
        self.channels = Storage()
        self.roles = Storage()
        self.members = Storage()
        self.messages = Storage()
        self.interactions = Storage()
