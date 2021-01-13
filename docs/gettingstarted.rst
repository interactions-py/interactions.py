Getting Started
===============

Now that things have been explained through the `quickstart`_ page for you
to begin making slash commands for your bot, now it is time to discuss some
of the much more rather advanced or complicated aspects of slash commands.
Our first discussion will be covering over the implementation of options in
your commands.

First, let's explain by how commands are parsed through the Discord Bot API.
As you may know, Discord relies a lot on the interaction of HTTP Requests and
JSON tables. As is with the case here, commands are the exact same way with
having JSON tables to structure the design of it for Discord to understand. We
can apply this information likewise with how options are to be designed in the
Python code. Below attached is from the *Discord Developer Portal* on Slash
Commands for showing how options are designed.

+-------------+--------------------------------------------+----------------------------------------------------------------------------------------------------+
| **Field**   | **Type**                                   | **Description**                                                                                    |
+-------------+--------------------------------------------+----------------------------------------------------------------------------------------------------+
| type        | int                                        | value of ApplicationCommandOptionType                                                              |
+-------------+--------------------------------------------+----------------------------------------------------------------------------------------------------+
| name        | string                                     | 1-32 character name matching ``^[\w-]{1,32}$``                                                     |
+-------------+--------------------------------------------+----------------------------------------------------------------------------------------------------+
| description | string                                     | 1-100 character description                                                                        |
+-------------+--------------------------------------------+----------------------------------------------------------------------------------------------------+
| default?    | bool                                       | the first required option for the user to complete--only one option can be default                 |
+-------------+--------------------------------------------+----------------------------------------------------------------------------------------------------+
| required?   | bool                                       | if the parameter is required or optional--default ``false``                                        |
+-------------+--------------------------------------------+----------------------------------------------------------------------------------------------------+
| choices?    | array of `ApplicationCommandOptionChoice`_ | choices for ``string`` and ``int`` types for the user to pick from                                 |
+-------------+--------------------------------------------+----------------------------------------------------------------------------------------------------+
| options?    | array of `ApplicationCommandOption`_       | if the option is a subcommand or subcommand group type, this nested options will be the parameters |
+-------------+--------------------------------------------+----------------------------------------------------------------------------------------------------+

This table shows us the way that Discord handles the structure of options for
slash commands through their Bot API. For visualization purposes, we'll quickly
make a JSON example (although we won't be using it) in order to explain how this
works:

.. code-block:: python

  {
    "name": "argOne",
    "description": "description of first argument",
    "type": 3, # STRING type,
    "required": True
  }
  
With this very basic understanding in mind, now we are able to begin programming
a simple Python script that will allow us to utilize this ability through one of
the many subclasses offered in *discord-py-slash-command*.

.. code-block:: python

  import discord
  from discord_slash import SlashCommand
  from discord_slash.utils import manage_commands # Allows us to manage the command settings.

  client = discord.Client(intents=discord.Intents.all())
  slash = SlashCommand(client, auto_register=True)

  guild_ids = [789032594456576001]

  @client.event
  async def on_ready():
      print("Ready!")

  @slash.slash(
    name="test",
    description="this returns the bot latency",
    options=[manage_commands.create_option(
      name = "argOne",
      description = "description of first argument",
      option_type = 3, # STRING type,
      required = True
    )],
    guild_ids=guild_ids
  )
  async def _test(ctx, argOne: str):
      await ctx.send(content=f"You responded with {argOne}.")

  client.run("your_bot_token_here")
  
The main changes that you need to know about are with the lines calling the import
of ``manage_commands``, as well as the ``options = [] ...`` code within the `@slash.slash()`
context coroutine. 

.. _quickstart: https://discord-py-slash-command.readthedocs.io/en/latest/quickstart.html
.. _ApplicationCommandOptionChoice: https://discord.com/developers/docs/interactions/slash-commands#applicationcommandoptionchoice
.. _ApplicationCommandOption: https://discord.com/developers/docs/interactions/slash-commands#applicationcommandoption

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   quickstart.rst
   gettingstarted.rst
   discord_slash.rst
   events.rst
   discord_slash.utils.rst
   faq.rst

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
