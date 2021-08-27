Getting Started
===============

Where do we start?
******************

Before we begin getting started on everything else, it is recommended to
check out the `quickstart`_ page first to get a basic grip on making
slash commands for your bot.

Making a slash command.
***********************

The basics.
-----------

First, let's explain by how commands are parsed through the Discord Bot API.

As you may know, Discord relies a lot on the interaction of HTTP Requests and
JSON tables. As is with the case here, commands are the exact same way with
having JSON tables to structure the design of it for Discord to understand. We
can apply this information likewise with how slash commands are to be designed
in the Python code. Below attached is from the *Discord Developer Portal* on Slash
Commands for showing how they are designed.

+-------------+--------------------------------------------+-----------------------------------------------------------------------------------------------------+
| **Field**   | **Type**                                   | **Description**                                                                                     |
+-------------+--------------------------------------------+-----------------------------------------------------------------------------------------------------+
| name        | string                                     | 1-32 character name matching ``^[\w-]{1,32}$``.                                                     |
+-------------+--------------------------------------------+-----------------------------------------------------------------------------------------------------+
| description | string                                     | 1-100 character description.                                                                        |
+-------------+--------------------------------------------+-----------------------------------------------------------------------------------------------------+
| options?    | array of `ApplicationCommandOption`_       | if the option is a subcommand or subcommand group type, this nested options will be the parameters. |
+-------------+--------------------------------------------+-----------------------------------------------------------------------------------------------------+

This table shows us the way that Discord handles the structure of commands for
slash commands through their Bot API. For visualization purposes, we'll quickly
make a JSON example (although we won't be using it) in order to explain how this
works:

.. code-block:: python

  {
    "name": "test",
    "description": "This is just a test command, nothing more.",
  }
  
Now that we have a basic understanding of how the JSON table works, we can
take this knowledge and convert it into a decorator method for the Python
code as shown below:

.. code-block:: python

  @slash.slash(name="test",
               description="This is just a test command, nothing more.")
  async def test(ctx):
    await ctx.send(content="Hello World!")
    
Now that we've gone over how Discord handles the declaration of slash commands
through their Bot API, let's go over what some of the other things mean within
the *logical* part of our code, the command function:


Giving some options for variety.
--------------------------------

The next thing that we will begin to talk about is the implementation of options,
otherwise well-known as "arguments" in discord.py commands.

The JSON structure of options are designed up to be similar to the same premise
of how a slash command is declared. Below is the given table of how an option
JSON would appear as:

+-------------+--------------------------------------------+-----------------------------------------------------------------------------------------------------+
| **Field**   | **Type**                                   | **Description**                                                                                     |
+-------------+--------------------------------------------+-----------------------------------------------------------------------------------------------------+
| type        | int                                        | value of `ApplicationCommandOptionType`_.                                                           |
+-------------+--------------------------------------------+-----------------------------------------------------------------------------------------------------+
| name        | string                                     | 1-32 character name matching ``^[\w-]{1,32}$``.                                                     |
+-------------+--------------------------------------------+-----------------------------------------------------------------------------------------------------+
| description | string                                     | 1-100 character description.                                                                        |
+-------------+--------------------------------------------+-----------------------------------------------------------------------------------------------------+
| default?    | bool                                       | the first required option for the user to complete--only one option can be default.                 |
+-------------+--------------------------------------------+-----------------------------------------------------------------------------------------------------+
| required?   | bool                                       | if the parameter is required or optional--default ``false``.                                        |
+-------------+--------------------------------------------+-----------------------------------------------------------------------------------------------------+
| choices?    | array of `ApplicationCommandOptionChoice`_ | choices for ``string`` and ``int`` types for the user to pick from.                                 |
+-------------+--------------------------------------------+-----------------------------------------------------------------------------------------------------+
| options?    | array of `ApplicationCommandOption`_       | if the option is a subcommand or subcommand group type, this nested options will be the parameters. |
+-------------+--------------------------------------------+-----------------------------------------------------------------------------------------------------+

Now we have an idea of how options are declared. With this in mind, let's quickly make a JSON
example in order to visualize this concept even further:

.. code-block:: python

  {
    "name": "test",
    "description": "This is just a test command, nothing more.",
    "options": [
      {
        "name": "optone",
        "description": "This is the first option we have.",
        "type": 3,
        "required": "false"
      }
    ]
  }

While the table in the basics mentions an array in particular called ``ApplicationCommandOptionType``,
there isn't that much of an explanation on how this works. Let's put this into better laymen
terms on what this means with a table below showing all of these values:

+-------------------+-----------+
| **Name**          | **Value** |
+-------------------+-----------+
| SUB_COMMAND       | 1         |
+-------------------+-----------+
| SUB_COMMAND_GROUP | 2         |
+-------------------+-----------+
| STRING            | 3         |
+-------------------+-----------+
| INTEGER           | 4         |
+-------------------+-----------+
| BOOLEAN           | 5         |
+-------------------+-----------+
| USER              | 6         |
+-------------------+-----------+
| CHANNEL           | 7         |
+-------------------+-----------+
| ROLE              | 8         |
+-------------------+-----------+

The purpose of having the ``ApplicationCommandOptionType`` value passed into our option JSON structure
is so that we can help the Discord UI understand what kind of value we're inputting here. For instance,
if we're wanting to put in a string response, we'll pass the ID 3 so that the UI of Discord chat bar
knows to format it visually this way. If we're looking for a user, then we'll pass ID 6 so that it presents
us with a list of users in our server instead, making it easier on our lives. 

This is not to be confused, however, with formatting the response type itself. This is merely a method so
that the API wrapper can help us with passing the correct type or instance variable with the arguments of the
command function's code.

Now, we can finally visualize this by coding an example of this being used in the Python code shown below.

.. code-block:: python

  from discord_slash.utils.manage_commands import create_option
  
  @slash.slash(name="test",
               description="This is just a test command, nothing more.",
               options=[
                 create_option(
                   name="optone",
                   description="This is the first option we have.",
                   option_type=3,
                   required=False
                 )
               ])
  async def test(ctx, optone: str):
    await ctx.send(content=f"I got you, you said {optone}!")
    
Additionally, we could also declare the type of our command's option through this method shown here:

.. code-block:: python

  from discord_slash.model import SlashCommandOptionType
  
  (...)
  
                  option_type=SlashCommandOptionType.STRING
                  
More in the option? Give them a choice.
---------------------------------------

Alas, there is also a way to give even more information to options with Discord's Slash Commands:
a choice. Not like something that you're given at birth of when you become of legal age as an adult,
we're not here to give you *that* kind of life advice, but the choice of what value you want your 
option to rather pass. Below is a table that shows the JSON structure of how choices are represented
for an option:

+-------------+--------------------------------------------+-----------------------------------------------------------------------------------------------------+
| **Field**   | **Type**                                   | **Description**                                                                                     |
+-------------+--------------------------------------------+-----------------------------------------------------------------------------------------------------+
| name        | string                                     | 1-32 character choice name.                                                                         |
+-------------+--------------------------------------------+-----------------------------------------------------------------------------------------------------+
| value       | string or int                              | value of the choice, up to 100 characters if string.                                                |
+-------------+--------------------------------------------+-----------------------------------------------------------------------------------------------------+

This time, only 2 fields are able to be passed for this. Below is a JSON example of how this would
be designed:

.. code-block:: python

  {
    "name": "ChoiceOne",
    "value": "Hello command, this is my value!"
  }
    
To make it really simple, the ``name`` field is only to be used for how you want the choice to be presented
through Discord's UI. It's the "appearance" of how you want your choice shown, not the actual returned value
of it. Hence, this is why ``value`` is the second field passed for that, which can be either in the form of 
a string or integer. Below is an implementation of this design in the Python code:

.. code-block:: python

  from discord_slash.utils.manage_commands import create_option, create_choice
  
  @slash.slash(name="test",
               description="This is just a test command, nothing more.",
               options=[
                 create_option(
                   name="optone",
                   description="This is the first option we have.",
                   option_type=3,
                   required=False,
                   choices=[
                    create_choice(
                      name="ChoiceOne",
                      value="DOGE!"
                    ),
                    create_choice(
                      name="ChoiceTwo",
                      value="NO DOGE"
                    )
                  ]
                 )
               ])
  async def test(ctx, optone: str):
    await ctx.send(content=f"Wow, you actually chose {optone}? :(")

Want to restrict access? Setup permissions!
-------------------------------------------

Slash commands also support the ability to set permissions to allow only certain roles and/or users 
to run a slash command. Permissions can be applied to both global and guild based commands. They 
are defined per guild, per top-level command (the base command for subcommands), and each guild can have multiple permissions. Here is the table that shows the JSON 
structure of how permissions are represented:

+-------------+--------------------------------------------+-----------------------------------------------------------------------------------------------------+
| **Field**   | **Type**                                   | **Description**                                                                                     |
+-------------+--------------------------------------------+-----------------------------------------------------------------------------------------------------+
| id          | int                                        | Snowflake value of type specified. Represents the target to apply permissions on.                   |
+-------------+--------------------------------------------+-----------------------------------------------------------------------------------------------------+
| type        | int                                        | An `ApplicationCommandPermissionType`_.                                                             |
+-------------+--------------------------------------------+-----------------------------------------------------------------------------------------------------+
| permission  | boolean                                    | ``True`` to allow, ``False`` to disallow.                                                           |
+-------------+--------------------------------------------+-----------------------------------------------------------------------------------------------------+

How the type parameter works is very simple. Discord has many ids to represent different things. As you can 
set permissions to apply for User or Role, `ApplicationCommandPermissionType`_ is used. It's a number and
following table shows the supported id types for permissions:

+-------------------+-----------+
| **Name**          | **Value** |
+-------------------+-----------+
| Role              | 1         |
+-------------------+-----------+
| User              | 2         |
+-------------------+-----------+

This is an example of how a single permission will look when represented as a json object:

.. code-block:: python

  {
    "id": 12345678,
    "type": 1,
    "permission": True 
  }

Now, let take a look at an example. The slash command decorator has a permissions parameter where
it takes in a dictionary. The key being the guild id to apply permissions on, and value being the list
of permissions to apply. For each permission, we can use the handy ``create_permission`` method to 
build the permission json explained above.

In this case, we are setting 2 permissions for a guild with an id of ``12345678``. Firstly, we are allowing
role with id ``99999999`` and disallowing user with id ``88888888`` from running the slash command.

.. code-block:: python

  from discord_slash.utils.manage_commands import create_permission
  from discord_slash.model import SlashCommandPermissionType

  @slash.slash(name="test",
              description="This is just a test command, nothing more.",
              permissions={
                12345678: [
                  create_permission(99999999, SlashCommandPermissionType.ROLE, True),
                  create_permission(88888888, SlashCommandPermissionType.USER, False)
                ]
             })
  async def test(ctx):
    await ctx.send(content="Hello World!")

Alternatively, you can use the ``@slash.permission`` decorator to define your guild permissions for the 
command as show in the following example:

.. code-block:: python

  from discord_slash.utils.manage_commands import create_permission
  from discord_slash.model import SlashCommandPermissionType

  @slash.slash(name="test",
               description="This is just a test command, nothing more.")
  @slash.permission(guild_id=12345678, 
                    permissions=[
                      create_permission(99999999, SlashCommandPermissionType.ROLE, True), 
                      create_permission(88888888, SlashCommandPermissionType.USER, False)
                    ])
  async def test(ctx):
    await ctx.send(content="Hello World!")

But what about buttons?
-----------------------
This library supports components (buttons, actionrows, selects, etc.). Take a look here: `components`_.

Making a message/menu command.
******************************
Lucky for you, this library has recently added support for context menus! Let's take a look into how they're designed.

Please note that the current limit for context menus with the Discord API is **5.**

A menu command (context menu) is an easy way for bot developers to program optionless and choiceless commands into their bot
which can be easily accessible by right clicking on a user and/or message present. Below is a table of the supported keys and
values:

+-------------+--------------------------------------------+-----------------------------------------------------------------------------------------------------+
| **Field**   | **Type**                                   | **Description**                                                                                     |
+-------------+--------------------------------------------+-----------------------------------------------------------------------------------------------------+
| name        | string                                     | The name of the context menu command.                                                               |
+-------------+--------------------------------------------+-----------------------------------------------------------------------------------------------------+
| type        | int                                        | An `ApplicationCommandType`_.                                                                       |
+-------------+--------------------------------------------+-----------------------------------------------------------------------------------------------------+

The following table below represents how it would be shown as a JSON object:

.. code-block:: python

  {
    "name": "Name of my command.",
    "type": 3
  }

The following table explains more about the ``type`` parameter being passed, which there are three of: ``CHAT_INPUT``, ``USER`` and ``MESSAGE``. By default, the type will
always be the first. This is because it is a registered type that is used to process slash commands, and should not be used for when you are declaring context menu
commands in your bot's code at all:

+------------+-----------+
| **Name**   | **Value** |
+------------+-----------+
| CHAT_INPUT | 1         |
+------------+-----------+
| USER       | 2         |
+------------+-----------+
| MESSAGE    | 3         |
+------------+-----------+

Unlike ``manage_commands`` and ``manage_components``, you will have to use a decorator for now to register them:

.. code-block :: python

  from discord_slash.context import MenuContext
  from discord_slash.model import ContextMenuType

  @slash.context_menu(target=ContextMenuType.MESSAGE,
                      name="commandname",
                      guild_ids=[789032594456576001])
  async def commandname(ctx: MenuContext):
      await ctx.send(
          content=f"Responded! The content of the message targeted: {ctx.target_message.content}",
          hidden=True
      )

The ``@slash.context_menu`` decorator takes in the context type as given (to either appear when you right-click on a user or when you right-click on a message) as well
as the name of the command, and any guild IDs if given if you would like to make it applicable to only a guild. **We only accept connected names** for the time being,
although context menus will have the ability to have spaces in their name in the future when development further progresses.

You are able to also use the ``@cog_ext.cog_context_menu`` path which will require an import from ``cog_ext.py`` respectively, however, it is worth nothing that
the ``target`` kwarg for the decorator **must** be brought to the very end.

Can I use components with context menus?
----------------------------------------
Of course! However, you will need to add in some additional code in order for both of the separate contexts to work seamlessly. Below is the given code of what will need
to be changed:

.. code-block :: python

  from discord_slash.context import ComponentContext, MenuContext
  from discord_slash.model import ContextMenuType
  from typing import Union

  ...

  async def my_new_command(ctx: Union[ComponentContext, MenuContext]):
    ...

Hey, what about component/[X] listening?
----------------------------------------
The decision has been made that this will not be implemented because of two reasons: context menus currently have no ability to hold any options or choices, so listening
for any responses would be currently pointless. Additionally, component listening is already a built-in feature that does not require further customized and new decorators
for explicitly context menus, as they're more universal.

Nested commands as subcommands.
*******************************
Before you get into learning how to create a subcommand, please be sure to read up on the documentation above given for how slash commands are made.

Subcommands are way to "nest" your slash commands under one (or more) given names, as either a "base" name or a "grouping" of an existing base. When this is said, it will initially appear very confusing. Let's use the table shown below as a way to introduce the new fields/properties that can be applied for a slash command to become a subcommand:

+------------------------------+--------------------------------------------+-----------------------------------------------------------------------------------------------------+
| **Field**                    | **Type**                                   | **Description**                                                                                     |
+------------------------------+--------------------------------------------+-----------------------------------------------------------------------------------------------------+
| base                         | string                                     | The name of the subcommand "base."                                                                  |
+------------------------------+--------------------------------------------+-----------------------------------------------------------------------------------------------------+
| subcommand_group             | string                                     | The name for the group of commands under the "base." Field is optional.                             |
+------------------------------+--------------------------------------------+-----------------------------------------------------------------------------------------------------+
| base_description             | string                                     | The description when the base is active in the UX chat bar. Defaults to ``None``.                   |
+------------------------------+--------------------------------------------+-----------------------------------------------------------------------------------------------------+
| subcommand_group_description | string                                     | The name for the group of commands under the "base." Defaults to ``None``.                          |
+------------------------------+--------------------------------------------+-----------------------------------------------------------------------------------------------------+

This table is importantly distinguishing the **library's** naming conventions and not the way that th eDiscord API handles it. The API does subcommand grouping and bases through the options of a slash command, so we decided to create a decorator instead to make this easy for bot developers alike to use. We will not be giving a JSON example of this because of this reason.

.. code-block :: python
  
  # This will appear as "/bot latency" as latency is not an option,
  # but apart of the command name itself.
  @slash.subcommand(base="bot",
                    name="latency",
                    description="Returns the bot's latency.")
  async def bot_latency(ctx):
    await ctx.send(f"Hello! {round(bot.latency * 1000)} ms.")
    
If you would like to add a group instead, you may simply base the ``subcommand_group``` kwarg into the decorator. Please note that the slash command limit is 25 commands per subcommand group per subcommand base. (Laymen's term for 25 subcommands in a group, and 25 groups in a base. This is not a global exception and may also apply as a limitation for guild commands.)

Handling my errors.
*******************

Thankfully, we try to make a majority of our error handling very simple. If you would like to learn more about how to handle your errors, please refer to our `errors`_ page.
If you are looking for listener events, then check our `listeners`_ page instead.

As a side-note, as of version 3.0, message/menu commands (context menus) are handled under the ``on_slash_command_error`` event.

.. _quickstart: quickstart.html
.. _components: components.html
.. _errors: discord_slash.error.html
.. _listeners: events.html
.. _ApplicationCommandOptionType: https://discord.com/developers/docs/interactions/slash-commands#applicationcommandoptiontype
.. _ApplicationCommandOptionChoice: https://discord.com/developers/docs/interactions/slash-commands#applicationcommandoptionchoice
.. _ApplicationCommandOption: https://discord.com/developers/docs/interactions/slash-commands#applicationcommandoption
.. _ApplicationCommandPermissionType: https://discord.com/developers/docs/interactions/slash-commands#applicationcommandpermissions
.. _ApplicationCommandType: https://discord.com/developers/docs/interactions/application-commands#application-command-object-application-command-types
