Quickstart
==========

Before doing anything, it is highly recommended to read discord.py's quickstart.
You can find it by clicking :ref:`this <discord:quickstart>`.

Firstly, we will begin by installing the python library extension for discord.py:

.. code-block::

    pip install -U discord-py-slash-command

Then, let's invite the bot. See discord.py's bot account create tutorial.
After reading that, there is one more step before inviting your bot.
The second step will now be setting your scope correctly for the bot to
properly recognize slash commands, as shown here:

.. image:: images/scope.jpg

Then, invite your bot to your guild.

Now, let's create a simple bot. Create one Python code file.
For this example, ``main.py`` will be used.

.. code-block:: python

    import discord
    from discord_slash import SlashCommand # Importing the newly installed library.

    client = discord.Client(intents=discord.Intents.all())
    slash = SlashCommand(client, sync_commands=True) # Declares slash commands through the client.

    @client.event
    async def on_ready():
        print("Ready!")

    client.run("your_bot_token_here")

Let's give this a run. When you run this code, you'll see... nothing but ``Ready!``.

That's completely normal, because we haven't defined any slash commands yet.
We can do so by adding this code shown here:

.. code-block:: python

    import discord
    from discord_slash import SlashCommand # Importing the newly installed library.

    client = discord.Client(intents=discord.Intents.all())
    slash = SlashCommand(client, sync_commands=True) # Declares slash commands through the client.

    guild_ids = [789032594456576001] # Put your server ID in this array.

    @client.event
    async def on_ready():
        print("Ready!")

    @slash.slash(name="ping", guild_ids=guild_ids)
    async def _ping(ctx): # Defines a new "context" (ctx) command called "ping."
        await ctx.respond()
        await ctx.send(f"Pong! ({client.latency*1000}ms)")

    client.run("your_bot_token_here")

Let's explain some of the major code differences between the prior examples shown
here to give a better understanding of what is going on:

- ``guild_ids = [789032594456576001]``: This is for adding your command as a guild command.

Otherwise, you need to wait for an hour to wait until your command is added. This is due
to the code recognizing the new slash command as a **global** command instead of what we
originally want, a *guild* slash command.

- ``@slash.slash(name="ping", ...`` ~ ``await ctx.send(...)``: This adds a new slash command.

This command basically sends a request to the API declaring a new command to exist as an HTTP
request through the Bot v8 API.

Congratulations! You just created a very simple slash command bot! While, yes, this quickstart doesn't
cover everything, this still shows the basics of the library extension. In order to learn more about
the advanced parts of adding slash commands, it is recommended to check out the other sections of our
docs.

Still have any questions? Feel free to join the Discord server by clicking `this <https://discord.gg/KkgMBVuEkx>`_.
