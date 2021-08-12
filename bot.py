import logging
from typing import Union
from discord_slash import SlashCommand, SlashContext, ComponentContext, MenuContext
from discord_slash.model import ContextMenuType, ButtonStyle
from discord_slash.utils.manage_components import create_actionrow, create_button
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

@slash.context_menu(ContextMenuType.USER, name="Testing User Space", guild_ids=[852402668294766612])
async def testuser(ctx: MenuContext):
    await ctx.send("test!")

@slash.context_menu(ContextMenuType.MESSAGE, name="Testing Name Space", guild_ids=[852402668294766612])
async def testmsg(ctx: Union[ComponentContext, MenuContext]):
    print(ctx.target)
    await ctx.defer()
    await ctx.send(ctx.target["message"]["content"])

bot.run("Mzc5MzQzMzIyNTQ1NzgyNzg0.WgiY_w.8Mxf0hEjruTUs5SQDpKhOxUPquk", bot=True, reconnect=True)
