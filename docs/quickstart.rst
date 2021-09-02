Quickstart
==========

Before doing anything, it is highly recommended to read discord.py's quickstart.
You can find it by clicking :ref:`this here <discord:quickstart>`.

Firstly, we will begin by installing the python library extension for discord.py:

.. code-block::

    pip install -U discord-py-interactions

Then, let's invite the bot. See discord.py's bot account create tutorial.
After reading that, there is one more step before inviting your bot.
The second step will now be setting your scope correctly for the bot to
properly recognize slash commands, as shown here:

.. image:: _static/scope.jpg

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

That's completely normal. Why is that? Well, it's because we haven't defined any actual
slash commands just yet. We can do that by adding this code shown here:

.. code-block:: python

    """
        Make sure this code is added before the client.run() call!
        It also needs to be under on_ready, otherwise, this will not work.
    """

    guild_ids = [789032594456576001] # Put your server ID in this array.

    @slash.slash(name="ping", guild_ids=guild_ids)
    async def _ping(ctx): # Defines a new "context" (ctx) command called "ping."
        await ctx.send(f"Pong! ({client.latency*1000}ms)")

.. note::
    In this example we responded directly to the interaction, however if you want to delay the response (if you need more than 3 seconds before sending a message)
    you can defer the response for up to 15 minutes with :meth:`ctx.defer() <.SlashContext.defer()>`, this displays a "Bot is thinking" message.
    However do not defer the response if you will be able to respond (send) within three seconds as this will cause a message to flash up

Let's compare some of the major code differences between the prior examples in order
to explain what's going on here:

- ``guild_ids = [789032594456576001]``: This is for adding your command as a guild command.

It is very important for us to make sure that we're declaring this part of the ``@slash.slash``
decorator if we're wanting to declare a guild command and not a **global** one. The reason as for
why this is needed is because the Discord Bot API can take up to 1 hour to register a global
command that is called via. the code here when this key-word argument is not passed.

- ``@slash.slash(name="ping", ...`` ~ ``await ctx.send(...)``: This adds a new slash command.

This command basically sends a request to the API declaring a new command to exist as an HTTP
request through the Bot v8 API.

Congratulations! You just created a very simple slash command bot! While, yes, this quickstart doesn't
cover everything, this still shows the basics of the library extension. In order to learn more about
the advanced parts of adding slash commands, it is recommended to check out the other sections of our
docs.

Still have any questions? Feel free to join the Discord server by clicking `this <https://discord.gg/KkgMBVuEkx>`_.
