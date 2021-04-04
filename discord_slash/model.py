import asyncio
import datetime
from contextlib import suppress
from enum import IntEnum

import discord
from discord.ext import commands
from discord.ext.commands import CommandOnCooldown
from discord.ext.commands.core import hooked_wrapped_callback

from . import error
from . import http


class CommandObject(commands.Command):
    """
    Slash command object of this extension.
    This is based on discord.ext.commands.Command, certain methods have been overridden / disabled to work with slash

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
        if cmd['func'] is not None:
            super().__init__(cmd['func'])
        # dpy commands set a load of attributes that break slash_commands
        # to prevent refactoring, call init first, then override with the below

        # overwrite specific dpy attributes
        self.aliases = []

        self.name = name.lower()
        self.func = cmd['func']
        self.description = self.brief = cmd["description"]
        self.allowed_guild_ids = cmd["guild_ids"] or []
        self.options = cmd["api_options"] or []
        self.connector = cmd["connector"] or {}
        self.has_subcommands = cmd["has_subcommands"]

    def __new__(cls, *args, **kwargs):
        # if you're wondering why this is done, it's because we need to ensure
        # we have a complete original copy of **kwargs even for classes that
        # mess with it by popping before delegating to the subclass __init__.
        # In order to do this, we need to control the instance creation and
        # inject the original kwargs through __new__ rather than doing it
        # inside __init__.
        self = super().__new__(cls)

        # we do a shallow copy because it's probably the most common use case.
        # this could potentially break if someone modifies a list or something
        # while it's in movement, but for now this is the cheapest and
        # fastest way to do what we want.
        self.__original_kwargs__ = kwargs.copy()

        # dpy slash uses args as well, so to avoid breaking, ive added this line
        self.__original_args__ = args
        return self

    def copy(self):
        ret = self.__class__(*self.__original_args__, **self.__original_kwargs__)
        return self._ensure_assignment_on_copy(ret)

    def update(self, **kwargs):
        """Updates :class:`Command` instance with updated attribute.

        This works similarly to the :func:`.command` decorator in terms
        of parameters in that they are passed to the :class:`Command` or
        subclass constructors, sans the name and callback.
        """
        self.__init__(*self.__original_args__, **dict(self.__original_kwargs__, **kwargs))

    @property
    def qualified_name(self):
        """:class:`str`: Retrieves the fully qualified command name.

        This is the full parent name with the command name as well.
        For example, in ``?one two three`` the qualified name would be
        ``one two three``.
        """
        if hasattr(self, "base"):
            # subcmd
            group = f"{self.subcommand_group + ' ' if self.subcommand_group is not None else ''}"
            return f"{self.base} {group}{self.name}"
        return self.name

    def __call__(self, *args, **kwargs):

        # context contains a method that is far better suited to invoking slash commands
        # so in order to remove potential bugs with this method, ive disabled it
        raise NotImplementedError("Please use SlashContext.InvokeCommand")

    @property
    def full_parent_name(self):
        """:class:`str`: Retrieves the fully qualified parent command name.

        This the base command name required to execute it. For example,
        in ``?one two three`` the parent name would be ``one two``.
        """
        if hasattr(self, "base"):
            group = f"{self.subcommand_group + ' ' if self.subcommand_group is not None else ''}"
            return f"{self.base}{group}".strip()
        else:
            return None

    async def prepare(self, ctx):
        ctx.command = self

        if not await self.can_run(ctx):
            raise error.CheckFailure

        if self._max_concurrency is not None:
            await self._max_concurrency.acquire(ctx)

        try:
            if self.cooldown_after_parsing:
                self._prepare_cooldowns(ctx)
            else:
                self._prepare_cooldowns(ctx)

            await self.call_before_hooks(ctx)
        except:
            if self._max_concurrency is not None:
                await self._max_concurrency.release(ctx)
            raise

    def _prepare_cooldowns(self, ctx):
        if self._buckets.valid:
            dt = ctx.created_at
            current = dt.replace(tzinfo=datetime.timezone.utc).timestamp()
            bucket = self._buckets.get_bucket(ctx, current)
            retry_after = bucket.update_rate_limit(current)
            if retry_after:
                raise CommandOnCooldown(bucket, retry_after)

    def is_on_cooldown(self, ctx):
        """Checks whether the command is currently on cooldown.

        Parameters
        -----------
        ctx: :class:`.Context`
            The invocation context to use when checking the commands cooldown status.

        Returns
        --------
        :class:`bool`
            A boolean indicating if the command is on cooldown.
        """
        if not self._buckets.valid:
            return False

        bucket = self._buckets.get_bucket(ctx)
        dt = ctx.created_at
        current = dt.replace(tzinfo=datetime.timezone.utc).timestamp()
        return bucket.get_tokens(current) == 0

    def reset_cooldown(self, ctx):
        """Resets the cooldown on this command.

        Parameters
        -----------
        ctx: :class:`.Context`
            The invocation context to reset the cooldown under.
        """
        if self._buckets.valid:
            bucket = self._buckets.get_bucket(ctx)
            bucket.reset()

    def get_cooldown_retry_after(self, ctx):
        """Retrieves the amount of seconds before this command can be tried again.

        .. versionadded:: 1.4

        Parameters
        -----------
        ctx: :class:`.Context`
            The invocation context to retrieve the cooldown from.

        Returns
        --------
        :class:`float`
            The amount of time left on this command's cooldown in seconds.
            If this is ``0.0`` then the command isn't on cooldown.
        """
        if self._buckets.valid:
            bucket = self._buckets.get_bucket(ctx)
            dt = ctx.created_at
            current = dt.replace(tzinfo=datetime.timezone.utc).timestamp()
            return bucket.get_retry_after(current)

    async def invoke(self, *args, **kwargs):
        """
        Invokes the command.

        :param args: Args for the command.
        :raises: .error.CheckFailure
        """
        await self.prepare(args[0])

        if self.cog:
            # handle cog commands without override

            injected = hooked_wrapped_callback(self, args[0], self.callback)
            return await injected(self.cog, *args, **kwargs)

        injected = hooked_wrapped_callback(self, args[0], self.callback)
        return await injected(*args, **kwargs)


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
        sub["has_subcommands"] = True  # For the inherited class.
        self.base = base.lower()
        self.subcommand_group = sub_group.lower() if sub_group else sub_group
        self.base_description = sub["base_desc"]
        self.subcommand_group_description = sub["sub_group_desc"]
        super().__init__(name, sub)


class CogCommandObject(CommandObject):
    """
    Slash command object but for Cog.

    .. warning::
        Do not manually init this model.
    """

    def __init__(self, *args):
        super().__init__(*args)
        self.cog = None  # Manually set this later.


class CogSubcommandObject(SubcommandObject):
    """
    Subcommand object but for Cog.

    .. warning::
        Do not manually init this model.
    """

    def __init__(self, *args):
        super().__init__(*args)
        self.cog = None  # Manually set this later.


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
