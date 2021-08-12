from discord_slash.context import MenuContext
from discord.ext.commands import Cog
from discord.ext.commands.context import Context
from discord_slash import cog_ext
from discord_slash.model import ContextMenuType

class Cog(Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_context_menu(ContextMenuType.MESSAGE, name="cog testing", guild_ids=[852402668294766612])
    async def cog_testing(self, ctx: MenuContext):
        await ctx.send("test!")

def setup(bot):
    bot.add_cog(Cog(bot))