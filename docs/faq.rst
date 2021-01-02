.. currentmodule:: discord_slash

Frequently Asked Questions
==========================

Why don't my slash commands show up?
************************************
If your slash commands don't show up then you have not added them to discord correctly. 

* Ensure that your application has the applications.commands scope in that guild
* If you're creating global commands then you may have to wait to up to 1 hour for them to update.It's suggested you use guild commands for testing.
* Follow the steps below

How do you add slash commands?
******************************

Creating a slash command is a two part process.

1. First you need to register the command with discord for the command to show up when you type ``/``.
2. Secondly you have to add it to your bot.

Create a slash command on Discord  
---------------------------------
Set :py:attr:`auto_register <client.SlashCommand.auto_register>` to ``True`` when you register the slash command client.

.. code-block:: python

   from discord_slash import SlashCommand
   
   slash = SlashCommand(client, auto_register=True)

Or if you prefer to have more control then you can use :py:mod:`discord_slash.utils.manage_commands`

Or you can made requests directly to discord's api, see their `docs <https://discord.com/developers/docs/interactions/slash-commands#registering-a-command>`_ on it.

Add the command to your bot
---------------------------
To add a slash command to your bot you need to use the decorator on a function, much like discord.py's command system but a bit different.


See :ref:`quickstart` for an example.


For normal commands: :py:meth:`SlashCommand.slash() <client.SlashCommand.slash>`, and for Subcommands: :py:meth:`SlashCommand.subcommand() <client.SlashCommand.subcommand>`


How to delete slash commands?
*****************************

You can enable auto deletion of unused commands by setting :py:attr:`auto_delete <client.SlashCommand.auto_delete>` to ``True``.

.. code-block:: python
   
   from discord_slash import SlashCommand
   slash = SlashCommand(auto_delete = True)

.. note::
   This will make a request for **every** single guild your bot is in.

Or you can do it manually:

* Deleting a single command with :py:func:`utils.manage_commands.remove_slash_command`
* Deleting all commands with :py:func:`utils.manage_commands.remove_all_commands`
* Deleting all commands in a specified guild, or all global commands :py:func:`utils.manage_commands.remove_all_commands_in`
* Making a request directly to `discord <https://discord.com/developers/docs/interactions/slash-commands#delete-global-application-command>`_ 

To delete a single command yourself you'll have to have the command id, which can be found by getting all commands for a guild / global commands.

What is the difference between ctx.send and ctx.channel.send?
*************************************************************
Also answers: How to send files?, How to get message object from send?

What is ctx.send
----------------
This sends a message or response to the slash command via the interaction response or interaction webhook.

What can this do?

1. Show command triggering message.
2. Hide the response so only author can see.

However, a few things are not supported:

1. Send files.
2. Get sent message as :py:class:`discord.Message <discord:Message>`. (can't react etc)
3. delete_after, etc.
4. Unable to use after 15 mins from the invocation.

What is ctx.channel.send?
-------------------------
``ctx.channel`` is the discord.py channel object for the channel that the slash command was used in.
``send()`` is the send in discord.py :py:func:`channel.send() <discord:TextChannel.send>`
This means that you can send files / add reactions / get the message etc.

.. warning:: 
   * If the bot is not in the guild, but slash commands are, ``ctx.channel`` will be ``None`` and this won't work.
   * If the bot does not have view / send permissions in that channel this also won't work, and slash commands show up no matter what the channel specific permissions.

What's not supported that supported in slash commands send:

1. Showing command triggering message.
2. Hiding the response so only author can see.

You can use them both together, just be aware of permissions. Try this:

.. code-block:: python

   await ctx.send(5) # Show command usage but don't send message 
   msg = await ctx.channel.send(...) # Send message with the channel object

Have any questions that are not answered here?
**********************************************
Join the `discord server <https://discord.gg/KkgMBVuEkx>`_ and ask!