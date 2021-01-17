import asyncio
import discord
from enum import IntEnum
from contextlib import suppress
from . import http
from . import error


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


class SlashMessage(discord.Message):
    """discord.py's :class:`discord.Message` but overridden ``edit`` and ``delete`` to work for slash command."""
    def __init__(self, *, state, channel, data, _http: http.SlashCommandRequest, bot_id, interaction_token):
        super().__init__(state=state, channel=channel, data=data)
        self._http = _http
        self.bot_id = bot_id
        self.__interaction_token = interaction_token

    async def edit(self, **fields):
        try:
            await super().edit(**fields)
        except discord.Forbidden:
            _resp = {}

            content = str(fields.get("content"))
            if content:
                _resp["content"] = str(content)

            embed = fields.get("embed")
            embeds = fields.get("embeds")
            if embed and embeds:
                raise error.IncorrectFormat("You can't use both `embed` and `embeds`!")
            if embed:
                embeds = [embed]
            if embeds:
                if not isinstance(embeds, list):
                    raise error.IncorrectFormat("Provide a list of embeds.")
                elif len(embeds) > 10:
                    raise error.IncorrectFormat("Do not provide more than 10 embeds.")
                _resp["embeds"] = [x.to_dict() for x in embeds]

            allowed_mentions = fields.get("allowed_mentions")
            _resp["allowed_mentions"] = allowed_mentions.to_dict() if allowed_mentions else \
                self._state.allowed_mentions.to_dict() if self._state.allowed_mentions else {}

            await self._http.edit(_resp, self.bot_id, self.__interaction_token, self.id)

            delete_after = fields.get("delete_after")
            if delete_after:
                await self.delete(delay=delete_after)

    async def delete(self, *, delay=None):
        try:
            await super().delete(delay=delay)
        except discord.Forbidden:
            if not delay:
                return await self._http.delete(self.bot_id, self.__interaction_token, self.id)

            async def wrap():
                with suppress(discord.HTTPException):
                    await asyncio.sleep(delay)
                    await self._http.delete(self.bot_id, self.__interaction_token, self.id)
            self._state.loop.create_task(wrap())
