from __future__ import annotations

import asyncio
import typing
from typing import (
    Annotated,
    Awaitable,
    Callable,
    Coroutine,
    Optional,
    Tuple,
    Any,
    TYPE_CHECKING,
    TypeVar,
)

import attrs

from interactions.client.const import MISSING, AsyncCallable
from interactions.client.errors import CommandOnCooldown, CommandCheckFailure, MaxConcurrencyReached
from interactions.client.mixins.serialization import DictSerializationMixin
from interactions.client.utils.attr_utils import docs
from interactions.client.utils.misc_utils import get_parameters, get_object_name, maybe_coroutine
from interactions.client.utils.serializer import no_export_meta
from interactions.models.internal.callback import CallbackObject
from interactions.models.internal.cooldowns import Cooldown, Buckets, MaxConcurrency, CooldownSystem
from interactions.models.internal.protocols import Converter

if TYPE_CHECKING:
    from interactions.models.internal.extension import Extension
    from interactions.models.internal.context import BaseContext

__all__ = ("BaseCommand", "check", "cooldown", "max_concurrency")


@attrs.define(eq=False, order=False, hash=False, kw_only=True)
class BaseCommand(DictSerializationMixin, CallbackObject):
    """
    An object all commands inherit from. Outlines the basic structure of a command, and handles checks.

    Attributes:
        extension: The extension this command belongs to.
        enabled: Whether this command is enabled
        checks: Any checks that must be run before this command can be run
        callback: The coroutine to be called for this command
        error_callback: The coroutine to be called when an error occurs
        pre_run_callback: A coroutine to be called before this command is run **but** after the checks
        post_run_callback: A coroutine to be called after this command has run

    """

    extension: "Optional[Extension]" = attrs.field(
        repr=False,
        default=None,
        metadata=docs("The extension this command belongs to") | no_export_meta,
    )

    enabled: bool = attrs.field(
        repr=False, default=True, metadata=docs("Whether this can be run at all") | no_export_meta
    )
    checks: list = attrs.field(
        repr=False,
        factory=list,
        metadata=docs("Any checks that must be *checked* before the command can run") | no_export_meta,
    )
    cooldown: Cooldown = attrs.field(
        repr=False,
        default=MISSING,
        metadata=docs("An optional cooldown to apply to the command") | no_export_meta,
    )
    max_concurrency: MaxConcurrency = attrs.field(
        default=MISSING,
        metadata=docs("An optional maximum number of concurrent instances to apply to the command") | no_export_meta,
    )

    callback: Callable[..., Coroutine] = attrs.field(
        repr=False,
        default=None,
        metadata=docs("The coroutine to be called for this command") | no_export_meta,
    )
    error_callback: Callable[..., Coroutine] = attrs.field(
        repr=False,
        default=None,
        metadata=no_export_meta | docs("The coroutine to be called when an error occurs"),
    )
    pre_run_callback: Callable[..., Coroutine] = attrs.field(
        default=None,
        metadata=no_export_meta
        | docs("The coroutine to be called before the command is executed, **but** after the checks"),
    )
    post_run_callback: Callable[..., Coroutine] = attrs.field(
        repr=False,
        default=None,
        metadata=no_export_meta | docs("The coroutine to be called after the command has executed"),
    )

    def __attrs_post_init__(self) -> None:
        if self.callback is not None:
            if hasattr(self.callback, "checks"):
                self.checks += self.callback.checks
            if hasattr(self.callback, "cooldown"):
                self.cooldown = self.callback.cooldown
            if hasattr(self.callback, "max_concurrency"):
                self.max_concurrency = self.callback.max_concurrency

    def __hash__(self) -> int:
        return id(self)

    async def __call__(self, context: "BaseContext", *args, **kwargs) -> None:
        """
        Calls this command.

        Args:
            context: The context of this command
            args: Any
            kwargs: Any

        """
        # signals if a semaphore has been acquired, for exception handling
        # if present assume one will be acquired
        max_conc_acquired = self.max_concurrency is not MISSING

        try:
            if await self._can_run(context):
                if self.pre_run_callback is not None:
                    await self.call_with_binding(self.pre_run_callback, context, *args, **kwargs)

                if self.extension is not None and self.extension.extension_prerun:
                    for prerun in self.extension.extension_prerun:
                        await prerun(context, *args, **kwargs)

                await self.call_callback(self.callback, context)

                if self.post_run_callback is not None:
                    await self.call_with_binding(self.post_run_callback, context, *args, **kwargs)

                if self.extension is not None and self.extension.extension_postrun:
                    for postrun in self.extension.extension_postrun:
                        await postrun(context, *args, **kwargs)

        except Exception as e:
            # if a MaxConcurrencyReached-exception is raised a connection was never acquired
            max_conc_acquired = not isinstance(e, MaxConcurrencyReached)

            if self.error_callback:
                await self.error_callback(e, context, *args, **kwargs)
            elif self.extension and self.extension.extension_error:
                await self.extension.extension_error(e, context, *args, **kwargs)
            else:
                raise
        finally:
            if self.max_concurrency is not MISSING and max_conc_acquired:
                await self.max_concurrency.release(context)

    @staticmethod
    def _get_converter_function(anno: type[Converter] | Converter, name: str) -> Callable[[BaseContext, str], Any]:
        num_params = len(get_parameters(anno.convert))

        # if we have three parameters for the function, it's likely it has a self parameter
        # so we need to get rid of it by initing - typehinting hates this, btw!
        # the below line will error out if we aren't supposed to init it, so that works out
        try:
            actual_anno: Converter = anno() if num_params == 3 else anno  # type: ignore
        except TypeError:
            raise ValueError(
                f"{get_object_name(anno)} for {name} is invalid: converters must have exactly 2 arguments."
            ) from None

        # we can only get to this point while having three params if we successfully inited
        if num_params == 3:
            num_params -= 1

        if num_params != 2:
            raise ValueError(
                f"{get_object_name(anno)} for {name} is invalid: converters must have exactly 2 arguments."
            )

        return actual_anno.convert

    async def try_convert(self, converter: Optional[Callable], context: "BaseContext", value: Any) -> Any:
        if converter is None:
            return value
        return await maybe_coroutine(converter, context, value)

    def param_config(self, annotation: Any, name: str) -> Tuple[Callable, Optional[dict]]:
        # This thing is complicated. i.py-annotations can either be annotated directly, or they can be annotated with Annotated[str, CMD_*]
        # This helper function handles both cases, and returns a tuple of the converter and its config (if any)
        if annotation is None:
            return None
        if typing.get_origin(annotation) is Annotated and (args := typing.get_args(annotation)):
            for ann in args:
                v = getattr(ann, name, None)
                if v is not None:
                    return (ann, v)
        return (annotation, getattr(annotation, name, None))

    async def call_callback(self, callback: Callable, context: "BaseContext") -> None:
        await self.call_with_binding(callback, context, **context.kwargs)  # type: ignore

    async def _can_run(self, context: "BaseContext") -> bool:
        """
        Determines if this command can be run.

        Args:
            context: The context of the command

        """
        max_conc_acquired = False  # signals if a semaphore has been acquired, for exception handling

        try:
            if not self.enabled:
                return False

            for _c in self.checks:
                if not await _c(context):
                    raise CommandCheckFailure(self, _c, context)

            if self.extension and self.extension.extension_checks:
                for _c in self.extension.extension_checks:
                    if not await _c(context):
                        raise CommandCheckFailure(self, _c, context)

            if self.max_concurrency is not MISSING and not await self.max_concurrency.acquire(context):
                raise MaxConcurrencyReached(self, self.max_concurrency)

            if self.cooldown is not MISSING and not await self.cooldown.acquire_token(context):
                raise CommandOnCooldown(self, await self.cooldown.get_cooldown(context))

            return True

        except Exception:
            if max_conc_acquired:
                await self.max_concurrency.release(context)
            raise

    def add_check(self, check: Callable[..., Awaitable[bool]]) -> None:
        """Adds a check into the command."""
        self.checks.append(check)

    def error(self, call: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
        """A decorator to declare a coroutine as one that will be run upon an error."""
        if not asyncio.iscoroutinefunction(call):
            raise TypeError("Error handler must be coroutine")
        self.error_callback = call
        return call

    def pre_run(self, call: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
        """A decorator to declare a coroutine as one that will be run before the command."""
        if not asyncio.iscoroutinefunction(call):
            raise TypeError("pre_run must be coroutine")
        self.pre_run_callback = call
        return call

    def post_run(self, call: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
        """A decorator to declare a coroutine as one that will be run after the command has."""
        if not asyncio.iscoroutinefunction(call):
            raise TypeError("post_run must be coroutine")
        self.post_run_callback = call
        return call


CommandT = TypeVar("CommandT", BaseCommand, AsyncCallable)


def check(check: Callable[..., Awaitable[bool]]) -> Callable[[CommandT], CommandT]:
    """
    Add a check to a command.

    Args:
        check: A coroutine as a check for this command

    """

    def wrapper(coro: CommandT) -> CommandT:
        if isinstance(coro, BaseCommand):
            coro.checks.append(check)
            return coro
        if not hasattr(coro, "checks"):
            coro.checks = []
        coro.checks.append(check)
        return coro

    return wrapper


def cooldown(
    bucket: Buckets, rate: int, interval: float, cooldown_system: typing.Type[CooldownSystem] | None = None
) -> Callable[[CommandT], CommandT]:
    """
    Add a cooldown to a command.

    Args:
        bucket: The bucket used to track cooldowns
        rate: How many commands may be ran per interval
        interval: How many seconds to wait for a cooldown
        cooldown_system: The cooldown system to use
    """

    def wrapper(coro: CommandT) -> CommandT:
        cooldown_obj = Cooldown(bucket, rate, interval, cooldown_system=cooldown_system)

        coro.cooldown = cooldown_obj

        return coro

    return wrapper


def max_concurrency(bucket: Buckets, concurrent: int) -> Callable[[CommandT], CommandT]:
    """
    Add a maximum number of concurrent instances to the command.

    Args:
        bucket: The bucket to enforce the maximum within
        concurrent: The maximum number of concurrent instances to allow

    """

    def wrapper(coro: CommandT) -> CommandT:
        max_conc = MaxConcurrency(concurrent, bucket)

        coro.max_concurrency = max_conc

        return coro

    return wrapper
