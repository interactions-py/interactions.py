from interactions import Extension
from interactions.client.errors import CommandCheckFailure, ExtensionLoadException
from interactions.ext.prefixed_commands import prefixed_command, PrefixedContext

__all__ = ("DebugExts",)


class DebugExts(Extension):
    @prefixed_command("debug_reload")
    async def reload(self, ctx: PrefixedContext, module: str) -> None:
        try:
            await self.drop_ext.callback(ctx, module)
        except ExtensionLoadException:
            pass
        await self.load_ext.callback(ctx, module)

    @prefixed_command("debug_load")
    async def load_ext(self, ctx: PrefixedContext, module: str) -> None:
        self.bot.load_extension(module)
        await ctx.message.add_reaction("🪴")

    @prefixed_command("debug_drop")
    async def drop_ext(self, ctx: PrefixedContext, module: str) -> None:
        self.bot.unload_extension(module)
        await ctx.message.add_reaction("💥")

    @reload.error
    @load_ext.error
    @drop_ext.error
    async def reload_error(self, error: Exception, ctx: PrefixedContext, *args) -> None:
        if isinstance(error, CommandCheckFailure):
            return await ctx.send("You do not have permission to execute this command")
        if isinstance(error, ExtensionLoadException):
            return await ctx.send(str(error))
        raise


def setup(bot) -> None:
    DebugExts(bot)
