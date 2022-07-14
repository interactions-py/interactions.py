Migration
=========

This page aims to serve as a guide towards helping users understand any breaking or otherwise important design choices made
between versions to guide towards easy migration between one another.

4.0.1 → 4.0.2
~~~~~~~~~~~~~~~

The biggest major change between these two versions is the way ``HTTPClient`` and modelled API schema objects are used.
In ``4.0.2``, a new ``_client`` attribute is added in model objects in order to use helper methods. This will not be needed
if you're working with dispatched events from the Gateway, however, manually generating your own model object for use
will need it appended as a key-word argument. The example below shows this change:

.. code-block:: python

    # 4.0.1
    data = await bot.http.get_channel(789032594456576004)
    channel = interactions.Channel(**data)

    # 4.0.2
    ...
    channel = interactions.Channel(**data, _client=bot.http)

This change was added in favor for being able to use endpoints in an abstracted state.

4.0.2 → 4.1.0
~~~~~~~~~~~~~~~

``4.1.0`` introduces numerous breaking changes that affect the bot developers' ability to work with mainly modifying
the way our Gateway processes information, as well as supplying a ``reason`` argument to ``HTTPClient``-based methods.

In this version, you are no longer required to give a ``reason`` for every HTTP request. You can instead send it as an optional,
which will work to keep any existing modifications of our codebase from breaking.

Additionally, modifying the way information is dispatched from the Gateway must be done like this now:

.. code-block:: python

    import interactions

    class ExtendedWebSocketClient(interactions.WebSocketClient):
        def _dispatch_event(self, event: str, data: dict):
            super()._dispatch_event(event, data)

            if event != "TYPING_START" and event == "INTERACTION_CREATE":
                ... # run your special interaction dispatch rules here.

We recommend that working in correspondence with this, you should be making use of our ``interactions.ext`` SDK framework.

A slight, yet another breaking change we made was dundering numerous attributes in our internal models.
You will now need to refer to the client's HTTP object as ``_http`` instead of ``http``. In order to view
the full list of these, we highly encourage you to view the documentation readily available.

The last, and most major change is the introduction of the ``MESSAGE_CONTENT`` privileged intent in the library.
Because of ``4.1.0`` using version 10 of the Discord API, this intent is now required for reading all message
content. In order to make sure your bot works still, you will need to enable this intent in your bot's developer
portal and add the intent to your current intents when connecting:

.. code-block:: python

    from interactions import Client, Intents

    bot = Client("TOKEN", intents=Intents.DEFAULT | Intents.GUILD_MESSAGE_CONTENT)

4.1.0 → 4.3.0
~~~~~~~~~~~~~~~

A new big change in this release is the implementation of the ``get`` utility method.
It allows you to no longer use ``**await bot._http...``.

You can get more information by reading the `get-documentation`_.


``4.3.0`` also introduces a new method of creating commands, subcommands, and options.
There are also numerous new features, such as a default scope and utilities.

The following example shows and explains how to create commands effortlessly and use new features mentioned above:

.. code-block:: python

    import interactions

    bot = interactions.Client("TOKEN", default_scope=1234567890)
    # the default scope will be applied to all commands except for those
    # that disable the feature in the command decorator via: `default_scope=False`

    @bot.command()
    async def command_name(ctx):
        """Command description"""
        ...  # do something here.
        # the name of the command is the coroutine name.
        # the description is the first line of the docstring or "No description set".

    @bot.command(default_scope=False)
    @interactions.option(str, name="opt1")  # description is optional.
    @interactions.option(4, name="opt2", description="This is an option.")
    @interactions.option(interactions.Channel, name="opt3", required=True)
    async def command_with_options(
        ctx, opt1: str, opt2, int, opt3: interactions.Channel = None
    ):
        ...  # do something here.
        # the default scope is disabled for this command, so this is a global command.
        # the option type is positional only, and can be a python type, an integer,
        # or supported interactions.py objects.
        # all other options are keyword only arguments.
        # the type amd name of the option are required, the rest are optional.

    # Subcommand system:
    @bot.command()
    async def base_command(ctx):
        ...  # do something here.
        # this is the base command of the subcommand system.

    @base_command.subcommand()
    async def subcommand1(ctx, base_res: interactions.BaseResult):
        ...  # do something here.
        # this is a subcommand of the base command.
        # the base result is the result of the base command, it is optional to have.
        # /base_command subcommand1

    # create subcommands *before* creating groups!

    @base_command.group()
    async def group1(ctx, base_res: interactions.BaseResult):
        ...  # do something here.
        # this symbolizes a group for subcommands.

    @group.subcommand()
    async def subcommand2(ctx, group_res: interactions.GroupResult):
        raise Exception("pretend an error happened here")
        # this is a subcommand of the group.
        # the group result is the result of the group, it is optional to have.
        # /base_command group1 subcommand2

    @base_command.group()
    async def group2(ctx):
        # this symbolizes a group for subcommands.
        # here, we will intentionally return StopCommand:
        return interactions.StopCommand
        # if this is returned, any callbacks afterwards in the same
        # command will not be executed.
        # for example, subcommand3 will not be executed.

    @group2.subcommand()
    async def subcommand3(ctx):
        ...  # do something here.
        # this is a subcommand of the group.
        # this will NOT be executed.
        # /base_command group2 subcommand3

    @base_command.error
    async def base_command_error(ctx, error):
        ...  # do something here.
        # remember the exception in subcommand2?
        # here, you can handle any errors that occur in the base command.
        # this is the error handler for the base command.
        # the error is the exception raised by the command.
        # you can have optional res, *args, and **kwargs
        # if your command is a subcommand or
        # there are options that you want to access.

    # utilities
    @bot.command()
    @interactions.autodefer()  # configurable
    async def autodefer_command(ctx):
        # it will automatically defer the command if the command is not
        # executed within the configured `delay` in the autodefer decorator.

        # ActionRow.new() utility:
        b1 = Button(style=1, custom_id="b1", label="b1")
        b2 = Button(style=1, custom_id="b2", label="b2")
        b3 = Button(style=1, custom_id="b3", label="b3")
        b4 = Button(style=1, custom_id="b4", label="b4")

        await ctx.send("Components:", components=interactions.ActionRow.new(b1, b2, b3, b4))
        # instead of the cumbersome ActionRow(components=[b1, b2, b3, b4])

        # spread_to_rows utility:
        await ctx.send("Components:", components=interactions.spread_to_rows(b1, b2, b3, b4, max_in_row=2))
        # configurable

    bot.start()

.. _get-documentation: https://interactionspy.readthedocs.io/en/latest/get.html#the-get-utility-method
