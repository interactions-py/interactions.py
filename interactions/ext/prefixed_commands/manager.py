import contextlib
from asyncio import TimeoutError
from collections import defaultdict
from typing import Optional, Callable, Any, Coroutine, cast, Iterable
from typing_extensions import Self

from interactions.api.events.base import RawGatewayEvent
from interactions.api.events.discord import MessageCreate
from interactions.api.events.internal import (
    CommandError,
    CommandCompletion,
    CallbackAdded,
    ExtensionUnload,
)
from interactions.client.client import Client
from interactions.client.utils.input_utils import get_args, get_first_word
from interactions.models.discord.enums import Intents
from interactions.models.discord.message import Message
from interactions.models.internal.listener import listen
from .command import PrefixedCommand
from .context import PrefixedContext
from .utils import when_mentioned

__all__ = ("PrefixedInjectedClient", "PrefixedManager", "setup")


class PrefixedInjectedClient(Client):
    """
    A semi-stub for a `Client` injected with prefixed commands.

    This should only be used for type hinting.
    """

    prefixed: "PrefixedManager"
    "The prefixed command manager for this client."


class PrefixedManager:
    """
    The main part of the extension. Deals with injecting itself in the first place.

    Parameters:
        client: The client instance.
        default_prefix: The default prefix to use. Defaults to `None`.
        generate_prefixes: An asynchronous function \
            that takes in a `Client` and `Message` object and returns either a \
            string or an iterable of strings. Defaults to `None`.
        prefixed_context: The object to instantiate for Prefixed Context
    """

    def __init__(
        self,
        client: Client,
        *,
        default_prefix: Optional[str | list[str]] = None,
        generate_prefixes: Optional[
            Callable[
                [Client, Message],
                Coroutine[Any, Any, str | list[str]],
            ]
        ] = None,
        prefixed_context: type[PrefixedContext] = PrefixedContext,
    ) -> None:
        # typehinting funkyness for better typehints
        client = cast(PrefixedInjectedClient, client)

        self.client = client
        self.default_prefix = default_prefix
        self.prefixed_context = prefixed_context
        self.commands: dict[str, PrefixedCommand] = {}
        self._ext_command_list: defaultdict[str, set[str]] = defaultdict(set)

        if (
            default_prefix or (generate_prefixes and generate_prefixes != when_mentioned)
        ) and Intents.MESSAGE_CONTENT not in client.intents:
            client.logger.warning(
                "Prefixed commands will not work since the required intent is not set -> Requires:"
                f" {Intents.MESSAGE_CONTENT.__repr__()} or usage of the default mention prefix as the prefix"
            )

        if default_prefix is None and generate_prefixes is None:
            # by default, use mentioning the bot as the prefix
            generate_prefixes = when_mentioned

        self.generate_prefixes = (  # type: ignore
            generate_prefixes if generate_prefixes is not None else self.generate_prefixes
        )

        self.client.prefixed = self

        self._dispatch_prefixed_commands = self._dispatch_prefixed_commands.copy_with_binding(self)
        self._register_command = self._register_command.copy_with_binding(self)
        self._handle_ext_unload = self._handle_ext_unload.copy_with_binding(self)

        self.client.add_listener(self._dispatch_prefixed_commands)
        self.client.add_listener(self._register_command)
        self.client.add_listener(self._handle_ext_unload)

    async def generate_prefixes(self, client: Client, msg: Message) -> str | list[str]:
        """
        Generates a list of prefixes a prefixed command can have based on the client and message.

        This can be overwritten by passing a function to generate_prefixes on initialization.

        Args:
            client: The client instance.
            msg: The message sent.

        Returns:
            The prefix(es) to check for.
        """
        return self.default_prefix  # type: ignore

    def add_command(self, command: PrefixedCommand) -> None:
        """
        Add a prefixed command to the manager.

        Args:
            command: The command to add.
        """
        if command.is_subcommand:
            raise ValueError("You cannot add subcommands to the client - add the base command instead.")

        command._parse_parameters()

        if self.commands.get(command.name):
            raise ValueError(f"Duplicate command! Multiple commands share the name/alias: {command.name}.")
        self.commands[command.name] = command

        for alias in command.aliases:
            if self.commands.get(alias):
                raise ValueError(f"Duplicate command! Multiple commands share the name/alias: {alias}.")
            self.commands[alias] = command

        if command.extension:
            self._ext_command_list[command.extension.extension_name].add(command.name)
            command.extension._commands.append(command)

    def get_command(self, name: str) -> Optional[PrefixedCommand]:
        """
        Gets a prefixed command by the name/alias specified.

        This function is able to resolve subcommands - fully qualified names can be used.
        For example, passing in ``foo bar`` would get the subcommand ``bar`` from the
        command ``foo``.

        Args:
            name: The name of the command to search for.

        Returns:
            The command object, if found.
        """
        if " " not in name:
            return self.commands.get(name)

        names = name.split()
        if not names:
            return None

        cmd = self.commands.get(names[0])
        if not cmd:
            return cmd

        for name in names[1:]:
            try:
                cmd = cmd.subcommands[name]
            except (AttributeError, KeyError):
                return None

        return cmd

    def _remove_cmd_and_aliases(self, name: str) -> None:
        if cmd := self.commands.pop(name, None):
            if cmd.extension:
                self._ext_command_list[cmd.extension.extension_name].discard(cmd.name)
                with contextlib.suppress(ValueError):
                    cmd.extension._commands.remove(cmd)

            for alias in cmd.aliases:
                self.commands.pop(alias, None)

    def remove_command(self, name: str, delete_parent_if_empty: bool = False) -> Optional[PrefixedCommand]:
        """
        Removes a prefixed command if it exists.

        If an alias is specified, only the alias will be removed.
        This function is able to resolve subcommands - fully qualified names can be used.
        For example, passing in ``foo bar`` would delete the subcommand ``bar``
        from the command ``foo``.

        Args:
            name: The command to remove.
            delete_parent_if_empty: Should the parent command be deleted if it \
                ends up having no subcommands after deleting the command specified? \
                Defaults to `False`.

        Returns:
            The command that was removed, if one was. If the command was not found,
            this function returns `None`.
        """
        command = self.get_command(name)

        if command is None:
            return None

        if name in command.aliases:
            command.aliases.remove(name)
            return command

        if command.parent:
            command.parent.remove_command(command.name)
        else:
            self._remove_cmd_and_aliases(command.name)

        if delete_parent_if_empty:
            while command.parent is not None and not command.parent.subcommands:
                if command.parent.parent:
                    _new_cmd = command.parent
                    command.parent.parent.remove_command(command.parent.name)
                    command = _new_cmd
                else:
                    self._remove_cmd_and_aliases(command.parent.name)
                    break

        return command

    @listen("callback_added")
    async def _register_command(self, event: CallbackAdded) -> None:
        """Registers a prefixed command, if there is one given."""
        if not isinstance(event.callback, PrefixedCommand):
            return

        cmd = event.callback
        cmd.extension = event.extension

        if not cmd.is_subcommand:
            self.add_command(cmd)

    @listen("extension_unload")
    async def _handle_ext_unload(self, event: ExtensionUnload) -> None:
        """Unregisters all prefixed commands in an extension as it is being unloaded."""
        for name in self._ext_command_list[event.extension.extension_name].copy():
            self.remove_command(name)

    @listen("raw_message_create", is_default_listener=True)
    async def _dispatch_prefixed_commands(self, event: RawGatewayEvent) -> None:  # noqa: C901
        """Determine if a prefixed command is being triggered, and dispatch it."""
        # don't waste time processing this if there are no prefixed commands
        if not self.commands:
            return

        data = event.data

        # many bots will not have the message content intent, and so will not have content
        # for most messages. since there's nothing for prefixed commands to work off of,
        # we might as well not waste time
        if not data.get("content"):
            return

        # webhooks and users labeled with the bot property are bots, and should be ignored
        if data.get("webhook_id") or data["author"].get("bot", False):
            return

        # now, we've done the basic filtering out, but everything from here on out relies
        # on a proper message object, so now we either hope its already in the cache or wait
        # on the processor

        # first, let's check the cache...
        message = self.client.cache.get_message(int(data["channel_id"]), int(data["id"]))

        # this huge if statement basically checks if the message hasn't been fully processed by
        # the processor yet, which would mean that these fields aren't fully filled
        if message and (
            (not message._guild_id and event.data.get("guild_id"))
            or (message._guild_id and not message.guild)
            or not message.channel
        ):
            message = None

        # if we didn't get a message, then we know we should wait for the message create event
        if not message:
            try:
                # i think 2 seconds is a very generous timeout limit
                msg_event: MessageCreate = await self.client.wait_for(
                    MessageCreate, checks=lambda e: int(e.message.id) == int(data["id"]), timeout=2
                )
                message = msg_event.message
            except TimeoutError:
                return

        if not message.content:
            return

        # here starts the actual prefixed command parsing part
        prefixes: str | Iterable[str] = await self.generate_prefixes(self.client, message)

        if isinstance(prefixes, str):
            # its easier to treat everything as if it may be an iterable
            # rather than building a special case for this
            prefixes = (prefixes,)  # type: ignore

        prefix_used = next(
            (prefix for prefix in prefixes if message.content.startswith(prefix)),
            None,
        )
        if not prefix_used:
            return

        context = self.prefixed_context.from_message(self.client, message)
        context.prefix = prefix_used

        content_parameters = message.content.removeprefix(prefix_used).strip()
        command: "Self | PrefixedCommand" = self  # yes, this is a hack

        while True:
            first_word: str = get_first_word(content_parameters)  # type: ignore
            if isinstance(command, PrefixedCommand):
                new_command = command.subcommands.get(first_word)
            else:
                new_command = command.commands.get(first_word)
            if not new_command or not new_command.enabled:
                break

            command = new_command
            content_parameters = content_parameters.removeprefix(first_word).strip()

        if not isinstance(command, PrefixedCommand) or not command.enabled:
            return

        context.command = command
        context.content_parameters = content_parameters.strip()
        context.args = get_args(context.content_parameters)
        try:
            if self.client.pre_run_callback:
                await self.client.pre_run_callback(context)
            await command(context)
            if self.client.post_run_callback:
                await self.client.post_run_callback(context)
        except Exception as e:
            self.client.dispatch(CommandError(ctx=context, error=e))
        finally:
            self.client.dispatch(CommandCompletion(ctx=context))


def setup(
    client: Client,
    *,
    default_prefix: Optional[str | list[str]] = None,
    generate_prefixes: Optional[
        Callable[
            [Client, Message],
            Coroutine[Any, Any, str | list[str]],
        ]
    ] = None,
    prefixed_context: type[PrefixedContext] = PrefixedContext,
) -> PrefixedManager:
    """
    Sets up prefixed commands. It is recommended to use this function directly to do so.

    Parameters:
        client: The client instance.
        default_prefix: The default prefix to use. Defaults to `None`.
        generate_prefixes: An asynchronous function \
            that takes in a `Client` and `Message` object and returns either a \
            string or an iterable of strings. Defaults to `None`.
        prefixed_context: The object to instantiate for Prefixed Context

    Returns:
        PrefixedManager: The class that deals with all things prefixed commands.
    """
    return PrefixedManager(
        client,
        default_prefix=default_prefix,
        generate_prefixes=generate_prefixes,
        prefixed_context=prefixed_context,
    )
