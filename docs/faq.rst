.. currentmodule:: discord_slash

Frequently Asked Questions
==========================

Why don't my slash commands show up?
************************************
If your slash commands don't show up, then you have not added them to Discord correctly. Check these items.

* Ensure that your application has the ``applications.commands`` scope in that guild.
* If you're creating global command, then you may have to wait up to 1 hour for them to update. It's suggested to use guild command for testing.
* Follow the steps below.

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

Any more questions?
*******************
Join the `discord server <https://discord.gg/KkgMBVuEkx>`_ and ask in ``#questions``!