import asyncio
import discord
from enum import IntEnum
from contextlib import suppress
from inspect import iscoroutinefunction
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
    :ivar allowed_guild_ids: List of the allowed guild id.
    :ivar options: List of the option of the command. Used for `auto_register`.
    :ivar connector: Kwargs connector of the command.
    :ivar __commands_checks__: Check of the command.
    """
    def __init__(self, name, cmd):  # Let's reuse old command formatting.
        self.name = name.lower()
        self.func = cmd["func"]
        self.description = cmd["description"]
        self.allowed_guild_ids = cmd["guild_ids"] or []
        self.options = cmd["api_options"] or []
        self.connector = cmd["connector"] or {}
        self.has_subcommands = cmd["has_subcommands"]
        # Ref https://github.com/Rapptz/discord.py/blob/master/discord/ext/commands/core.py#L1447
        # Since this isn't inherited from `discord.ext.commands.Command`, discord.py's check decorator will
        # add checks at this var.
        self.__commands_checks__ = []
        if hasattr(self.func, '__commands_checks__'):
            self.__commands_checks__ = self.func.__commands_checks__

    async def invoke(self, *args, **kwargs):
        """
        Invokes the command.

        :param args: Args for the command.
        :raises: .error.CheckFailure
        """
        can_run = await self.can_run(args[0])
        if not can_run:
            raise error.CheckFailure

        return await self.func(*args, **kwargs)

    def add_check(self, func):
        """
        Adds check to the command.

        :param func: Any callable. Coroutines are supported.
        """
        self.__commands_checks__.append(func)

    def remove_check(self, func):
        """
        Removes check to the command.

        .. note::
            If the function is not found at the command check, it will ignore.

        :param func: Any callable. Coroutines are supported.
        """
        with suppress(ValueError):
            self.__commands_checks__.remove(func)

    async def can_run(self, ctx) -> bool:
        """
        Whether the command can be run.

        :param ctx: SlashContext for the check running.
        :type ctx: .context.SlashContext
        :return: bool
        """
        res = [bool(x(ctx)) if not iscoroutinefunction(x) else bool(await x(ctx)) for x in self.__commands_checks__]
        return False not in res


class SubcommandObject(CommandObject):
    """
    Subcommand object of this extension.

    .. note::
        This model inherits :class:`.model.CommandObject`, so this has every variables from that.

    .. warning::
        Do not manually init this model.

    :ivar base: Name of the base slash command.
    :ivar subcommand_group: Name of the subcommand group. ``None`` if not exist.
    :ivar base_description: Description of the base command.
    :ivar subcommand_group_description: Description of the subcommand_group.
    """
    def __init__(self, sub, base, name, sub_group=None):
        sub["has_subcommands"] = True # For the inherited class.
        super().__init__(name, sub)
        self.base = base.lower()
        self.subcommand_group = sub_group.lower() if sub_group else sub_group
        self.base_description = sub["base_desc"]
        self.subcommand_group_description = sub["sub_group_desc"]


class CogCommandObject(CommandObject):
    """
    Slash command object but for Cog.

    .. warning::
        Do not manually init this model.
    """
    def __init__(self, *args):
        super().__init__(*args)
        self.cog = None  # Manually set this later.

    async def invoke(self, *args, **kwargs):
        """
        Invokes the command.

        :param args: Args for the command.
        :raises: .error.CheckFailure
        """
        can_run = await self.can_run(args[0])
        if not can_run:
            raise error.CheckFailure

        return await self.func(self.cog, *args, **kwargs)


class CogSubcommandObject(SubcommandObject):
    """
    Subcommand object but for Cog.

    .. warning::
        Do not manually init this model.
    """
    def __init__(self, *args):
        super().__init__(*args)
        self.cog = None  # Manually set this later.

    async def invoke(self, *args, **kwargs):
        """
        Invokes the command.

        :param args: Args for the command.
        :raises: .error.CheckFailure
        """
        can_run = await self.can_run(args[0])
        if not can_run:
            raise error.CheckFailure

        return await self.func(self.cog, *args, **kwargs)


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
        if issubclass(t, bool): return cls.BOOLEAN
        # The check for bool MUST be above the check for integers as booleans subclass integers
        if issubclass(t, int): return cls.INTEGER
        if issubclass(t, discord.abc.User): return cls.USER
        if issubclass(t, discord.abc.GuildChannel): return cls.CHANNEL
        if issubclass(t, discord.abc.Role): return cls.ROLE


class SlashMessage(discord.Message):
    """discord.py's :class:`discord.Message` but overridden ``edit`` and ``delete`` to work for slash command."""
    def __init__(self, *, state, channel, data, _http: http.SlashCommandRequest, interaction_token):
        # Yes I know it isn't the best way but this makes implementation simple.
        super().__init__(state=state, channel=channel, data=data)
        self._http = _http
        self.__interaction_token = interaction_token

    async def edit(self, **fields):
        """Refer :meth:`discord.Message.edit`."""
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

            await self._http.edit(_resp, self.__interaction_token, self.id)

            delete_after = fields.get("delete_after")
            if delete_after:
                await self.delete(delay=delete_after)

    async def delete(self, *, delay=None):
        """Refer :meth:`discord.Message.delete`."""
        try:
            await super().delete(delay=delay)
        except discord.Forbidden:
            if not delay:
                return await self._http.delete(self.__interaction_token, self.id)

            async def wrap():
                with suppress(discord.HTTPException):
                    await asyncio.sleep(delay)
                    await self._http.delete(self.__interaction_token, self.id)
            self._state.loop.create_task(wrap())
