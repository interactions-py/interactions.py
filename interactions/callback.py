# Normal libraries
from contextlib import suppress
from enum import IntEnum
from typing import (
    Any,
    Coroutine,
    Dict,
    List,
    Optional,
    Union
)
from asyncio import iscoroutinefunction
from datetime import datetime, timezone

# 3rd-party libraries
from discord.ext.commands import BucketType, CooldownMapping, CommandOnCooldown
from .context import Interaction, Menu, Command
from .error import InteractionException
from .types.enums import DefaultErrorEnum as errorcode, Menus


class Callback:
    """
    Objecting representing how commands are called and processed.
    
    .. warning::

        Do not manually initialize this class.

    :ivar function:
    :ivar cooldown:
    :ivar on_error:
    :ivar max_concurrency:
    :ivar buckets:
    :ivar bucket_is_valid:
    :ivar command_checks:
    """
    __slots__ = (
        "function",
        "cooldown",
        "on_error",
        "max_concurrency",
        "buckets",
        "bucket_is_valid",
        "command_checks"
    )
    function: Coroutine
    cooldown: Optional[Any]
    on_error: Optional[Coroutine]
    max_concurrency: Optional[Any]
    buckets: Optional[CooldownMapping]
    bucket_is_valid: bool
    command_checks: List[Coroutine]

    """
    Danny decided that to name his attributes differently,
    he would use a bunch of underscores, and in a very inconsistent
    manner because this is open-sourced.™

    New instance names reflect off of these ingenious thoughts and
    normalizes it as far as consistency goes so that nobody here
    needs to lose additional braincells.
    """

    def __init__(
            self,
            function: Coroutine
    ) -> None:
        """
        Instantiates the Callback class.
        
        :param function: The coroutine of the command.
        :type function: typing.Coroutine
        :return: None
        """
        self.function = function
        self.cooldown = None
        self.on_error = None

        if hasattr(self.func, "__commands_checks__"):
            self.command_checks = self.func.__commands_checks__
        if hasattr(self.func, "__commands_max_concurrency__"):
            self.max_concurrency = self.func.__commands_max_concurrency__

        try:
            self.buckets = CooldownMapping(self.cooldown)
        except TypeError:
            self.buckets = CooldownMapping(
                self.cooldown,
                BucketType.default
            )

    def error(
            self,
            coroutine: Coroutine
    ) -> Union[Coroutine, Optional[TypeError]]:
        """
        A decorator registering coroutines as localized errors.
        
        :param coroutine: The coroutine to register as an error.
        :type coroutine: typing.Coroutine
        :raises: TypeError
        :return: typing.Union[typing.Coroutine, typing.Optional[TypeError]]
        """
        self.on_error = coroutine
        if not iscoroutinefunction(coroutine):
            raise TypeError("The error handler must be a coroutine.")
        return coroutine

    def _prepare_cooldowns(
            self,
            ctx: Interaction
    ) -> Optional[CommandOnCooldown]:
        """
        Prepares all of the callback cooldown events to be fired.

        .. note::

            This code extends off of `core.py <https://github.com/Rapptz/discord.py/blob/master/discord/ext/commands/core.py#L765>`_ from discord.py.
        
        :param ctx: The context to check.
        :type ctx: .context.Interaction
        :return: typing.Optional[discord.ext.commands.CommandOnCooldown]
        """
        if self.buckets.valid:
            self.bucket_is_valid = True
            current: float = ctx.created_at.replace(
                tzinfo=timezone.utc
            ).timestamp()
            bucket: BucketType = self.buckets.get_bucket(ctx, current)
            retry_after = bucket.update_rate_limit(current)
            if retry_after:
                raise CommandOnCooldown(
                    bucket,
                    retry_after
                )

    async def check_concurrencies(
            self,
            ctx: Interaction
    ) -> None:
        """
        Checks alongside the cooldown and maximum concurrent values.

        :param ctx: The context to check.
        :type ctx: .context.Interaction
        :return: None
        """
        if self.max_concurrency is not None:
            await self.max_concurrency.acquire(ctx)
        try:
            self._prepare_cooldowns(ctx)
        except Exception:
            if self.max_concurrency is not None:
                await self.max_concurrency.release(ctx)
            raise

    async def invoke(
            self,
            *args,
            **kwargs
    ) -> Union[Coroutine, Optional[InteractionException]]:
        """that 
        Invokes the command being called.
        
        :param \*args: Multi-argument of the command.
        :param \**kwargs: Keyword-arguments of the command.
        :raises: .error.InteractionException
        :return: typing.Union[typing.Coroutine, typing.Optional[InteractionException]]
        """
        can_run: bool = await self.can_run(args[0])

        if not can_run:
            raise InteractionException(errorcode.CHECK_FAILURE)

        await self.check_concurrencies(args[0])

        if hasattr(self, "cog"):
            return await self.func(
                self.cog,
                *args,
                **kwargs
            )

        return await self.func(
            *args,
            **kwargs
        )

    def is_on_cooldown(
            self,
            ctx
    ) -> bool:
        """
        Returns whether the command is currently on a cooldown or not.

        :param ctx: Command
        :type ctx: .context.Command
        :return: bool
        """
        if not self.bucket_is_valid:
            return False

        bucket: BucketType = self.buckets.get_bucket(ctx.message)
        _datetime: datetime = ctx.message.edited_at or ctx.message.created_at
        current = _datetime.replace(
            tzinfo=timezone.utc
        ).timestamp()

        return bucket.get_tokens(current) == 0

    def reset_cooldown(
            self,
            ctx: Union[Command, Menu]
    ) -> Coroutine:
        """
        Resets the cooldown on the command.

        :param ctx: The context of the command.
        :type ctx: typing.Union[.context.Command, .context.Menu]
        :return: typing.Coroutine
        """
        if self.bucket_is_valid:
            bucket: BucketType = self.buckets.get_bucket(ctx.message)
            bucket.reset()

    def get_cooldown_time(
            self,
            ctx: Union[Command, Menu]
    ) -> float:
        """
        Returns the amount of time remaining on a command's cooldown before it can be tried again.

        :param ctx: The context of the command.
        :type ctx: typing.Union[.context.Command, .context.Menu]
        :return: float
        """
        if self._buckets.valid:
            bucket: BucketType = self.buckets.get_bucket(ctx.message)
            _datetime: datetime = ctx.message.edited_at or ctx.message.created_at
            current: float = _datetime.replace(tzinfo=datetime.timezone.utc).timestamp()
            return bucket.get_retry_after(current)

        return 0.0

    def add_check(
            self,
            function: Coroutine
    ) -> List[Coroutine]:
        """
        Adds a new check for the command.

        .. note::

            If the command is not able to be found, the check will be ignored.

        :param function: The coroutine of the command.
        :type function: typing.Coroutine
        :return: None
        """
        return self.command_checks.append(function)

    def remove_check(
            self,
            function: Coroutine
    ) -> List[Coroutine]:
        """
        Removes a check from the command.
        
        .. note::

            If the command is not able to be found, the check will then be ignored.
        """
        with suppress(ValueError):
            self.command_checks.remove(function)

    async def can_run(
            self,
            ctx: Union[Command, Menu]
    ) -> bool:
        """
        Returns whether the command is being to be ran or not.

        :param ctx: The context of the command.
        :type ctx: typing.Union[.context.Command, .context.Menu]
        :return: bool
        """
        res: bool = (
            bool(x(ctx)) if not iscoroutinefunction(x) else bool(await x(ctx))
            for x in self.command_checks
        )
        return res


class SlashCommand(Callback):
    """
    Object representing callback logic for type ``CHAT_INPUT`` application commands.

    .. warning::

        Do not manually initialize this class.

    :ivar base:
    :ivar sub:
    :ivar group:
    :ivar name:
    :ivar description:
    :ivar base_description:
    :ivar group_description:
    :ivar guild_ids:
    :ivar options:
    :ivar connector:
    :ivar has_subcommands:
    :ivar default_permission:
    :ivar permissions:
    """
    __slots__ = (
        "base",
        "sub",
        "group",
        "name",
        "description",
        "base_description",
        "group_description",
        "guild_ids",
        "options",
        "permissions",
        "default_permission",
        "connector",
        "has_subcommands",
        "cog"
    )
    base: Optional[str]
    sub: Optional[str]
    group: Optional[str]
    name: str
    description: Optional[str]
    guild_ids: Optional[List[int]]
    options: Optional[List[dict]]
    permissions: Optional[List[Dict[int, int]]]
    default_permission: bool
    connector: Optional[Dict[str, str]]
    has_subcommands: Optional[List[dict]]
    cog: Any

    def __init__(
            self,
            name: str,
            command: dict,
            sub: Optional[str] = None,
            base: Optional[str] = None,
            group: Optional[str] = None
    ) -> None:
        """
        Instantiates the SlashCommand class.
        
        :param name: The name of the slash command.
        :type name: str
        :param command: A dictionary set of keys with values assigned.
        :type command: dict
        :param sub: The name of the subcommand. Defaults to ``None``.
        :type sub: typing.Optional[str]
        :param base: The name of the subcommand base. Defaults to ``None``.
        :type group: typing.Optional[str]
        :param sub: The name of the subcommand group. Defaults to ``None``.
        :type group: typing.Optional[str]
        :return: None
        """
        super().__init__(command["function"])
        self.base = base
        self.sub = sub
        self.group = group
        self.name = name.lower()
        self.description = command["description"]
        self.guild_ids = command["guild_ids"] or []
        self.options = command["options"] or []
        self.permissions = command["permissions"] or {}
        self.default_permission = command["default_permission"]
        self.connector = command["connector"] or {}
        self.has_subcommands = command["has_subcommands"]
        self.cog = None


class Component(Callback):
    """
    Object representing callback logic for components.

    .. warning::

        Do not manually initialize this class.

    :ivar message_ids:
    :ivar custom_ids:
    :ivar keys:
    :ivar _type:
    """
    __slots__ = (
        "_type",
        "message_ids",
        "custom_ids",
        "keys",
        "cog"
    )
    _type: IntEnum
    message_ids: List[int]
    custom_ids: Optional[List[int]]
    cog: Any

    def __init__(
            self,
            function: Coroutine,
            _type: IntEnum,
            message_ids: List[int],
            custom_ids: Optional[List[int]] = [],
    ) -> None:
        """
        Instantiates the Component class.

        :param function: The coroutine of the command.
        :type function: typing.Coroutine
        :param _type: The type of component.
        :type _type: enum.IntEnum
        :param message_ids: A list of message IDs registered to component(s).
        :type message_ids: typing.List[int]
        :param custom_ids: A list of custom IDs registered to component(s).
        :type custom_ids: typing.Optional[typing.List[int]]
        """
        if _type not in (2, 3, None):
            raise InteractionException(errorcode.INCORRECT_FORMAT, message="Invalid component type {_type}.",
                                       _type=_type)
        super().__init__(function)
        self._type = _type
        self.message_ids = set(message_ids)
        self.custom_ids = set(custom_ids)
        self.keys = {
            (message_id, custom_id)
            for message_id in message_ids
            for custom_id in custom_ids
        }
        self.cog = None
