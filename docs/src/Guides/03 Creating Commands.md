# Creating Slash Commands

So you want to make a slash command (or interaction, as they are officially called), but don't know how to get started?
Then this is the right place for you.

## Your First Command

To create an interaction, simply define an asynchronous function and use the `@slash_command()` decorator above it.

Interactions need to be responded to within 3 seconds. To do this, use `await ctx.send()`.
If your code needs more time, don't worry. You can use `await ctx.defer()` to increase the time until you need to respond to the command to 15 minutes.
```python
from interactions import slash_command, SlashContext

@slash_command(name="my_command", description="My first command :)")
async def my_command_function(ctx: SlashContext):
    await ctx.send("Hello World")

@slash_command(name="my_long_command", description="My second command :)")
async def my_long_command_function(ctx: SlashContext):
    # need to defer it, otherwise, it fails
    await ctx.defer()

    # do stuff for a bit
    await asyncio.sleep(600)

    await ctx.send("Hello World")
```
???+ note
    Command names must be lowercase and can only contain `-` and `_` as special symbols and must not contain spaces.

When testing, it is recommended to use non-global commands, as they sync instantly.
For that, you can either define `scopes` in every command or set `debug_scope` in the bot instantiation which sets the scope automatically for all commands.

You can define non-global commands by passing a list of guild ids to `scopes` in the interaction creation.
```python
@slash_command(name="my_command", description="My first command :)", scopes=[870046872864165888])
async def my_command_function(ctx: SlashContext):
    await ctx.send("Hello World")
```

For more information, please visit the API reference [here](/interactions.py/API Reference/API Reference/models/Internal/application_commands/#interactions.models.internal.application_commands.slash_command).

## Subcommands

If you have multiple commands that fit under the same category, subcommands are perfect for you.

Let's define a basic subcommand:
```python
@slash_command(
    name="base",
    description="My command base",
    group_name="group",
    group_description="My command group",
    sub_cmd_name="command",
    sub_cmd_description="My command",
)
async def my_command_function(ctx: SlashContext):
    await ctx.send("Hello World")
```

This will show up in discord as `/base group command`. There are more ways to add additional subcommands:

=== ":one: Decorator"
    ```python
    @my_command_function.subcommand(
        group_name="group",
        group_description="My command group",
        sub_cmd_name="sub",
        sub_cmd_description="My subcommand",
    )
    async def my_second_command_function(ctx: SlashContext):
        await ctx.send("Hello World")
    ```

=== ":two: Repeat Definition"
    ```python
    @slash_command(
        name="base",
        description="My command base",
        group_name="group",
        group_description="My command group",
        sub_cmd_name="second_command",
        sub_cmd_description="My second command",
    )
    async def my_second_command_function(ctx: SlashContext):
        await ctx.send("Hello World")
    ```

    **Note:** This is particularly useful if you want to split subcommands into different files.

=== ":three: Class Definition"
    ```python
    base = SlashCommand(name="base", description="My command base")
    group = base.group(name="group", description="My command group")

    @group.subcommand(sub_cmd_name="second_command", sub_cmd_description="My second command")
    async def my_second_command_function(ctx: SlashContext):
        await ctx.send("Hello World")
    ```

For all of these, the "group" parts are optional, allowing you to do `/base command` instead.

???+ note
    You cannot mix group subcommands and non-group subcommands into one base command - you must either use all group subcommands or normal subcommands.


## But I Need More Options

Interactions can also have options. There are a bunch of different [types of options](/interactions.py/API Reference/API Reference/models/Internal/application_commands/#interactions.models.internal.application_commands.OptionType):

| Option Type               | Return Type                                | Description                                                                                 |
|---------------------------|--------------------------------------------|---------------------------------------------------------------------------------------------|
| `OptionType.STRING`      | `str`                                      | Limit the input to a string.                                                                |
| `OptionType.INTEGER`     | `int`                                      | Limit the input to a integer.                                                               |
| `OptionType.NUMBER`      | `float`                                    | Limit the input to a float.                                                                 |
| `OptionType.BOOLEAN`     | `bool`                                     | Let the user choose either `True` or `False`.                                               |
| `OptionType.USER`        | `Member` in guilds, else `User`            | Let the user choose a discord user from an automatically-generated list of options.         |
| `OptionType.CHANNEL`     | `GuildChannel` in guilds, else `DMChannel` | Let the user choose a discord channel from an automatically-generated list of options.      |
| `OptionType.ROLE`        | `Role`                                     | Let the user choose a discord role from an automatically-generated list of options.         |
| `OptionType.MENTIONABLE` | `DiscordObject`                            | Let the user chose any discord mentionable from an automatically generated list of options. |
| `OptionType.ATTACHMENT`  | `Attachment`                               | Let the user upload an attachment.                                                          |

Now that you know all the options you have for options, you can opt into adding options to your interaction.

You do that by using the `@slash_option()` decorator and passing the option name as a function parameter:
```python
from interactions import OptionType

@slash_command(name="my_command", ...)
@slash_option(
    name="integer_option",
    description="Integer Option",
    required=True,
    opt_type=OptionType.INTEGER
)
async def my_command_function(ctx: SlashContext, integer_option: int):
    await ctx.send(f"You input {integer_option}")
```

Options can either be required or not. If an option is not required, make sure to set a default value for them.

Always make sure to define all required options first, this is a Discord requirement!
```python
@slash_command(name="my_command", ...)
@slash_option(
    name="integer_option",
    description="Integer Option",
    required=False,
    opt_type=OptionType.INTEGER
)
async def my_command_function(ctx: SlashContext, integer_option: int = 5):
    await ctx.send(f"You input {integer_option}")
```

For more information, please visit the API reference [here](/interactions.py/API Reference/API Reference/models/Internal/application_commands/#interactions.models.internal.application_commands.slash_option).

## Restricting Options

If you are using an `OptionType.CHANNEL` option, you can restrict the channel a user can choose by setting `channel_types`:
```python
@slash_command(name="my_command", ...)
@slash_option(
    name="channel_option",
    description="Channel Option",
    required=True,
    opt_type=OptionType.CHANNEL,
    channel_types=[ChannelType.GUILD_TEXT]
)
async def my_command_function(ctx: SlashContext, channel_option: GUILD_TEXT):
    await channel_option.send("This is a text channel in a guild")

    await ctx.send("...")
```

You can also set an upper and lower limit for both `OptionType.INTEGER` and `OptionType.NUMBER` by setting `min_value` and `max_value`:
```python
@slash_command(name="my_command", ...)
@slash_option(
    name="integer_option",
    description="Integer Option",
    required=True,
    opt_type=OptionType.INTEGER,
    min_value=10,
    max_value=15
)
async def my_command_function(ctx: SlashContext, integer_option: int):
    await ctx.send(f"You input {integer_option} which is always between 10 and 15")
```

The same can be done with the length of an option when using `OptionType.STRING` by setting `min_length` and `max_length`:
```python
@slash_command(name="my_command", ...)
@slash_option(
    name="string_option",
    description="String Option",
    required=True,
    opt_type=OptionType.STRING,
    min_length=5,
    max_length=10
)
async def my_command_function(ctx: SlashContext, string_option: str):
    await ctx.send(f"You input `{string_option}` which is between 5 and 10 characters long")
```

!!! danger "Option Names"
    Be aware that the option `name` and the function parameter need to be the same (In this example both are `integer_option`).


## But I Want A Choice

If your users ~~are dumb~~ constantly misspell specific strings, it might be wise to set up choices.
With choices, the user can no longer freely input whatever they want, instead, they must choose from a curated list.

To create a choice, simply fill `choices` in `@slash_option()`. An option can have up to 25 choices:
```python
from interactions import SlashCommandChoice

@slash_command(name="my_command", ...)
@slash_option(
    name="integer_option",
    description="Integer Option",
    required=True,
    opt_type=OptionType.INTEGER,
    choices=[
        SlashCommandChoice(name="One", value=1),
        SlashCommandChoice(name="Two", value=2)
    ]
)
async def my_command_function(ctx: SlashContext, integer_option: int):
    await ctx.send(f"You input {integer_option} which is either 1 or 2")
```

For more information, please visit the API reference [here](/interactions.py/API Reference/API Reference/models/Internal/application_commands/#interactions.models.internal.application_commands.SlashCommandChoice).

## I Need More Than 25 Choices

Looks like you want autocomplete options. These dynamically show users choices based on their input.
The downside is that you need to supply the choices on request, making this a bit more tricky to set up.

To use autocomplete options, set `autocomplete=True` in `@slash_option()`:
```python
@slash_command(name="my_command", ...)
@slash_option(
    name="string_option",
    description="String Option",
    required=True,
    opt_type=OptionType.STRING,
    autocomplete=True
)
async def my_command_function(ctx: SlashContext, string_option: str):
    await ctx.send(f"You input {string_option}")
```

Then you need to register the autocomplete callback, aka the function Discord calls when users fill in the option.

In there, you have three seconds to return whatever choices you want to the user. In this example we will simply return their input with "a", "b" or "c" appended:
```python
from interactions import AutocompleteContext

@my_command.autocomplete("string_option")
async def autocomplete(self, ctx: AutocompleteContext):
    # make sure this is done within three seconds
    await ctx.send(
        choices=[
            {
                "name": f"{ctx.input_text}a",
                "value": f"{ctx.input_text}a",
            },
            {
                "name": f"{ctx.input_text}b",
                "value": f"{ctx.input_text}b",
            },
            {
                "name": f"{ctx.input_text}c",
                "value": f"{ctx.input_text}c",
            },
        ]
    )
```

## But I Don't Like Decorators

You are in luck. There are currently four different ways to create interactions, one does not need any decorators at all.

=== ":one: Multiple Decorators"
    ```python
    @slash_command(name="my_command", description="My first command :)")
    @slash_option(
        name="integer_option",
        description="Integer Option",
        required=True,
        opt_type=OptionType.INTEGER
    )
    async def my_command_function(ctx: SlashContext, integer_option: int):
        await ctx.send(f"You input {integer_option}")
    ```

=== ":two: Single Decorator"
    ```python
    from interactions import SlashCommandOption

    @slash_command(
        name="my_command",
        description="My first command :)",
        options=[
            SlashCommandOption(
                name="integer_option",
                description="Integer Option",
                required=True,
                type=OptionType.INTEGER
            )
        ]
    )
    async def my_command_function(ctx: SlashContext, integer_option: int):
        await ctx.send(f"You input {integer_option}")
    ```

=== ":three: Function Annotations"
    ```python
    from interactions import slash_int_option

    @slash_command(name="my_command", description="My first command :)")
    async def my_command_function(ctx: SlashContext, integer_option: slash_int_option("Integer Option")):
        await ctx.send(f"You input {integer_option}")
    ```

=== ":four: Manual Registration"
    ```python
    from interactions import SlashCommandOption

    async def my_command_function(ctx: SlashContext, integer_option: int):
        await ctx.send(f"You input {integer_option}")

    bot.add_interaction(
        command=SlashCommand(
            name="my_command",
            description="My first command :)",
            options=[
                SlashCommandOption(
                    name="integer_option",
                    description="Integer Option",
                    required=True,
                    type=OptionType.INTEGER
                )
            ]
        )
    )
    ```

## I Don't Want My Friends Using My Commands

How rude.

Anyway, this is somewhat possible with command permissions.
While you cannot explicitly block / allow certain roles / members / channels to use your commands on the bot side, you can define default permissions which members need to have to use the command.

However, these default permissions can be overwritten by server admins, so this system is not safe for stuff like owner only eval commands.
This system is designed to limit access to admin commands after a bot is added to a server, before admins have a chance to customise the permissions they want.

If you do not want admins to be able to overwrite your permissions, or the permissions are not flexible enough for you, you should use [checks][check-this-out].

In this example, we will limit access to the command to members with the `MANAGE_EVENTS` and `MANAGE_THREADS` permissions.
There are two ways to define permissions.

=== ":one: Decorators"
    ```py
    from interactions import Permissions, slash_default_member_permission

    @slash_command(name="my_command")
    @slash_default_member_permission(Permissions.MANAGE_EVENTS)
    @slash_default_member_permission(Permissions.MANAGE_THREADS)
    async def my_command_function(ctx: SlashContext):
        ...
    ```

=== ":two: Function Definition"
    ```py
    from interactions import Permissions

    @slash_command(
        name="my_command",
        default_member_permissions=Permissions.MANAGE_EVENTS | Permissions.MANAGE_THREADS,
    )
    async def my_command_function(ctx: SlashContext):
        ...
    ```

Multiple permissions are defined with the bitwise OR operator `|`.

### Blocking Commands in DMs

You can also block commands in DMs. To do that, just set `dm_permission` to false.

```py
@slash_command(
    name="my_guild_only_command",
    dm_permission=False,
)
async def my_command_function(ctx: SlashContext):
    ...
```

### Context Menus

Both default permissions and DM blocking can be used the same way for context menus, since they are normal slash commands under the hood.

### Check This Out

Checks allow you to define who can use your commands however you want.

There are a few pre-made checks for you to use, and you can simply create your own custom checks.

=== "Build-In Check"
    Check that the author is the owner of the bot:

    ```py
    from interactions import is_owner

    @is_owner()
    @slash_command(name="my_command")
    async def my_command_function(ctx: SlashContext):
        ...
    ```

=== "Custom Check"
    Check that the author's name starts with `a`:

    ```py
    from interactions import check

    async def my_check(ctx: Context):
        return ctx.author.name.startswith("a")

    @check(check=my_check)
    @slash_command(name="my_command")
    async def my_command_function(ctx: SlashContext):
        ...
    ```

=== "Reusing Checks"
    You can reuse checks in extensions by adding them to the extension check list

    ```py
    from interactions import Extension

    class MyExtension(Extension):
        def __init__(self, bot) -> None:
            super().__init__(bot)
            self.add_ext_check(is_owner())

    @slash_command(name="my_command")
    async def my_command_function(ctx: SlashContext):
        ...

    @slash_command(name="my_command2")
    async def my_command_function2(ctx: SlashContext):
        ...

    def setup(bot) -> None:
        MyExtension(bot)
    ```

    The check will be checked for every command in the extension.



## I Don't Want To Define The Same Option Every Time

If you are like me, you find yourself reusing options in different commands and having to redefine them every time which is both annoying and bad programming.

Luckily, you can simply make your own decorators that themselves call `@slash_option()`:
```python
def my_own_int_option():
    """Call with `@my_own_int_option()`"""

    def wrapper(func):
        return slash_option(
            name="integer_option",
            description="Integer Option",
            opt_type=OptionType.INTEGER,
            required=True
        )(func)

    return wrapper


@slash_command(name="my_command", ...)
@my_own_int_option()
async def my_command_function(ctx: SlashContext, integer_option: int):
    await ctx.send(f"You input {integer_option}")
```

The same principle can be used to reuse autocomplete options.

## Simplified Error Handling

If you want error handling for all commands, you can override `Client` and define your own.
Any error from interactions will trigger `on_command_error`. That includes context menus.

In this example, we are logging the error and responding to the interaction if not done so yet:
```python
from interactions import Client
from interactions.api.events import CommandError

class CustomClient(Client):
    @listen(disable_default_listeners=True)  # tell the dispatcher that this replaces the default listener
    async def on_command_error(self, event: CommandError):
        logger.error(event.error)
        if not event.ctx.responded:
            await event.ctx.send("Something went wrong.")

client = CustomErrorClient(...)
```

There also is `on_command` which you can overwrite too. That fires on every interactions usage.

## I Need A Custom Parameter Type

If your bot is complex enough, you might find yourself wanting to use custom models in your commands.

To do this, you'll want to use a string option, and define a converter. Information on how to use converters can be found [on the converter page](/Guides/08 Converters).
