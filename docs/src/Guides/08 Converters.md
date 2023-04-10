# Converters

If your bot is complex enough, you might find yourself wanting to use custom models in your commands. Converters are classes that allow you to do just that, and can be used in both slash and prefixed commands.

This can be useful if you frequently find yourself starting commands with `thing = lookup(thing_name)`.

## Inline Converters

If you do not wish to create an entirely new class, you can simply add a `convert` function in your existing class:

```python
class DatabaseEntry():
    name: str
    description: str
    score: int

    @classmethod  # you can also use staticmethod
    async def convert(cls, ctx: BaseContext, value: str) -> DatabaseEntry:
        """This is where the magic happens"""
        return cls(hypothetical_database.lookup(ctx.guild.id, value))

# Slash Command:
@slash_command(name="lookup", description="Gives info about a thing from the db")
@slash_option(
    name="thing",
    description="The user enters a string",
    required=True,
    opt_type=OptionType.STRING
)
async def my_command_function(ctx: InteractionContext, thing: DatabaseEntry):
    await ctx.send(f"***{thing.name}***\n{thing.description}\nScore: {thing.score}/10")

# Prefixed Command:
@prefixed_command()
async def my_command_function(ctx: InteractionContext, thing: DatabaseEntry):
    await ctx.reply(f"***{thing.name}***\n{thing.description}\nScore: {thing.score}/10")
```

As you can see, a converter can transparently convert what Discord sends you (a string, a user, etc) into something more complex (a pokemon card, a scoresheet, etc).

## `Converter`

You may also use the `Converter` class that `interactions.py` has as well.

```python
class UpperConverter(Converter):
    async def convert(ctx: BaseContext, argument: str):
        return argument.upper()

# Slash Command:
@slash_command(name="upper", description="Sends back the input in all caps.")
@slash_option(
    name="to_upper",
    description="The thing to make all caps.",
    required=True,
    opt_type=OptionType.STRING
)
async def upper(ctx: InteractionContext, to_upper: UpperConverter):
    await ctx.send(to_upper)

# Prefixed Command:
@prefixed_command()
async def upper(ctx: PrefixedContext, to_upper: UpperConverter):
    await ctx.reply(to_upper)
```

## Discord Model Converters

There are `Converter`s that represent some Discord models that you can subclass from. These are largely useful for prefixed commands, but you may find a use for them elsewhere.

A table of objects and their respective converter is as follows:

| Discord Model                          | Converter                     |
|----------------------------------------|-------------------------------|
| `SnowflakeObject`                      | `SnowflakeConverter`          |
| `BaseChannel`, `TYPE_ALL_CHANNEL`      | `BaseChannelConverter`        |
| `DMChannel`, `TYPE_DM_CHANNEL`         | `DMChannelConverter`          |
| `DM`                                   | `DMConverter`                 |
| `DMGroup`                              | `DMGroupConverter`            |
| `GuildChannel`, `TYPE_GUILD_CHANNEL`   | `GuildChannelConverter`       |
| `GuildNews`                            | `GuildNewsConverter`          |
| `GuildCategory`                        | `GuildCategoryConverter`      |
| `GuildText`                            | `GuildTextConverter`          |
| `ThreadChannel`, `TYPE_THREAD_CHANNEL` | `ThreadChannelConverter`      |
| `GuildNewsThread`                      | `GuildNewsThreadConverter`    |
| `GuildPublicThread`                    | `GuildPublicThreadConverter`  |
| `GuildPrivateThread`                   | `GuildPrivateThreadConverter` |
| `VoiceChannel`, `TYPE_VOICE_CHANNEL`   | `VoiceChannelConverter`       |
| `GuildVoice`                           | `GuildVoiceConverter`         |
| `GuildStageVoice`                      | `GuildStageVoiceConverter`    |
| `TYPE_MESSAGEABLE_CHANNEL`             | `MessageableChannelConverter` |
| `User`                                 | `UserConverter`               |
| `Member`                               | `MemberConverter`             |
| `Guild`                                | `GuildConverter`              |
| `Role`                                 | `RoleConverter`               |
| `PartialEmoji`                         | `PartialEmojiConverter`       |
| `CustomEmoji`                          | `CustomEmojiConverter`        |


## `typing.Annotated`

Using `typing.Annotated` can allow you to have more proper typehints when using converters:

```python
class UpperConverter(Converter):
    async def convert(ctx: BaseContext, argument: str):
        return argument.upper()

# Slash Command:
@slash_command(name="upper", description="Sends back the input in all caps.")
@slash_option(
    name="to_upper",
    description="The thing to make all caps.",
    required=True,
    opt_type=OptionType.STRING
)
async def upper(ctx: InteractionContext, to_upper: Annotated[str, UpperConverter]):
    await ctx.send(to_upper)

# Prefixed Command:
@prefixed_command()
async def upper(ctx: PrefixedContext, to_upper: Annotated[str, UpperConverter]):
    await ctx.reply(to_upper)
```

For slash commands, `interactions.py` will find the first argument in `Annotated` (besides for the first argument) that are like the converters in this guide and use that.
For prefixed commands, `interactions.py` will always use the second parameter in `Annotated` as the actual converter/parameter to process.
