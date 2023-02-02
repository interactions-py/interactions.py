# Extensions

Damn, your code is getting pretty messy now, huh? Wouldn't it be nice if you could organise your commands and listeners into separate files?

Well let me introduce you to `Extensions`<br>
Extensions allow you to split your commands and listeners into separate files to allow you to better organise your project,
as well as that, they allow you to reload Extensions without having to shut down your bot.

Sounds pretty good right? Well, let's go over how you can use them:

## Usage

Below is an example of a bot, one with extensions, one without.

??? Hint "Example Usage:"
    === "Without Extensions"
        ```python
        # File: `main.py`
        import logging

        import interactions.const
        from interactions.client import Client
        from interactions.models.application_commands import slash_command, slash_option
        from interactions.models.context import InteractionContext
        from interactions.models.discord_objects.components import Button, ActionRow
        from interactions.models.enums import ButtonStyle
        from interactions.models.enums import Intents
        from interactions.models.events import Component
        from interactions.models.listener import listen
        from interactions.ext import prefixed_commands
        from interactions.ext.prefixed_commands import prefixed_command

        logging.basicConfig()
        cls_log = logging.getLogger(interactions.const.logger_name)
        cls_log.setLevel(logging.DEBUG)

        bot = Client(intents=Intents.DEFAULT, sync_interactions=True, asyncio_debug=True)
        prefixed_commands.setup(bot)


        @listen()
        async def on_ready():
            print("Ready")
            print(f"This bot is owned by {bot.owner}")


        @listen()
        async def on_guild_create(event):
            print(f"guild created : {event.guild.name}")


        @listen()
        async def on_message_create(event):
            print(f"message received: {event.message.content}")


        @listen()
        async def on_component(event: Component):
            ctx = event.context
            await ctx.edit_origin("test")


        @prefixed_command()
        async def multiple_buttons(ctx):
            await ctx.send(
                "2 buttons in a row",
                components=[Button(ButtonStyle.BLURPLE, "A blurple button"), Button(ButtonStyle.RED, "A red button")],
            )


        @prefixed_command()
        async def action_rows(ctx):
            await ctx.send(
                "2 buttons in 2 rows, using nested lists",
                components=[[Button(ButtonStyle.BLURPLE, "A blurple button")], [Button(ButtonStyle.RED, "A red button")]],
            )


        @prefixed_command()
        async def action_rows_more(ctx):
            await ctx.send(
                "2 buttons in 2 rows, using explicit action_rows lists",
                components=[
                    ActionRow(Button(ButtonStyle.BLURPLE, "A blurple button")),
                    ActionRow(Button(ButtonStyle.RED, "A red button")),
                ],
            )


        bot.start("Token")
        ```

    === "With Extensions"
        ```python
        # File: `main.py`
        import logging

        import interactions.const
        from interactions.client import Client
        from interactions.models.context import ComponentContext
        from interactions.models.enums import Intents
        from interactions.models.events import Component
        from interactions.models.listener import listen
        from interactions.ext import prefixed_commands


        logging.basicConfig()
        cls_log = logging.getLogger(interactions.const.logger_name)
        cls_log.setLevel(logging.DEBUG)

        bot = Client(intents=Intents.DEFAULT, sync_interactions=True, asyncio_debug=True)
        prefixed_commands.setup(bot)


        @listen()
        async def on_ready():
            print("Ready")
            print(f"This bot is owned by {bot.owner}")


        @listen()
        async def on_guild_create(event):
            print(f"guild created : {event.guild.name}")


        @listen()
        async def on_message_create(event):
            print(f"message received: {event.message.content}")


        @listen()
        async def on_component(event: Component):
            ctx = event.context
            await ctx.edit_origin("test")


        bot.load_extension("test_components")
        bot.start("Token")

        ```
        ```python

        # File: `test_components.py`

        from interactions.models.command import prefixed_command
        from interactions.models.discord_objects.components import Button, ActionRow
        from interactions.models.enums import ButtonStyle
        from interactions.models.extension import Extension
        from interactions.ext.prefixed_commands import prefixed_command


        class ButtonExampleSkin(Extension):
            @prefixed_command()
            async def blurple_button(self, ctx):
                await ctx.send("hello there", components=Button(ButtonStyle.BLURPLE, "A blurple button"))

            @prefixed_command()
            async def multiple_buttons(self, ctx):
                await ctx.send(
                    "2 buttons in a row",
                    components=[Button(ButtonStyle.BLURPLE, "A blurple button"), Button(ButtonStyle.RED, "A red button")],
                )

            @prefixed_command()
            async def action_rows(self, ctx):
                await ctx.send(
                    "2 buttons in 2 rows, using nested lists",
                    components=[[Button(ButtonStyle.BLURPLE, "A blurple button")], [Button(ButtonStyle.RED, "A red button")]],
                )

            @prefixed_command()
            async def action_rows_more(self, ctx):
                await ctx.send(
                    "2 buttons in 2 rows, using explicit action_rows lists",
                    components=[
                        ActionRow(Button(ButtonStyle.BLURPLE, "A blurple button")),
                        ActionRow(Button(ButtonStyle.RED, "A red button")),
                    ],
                )


        def setup(bot):
            ButtonExampleSkin(bot)
        ```

Extensions are effectively just another python file that contains a class that inherits from an object called `Extension`,
inside this extension, you can put whatever you would like. And upon loading, the contents are added to the bot.

```python
from interactions import Extension


class SomeClass(Extension):
    ...


def setup(bot):
    # This is called by interactions.py so it knows how to load the Extension
    SomeClass(bot)
```
As you can see, there's one extra bit, a function called `setup`, this function acts as an entry point for interactions.py,
so it knows how to load the extension properly.

To load a extension, you simply add the following to your `main` script, just above `bot.start`:

```python
...

bot.load_extension("Filename_here")

bot.start("token")
```

Now, for the cool bit of Extensions, reloading. Extensions allow you to edit your code, and reload it, without restarting the bot.
To do this, simply run `bot.reload_extension("Filename_here")` and your new code will be used. Bare in mind any tasks your extension
is doing will be abruptly stopped.


You can pass keyword-arguments to the `load_extension`, `unload_extension` and `reload_extension` extension management methods.
Any arguments you pass to the `setup` or `teardown` methods, will also be passed to the `Extension.drop` method.

Here is a basic "Extension switching" example:

```python
from interactions import Extension


class SomeExtension(Extension):
    def __init__(self, bot, some_arg: int = 0):
        ...


class AnotherExtension(Extension):
    def __init__(self, bot, another_arg: float = 0.0):
        ...


def setup(bot, default_extension: bool, **kwargs):  # We don't care about other arguments here.
    if default_extension:
        SomeExtension(bot, **kwargs)
    else:
        AnotherExtension(bot, **kwargs)


...

bot.load_extension("Filename_here", default_extension=False, another_arg=3.14)
# OR
bot.load_extension("Filename_here", default_extension=True, some_arg=555)
```
