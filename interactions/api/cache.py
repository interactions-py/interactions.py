from collections import OrderedDict
from typing import Any, List, Type

from .models.channel import Channel
from .models.guild import Guild
from .models.member import Member
from .models.message import Message
from .models.role import Role
from .models.user import User


class Item(object):
    """
    A class representing the defined item in a stored dataset.

    :ivar id: The ID of the item.
    :ivar value: The item itself.
    :ivar type: The ID type representation.
    """

    __slots__ = ("id", "value", "type")
    id: str
    value: Any
    type: Type

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


class Storage(OrderedDict):
    """
    A class representing a set of items stored as a cache state.

    :ivar values: The list of items stored.
    """

    __slots__ = "values"
    values: List[Item]

    def __init__(self) -> None:
        super().__init__()

    def add(self, item: Item) -> List[Item]:
        """
        Adds a new item to the storage.

        :param item: The item to add.
        :type item: interactions.api.cache.Item
        :return: typing.List[interactions.api.cache.Item]
        """
        self.values.update({item.id: item.value})
        return self.values


class Cache:
    """
    A class representing the cache.
    This cache collects all of the HTTP requests made for
    the represented instances of the class.

    :ivar dms: The cached Direct Messages.
    :ivar self_guilds: The cached guilds upon gateway connection.
    :ivar guilds: The cached guilds after ready.
    :ivar channels: The cached channels of guilds.
    :ivar roles: The cached roles of guilds.
    :ivar members: The cached members of guilds and threads.
    :ivar messages: The cached messages of DMs and channels.
    :ivar users: The cached users upon interaction.
    """

    dms: Storage = Storage()
    self_guilds: Storage = Storage()
    guilds: Storage = Storage()
    channels: Storage = Storage()
    roles: Storage = Storage()
    members: Storage = Storage()
    messages: Storage = Storage()
    users: Storage = Storage()

    def add_dm(self, dm: Channel) -> Item:
        """
        Adds a DM to the cache.

        :param dm: The Direct Message to add.
        :type dm: interactions.api.models.channel.Channel
        :return: interactions.api.cache.Item
        """
        return self.dms.add(dm)

    def get_dm(self, id: str) -> Item:
        """
        Gets a DM from the cache.

        :param id: The ID of the Direct Message.
        :type id: str
        :return: interactions.api.cache.Item
        """
        if id in self.dms.keys():
            return self.dms.get(id)

    def add_self_guild(self, guild: Guild) -> Item:
        """
        Adds a combed guild from the gateway to the cache.

        :param dm: The guild to add.
        :type dm: interactions.api.models.guild.guild
        :return: interactions.api.cache.Item
        """
        return self.self_guilds.add(guild)

    def get_self_guild(self, id: str) -> Item:
        """
        Gets a combed guild from the cache.

        :param id: The ID of the guild.
        :type id: str
        :return: interactions.api.cache.Item
        """
        if id in self.self_guilds.keys():
            return self.self_guilds.get(id)

    def add_guild(self, guild: Guild) -> Item:
        """
        Adds a guild after the ready event to the cache.

        :param dm: The guild to add.
        :type dm: interactions.api.models.guild.Guild
        :return: interactions.api.cache.Item
        """
        return self.guilds.add(guild)

    def get_guild(self, id: str) -> Item:
        """
        Gets a new guild from the cache.

        :param id: The ID of the guild.
        :type id: str
        :return: interactions.api.cache.Item
        """
        if id in self.guilds.keys():
            return self.guilds.get(id)

    def add_channel(self, channel: Channel) -> Item:
        """
        Adds a channel to the cache.

        :param dm: The channel to add.
        :type dm: interactions.api.models.channel.Channel
        :return: interactions.api.cache.Item
        """
        return self.channels.add(channel)

    def get_channel(self, guild_id: str, channel_id: str) -> Item:
        """
        Gets a channel from the cache.

        :param guild_id: The ID of the guild.
        :type guild_id: str
        :param channel_id: The ID of the channel.
        :type channel_id: str
        :return: interactions.api.cache.Item
        """
        if guild_id in self.guilds.keys():
            guild = self.guilds.get(guild_id)
            if channel_id in guild.get("channels"):
                return self.channels.get(channel_id)

    def add_role(self, role: Role) -> Item:
        """
        Adds a role to the cache.

        :param dm: The role to add.
        :type dm: interactions.api.models.role.Role
        :return: interactions.api.cache.Item
        """
        return self.roles.add(role)

    def get_role(self, guild_id: str, member_id: str, role_id: str) -> Item:
        """
        Gets a role from the cache.

        :param guild_id: The ID of the guild.
        :type guild_id: str
        :param member_id: The ID of the member.
        :type member_id: str
        :param role_id: The ID of the role.
        :type role_id: str
        :return: interactions.api.cache.Item
        """
        if guild_id in self.guilds.keys():
            guild = self.guilds.get(guild_id)
            if member_id in guild.get("members"):
                member = self.members.get(member_id)
                if role_id in member.get("roles"):
                    return self.roles.get(role_id)

    def add_member(self, member: Member) -> Item:
        """
        Adds a member to the cache.

        :param dm: The member to add.
        :type dm: interactions.api.models.member.Member
        :return: interactions.api.cache.Item
        """
        return self.members.add(member)

    def get_member(self, guild_id: str, member_id: str) -> Item:
        """
        Gets a member from the cache.

        :param guild_id: The ID of the guild.
        :type guild_id: str
        :param member_id: The ID of the member.
        :type member_id: str
        :return: interactions.api.cache.Item
        """
        if guild_id in self.guilds.keys():
            guild = self.guilds.get(guild_id)
            if member_id in guild.get("members"):
                return self.members.get(member_id)

    def add_message(self, message: Message) -> Item:
        """
        Adds a message to the cache.

        :param dm: The message to add.
        :type dm: interactions.api.models.message.Message
        :return: interactions.api.cache.Item
        """
        return self.messages.add(message)

    def get_message(self, guild_id: str, channel_id: str, message_id: str) -> Item:
        """
        Gets a message from the cache.

        :param guild_id: The ID of the guild.
        :type guild_id: str
        :param channel_id: The ID of the channel.
        :type channel_id: str
        :param message_id: The ID of the message.
        :type message_id: str
        :return: interactions.api.cache.Item
        """
        if guild_id in self.guilds.keys():
            guild = self.guilds.get(guild_id)
            if channel_id in guild.get("channels"):
                channel = self.channels.get(channel_id)
                if message_id in channel.get("messages"):
                    return self.messages.get(message_id)

    def add_user(self, user: User) -> Item:
        """
        Adds a user to the cache.

        :param dm: The user to add.
        :type dm: interactions.api.models.user.User
        :return: interactions.api.cache.Item
        """
        return self.users.add(user)

    def get_user(self, id: str) -> Item:
        """
        Gets a user from the cache.

        :param id: The ID of the user.
        :type id: str
        :return: interactions.api.cache.Item
        """
        if id in self.users.keys():
            return self.users.get(id)
