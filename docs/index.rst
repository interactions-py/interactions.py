.. discord-py-slash-command documentation master file, created by
   sphinx-quickstart on Sat Dec 12 13:49:27 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to discord-py-slash-command's documentation!
====================================================

discord-py-slash-command is simple discord.py extension
for using Discord's Slash Command feature.

Example:

.. code-block:: python

    import discord
    from discord.ext import commands
    from discord_slash import SlashCommand
    from discord_slash import SlashContext

    bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
    slash = SlashCommand(bot)


    @slash.slash(name="test")
    async def _test(ctx: SlashContext):
        embed = discord.Embed(title="embed test")
        await ctx.send(content="test", embeds=[embed])


    bot.run("discord_token")

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   quickstart.rst
   discord_slash.rst
   events.rst
   discord_slash.utils.rst



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
