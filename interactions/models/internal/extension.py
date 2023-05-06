import asyncio
import inspect
import typing
from typing import Awaitable, Dict, List, TYPE_CHECKING, Callable, Coroutine, Optional

import interactions.models.internal as models
import interactions.api.events as events
from interactions.models.internal.callback import CallbackObject
from interactions.client.const import MISSING
from interactions.client.utils.misc_utils import wrap_partial
from interactions.models.internal.tasks import Task

if TYPE_CHECKING:
    from interactions.client import Client
    from interactions.models.discord import Snowflake_Type
    from interactions.models.internal import AutoDefer, BaseCommand, InteractionCommand, Listener
    from interactions.models.internal import BaseContext


__all__ = ("Extension",)


class Extension:
    """
    A class that allows you to separate your commands and listeners into separate files. Skins require an entrypoint in the same file called `setup`, this function allows client to load the Extension.

    ??? Hint "Example Usage:"
        ```python
        class ExampleExt(Extension):
            def __init__(self, bot):
                print("Extension Created")

            @prefixed_command()
            async def some_command(self, context):
                await ctx.send(f"I was sent from a extension called {self.name}")
        ```

    Attributes:
        bot Client: A reference to the client
        name str: The name of this Extension (`read-only`)
        description str: A description of this Extension
        extension_checks str: A list of checks to be ran on any command in this extension
        extension_prerun List: A list of coroutines to be run before any command in this extension
        extension_postrun List: A list of coroutines to be run after any command in this extension
        interaction_tree Dict: A dictionary of registered application commands in a tree

    """

    bot: "Client"
    name: str
    extension_name: str
    description: str
    extension_checks: List
    extension_prerun: List
    extension_postrun: List
    extension_error: Optional[Callable[..., Coroutine]]
    interaction_tree: Dict["Snowflake_Type", Dict[str, "InteractionCommand" | Dict[str, "InteractionCommand"]]]
    _commands: List
    _listeners: List
    auto_defer: "AutoDefer"

    class Metadata:
        """Info about the Extension"""

        name: str
        """The name of this Extension"""
        version: str
        """The version of this Extension"""
        url: str
        """The repository url of this Extension"""
        description: str
        """A description of this Extension"""
        requirements: List[str]
        """A list of requirements for this Extension"""

    def __new__(cls, bot: "Client", *args, **kwargs) -> "Extension":
        instance = super().__new__(cls)
        instance.bot = bot
        instance.client = bot

        instance.name = cls.__name__
        instance.extension_checks = []
        instance.extension_prerun = []
        instance.extension_postrun = []
        instance.extension_error = None
        instance.interaction_tree = {}
        instance.auto_defer = MISSING

        instance.description = kwargs.get("Description")
        if not instance.description:
            instance.description = inspect.cleandoc(cls.__doc__) if cls.__doc__ else None

        # load commands from class
        instance._commands = []
        instance._listeners = []

        callables: list[tuple[str, typing.Callable]] = inspect.getmembers(
            instance, predicate=lambda x: isinstance(x, (CallbackObject, Task))
        )

        for _name, val in callables:
            if isinstance(val, models.BaseCommand):
                val.extension = instance
                val = wrap_partial(val, instance)
                bot.add_command(val)
                instance._commands.append(val)

            elif isinstance(val, Task):
                wrap_partial(val, instance)

            elif isinstance(val, models.Listener):
                val.extension = instance
                val = val.copy_with_binding(instance)
                bot.add_listener(val)  # type: ignore
                instance._listeners.append(val)
            elif isinstance(val, models.GlobalAutoComplete):
                val.extension = instance
                val = val.copy_with_binding(instance)
                bot.add_global_autocomplete(val)
        bot.dispatch(events.ExtensionCommandParse(extension=instance, callables=callables))

        instance.extension_name = inspect.getmodule(instance).__name__
        instance.bot.ext[instance.name] = instance

        if hasattr(instance, "async_start"):
            if inspect.iscoroutinefunction(instance.async_start):
                bot.async_startup_tasks.append((instance.async_start, (), {}))
            else:
                raise TypeError("async_start is a reserved method and must be a coroutine")

        bot.dispatch(events.ExtensionLoad(extension=instance))
        return instance

    @property
    def __name__(self) -> str:
        return self.name

    @property
    def commands(self) -> List["BaseCommand"]:
        """Get the commands from this Extension."""
        return self._commands

    @property
    def listeners(self) -> List["Listener"]:
        """Get the listeners from this Extension."""
        return self._listeners

    def drop(self) -> None:
        """Called when this Extension is being removed."""
        for func in self._commands:
            if isinstance(func, models.ModalCommand):
                for listener in func.listeners:
                    # noinspection PyProtectedMember
                    self.bot._modal_callbacks.pop(listener)
            elif isinstance(func, models.ComponentCommand):
                for listener in func.listeners:
                    # noinspection PyProtectedMember
                    self.bot._component_callbacks.pop(listener)
            elif isinstance(func, models.InteractionCommand):
                for scope in func.scopes:
                    if self.bot.interactions_by_scope.get(scope):
                        self.bot.interactions_by_scope[scope].pop(func.resolved_name, [])
        for func in self.listeners:
            self.bot.listeners[func.event].remove(func)

        self.bot.ext.pop(self.name, None)
        self.bot.dispatch(events.ExtensionUnload(extension=self))
        self.bot.logger.debug(f"{self.name} has been drop")

    def add_ext_auto_defer(self, enabled: bool = True, ephemeral: bool = False, time_until_defer: float = 0.0) -> None:
        """
        Add a auto defer for all commands in this extension.

        Args:
            enabled: Should the command be deferred automatically
            ephemeral: Should the command be deferred as ephemeral
            time_until_defer: How long to wait before deferring automatically

        """
        self.auto_defer = models.AutoDefer(enabled=enabled, ephemeral=ephemeral, time_until_defer=time_until_defer)

    def add_ext_check(self, coroutine: Callable[["BaseContext"], Awaitable[bool]]) -> None:
        """
        Add a coroutine as a check for all commands in this extension to run. This coroutine must take **only** the parameter `context`.

        ??? Hint "Example Usage:"
            ```python
            def __init__(self, bot):
                self.add_ext_check(self.example)

            @staticmethod
            async def example(context: BaseContext):
                if context.author.id == 123456789:
                    return True
                return False
            ```
        Args:
            coroutine: The coroutine to use as a check

        """
        if not asyncio.iscoroutinefunction(coroutine):
            raise TypeError("Check must be a coroutine")

        if not self.extension_checks:
            self.extension_checks = []

        self.extension_checks.append(coroutine)

    def add_extension_prerun(self, coroutine: Callable[..., Coroutine]) -> None:
        """
        Add a coroutine to be run **before** all commands in this Extension.

        !!! note
            Pre-runs will **only** be run if the commands checks pass

        ??? Hint "Example Usage:"
            ```python
            def __init__(self, bot):
                self.add_extension_prerun(self.example)

            async def example(self, context: BaseContext):
                await ctx.send("I ran first")
            ```

        Args:
            coroutine: The coroutine to run

        """
        if not asyncio.iscoroutinefunction(coroutine):
            raise TypeError("Callback must be a coroutine")

        if not self.extension_prerun:
            self.extension_prerun = []
        self.extension_prerun.append(coroutine)

    def add_extension_postrun(self, coroutine: Callable[..., Coroutine]) -> None:
        """
        Add a coroutine to be run **after** all commands in this Extension.

        ??? Hint "Example Usage:"
            ```python
            def __init__(self, bot):
                self.add_extension_postrun(self.example)

            async def example(self, context: BaseContext):
                await ctx.send("I ran first")
            ```

        Args:
            coroutine: The coroutine to run

        """
        if not asyncio.iscoroutinefunction(coroutine):
            raise TypeError("Callback must be a coroutine")

        if not self.extension_postrun:
            self.extension_postrun = []
        self.extension_postrun.append(coroutine)

    def set_extension_error(self, coroutine: Callable[..., Coroutine]) -> None:
        """
        Add a coroutine to handle any exceptions raised in this extension.

        ??? Hint "Example Usage:"
            ```python
            def __init__(self, bot):
                self.set_extension_error(self.example)

        Args:
            coroutine: The coroutine to run

        """
        if not asyncio.iscoroutinefunction(coroutine):
            raise TypeError("Callback must be a coroutine")

        if self.extension_error:
            self.bot.logger.warning("Extension error callback has been overridden!")
        self.extension_error = coroutine
