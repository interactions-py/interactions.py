import asyncio
import platform
import tracemalloc

from interactions import (
    Client,
    Extension,
    listen,
    slash_command,
    InteractionContext,
    Timestamp,
    TimestampStyles,
    Intents,
)
from interactions.client.const import __version__, __py_version__
from interactions.models.internal import checks
from .debug_application_cmd import DebugAppCMD
from .debug_exec import DebugExec
from .debug_exts import DebugExts
from .utils import get_cache_state, debug_embed

__all__ = ("DebugExtension",)


class DebugExtension(DebugExec, DebugAppCMD, DebugExts, Extension):
    class Metadata(Extension.Metadata):
        name = "Debug Extension"
        description = "Debugging utilities for interactions.py"
        version = "1.0.0"
        url = "https://github.com/interactions-py/interactions.py"
        requirements = ["interactions>=5.0.0"]

    def __init__(self, bot: Client) -> None:
        bot.logger.info("Debug Extension is mounting!")

        super().__init__(bot)
        self.add_ext_check(checks.is_owner())

        tracemalloc.start()
        bot.logger.warning("Tracemalloc started")

        self.client.http.show_ratelimit_traceback = True
        bot.logger.warning("Ratelimit tracebacks enabled")

    async def async_start(self) -> None:
        loop = asyncio.get_running_loop()
        loop.set_debug(True)
        self.bot.logger.warning("Asyncio debug mode enabled")

    @listen()
    async def on_startup(self) -> None:
        self.bot.logger.info(f"Started {self.bot.user.tag} [{self.bot.user.id}] in Debug Mode")

        self.bot.logger.info(f"Caching System State: \n{get_cache_state(self.bot)}")

    @slash_command(
        "debug",
        sub_cmd_name="info",
        sub_cmd_description="Get basic information about the bot",
    )
    async def debug_info(self, ctx: InteractionContext) -> None:
        await ctx.defer()

        uptime = Timestamp.fromdatetime(self.bot.start_time)
        e = debug_embed("General")
        e.set_thumbnail(self.bot.user.avatar.url)
        e.add_field("Operating System", platform.platform())

        e.add_field("Version Info", f"I.py@{__version__} | Py@{__py_version__}")

        e.add_field("Start Time", f"{uptime.format(TimestampStyles.RelativeTime)}")

        if privileged_intents := [i.name for i in self.bot.intents if i in Intents.PRIVILEGED]:
            e.add_field("Privileged Intents", " | ".join(privileged_intents))

        e.add_field("Loaded Exts", ", ".join(self.bot.ext))

        e.add_field("Guilds", str(len(self.bot.guilds)))

        await ctx.send(embeds=[e])

    @debug_info.subcommand("cache", sub_cmd_description="Get information about the current cache state")
    async def cache_info(self, ctx: InteractionContext) -> None:
        await ctx.defer()
        e = debug_embed("Cache")

        e.description = f"```prolog\n{get_cache_state(self.bot)}\n```"
        await ctx.send(embeds=[e])

    @debug_info.subcommand("shutdown", sub_cmd_description="Shutdown the bot.")
    async def shutdown(self, ctx: InteractionContext) -> None:
        await ctx.send("Shutting down 😴")
        await self.bot.stop()


def setup(bot: Client) -> None:
    DebugExtension(bot)
