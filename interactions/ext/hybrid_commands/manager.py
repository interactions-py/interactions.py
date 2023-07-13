from typing import cast, Callable, Any

from interactions import Client, BaseContext, listen
from interactions.api.events import CallbackAdded, ExtensionUnload
from interactions.ext import prefixed_commands as prefixed

from .context import HybridContext
from .hybrid_slash import (
    _values_wrapper,
    base_subcommand_generator,
    HybridSlashCommand,
    _HybridToPrefixedCommand,
    slash_to_prefixed,
)

__all__ = ("HybridManager", "setup")


def add_use_slash_command_message(
    prefixed_cmd: _HybridToPrefixedCommand, slash_cmd: HybridSlashCommand
) -> _HybridToPrefixedCommand:
    if prefixed_cmd.has_binding:

        def wrap_old_callback(func: Callable) -> Any:
            async def _msg_callback(self, ctx: prefixed.PrefixedContext, *args, **kwargs):
                await ctx.reply(f"This command has been updated. Please use {slash_cmd.mention(ctx.guild_id)} instead.")
                await func(ctx, *args, **kwargs)

            return _msg_callback

    else:

        def wrap_old_callback(func: Callable) -> Any:
            async def _msg_callback(ctx: prefixed.PrefixedContext, *args, **kwargs):
                await ctx.reply(f"This command has been updated. Please use {slash_cmd.mention(ctx.guild_id)} instead.")
                await func(ctx, *args, **kwargs)

            return _msg_callback

    prefixed_cmd.callback = wrap_old_callback(prefixed_cmd.callback)
    return prefixed_cmd


class HybridManager:
    """
    The main part of the extension. Deals with injecting itself in the first place.

    Parameters:
        client: The client instance.
        hybrid_context: The object to instantiate for Hybrid Context
        use_slash_command_msg: If enabled, will send out a message encouraging users to use the slash command \
            equivalent whenever they use the prefixed command version.
    """

    def __init__(
        self, client: Client, *, hybrid_context: type[BaseContext] = HybridContext, use_slash_command_msg: bool = False
    ) -> None:
        if not hasattr(client, "prefixed") or not isinstance(client.prefixed, prefixed.PrefixedManager):
            raise TypeError("Prefixed commands are not set up for this bot.")

        self.hybrid_context = hybrid_context
        self.use_slash_command_msg = use_slash_command_msg

        self.client = cast(prefixed.PrefixedInjectedClient, client)
        self.ext_command_list: dict[str, list[str]] = {}

        self.client.add_listener(self.add_hybrid_command.copy_with_binding(self))
        self.client.add_listener(self.handle_ext_unload.copy_with_binding(self))

        self.client.hybrid = self

    @listen("on_callback_added")
    async def add_hybrid_command(self, event: CallbackAdded):
        if (
            not isinstance(event.callback, HybridSlashCommand)
            or not event.callback.callback
            or event.callback._dummy_base
        ):
            return

        cmd = event.callback
        prefixed_transform = slash_to_prefixed(cmd)

        if self.use_slash_command_msg:
            prefixed_transform = add_use_slash_command_message(prefixed_transform, cmd)

        if cmd.is_subcommand:
            base = None
            if not (base := self.client.prefixed.commands.get(str(cmd.name))):
                base = base_subcommand_generator(
                    str(cmd.name),
                    list(_values_wrapper(cmd.name.to_locale_dict())) + cmd.aliases,
                    str(cmd.name),
                    group=False,
                )
                self.client.prefixed.add_command(base)

            if cmd.group_name:  # group command
                group = None
                if not (group := base.subcommands.get(str(cmd.group_name))):
                    group = base_subcommand_generator(
                        str(cmd.group_name),
                        list(_values_wrapper(cmd.group_name.to_locale_dict())) + cmd.aliases,
                        str(cmd.group_name),
                        group=True,
                    )
                    base.add_command(group)
                base = group

            # since this is added *after* the base command has been added to the bot, we need to run
            # this function ourselves
            prefixed_transform._parse_parameters()
            base.add_command(prefixed_transform)
        else:
            self.client.prefixed.add_command(prefixed_transform)

        if cmd.extension:
            self.ext_command_list.setdefault(cmd.extension.extension_name, []).append(cmd.resolved_name)

    @listen("extension_unload")
    async def handle_ext_unload(self, event: ExtensionUnload) -> None:
        if not self.ext_command_list.get(event.extension.extension_name):
            return

        for cmd in self.ext_command_list[event.extension.extension_name]:
            self.client.prefixed.remove_command(cmd, delete_parent_if_empty=True)

        del self.ext_command_list[event.extension.extension_name]


def setup(
    client: Client, *, hybrid_context: type[BaseContext] = HybridContext, use_slash_command_msg: bool = False
) -> HybridManager:
    """
    Sets up hybrid commands. It is recommended to use this function directly to do so.

    !!! warning
        Prefixed commands need to be set up prior to using this.

    Args:
        client: The client instance.
        hybrid_context: The object to instantiate for Hybrid Context
        use_slash_command_msg: If enabled, will send out a message encouraging users to use the slash command \
            equivalent whenever they use the prefixed command version.

    Returns:
        HybridManager: The class that deals with all things hybrid commands.
    """
    return HybridManager(client, hybrid_context=hybrid_context, use_slash_command_msg=use_slash_command_msg)
