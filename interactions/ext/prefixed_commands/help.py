import functools
from logging import Logger

import attrs

from interactions import Embed, get_logger
from interactions.ext.paginators import Paginator
from interactions.models.discord.color import BrandColors, Color
from .command import prefixed_command, PrefixedCommand
from .context import PrefixedContext
from .manager import PrefixedInjectedClient

__all__ = ("PrefixedHelpCommand",)


@attrs.define(eq=False, order=False, hash=False, slots=True)
class PrefixedHelpCommand:
    """A help command for all prefixed commands in a bot."""

    client: "PrefixedInjectedClient" = attrs.field()
    """The client to use for the help command."""

    show_hidden: bool = attrs.field(default=False, kw_only=True)
    """Should hidden commands be shown?"""
    show_disabled: bool = attrs.field(default=False, kw_only=True)
    """Should disabled commands be shown?"""
    run_checks: bool = attrs.field(default=False, kw_only=True)
    """Should only commands that's checks pass be shown?"""
    show_self: bool = attrs.field(default=False, kw_only=True)
    """Should this command be shown in the help message?"""
    show_usage: bool = attrs.field(default=False, kw_only=True)
    """Should usage for commands be shown?"""
    show_aliases: bool = attrs.field(default=False, kw_only=True)
    """Should aliases for commands be shown?"""
    show_prefix: bool = attrs.field(default=False, kw_only=True)
    """Should the prefix be shown?"""
    embed_color: Color = attrs.field(default=BrandColors.BLURPLE, kw_only=True)
    """The colour to show in the Embeds."""

    embed_title: str = attrs.field(default="{username} Help Command", kw_only=True)
    """The title to use in the embed. {username} will be replaced by the client's username."""
    not_found_message: str = attrs.field(default="Sorry! No command called `{cmd_name}` was found.", kw_only=True)
    """The message to send when a command was not found. {cmd_name} will be replaced by the requested command."""
    fallback_help_string: str = attrs.field(default="No help message available.", kw_only=True)
    """The text to display when a command does not have a help string defined."""
    fallback_brief_string: str = attrs.field(default="No help message available.", kw_only=True)
    """The text to display when a command does not have a brief string defined."""

    _cmd: PrefixedCommand = attrs.field(init=False, default=None)
    logger: Logger = attrs.field(init=False, factory=get_logger)

    def __attrs_post_init__(self) -> None:
        if not self._cmd:
            self._cmd = self._callback  # type: ignore

    def register(self) -> None:
        """Registers the help command."""
        if not isinstance(self._cmd.callback, functools.partial):
            # prevent wrap-nesting
            self._cmd.callback = functools.partial(self._cmd.callback, self)

        # replace existing help command if found
        if "help" in self.client.prefixed.commands:
            self.logger.warning("Replacing existing help command.")
            del self.client.prefixed.commands["help"]

        self.client.prefixed.add_command(self._cmd)  # type: ignore

    async def send_help(self, ctx: PrefixedContext, cmd_name: str | None) -> None:
        """
        Send a help message to the given context.

        Args:
            ctx: The context to use.
            cmd_name: An optional command name to send help for.
        """
        await self._callback.callback(ctx, cmd_name)  # type: ignore

    @prefixed_command(name="help")
    async def _callback(self, ctx: PrefixedContext, *, cmd_name: str | None = None) -> None:
        if cmd_name:
            return await self._help_specific(ctx, cmd_name)
        await self._help_list(ctx)

    async def _help_list(self, ctx: PrefixedContext) -> None:
        cmds = await self._gather(ctx)

        output = []
        for cmd in cmds.values():
            _temp = self._generate_command_string(cmd, ctx)
            _temp += f"\n{cmd.brief or self.fallback_brief_string}"

            output.append(self._sanitise_mentions(_temp))
        if len("\n".join(output)) > 500:
            paginator = Paginator.create_from_list(self.client, output, page_size=500)
            paginator.default_color = self.embed_color
            paginator.default_title = self.embed_title.format(username=self.client.user.username)
            await paginator.send(ctx)
        else:
            embed = Embed(
                title=self.embed_title.format(username=self.client.user.username),
                description="\n".join(output),
                color=self.embed_color,
            )
            await ctx.reply(embeds=embed)

    async def _help_specific(self, ctx: PrefixedContext, cmd_name: str) -> None:
        cmds = await self._gather(ctx)

        if cmd := cmds.get(cmd_name.lower()):
            _temp = self._generate_command_string(cmd, ctx)
            _temp += f"\n{cmd.help or self.fallback_help_string}"
            await ctx.reply(self._sanitise_mentions(_temp))
        else:
            await ctx.reply(self.not_found_message.format(cmd_name=cmd_name))

    async def _gather(self, ctx: PrefixedContext | None = None) -> dict[str, PrefixedCommand]:
        """
        Gather commands based on the rules set out in the class attributes.

        Args:
            ctx: The context to use to establish usability.

        Returns:
            dict[str, PrefixedCommand]: A list of commands fit the class attribute configuration.
        """
        out: dict[str, PrefixedCommand] = {}

        for cmd in frozenset(self.client.prefixed.commands.values()):
            if not cmd.enabled and not self.show_disabled:
                continue

            if cmd == self._cmd and not self.show_self:
                continue

            if cmd.hidden and not self.show_hidden:
                continue

            if ctx and cmd.checks and not self.run_checks:
                # cmd._can_run would check the cooldowns, we don't want that so manual calling is required
                for _c in cmd.checks:
                    if not await _c(ctx):
                        continue

                if cmd.extension and cmd.extension.extension_checks:
                    for _c in cmd.extension.extension_checks:
                        if not await _c(ctx):
                            continue

            out[cmd.qualified_name] = cmd

        return out

    def _sanitise_mentions(self, text: str) -> str:
        """
        Replace mentions with a format that won't ping or look weird in code blocks.

        Args:
            The text to sanitise.
        """
        mappings = {
            "@everyone": "@\u200beveryone",
            "@here": "@\u200bhere",
            f"<@{self.client.user.id}>": f"@{self.client.user.username}",
            f"<@!{self.client.user.id}>": f"@{self.client.user.username}",
        }
        for source, target in mappings.items():
            text = text.replace(source, target)

        return text

    def _generate_command_string(self, cmd: PrefixedCommand, ctx: PrefixedContext) -> str:
        """
        Generate a string based on a command, class attributes, and the context.

        Args:
            cmd: The command in question.
            ctx: The context for this command.
        """
        _temp = f"`{ctx.prefix if self.show_prefix else ''}{cmd.qualified_name}`"

        if cmd.aliases and self.show_aliases:
            _temp += "|" + "|".join([f"`{a}`" for a in cmd.aliases])

        if cmd.usage and self.show_usage:
            _temp += f" {cmd.usage}"
        return _temp
