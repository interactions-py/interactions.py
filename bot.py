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
    sync_commands=False
)

@bot.event
async def on_ready():
    print("we're live!")

@slash.slash(name="testcmd", guild_ids=[852402668294766612])
async def testcmd(ctx: SlashContext):
    print(ctx)
    await ctx.send("test!")

@slash.context_menu(ContextMenuType.MESSAGE, name="testname", guild_ids=[852402668294766612])
async def testname(ctx: MenuContext):
    await ctx.send("test!", hidden=True)

bot.run(open(".TOKEN", "r").read(), reconnect=True, bot=True)