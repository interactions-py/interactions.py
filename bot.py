import logging
from discord_slash import SlashCommand, SlashContext, MenuContext
from discord_slash.model import ContextMenuType
from discord import Intents
from discord.ext.commands import Bot

bot = Bot(
    command_prefix="/",
    help_command=None,
    intents=Intents.default()
)
slash = SlashCommand(
    bot,
    sync_commands=True
)
log = logging.Logger(name="errors.log", level=logging.DEBUG)

bot.load_extension("cog")

@bot.event
async def on_ready():
    print("we're live!")

@bot.event
async def on_slash_command_error(ctx, ex):
    log.debug(ctx)
    log.debug(ex)

@slash.slash(name="testcmd", guild_ids=[852402668294766612])
async def testcmd(ctx: SlashContext):
    await ctx.send("test2!")

@slash.context_menu(ContextMenuType.USER, name="testuser", guild_ids=[852402668294766612])
async def testuser(ctx: MenuContext):
    await ctx.send("test!")

@slash.context_menu(ContextMenuType.MESSAGE, name="Testing Name Space", guild_ids=[852402668294766612])
async def testmsg(ctx: MenuContext):
    await ctx.send("test!")

for cmd in slash.commands["context"]:
    print(slash.commands["context"][cmd]._type)

bot.run("Mzc5MzQzMzIyNTQ1NzgyNzg0.WgiY_w.uVRHvtT5KmGFuZ3zOiH_Y3MoGfc", bot=True, reconnect=True)
