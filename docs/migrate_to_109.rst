Migrate To 1.0.9
================

1.0.9 Update includes many feature add/rewrite for easier and better usage.
However, due to that, it includes many critical breaking changes.

This page will show how to deal with those changes.

SlashContext
************

.send() / .delete() / .edit()
-----------------------------

Before:

.. code-block:: python

    # Case 1
    await ctx.send(4, content="Hello, World! This is initial message.")
    await ctx.edit(content="Or nevermind.")
    await ctx.delete()
    await ctx.send(content="This is followup message.")

    # Case 2
    await ctx.send(content="This is secret message.", complete_hidden=True)

After:

.. code-block:: python

    # Case 1
    await ctx.respond()
    msg = await ctx.send("Hello, World! This is initial message.")
    await msg.edit(content="Or nevermind.")
    await msg.delete()
    await ctx.send("This is followup message.")

    # Case 2
    await ctx.respond(eat=True)
    await ctx.send("This is secret message.", hidden=True)

Objects of the command invoke
-----------------------------

Before:

.. code-block:: python

    author_id = ctx.author.id if isinstance(ctx.author, discord.Member) else ctx.author
    channel_id = ctx.channel.id if isinstance(ctx.channel, discord.TextChannel) else ctx.channel
    guild_id = ctx.guild.id if isinstance(ctx.guild, discord.Guild) else ctx.guild
    ...

After:

.. code-block:: python

    author_id = ctx.author_id
    channel_id = ctx.channel_id
    guild_id = ctx.guild_id
    ...


Cog Support
***********

Before:

.. code-block:: python

    class Slash(commands.Cog):
        def __init__(self, bot):
            if not hasattr(bot, "slash"):
                # Creates new SlashCommand instance to bot if bot doesn't have.
                bot.slash = SlashCommand(bot, override_type=True)
            self.bot = bot
            self.bot.slash.get_cog_commands(self)

        def cog_unload(self):
            self.bot.slash.remove_cog_commands(self)

        ...

After:

.. code-block:: python

    class Slash(commands.Cog):
        def __init__(self, bot):
            if not hasattr(bot, "slash"):
                # Creates new SlashCommand instance to bot if bot doesn't have.
                bot.slash = SlashCommand(bot, override_type=True)
            self.bot = bot

        ...

Note that removing `if not hasattr(...):` block then moving to main file like this is also recommended.

.. code-block:: python

    bot = commands.Bot(...)
    slash = SlashCommand(bot)
    # No worries for not doing `bot.slash` because its automatically added now.
    ...

Auto-convert
------------

It got deleted, so please remove all of it if you used it.
