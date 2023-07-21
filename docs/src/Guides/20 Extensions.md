# Extensions

## Introduction

Your code's getting pretty big and messy being in a single file, huh? Wouldn't it be nice if you could organise your commands and listeners into separate files?

Well let me introduce you to `Extensions`!<br>
Extensions allow you to split your commands and listeners into separate files to allow you to better organise your project.
They also come with the additional benefit of being able to reload parts of your bot without shutting down your bot.

For example, you can see the difference of a bot with and without extensions:

??? Hint "Examples:"
    === "Without Extensions"
        ```python
        from interactions import ActionRow, Button, ButtonStyle, Client, listen, slash_command
        from interactions.api.events import Component, GuildJoin, MessageCreate, Startup

        bot = Client()


        @listen(Startup)
        async def on_startup():
            print(f"Ready - this bot is owned by {bot.owner}")


        @listen(GuildJoin)
        async def on_guild_join(event: GuildJoin):
            print(f"Guild joined : {event.guild.name}")


        @listen(MessageCreate)
        async def on_message_create(event: MessageCreate):
            print(f"message received: {event.message}")


        @listen()
        async def on_component(event: Component):
            ctx = event.ctx
            await ctx.edit_origin(content="test")


        @slash_command()
        async def multiple_buttons(ctx):
            await ctx.send(
                "2 buttons in a row",
                components=[
                    Button(style=ButtonStyle.BLURPLE, label="A blurple button"),
                    Button(style=ButtonStyle.RED, label="A red button"),
                ],
            )


        @slash_command()
        async def action_rows(ctx):
            await ctx.send(
                "2 buttons in 2 rows, using nested lists",
                components=[
                    [Button(style=ButtonStyle.BLURPLE, label="A blurple button")],
                    [Button(style=ButtonStyle.RED, label="A red button")],
                ],
            )


        @slash_command()
        async def action_rows_more(ctx):
            await ctx.send(
                "2 buttons in 2 rows, using explicit action_rows lists",
                components=[
                    ActionRow(Button(style=ButtonStyle.BLURPLE, label="A blurple button")),
                    ActionRow(Button(style=ButtonStyle.RED, label="A red button")),
                ],
            )


        bot.start("token")
        ```

    === "With Extensions"
        ```python
        # File: `main.py`
        from interactions import Client, listen
        from interactions.api.events import Component, GuildJoin, MessageCreate, Startup

        bot = Client()


        @listen(Startup)
        async def on_startup():
            print(f"Ready - this bot is owned by {bot.owner}")


        @listen(GuildJoin)
        async def on_guild_join(event: GuildJoin):
            print(f"Guild joined : {event.guild.name}")


        @listen(MessageCreate)
        async def on_message_create(event: MessageCreate):
            print(f"message received: {event.message}")


        @listen()
        async def on_component(event: Component):
            ctx = event.ctx
            await ctx.edit_origin(content="test")


        bot.load_extension("test_components")
        bot.start("token")
        ```
        ```python

        # File: `test_components.py`

        from interactions import ActionRow, Button, ButtonStyle, Extension, slash_command


        class ButtonExampleSkin(Extension):
            @slash_command()
            async def multiple_buttons(self, ctx):
                await ctx.send(
                    "2 buttons in a row",
                    components=[
                        Button(style=ButtonStyle.BLURPLE, label="A blurple button"),
                        Button(style=ButtonStyle.RED, label="A red button"),
                    ],
                )


            @slash_command()
            async def action_rows(self, ctx):
                await ctx.send(
                    "2 buttons in 2 rows, using nested lists",
                    components=[
                        [Button(style=ButtonStyle.BLURPLE, label="A blurple button")],
                        [Button(style=ButtonStyle.RED, label="A red button")],
                    ],
                )


            @slash_command()
            async def action_rows_more(self, ctx):
                await ctx.send(
                    "2 buttons in 2 rows, using explicit action_rows lists",
                    components=[
                        ActionRow(Button(style=ButtonStyle.BLURPLE, label="A blurple button")),
                        ActionRow(Button(style=ButtonStyle.RED, label="A red button")),
                    ],
                )
        ```

Sounds pretty good right? Well, let's go over how you can use them:

## Basic Usage

### Setup

Extensions are effectively just another Python file that contains a class that inherits from an object called `Extension`,
inside this extension.

For example, this is a valid extension file:

```python
from interactions import Extension

class MyExtension(Extension):
    pass
```

??? note "Differences from Other Python Discord Libraries"
    If you come from another Python Discord library, you might have seen that there's no `__init__` and `setup` function in this example.
    They still do exist as functions you *can* use (as discussed later), but interactions.py will do the appropriate logic to handle extensions
    without either of the two.

    For example, the following does the exact same thing as the above extension file:

    ```python
    from interactions import Extension

    class MyExtension(Extension):
        def __init__(self, bot):
            self.bot = bot

    def setup(bot):
        # yes, the bot does not need to do any special logic - you just need to pass it into the extension
        MyExtension(bot)
    ```

### Events and Commands

You probably want extensions to do a little bit more than just exist though. Most likely, you want some events and commands
in here. Thankfully, they're relatively simple to do. Expanding on the example a bit, a slash command looks like this:

```python
from interactions import Extension, slash_command, SlashContext

class MyExtension(Extension):
    @slash_command()
    async def test(self, ctx: SlashContext):
        await ctx.send("Hello world!")
```

As you can see, they're almost identical to how you declare slash commands in your main bot file, even using the same decorator.
The only difference is the `self` variable - this is the instance of the extension that the command is being called in, and is
standard for functions inside of classes. Events follow a similar principal.

interactions.py will automatically add all commands and events to the bot when you load the extension (discussed later),
so you don't need to worry about that.

#### Accessing the Bot

When an extension is loaded, the library automatically sets the `bot` for you. With this in mind, you can access your client using `self.bot`.
Using `self.client` also works - they are just aliases to each other.

```python
class MyExtension(Extension):
    @slash_command()
    async def test(self, ctx: SlashContext):
        await ctx.send(f"Hello, I'm {self.bot.user.mention}!")
```

This also allows you to share data between extensions and the main bot itself. `Client` allows storing data in unused attributes,
so you can do something like this:

```python
from interactions import Client

# main.py
bot = Client(...)
bot.my_data = "Hello world"

# extension.py
class MyExtension(Extension):
    @slash_command()
    async def test(self, ctx: SlashContext):
        await ctx.send(f"My data: {self.bot.my_data}!")
```

### Loading the Extension

Now that you've got your extension, you need to load it.

Let's pretend the extension is in a file called `extension.py`, and it looks like the command example:

```python
from interactions import Extension, slash_command, SlashContext

class MyExtension(Extension):
    @slash_command()
    async def test(self, ctx: SlashContext):
        await ctx.send("Hello world!")
```

Now, let's say you have a file called `main.py` in the same directory that actually has the bot in it:

```python
bot = Client(...)
bot.start("token")
```

To load the extension, you just need to use `bot.load_extension("filename.in_import_style")` before `bot.start`. So, in this case, it would look like this:

```python
bot = Client(...)
bot.load_extension("extension")
bot.start("token")
```

And that's it! Your extension is now loaded and ready to go.

#### "Import Style"

In the example above, the filename is passed to `load_extension` without the `.py` extension. This is because interactions.py actually does an
*import* when loading the extension, so whatever string you give it needs to be a valid Python import path. This means that if you have a file structure like this:

```
main.py
exts/
    extension.py
```

You would need to pass `exts.extension` to `load_extension`, as that's the import path to the extension file.

#### Reloading and Unloading Extensions

You can also reload and unload extensions. To do this, you use `bot.reload_extension` and `bot.unload_extension` respectively.

```python
bot.reload_extension("extension")
bot.unload_extension("extension")
```

Reloading and unloading extensions allows you to edit your code without restarting the bot, and to remove extensions you no longer need.
For example, if you organize your extensions so that moderation commands are in one extension, you can reload that extension (and so only moderation-related commands)
as you edit them.

### Initialization

You may want to do some logic to do when loading a specific extension. For that, you can add the `__init__` method, which takes a `Client` instance, in your extension:

```python
class MyExtension(Extension):
    def __init__(self, bot):
        # do some initialization here
        pass
```

#### Asynchronous Initialization

As usual, `__init__` is synchronous. This may pose problems if you're trying to do something asynchronous in it, so there are various ways of solving it.

If you're okay with only doing the asynchronous logic as the bot is starting up (and never again), there are two methods:

=== "`async_start`"
    ```python
    class MyExtension(Extension):
        async def async_start(self):
            # do some initialization here
            pass
    ```

=== "`Startup` Event"
    ```python
    from interactions.api.events import Startup

    class MyExtension(Extension):
        @event(Startup)
        async def startup(self):
            # do some initialization here
            pass
    ```

If you want to do the asynchronous logic every time the extension is loaded, you'll need to use `asyncio.create_task`:

```python
import asyncio

class MyExtension(Extension):
    def __init__(self, bot):
        asyncio.create_task(self.async_init())

    async def async_init(self):
        # do some initialization here
        pass
```

!!! warning "Warning about `asyncio.create_task`"
    `asyncio.create_task` only works *if there is an event loop.* For the sake of simplicity we won't discuss what that is too much,
    but the loop is only created when `asyncio.run()` is called (as it is in `bot.start()`). This means that if you call `asyncio.create_task`
    before `bot.start()`, it will not work. If you need to do asynchronous logic before the bot starts, you'll need to load the extension
    in an asynchronous function and use `await bot.astart()` instead of `bot.start()`.

    For example, this format of loading extensions will allow you to use `asyncio.create_task`:

    ```python
    bot = Client(...)

    async def main():
        # event loop made!
        bot.load_extension("extension")
        await bot.astart("token")

    asyncio.run(main())
    ```

### Cleanup

You may have some logic to do while unloading a specific extension. For that, you can override the `drop` method in your extension:

```python
class MyExtension(Extension):
    def drop(self):
        # do some cleanup here
        super().drop()  # important - this part actually does the unloading
```

The `drop` method is synchronous. If you need to do something asynchronous, you can create a task with `asyncio` to do it:

???+ note "Note about `asyncio.create_task`"
    Usually, there's always an event loop running when unloading an extension (even when the bot is shutting down), so you can use `asyncio.create_task` without any problems.
    However, if you are unloading an extension before `asyncio.run()` has called, the warning from above applies.

```python
import asyncio

class MyExtension(Extension):
    def drop(self):
        asyncio.create_task(self.async_drop())
        super().drop()

    async def async_drop(self):
        # do some cleanup here
        pass
```

## Advanced Usage

### Loading All Extensions In a Folder

Sometimes, you may have a lot of extensions contained in one folder. Writing them all out is both time consuming and not very scalable, so you may want an easier way to load them.

If your folder with all of your extensions is "flat" (only containing Python files for extensions and no subfolders), then your best bet is to use [`pkgutil.iter_modules`](https://docs.python.org/3/library/pkgutil.html#pkgutil.iter_modules) and a for loop:
```python
import pkgutil

# replace "exts" with your folder name
extension_names = [m.name for m in pkgutil.iter_modules(["exts"], prefix="exts.")]
for extension in extension_names:
    bot.load_extension(extension)
```

`iter_modules` finds all modules (which include Python extension files) in the directories provided. By default, this *just* returns the module/import name without the folder name, so we need to add the folder name back in through the `prefix` argument.
Note how the folder passed and the prefix are basically the same thing - the prefix just has a period at the the end.

If your folder with all of your extensions is *not* flat (for example, if you have subfolders in the extension folder containing Python files for extensions), you'll likely want to use [`glob.glob`](https://docs.python.org/3/library/glob.html#glob.glob) instead:
```python
import glob

# replace "exts" with your folder name
ext_filenames = glob.glob("exts/**/*.py")
extension_names = [filename.removesuffix(".py").replace("/", ".") for filename in ext_filenames]
for extension in extension_names:
    bot.load_extension(extension)
```

Note that `glob.glob` returns the *filenames* of all files that match the pattern we provided. To turn it into a module/import name, we need to remove the ".py" suffix and replace the slashes with periods.
On Windows, you may need to replace the slashes with backslashes instead.

???+ note "Note About Loading Extensions From a File"
    While these are two possible ways, they are by no means the *only* ways of finding all extensions in the folder and loading them. Which method is best method depends on your use case and is purely subjective.


### The `setup`/`teardown` Function

You may have noticed that the `Extension` in the extension file is simply just a class, with no way of loading it. interactions.py is smart enough to detect `Extension` subclasses
and use them when loading from a file, but if you want more customization when loading an extension, you'll need to use the `setup` function.

The `setup` function should be *outside* of any `Extension` subclass, and takes in the bot instance, like so:

```python
class MyExtension(Extension):
    ...

def setup(bot):
    # insert logic here
    MyExtension(bot)
```

Here, the `Extension` subclass is initialized inside the `setup` function, and does not need to do any special function to add the extension in beyond being created using the instance.

A similar function can be used for cleanup, called `teardown`. It takes no arguments, and should be outside of any `Extension` subclass, like so:

```python
class MyExtension(Extension):
    ...

def teardown():
    # insert logic here
    pass
```

You usually do not need to worry about unloading the specific extensions themselves, as interactions.py will do that for you.

### Passing Arguments to Extensions

If you would like to pass more than just the bot while initializing an extension, you can pass keyword arguments to the `load_extension` method:

```python
class MyExtension(Extension):
    def __init__(self, bot, some_arg: int = 0):
        ...

bot.load_extension("extension", some_arg=5)
```

If you're using a `setup` function, the argument will be passed to that function instead, so you'll need to pass it to the `Extension` subclass yourself:

```python
class MyExtension(Extension):
    ...

def setup(bot, some_arg: int = 0):
    MyExtension(bot, some_arg)
```

## Extension-Wide Checks

Sometimes, it is useful to have a check run before running any command in an extension. Thankfully, all you need to do is use `add_ext_check`:

```python
class MyExtension(Extension):
    def __init__(self, bot: Client):
        self.add_ext_check(self.a_check)

    async def a_check(ctx: SlashContext) -> bool:
        return bool(ctx.author.name.startswith("a"))

    @slash_command(...)
    async def my_command(...):
        # only ran with people whose names start with an a
        ...
```

### Global Checks

You may want to have a check that runs on every command in a bot. If all of your commands are in extensions (a good idea), you can use
a custom subclass of `Extension` to do it:

```python
# file 1
class CustomExtension(Extension):
    def __init__(self, client: Client):
        self.client = client
        self.add_ext_check(self.a_check)

    async def a_check(ctx: InteractionContext) -> bool:
        return bool(ctx.author.name.startswith("a"))

# file 2
class MyExtension(CustomExtension):
    @slash_command(...)
    async def my_command(...):
        ...
```

### Pre And Post Run Events

Pre- and post-run events are similar to checks. They run before and after a command is invoked, respectively:

```python
from interactions import BaseContext

class MyExtension(Extension):
    def __init__(self, bot: Client):
        self.add_extension_prerun(self.pre_run)
        self.add_extension_postrun(self.post_run)

    async def pre_run(ctx: BaseContext):
        print(f"Command started at: {datetime.datetime.now()}")

    async def post_run(ctx: BaseContext):
        print(f"Command done at: {datetime.datetime.now()}")

    @slash_command(...)
    async def my_command(...):
        # pre and post run will be ran before/after this command
        ...
```

### Extension-Wide Error Handlers

Sometimes, you may want to have a custom error handler for all commands in an extension. You can do this by using `set_extension_error`:

```python
class MyExtension(Extension):
    def __init__(self, bot: Client):
        self.set_extension_error(self.error_handler)

    async def error_handler(self, error: Exception, ctx: BaseContext):
        # handle the error here
        ...
```

??? note "Error Handling Priority"
    Only one error handler will run. Similar to CSS, the most specific handler takes precedence.
    This goes: command error handlers -> extension -> listeners.

### Extension Auto Defer

You may want to automatically defer all commands in that extension. You can do this by using `add_ext_auto_defer`:

```python
class MyExtension(Extension):
    def __init__(self, bot: Client):
        self.add_ext_auto_defer(enabled=True, ephemeral=False, time_until_defer=0.5)
```

??? note "Auto Defer Handling Priority"
    Similar to errors, only one auto defer will be run, and the most specific auto defer takes precendence.
    This goes: command auto defer -> extension -> bot.
