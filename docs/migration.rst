Migration
+++++++++
This page contains instructions on how to migrate between versions with breaking changes.

Migrate To V2.0.0
=================
This update introduced component support, and removed support for positional arguments.

To resolve long standing issues with the library, we have removed positional argument support. From now on, only keyword arguments are supported. As such you may need to update your commands.

Put simply, you will need to make sure your command parameters are named the same as your options, or use the connector argument.


Example
*******

.. code-block:: python

    # Example 1
    @slash.slash(name="example_command", options=[
        manage_commands.create_option(name="opt_one", [...]),
        manage_commands.create_option(name="opt_two", [...])
    ])
    async def example_command(ctx, opt_one, opt_two):
        await ctx.send(f"{opt_one=}, {opt_two=}")

    # Example 2
    @slash.slash(name="example_command", options=[
        manage_commands.create_option(name="opt_one", [...]),
        manage_commands.create_option(name="opt_two", [...])
        ],
        connector={"opt_one": "optone",
                    "opt_two": "opttwo"})
    async def example_command(ctx, optone, opttwo):
        await ctx.send(f"{optone=}, {opttwo=}")

Migrate To V1.1.0
==================
Changes that you'll need to make in this version are mainly because of a new ui from discord, more info `here <https://github.com/discord/discord-api-docs/pull/2615>`_

Responding / Deferring
**********************

In regards to :class:`SlashContext` the methods ``.respond`` and ``.ack`` have been removed, and ``.defer`` added.
Deferring a message will allow you to respond for up to 15 mins, but you'll have to defer within three seconds.
When you defer the user will see a "this bot is thinking" message until you send a message, This message can be ephemeral (hidden) or visible.
``.defer`` has a ``hidden`` parameter, which will make the deferred message ephemeral.

We suggest deferring if you might take more than three seconds to respond, but if you will call ``.send`` before three seconds then don't.

.. note::
    You **must** respond with ``.send`` within 15 minutes of the command being invoked to avoid an "interaction failed" message, if you defer.
    This is especially relevant for bots that had 'invisible' commands, where the invocation was not shown.
    If you wish to have the invocation of the command not visible, send an ephemeral success message, and then do what you used to.
    It is no longer possible to "eat" the invocation.
    ``ctx.channel.send`` does **not** count as responding.

Example
*******

.. code-block:: python

    # Before
    @slash.slash(...)
    async def command(ctx, ...):
        await ctx.respond()
        await ctx.send(...)

    # After 1
    @slash.slash(...)
    async def command(ctx, ...):
        await ctx.send(...)

    # After 2
    @slash.slash(...)
    async def command(ctx, ...):
        await ctx.defer()
        # Process that takes time
        await ctx.send(...)


Sending hidden messages
***********************
The method ``.send_hidden`` on :class:`SlashContext` has been removed. Use ``.send(hidden = True, ..)`` instead.

SlashContext
************
``ctx.sent`` has been renamed to :attr:`ctx.responded <.SlashContext.responded>`


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
    await ctx.respond()  # This is optional, but still recommended to.
    msg = await ctx.send("Hello, World! This is initial message.")
    await msg.edit(content="Or nevermind.")
    await msg.delete()
    await ctx.send("This is followup message.")

    # Case 2
    await ctx.respond(eat=True)  # Again, this is optional, but still recommended to.
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


Auto-registering
****************

We've changed the method of automatically registering commands to API to reduce the request amount
and prevent rate limit. So, `auto_register` and `auto_delete` parameter is now removed. Please change your SlashContext
params like this.

Before:

.. code-block:: python

    slash = SlashContext(..., auto_register=True, auto_delete=True)  # Either one can be false.

After:

.. code-block:: python

    slash = SlashContext(..., sync_commands=True)

Cog Support
***********

Before:

.. code-block:: python

    class Slash(commands.Cog):
        def __init__(self, bot):
            if not hasattr(bot, "slash"):
                # Creates new SlashCommand instance to bot if bot doesn't have.
                bot.slash = SlashCommand(bot, override_type=True)
            # Note that hasattr block is optional, meaning you might not have it.
            # Its completely fine, and ignore it.
            self.bot = bot
            self.bot.slash.get_cog_commands(self)

        def cog_unload(self):
            self.bot.slash.remove_cog_commands(self)

        ...

After:

.. code-block:: python

    class Slash(commands.Cog):
        def __init__(self, bot):
            self.bot = bot

        ...

As you can see `if not hasattr(...):` block is removed, moving to main file like this is necessary.

.. code-block:: python

    bot = commands.Bot(...)
    slash = SlashCommand(bot)
    # No worries for not doing `bot.slash` because its automatically added now.
    ...

Auto-convert
------------

It got deleted, so please remove all of it if you used it.

Also, we've added `connector` parameter, which is for helping passing options as kwargs
if your command option is other that english.

Usage:

.. code-block:: python

    {
        "example-arg": "example_arg",
        "시간": "hour"
    }
