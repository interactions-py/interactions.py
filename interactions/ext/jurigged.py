import inspect
from pathlib import Path
from types import ModuleType
from typing import Callable, Dict

from interactions import Extension, SlashCommand, Client
from interactions.client.errors import ExtensionLoadException, ExtensionNotFound
from interactions.client.utils.misc_utils import find
from interactions.client.const import get_logger

try:
    from jurigged import watch, CodeFile
    from jurigged.live import WatchOperation
    from jurigged.codetools import (
        AddOperation,
        DeleteOperation,
        UpdateOperation,
        LineDefinition,
    )
except ModuleNotFoundError:
    get_logger().error(
        "jurigged not installed, cannot enable jurigged integration.  Install with `pip install discord-py-interactions[jurigged]`"
    )
    raise


__all__ = ("Jurigged", "setup")


def get_all_commands(module: ModuleType) -> Dict[str, Callable]:
    """
    Get all SlashCommands from a specified module.

    Args:
        module: Module to extract commands from
    """
    commands = {}

    def is_extension(e) -> bool:
        """Check that an object is an extension."""
        return inspect.isclass(e) and issubclass(e, Extension) and e is not Extension

    def is_slashcommand(e) -> bool:
        """Check that an object is a slash command."""
        return isinstance(e, SlashCommand)

    for _name, item in inspect.getmembers(module, is_extension):
        inspect_result = inspect.getmembers(item, is_slashcommand)
        exts = []
        for _, val in inspect_result:
            exts.append(val)
        commands[f"{module.__name__}"] = exts

    return {k: v for k, v in commands.items() if v is not None}


class Jurigged(Extension):
    def __init__(self, *_, poll=False) -> None:
        self.poll = poll
        self.command_cache = {}
        self.watcher = None

    async def async_start(self) -> None:
        """Jurigged starting utility."""
        self.bot.logger.warning("Setting sync_ext to True by default for syncing changes")
        self.bot.sync_ext = True

        self.bot.logger.info("Loading jurigged")
        path = Path().resolve()
        self.watcher = watch(f"{path}/[!.]*.py", logger=self.jurigged_log, poll=self.poll)
        self.watcher.prerun.register(self.jurigged_prerun)
        self.watcher.postrun.register(self.jurigged_postrun)

    def jurigged_log(self, event: WatchOperation | AddOperation | DeleteOperation | UpdateOperation) -> None:
        """
        Log a jurigged event

        Args:
            event: jurigged event
        """
        if isinstance(event, WatchOperation):
            self.bot.logger.debug(f"Watch {event.filename}")
        elif isinstance(event, (Exception, SyntaxError)):
            self.bot.logger.exception("Jurigged encountered an error", exc_info=True)
        else:
            action = None
            lineno = event.defn.stashed.lineno
            dotpath = event.defn.dotpath()
            extra = ""

            if isinstance(event.defn, LineDefinition):
                dotpath = event.defn.parent.dotpath()
                extra = f" | {event.defn.text}"

            if isinstance(event, AddOperation):
                action = "Run" if isinstance(event.defn, LineDefinition) else "Add"
            elif isinstance(event, UpdateOperation):
                action = "Update"
            elif isinstance(event, DeleteOperation):
                action = "Delete"
            if not action:
                self.bot.logger.debug(event)
            else:
                event_str = "{action} {dotpath}:{lineno}{extra}"
                self.bot.logger.debug(event_str.format(action=action, dotpath=dotpath, lineno=lineno, extra=extra))

    def jurigged_prerun(self, _path: str, cf: CodeFile) -> None:
        """
        Jurigged prerun event.

        Args:
            _path: Path to file
            cf: File information
        """
        if self.bot.get_ext(cf.module_name):
            self.bot.logger.debug(f"Caching {cf.module_name}")
            self.command_cache = get_all_commands(cf.module)

    def jurigged_postrun(self, _path: str, cf: CodeFile) -> None:  # noqa: C901
        """
        Jurigged postrun event.

        Args:
            _path: Path to file
            cf: File information
        """
        if not self.bot.get_ext(cf.module_name):
            return
        self.bot.logger.debug(f"Checking {cf.module_name}")
        commands = get_all_commands(cf.module)

        self.bot.logger.debug("Checking for changes")
        for module, cmds in commands.items():
            # Check if a module was removed
            if module not in commands:
                self.bot.logger.debug(f"Module {module} removed")
                self.bot.unload_extension(module)

            # Check if a module is new
            elif module not in self.command_cache:
                self.bot.logger.debug(f"Module {module} added")
                try:
                    self.bot.load_extension(module)
                except ExtensionLoadException:
                    self.bot.logger.warning(f"Failed to load new module {module}")

            # Check if a module has more/less commands
            elif len(self.command_cache[module]) != len(cmds):
                self.bot.logger.debug("Number of commands changed, reloading")
                try:
                    self.bot.reload_extension(module)
                except ExtensionNotFound:
                    try:
                        self.bot.load_extension(module)
                    except ExtensionLoadException:
                        self.bot.logger.warning(f"Failed to update module {module}")
                except ExtensionLoadException:
                    self.bot.logger.warning(f"Failed to update module {module}")

            # Check each command for differences
            else:
                for cmd in cmds:
                    old_cmd = find(
                        lambda x, cmd=cmd: x.resolved_name == cmd.resolved_name,
                        self.command_cache[module],
                    )

                    # Extract useful info
                    old_args = old_cmd.options
                    old_arg_names = []
                    new_arg_names = []
                    if old_args:
                        old_arg_names = [x.name.default for x in old_args]
                    new_args = cmd.options
                    if new_args:
                        new_arg_names = [x.name.default for x in new_args]

                    # No changes
                    if not old_args and not new_args:
                        continue

                    # Check if number of args has changed
                    if len(old_arg_names) != len(new_arg_names):
                        self.bot.logger.debug("Number of arguments changed, reloading")
                        try:
                            self.bot.reload_extension(module)
                        except Exception:
                            self.bot.logger.exception(f"Failed to update module {module}", exc_info=True)

                    # Check if arg names have changed
                    elif len(set(old_arg_names) - set(new_arg_names)) > 0:
                        self.bot.logger.debug("Argument names changed, reloading")
                        try:
                            self.bot.reload_extension(module)
                        except Exception:
                            self.bot.logger.exception(f"Failed to update module {module}", exc_info=True)

                    # Check if arg types have changed
                    elif any(new_args[idx].type != x.type for idx, x in enumerate(old_args)):
                        self.bot.logger.debug("Argument types changed, reloading")
                        try:
                            self.bot.reload_extension(module)
                        except Exception:
                            self.bot.logger.exception(f"Failed to update module {module}", exc_info=True)
                    else:
                        self.bot.logger.debug("No changes detected")
        self.command_cache.clear()


def setup(
    bot: Client,
    poll: bool = False,
) -> None:
    Jurigged(bot, poll=poll)
