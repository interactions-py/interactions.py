import discord
from enum import IntEnum


class CommandObject:
    """
    Slash command object of this extension.

    .. warning::
        Do not manually init this model.

    :ivar name: Name of the command.
    :ivar func: The coroutine of the command.
    :ivar description: Description of the command.
    :ivar auto_convert: Dictionary of the `auto_convert` of the command.
    :ivar allowed_guild_ids: List of the allowed guild id.
    :ivar options: List of the option of the command. Used for `auto_register`.
    """
    def __init__(self, name, cmd):  # Let's reuse old command formatting.
        self.name = name.lower()
        self.func = cmd["func"]
        self.description = cmd["description"]
        self.auto_convert = cmd["auto_convert"] or {}
        self.allowed_guild_ids = cmd["guild_ids"] or []
        self.options = cmd["api_options"] or []
        self.has_subcommands = cmd["has_subcommands"]

    def invoke(self, *args):
        """
        Invokes the command.

        :param args: Args for the command.
        :return: Coroutine
        """
        return self.func(*args)


class SubcommandObject:
    """
    Subcommand object of this extension.

    .. warning::
        Do not manually init this model.

    :ivar base: Name of the base slash command.
    :ivar subcommand_group: Name of the subcommand group. ``None`` if not exist.
    :ivar name: Name of the subcommand.
    :ivar func: The coroutine of the command.
    :ivar description: Description of the command.
    :ivar base_description: Description of the base command.
    :ivar subcommand_group_description: Description of the subcommand_group.
    :ivar auto_convert: Dictionary of the `auto_convert` of the command.
    :ivar allowed_guild_ids: List of the allowed guild id.
    """
    def __init__(self, sub, base, name, sub_group=None):
        self.base = base.lower()
        self.subcommand_group = sub_group.lower() if sub_group else sub_group
        self.name = name.lower()
        self.func = sub["func"]
        self.description = sub["description"]
        self.base_description = sub["base_desc"]
        self.subcommand_group_description = sub["sub_group_desc"]
        self.auto_convert = sub["auto_convert"] or {}
        self.allowed_guild_ids = sub["guild_ids"] or []
        self.options = sub["api_options"] or []

    def invoke(self, *args):
        """
        Invokes the command.

        :param args: Args for the command.
        :return: Coroutine
        """
        return self.func(*args)


class CogCommandObject(CommandObject):
    """
    Slash command object but for Cog.

    .. warning::
        Do not manually init this model.
    """
    def __init__(self, *args):
        super().__init__(*args)
        self.cog = None  # Manually set this later.

    def invoke(self, *args):
        """
        Invokes the command.

        :param args: Args for the command.
        :return: Coroutine
        """
        return self.func(self.cog, *args)


class CogSubcommandObject(SubcommandObject):
    """
    Subcommand object but for Cog.

    .. warning::
        Do not manually init this model.
    """
    def __init__(self, *args):
        super().__init__(*args)
        self.cog = None  # Manually set this later.

    def invoke(self, *args):
        """
        Invokes the command.

        :param args: Args for the command.
        :return: Coroutine
        """
        return self.func(self.cog, *args)


class SlashCommandOptionType(IntEnum):
    """
    Equivalent of `ApplicationCommandOptionType <https://discord.com/developers/docs/interactions/slash-commands#applicationcommandoptiontype>`_  in the Discord API.
    """
    SUB_COMMAND = 1
    SUB_COMMAND_GROUP = 2
    STRING = 3
    INTEGER = 4
    BOOLEAN = 5
    USER = 6
    CHANNEL = 7
    ROLE = 8

    @classmethod
    def from_type(cls, t: type):
        """
        Get a specific SlashCommandOptionType from a type (or object).

        :param t: The type or object to get a SlashCommandOptionType for.
        :return: :class:`.model.SlashCommandOptionType` or ``None``
        """
        if issubclass(t, str): return cls.STRING
        if issubclass(t, int): return cls.INTEGER
        if issubclass(t, bool): return cls.BOOLEAN
        if issubclass(t, discord.abc.User): return cls.USER
        if issubclass(t, discord.abc.GuildChannel): return cls.CHANNEL
        if issubclass(t, discord.abc.Role): return cls.ROLE
