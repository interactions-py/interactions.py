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
    async def convert(cls, ctx: Context, value: str) -> DatabaseEntry:
        """This is where the magic happens"""
        return cls(hypothetical_database.lookup(ctx.guild.id, value))

# Slash Command:
@slash_command(name="lookup", description="Gives info about a thing from the db")
@slash_option(
    name="thing",
    description="The user enters a string",
    required=True,
    opt_type=OptionTypes.STRING
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

You may also use the `Converter` class that `NAFF` has as well.

```python
class UpperConverter(Converter):
    async def convert(ctx: PrefixedContext, argument: str):
        return argument.upper()

# Slash Command:
@slash_command(name="upper", description="Sends back the input in all caps.")
@slash_option(
    name="to_upper",
    description="The thing to make all caps.",
    required=True,
    opt_type=OptionTypes.STRING
)
async def upper(ctx: InteractionContext, to_upper: UpperConverter):
    await ctx.send(to_upper)

# Prefixed Command:
@prefixed_command()
async def upper(ctx: PrefixedContext, to_upper: UpperConverter):
    await ctx.reply(to_upper)
```

## Built-in Converters

### Context-based Arguments

The library provides `CMD_ARGS`, `CMD_AUTHOR`, `CMD_BODY`, and `CMD_CHANNEL` to get the arguments, the author, the body, and the channel of an instance of a command based on its context. While you can do these yourself in the command itself, having this as an argument may be useful to you, especially for cases where you only have one argument that takes in the rest of the message:

```python
# this example is only viable for prefixed commands
# the other CMD_* can be used with slash commands, however
@prefixed_command()
async def say(ctx: PrefixedContext, content: CMD_BODY):
    await ctx.reply(content)
```

### Discord Model Converters

There are also `Converter`s that represent some Discord models that you can subclass from. These are largely useful for prefixed commands, but you may find a use for them elsewhere.

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
