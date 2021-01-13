.. currentmodule:: discord_slash

Frequently Asked Questions
==========================

Why don't my slash commands show up?
************************************
If your slash commands don't show up, then you have not added them to Discord correctly. Check these items.

* Ensure that your application has the ``applications.commands`` scope in that guild.
* If you're creating global command, then you may have to wait up to 1 hour for them to update. It's suggested to use guild command for testing.
* See `How to add slash commands?`.

How to add slash commands?
******************************

Adding a slash command is a two part process.

1. Registering the command to Discord so the command show up when you type ``/``.
2. Adding it to your bot.

Add a slash command on Discord
---------------------------------
If you want your commands automatically registered, set ``auto_register`` to ``True`` at :class:`.client.SlashCommand`.

.. code-block:: python

   from discord_slash import SlashCommand
   
   slash = SlashCommand(client, auto_register=True)

Or, if you prefer to have more control, you can use :mod:`.utils.manage_commands`.

Or, you can made requests directly to Discord API, read the `docs <https://discord.com/developers/docs/interactions/slash-commands#registering-a-command>`_.

Add the command to your bot
---------------------------
To add a slash command to your bot, you need to use the decorator on a coroutine, just like discord.py's command system but a bit different.

See :ref:`quickstart` for an example.

For normal slash command, use :meth:`.client.SlashCommand.slash`, and for subcommand, use :meth:`.client.SlashCommand.subcommand`.

How to delete slash commands?
*****************************

You can enable auto deletion of unused commands by setting ``auto_delete`` to ``True`` at :class:`.client.SlashCommand`.

.. code-block:: python
   
   from discord_slash import SlashCommand
   slash = SlashCommand(auto_delete = True)

.. note::
   This will make a request for **every** single guild your bot is in.

Or you can do it manually by this methods:

* Deleting a single command with :meth:`utils.manage_commands.remove_slash_command`
* Deleting all commands using :meth:`utils.manage_commands.remove_all_commands`
* Deleting all commands in a specified guild, or all global commands by :meth:`utils.manage_commands.remove_all_commands_in`
* Making a HTTP request to `discord <https://discord.com/developers/docs/interactions/slash-commands#delete-global-application-command>`_

To delete a single command yourself you'll have to have the command id, which can be found by getting all commands for a guild / global commands.

What is the difference between ctx.send and ctx.channel.send?
*************************************************************
* Also answers: How to send files?, How to get :class:`discord.Message` object from ``.send()``?, etc.

ctx.send
--------
This sends a message or response of the slash command via the interaction response or interaction webhook.

These are available by this:

1. Show command triggering message. (a.k.a. ACK)
2. Hide the response so only message author can see.

However, a few things are not supported:

1. Sending files.
2. Getting sent message as :class:`discord.Message`, so you can't add reactions, etc.
3. ``delete_after``, etc.
4. Unable to use after 15 mins from the invocation.

ctx.channel.send
----------------
``ctx.channel`` is the :class:`discord.TextChannel` object for the channel that the slash command was used in.
``send()`` is the sending coroutine in discord.py. (:meth:`discord.TextChannel.send`)
This means that you can send files , add reactions, get the message, etc.

.. warning:: 
   * If the bot is not in the guild, but slash commands are, ``ctx.channel`` will be ``None`` and this won't work.
   * If the bot does not have view/send permissions in that channel this also won't work, but slash commands show up no matter what the channel specific permissions.

These are not supported compared to ``ctx.send``:

1. Showing command triggering message.
2. Hiding the response so only message author can see.

You can use them both together, just be aware of permissions. Try this:

.. code-block:: python

   await ctx.send(5) # Show command usage but don't send message 
   msg = await ctx.channel.send(...) # Send message with the channel object

Can I use something of discord.py's in this extension?
******************************************************
Most things work, but a few that are listed below don't.

Checks
------
discord.py check decorators won't work due to the context of this extension being different from discord.py's. 

Examples: ``@commands.check()``, ``@commands.has_permissions()``, ``@commands.guild_only()``


Events
------
Command-related events like ``on_command_error``, ``on_command``, etc.
This extension triggers some events, check the `events docs <https://discord-py-slash-command.readthedocs.io/en/latest/events.html#>`_ 

Converters
----------
Use ``options=[...]`` or ``auto_convert=[...]`` on the slash command / subcommand decorator instead.

Note:
Pretty much anything from the discord's commands extension doesn't work, also some bot things.

.. warning::
   If you use something that might take a while, eg ``wait_for`` you'll run into two issues:

   1. If you don't respond within 3 seconds (``ctx.send()``) discord invalidates the interaction.
   2. The interaction only lasts for 15 minutes, so if you try and send something with the interaction (``ctx.send``) more than 15 mins after the command was ran it won't work.

   As an alternative you can use ``ctx.channel.send`` but this relies on the the bot being in the guild, and the bot having send perms in that channel.

Why isn't [something] in SlashContext?
**************************************
Simple answer is this: The way discord handles slash commands means that the slash command handler has to be different to discord.py's command handler.

One example is ``ctx.message``:  
``message`` is not available because the slash command usage sending is dependant on what send_type you respond with on ``ctx.send``, so discord doesn't supply the message when sending the interaction.
Others things are also missing due to similar reasons.

Any more questions?
*******************
Join the `discord server <https://discord.gg/KkgMBVuEkx>`_ and ask in ``#questions``!