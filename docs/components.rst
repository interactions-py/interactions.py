How to use components
=====================


So you've seen the new fancy buttons and want to give them a try, but dont know where to start. No problem!

First lets cover the basics. Discord messages can have *components*, such as buttons, dropdowns etc. These components sit in whats called an "action row". An action row can hold 5 components at a time. Your message can have 5 action rows, so thats a total of 25 components!

Sending some components
_______________________

.. note:: This will work in both slash commands, and discord.py commands

First we need to create some buttons, lets put them in a list for now. We'll use :meth:`create_button() <discord_slash.utils.manage_components>` to create a green button

.. code-block:: python

    from discord_slash.utils.manage_components import create_button, create_actionrow
    from discord_slash.model import ButtonStyle

    buttons = [
                create_button(
                    style=ButtonStyle.green,
                    label="A Green Button"
                ),
              ]

So we have a button, but where do we use it. Let's create an action row with :func:`create_actionrow() <discord_slash.utils.manage_components>` and put our buttons in it

.. code-block:: python

    action_row = create_actionrow(*buttons)


Fantastic, we now have an action row with a green button in it, now lets get it sent in discord

.. code-block:: python

    await ctx.send("My Message", components=[action_row])


And to bring it all together, you could use this:

.. code-block:: python

    from discord_slash.utils.manage_components import create_button, create_actionrow
    from discord_slash.model import ButtonStyle

    await ctx.send("My Message", components=[
                                        create_actionrow(
                                            create_button(style=ButtonStyle.green, label="A Green Button"))
                                        ])

Now if you've followed along, you have a green button in discord! But theres a problem, whenever you click it you see that the ``interaction failed``. Why is that?
Well, in Discord, clicking buttons and using slash commands are called ``interactions``, and Discord doesn't know if we've received them or not unless we tell Discord. So how do we do that?

Responding to interactions
__________________________

When responding, you have 3 choices in how you handle interactions. You can either wait for them in the command itself, or listen for them in a global event handler (similar to :func:`on_slash_command_error`), or register async function as component callback.

Wait_for
********

Lets go through the most common method first, responding in the command itself. We simply need to :func:`wait_for` the event, just like you do for reactions. For this we're going to use :func:`wait_for_component() <discord_slash.utils.manage_components>`, and we're going to only wait for events from the action row we just sent.
This method will return a :class:`ComponentContext <discord_slash.context.ComponentContext>` object that we can use to respond. For this example, we'll just edit the original message (:meth:`edit_origin() <discord_slash.context.ComponentContext.edit_origin>`, uses same logic as :func:`edit()`)

.. code-block:: python

    from discord_slash.utils.manage_components import wait_for_component

    await ctx.send("My Message", components=[action_row])
    # note: this will only catch one button press, if you want more, put this in a loop
    button_ctx: ComponentContext = await wait_for_component(bot, components=action_row)
    await button_ctx.edit_origin(content="You pressed a button!")

.. note:: It's worth being aware that if you handle the event in the command itself, it will not persist reboots. As such when you restart the bot, the interaction will fail

Global event handler
********************

Next we'll go over the alternative, a global event handler. This works just the same as :func:`on_slash_command_error` or `on_ready`. But note that this code will be triggered on any components interaction.

.. code-block:: python

    @bot.event
    async def on_component(ctx: ComponentContext):
        # you may want to filter or change behaviour based on custom_id or message
        await ctx.edit_origin(content="You pressed a button!")

Component callbacks
********************

There is one more method - making a function that'll be component callback - triggered when components in a specified message or specific ``custom_id`` are used.
Let's register our callback function via decorator :meth:`component_callback() <discord_slash.client.SlashCommand.component_callback>`, in similar ways to slash commands.

.. code-block:: python

    @slash.component_callback()
    async def hello(ctx: ComponentContext):
        await ctx.edit_origin(content="You pressed a button!")

In this example, :func:`hello` will be triggered when you receive interaction event from a component with a `custom_id` set to `"hello"`. Just like slash commands, the callback's `custom_id` defaults to the function name.
You can also register such callbacks in cogs using :func:`cog_component() <discord_slash.cog_ext>`
Additionally, component callbacks can be dynamically added, removed or edited - see :class:`SlashCommand <discord_slash.client.SlashCommand>`

But [writer], I dont want to edit the message
*********************************************

Well lucky for you, you don't have to. You can either respond silently, with a thinking animation, or send a whole new message. Take a look here: :class:`ComponentContext <discord_slash.context.ComponentContext>`

How do I know which button was pressed?
_______________________________________

Each button gets a ``custom_id`` (which is always a string), this is a unique identifier of which button is being pressed. You can specify what the ID is when you define your button, if you don't; a random one will be generated. When handling the event, simply check the custom_id, and handle accordingly.

What about selects / Dropdowns?
_______________________________

Yep we support those too. You use them much the same as buttons. You can only have 1 select per action row, but each select can have up to 25 options in it!

.. code-block:: python

    from discord_slash.utils.manage_components import create_select, create_select_option, create_actionrow

    select = create_select(
        options=[# the options in your dropdown
            create_select_option("Lab Coat", value="coat", emoji="🥼"),
            create_select_option("Test Tube", value="tube", emoji="🧪"),
            create_select_option("Petri Dish", value="dish", emoji="🧫"),
        ],
        placeholder="Choose your option",  # the placeholder text to show when no options have been chosen
        min_values=1,  # the minimum number of options a user must select
        max_values=2,  # the maximum number of options a user can select
    )
    
    await ctx.send("test", components=[create_actionrow(select)])  # like action row with buttons but without * in front of the variable

    @bot.event
    async def on_component(ctx: ComponentContext):
        # ctx.selected_options is a list of all the values the user selected
        await ctx.send(content=f"You selected {ctx.selected_options}")

Additionally, you can pass ``description`` as a keyword-argument for ``create_select_option()`` if you so wish.
