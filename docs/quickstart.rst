Quickstart
==========

Installing
**********

**discord-interactions** is a :ref:`Python library <index:discord-interactions>` for the Discord Application Programming Interface. (API)
A library in Python has to be installed through the `pip` file. Run this in your terminal/command line
in order to install our library:

``pip install -U discord-py-interactions``

Creating a Bot
**************

Before you can run your Bot, you have to create it first. If you did it already, make sure you :ref:`invited <quickstart:Invite the Bot to your guild>` your Bot properly.

In order to create your Bot, you need to create an application first.
Go to the `discord applications page`_ for that. After you logged in, you will see this at the top:

.. image:: _static/create_application.png

Click the ``New Application`` button, enter a name and then click ``create``.

.. note:: The name you choose is going to be your Bots name.

You will be redirected to a new page. On the left you will see this:

.. image:: _static/applications_left.png

Click on ``Bot``. You again will be redirected to another page, looking like this:

.. image:: _static.build_a_bot.png

Click on ``Add Bot`` and then on ``Yes, do it!``.

And that's it! You created your Bot!

.. warning::
    You will see a field called ``TOKEN``. This is the access token, used to run your bot.
    You will need this later to start your Bot.

    **Do NOT give this to other persons! They can get full control over your Bot with your token and execute what they want!**

    If you revealed your token, you should **immediately** go to your Bots application page and click the ``Regenerate`` Button under your token. This will delete the old token, so your bot can't be run with it anymore.


Invite the Bot to your guild
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Now you have a Bot, but you can't create commands because it isn't in any guilds. So, let's invite it to your guild!

.. image:: _static/OAuth2_left.png

Click on ``OAuth2``, then on ``URL Generator``.

You have to enable the ``bot`` and ``application.commands`` scope, to allow your bot to create slash commands.

.. image:: _static/scopes_OAuth2.png

After setting that up, a ``BOT PERMISSIONS`` field will appear. You can choose permissions you want to have your bot there.

When you are done with choosing the permissions, go to the bottom of the page, copy the the url and open it in a new window.

You will be prompted to a new page. Select your guild, click ``Authorise`` and your Bot should show up in your guild.

Now you can go on with running your bot and creating your first commands!



Running the Bot and creating commands
*************************************

Bots can be a little confusing to create. That's why we've decided to try and make the process
as streamlined as humanly possible, in order for it to be friendlier to understand for our
fellow bot developers. Please note that **a Discord bot should not be your first project if you're
learning how to code**. There are plenty of other projects to consider first before this, as a
Discord bot is not exactly beginner-friendly.


First, let's run the bot:
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    import interactions

    bot = interactions.Client(token="your_secret_bot_token")


    bot.start()

And that's it! Your bot should now turn online in discord!

Let's take a look now at what is happening here:

* ``import interactions`` -- This is the import line. If this returns a ``ModuleNotFoundError``, please look at our section on how to :ref:`install <quickstart:Installing>` here.
* ``bot = interactions.Client(token="your_secret_bot_token")`` -- This is the ``bot`` variable that defines our bot. This basically instantiates the :ref:`application client <client:Bot Client>`, which requires a ``token`` keyword-argument to be passed. You have to put in your (previously mentioned) secret token here.
* ``bot.start()`` -- Finally, this is what tells our library to turn your bot from offline to online.


Now, let's create our first slash command:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    import interactions

    bot = interactions.Client(token="your_secret_bot_token")

    @bot.command(
        name="my_first_command",
        description="This is the first command I made!",
        scope=the_id_of_your_guild,
    )
    async def my_first_command(ctx: interactions.CommandContext):
        await ctx.send("Hi there!")

    bot.start()

Now, let's look what the new parts of the code are doing:

* ``@bot.command()`` -- This is something known as a *decorator* in Python. This decorator is in charge and responsible of making sure that the Discord API is told about the slash/sub command that you wish to create, and sends an HTTP request correspondingly. Any changes to the information contained in this decorator will be synchronously updated with the API automatically for you. The ``scope`` field shown here is optional, which represents a guild command if you wish to have a command appear in only specific servers that bot is in. This can be a guild object or the ID.
* ``name`` -- This is the name of your command.
* ``description`` -- This is the description of your command.
* ``async def my_first_command(ctx: interactions.CommandContext):`` -- This here is called our "command coroutine," or what our library internally calls upon each time it recognizes an interaction event from the Discord API that affiliates with the data we've put into the decorator above it. Please note that ``ctx`` is an abbreviation for :ref:`context <context:Event Context>`.
* ``await ctx.send("Hi there!")`` -- This sends the response to your command.

.. note:: ``name`` and ``description`` are required.


.. important:: Difference between global and guild slash commands:

    * guild slash commands are instantly available in the guild with the given id. In order to copy your guild ID you have to enable the developer mode in discord and then right-click on the guild. This is also shown in the pictures beyond.
    * global commands are created by *not* including the ``scope`` argument into the ``@bot.command`` decorator. They will appear in all guilds your Bot is in. This process can take up to one hour to be completed on all guilds.

.. image:: _static/dev_mode_discord.png
.. image:: _static/copy_guild_id.png


Next, let's create an Option
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:ref:`Options <models.command:Application Command Models>` are extra arguments of a command, filled in by the user executing the command.

.. code-block:: python

    import interactions

    bot = interactions.Client(token="your_secret_bot_token")

    @bot.command(
        name="say_something",
        description="say something!",
        scope=the_id_of_your_guild,
        options = [
            interactions.Option(
                name="text",
                description="What you want to say",
                type=interactions.OptionType.STRING,
                required=True,
            ),
        ],
    )
    async def my_first_command(ctx: interactions.CommandContext, text: str):
        await ctx.send(f"You said '{text}'!")

    bot.start()


.. note:: The limit for options per command is 25.

Do you want to create subcommands? Here's how to do it:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    @bot.command(
        name="base_command",
        description="This description isn't seen in UI (yet?)",
        scope=guild_id,
        options= [
            interactions.Option(
                name="command_name",
                description="A descriptive description",
                type=interactions.OptionType.SUB_COMMAND,
                options=[
                    interactions.Option(
                        name="option",
                        description="A descriptive description",
                        type=interactions.OptionType.INTEGER,
                        required=False,
                    ),
            interactions.Option(
                name="second_command",
                description="A descriptive description",
                type=interactions.OptionType.SUB_COMMAND,
                options=[
                    interactions.Option(
                        name="second_option",
                        description="A descriptive description",
                        type=interactions.OptionType.STRING,
                        required=True,
                    ),
                ],
            ),
        ],
    )
    async def cmd(ctx: interactions.CommandContext, sub_command: str, second_option: str, option: int = None):
        if sub_command == "command_name":
          await ctx.send(f"You selected the command_name sub command and put in {option}")
        elif sub_command == "second_command":
          await ctx.send(f"You selected the second_command sub command and put in {second_option}")

.. note::
    You can add a SUB_COMMAND_GROUP in between the base and command.


Special type of commands: Context menus
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

While, granted that application commands are way more intuitive and easier to work with as both
a bot developer and user from a UX approach, some may not want to always type the same command
over and over again to repeat a repetitive task. Introducing: **context menus.** Also
known as "user" and "message" respectively, this simple switch in command structure allows you to
quickly empower your bot with the ability to make right-click actions with menial effort.

In order to create a menu-based command, all you need to do is simply add this one line into
your ``@command`` decorator:

.. code-block:: python

    @bot.command(
        type=interactions.ApplicationCommandType.USER,
        name="User Command",
        scope=1234567890
    )
    async def test(ctx):
        await ctx.send(f"You have applied a command onto user {ctx.target.user.username}!")

.. important:: The structure of a menu command differs significantly from that of a regular one:

    - You cannot have any options or choices.
    - You cannot have a description.
    - The ``name`` filter follows a different regex pattern.


Creating and sending Components
*******************************

Being able to run your own commands is very useful for a lot of automation-related purposes
as a bot developer, however, we also have something that we're able to introduce for both
the developer and a user to use that will be the "sprinkles" on top of a cupcake, so-to-speak:
components.

Components are ways of being able to select pre-defined data, or define your own. They're very
simple but quite powerful when put into practice This code block below shows a simplified
implementation of a component:

.. code-block:: python

    button = interactions.Button(
        style=interactions.ButtonStyle.PRIMARY,
        label="hello world!",
        custom_id="hello"
    )

    @bot.command(
        name="button_test",
        description="This is the first command I made!",
        scope=the_id_of_your_guild,
    )
    async def button_test(ctx):
        await ctx.send("testing", components=button)

    @bot.component("hello"")
    async def button_response(ctx):
        await ctx.send("You clicked the Button :O", ephemeral=True)

    bot.start()

This is a design that we ended up choosing to simplify responding
to buttons when someone presses on one, and to allow bot developers
to plug in *which* button they want a response to. No more ``wait_for_component``
and ``wait_for`` functions with huge if-else chains; this removes
redundancy in your code and overall eases into the practice of modularity.

What kinds of components are there?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As a bot developer, this may be fairly important for you to want to know.
Different components provide difference user experiences, interactions
and results. Currently you can choose between two components that Discord
provides: a ``Button`` and ``SelectMenu``. You're able to `find these component
types`_ here.

How do I send components in a row?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You are also able to organize these components into rows, which are defined
as ``ActionRow``'s. It is worth noting that you can have only a maximum of
5 per message that you send. This code block below shows how:

.. code-block:: python

    button = interactions.Button(
        style=interactions.ButtonStyle.PRIMARY,
        label="hello world!",
        custom_id="hello",
    )

    button2 = interactions.Button(
        style=interactions.ButtonStyle.DANGER,
        label="bye bye!",
        custom_id="bye!",
    )


    row = interactions.ActionRow(
        components=[button1, button2]
    )

    @bot.command(...)
    async def test(ctx):
        await ctx.send("rows!", components=row)

By default, the ``components`` keyword-argument field in the context sending
method will always support ``ActionRow``-less sending: you only need to declare
rows whenever you need or want to. This field will also support raw arrays and
tables, if you so wish to choose to not use our class objects instead.

.. _Client: https://discord-interactions.rtfd.io/en/stable/client.html
.. _find these component types: https://discord-interactions.readthedocs.io/en/stable/models.component.html
.. _discord applications page: https://discord.com/developers/applications
