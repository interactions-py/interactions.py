import asyncio
import inspect
from typing import Awaitable, Dict, List, TYPE_CHECKING, Callable, Coroutine, Optional

import interactions.models.internal as naff
from interactions.client.const import MISSING
from interactions.client.utils.misc_utils import wrap_partial
from interactions.models.internal import ContextMenu
from interactions.models.internal.tasks import Task

if TYPE_CHECKING:
    from interactions.client import Client
    from interactions.models.discord import Snowflake_Type
    from interactions.models.internal import AutoDefer, BaseCommand, InteractionCommand, Listener
    from interactions.models.internal import Context


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

    def __new__(cls, bot: "Client", *args, **kwargs) -> "Extension":
        new_cls = super().__new__(cls)
        new_cls.bot = bot
        new_cls.name = cls.__name__
        new_cls.extension_checks = []
        new_cls.extension_prerun = []
        new_cls.extension_postrun = []
        new_cls.extension_error = None
        new_cls.interaction_tree = {}
        new_cls.auto_defer = MISSING

        new_cls.description = kwargs.get("Description", None)
        if not new_cls.description:
            new_cls.description = inspect.cleandoc(cls.__doc__) if cls.__doc__ else None

        # load commands from class
        new_cls._commands = []
        new_cls._listeners = []

        for _name, val in inspect.getmembers(
            new_cls, predicate=lambda x: isinstance(x, (internal.BaseCommand, internal.Listener, Task))
        ):
            if isinstance(val, internal.BaseCommand):
                val.extension = new_cls
                val = wrap_partial(val, new_cls)

                if not isinstance(val, internal.PrefixedCommand) or not val.is_subcommand:
                    # we do not want to add prefixed subcommands
                    new_cls._commands.append(val)

                    if isinstance(val, internal.ModalCommand):
                        bot.add_modal_callback(val)
                    elif isinstance(val, internal.ComponentCommand):
                        bot.add_component_callback(val)
                    elif isinstance(val, internal.HybridCommand):
                        bot.add_hybrid_command(val)
                    elif isinstance(val, internal.InteractionCommand):
                        if not bot.add_interaction(val):
                            continue
                        base, group, sub, *_ = val.resolved_name.split(" ") + [None, None]
                        for scope in val.scopes:
                            if scope not in new_cls.interaction_tree:
                                new_cls.interaction_tree[scope] = {}
                            if group is None or isinstance(val, ContextMenu):
                                new_cls.interaction_tree[scope][val.resolved_name] = val
                            elif group is not None:
                                if not (current := new_cls.interaction_tree[scope].get(base)) or isinstance(
                                    current, internal.InteractionCommand
                                ):
                                    new_cls.interaction_tree[scope][base] = {}
                                if sub is None:
                                    new_cls.interaction_tree[scope][base][group] = val
                                else:
                                    if not (current := new_cls.interaction_tree[scope][base].get(group)) or isinstance(
                                        current, internal.InteractionCommand
                                    ):
                                        new_cls.interaction_tree[scope][base][group] = {}
                                    new_cls.interaction_tree[scope][base][group][sub] = val
                    else:
                        bot.add_prefixed_command(val)

            elif isinstance(val, internal.Listener):
                val = val.copy_with_binding(new_cls)
                bot.add_listener(val)
                new_cls.listeners.append(val)
            elif isinstance(val, Task):
                wrap_partial(val, new_cls)

        bot.logger.debug(
            f"{len(new_cls._commands)} commands and {len(new_cls.listeners)} listeners"
            f" have been loaded from `{new_cls.name}`"
        )

        new_cls.extension_name = inspect.getmodule(new_cls).__name__
        new_cls.bot.ext[new_cls.name] = new_cls

        if hasattr(new_cls, "async_start"):
            if inspect.iscoroutinefunction(new_cls.async_start):
                bot.async_startup_tasks.append(new_cls.async_start())
            else:
                raise TypeError("async_start is a reserved method and must be a coroutine")

        return new_cls

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
            if isinstance(func, internal.ModalCommand):
                for listener in func.listeners:
                    # noinspection PyProtectedMember
                    self.bot._modal_callbacks.pop(listener)
            elif isinstance(func, internal.ComponentCommand):
                for listener in func.listeners:
                    # noinspection PyProtectedMember
                    self.bot._component_callbacks.pop(listener)
            elif isinstance(func, internal.InteractionCommand):
                for scope in func.scopes:
                    if self.bot.interactions.get(scope):
                        self.bot.interactions[scope].pop(func.resolved_name, [])

                if isinstance(func, internal.HybridCommand):
                    # here's where things get complicated - we need to unload the prefixed command
                    # by necessity, there's a lot of logic here to determine what needs to be unloaded
                    if not func.callback:  # not like it was added
                        return

                    if func.is_subcommand:
                        prefixed_base = self.bot.prefixed_commands.get(str(func.name))
                        _base_cmd = prefixed_base
                        if not prefixed_base:
                            # if something weird happened here, here's a safeguard
                            continue

                        if func.group_name:
                            prefixed_base = prefixed_base.subcommands.get(str(func.group_name))
                            if not prefixed_base:
                                continue

                        prefixed_base.remove_command(str(func.sub_cmd_name))

                        if not prefixed_base.subcommands:
                            # the base cmd is now empty, delete it
                            if func.group_name:
                                _base_cmd.remove_command(str(func.group_name))  # type: ignore

                                # and now the base command is empty
                                if not _base_cmd.subcommands:  # type: ignore
                                    # in case you're curious, i did try to put the below behavior
                                    # in a function here, but then it turns out a weird python
                                    # bug can happen if i did that
                                    if cmd := self.bot.prefixed_commands.pop(str(func.name), None):
                                        for alias in cmd.aliases:
                                            self.bot.prefixed_commands.pop(alias, None)

                            elif cmd := self.bot.prefixed_commands.pop(str(func.name), None):
                                for alias in cmd.aliases:
                                    self.bot.prefixed_commands.pop(alias, None)

                    elif cmd := self.bot.prefixed_commands.pop(str(func.name), None):
                        for alias in cmd.aliases:
                            self.bot.prefixed_commands.pop(alias, None)

            elif isinstance(func, internal.PrefixedCommand):
                if not func.is_subcommand:
                    self.bot.prefixed_commands.pop(func.name, None)
                    for alias in func.aliases:
                        self.bot.prefixed_commands.pop(alias, None)
        for func in self.listeners:
            self.bot.listeners[func.event].remove(func)

        self.bot.ext.pop(self.name, None)
        self.bot.logger.debug(f"{self.name} has been drop")

    def add_ext_auto_defer(self, ephemeral: bool = False, time_until_defer: float = 0.0) -> None:
        """
        Add a auto defer for all commands in this extension.

        Args:
            ephemeral: Should the command be deferred as ephemeral
            time_until_defer: How long to wait before deferring automatically

        """
        self.auto_defer = internal.AutoDefer(enabled=True, ephemeral=ephemeral, time_until_defer=time_until_defer)

    def add_ext_check(self, coroutine: Callable[["Context"], Awaitable[bool]]) -> None:
        """
        Add a coroutine as a check for all commands in this extension to run. This coroutine must take **only** the parameter `context`.

        ??? Hint "Example Usage:"
            ```python
            def __init__(self, bot):
                self.add_ext_check(self.example)

            @staticmethod
            async def example(context: Context):
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

            async def example(self, context: Context):
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

            async def example(self, context: Context):
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
