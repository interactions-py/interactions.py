# discord-py-slash-command
Simple Discord Slash Commands extension for [discord.py](https://github.com/Rapptz/discord.py).

## Example
Normal usage:
```py
import discord
from discord.ext import commands
from discord_slash import SlashCommand
from discord_slash import SlashContext

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
slash = SlashCommand(bot)


@slash.slash(name="test")
async def _test(ctx: SlashContext):
    embed = discord.Embed(title="embed test")
    await ctx.send(content="test", embeds=[embed])


bot.run("discord_token")
```

Cog(Not Recommended):
```py
import discord
from discord.ext import commands
from discord_slash import SlashCommand
from discord_slash import SlashContext


class Slash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.slash = SlashCommand(bot, override_type=True)
        # Cog is only supported by commands ext, so just skip checking type.

        # Make sure all commands should be inside `__init__`
        # or some other functions that can put commands.
        @self.slash.slash(name="test")
        async def _test(ctx: SlashContext):
            await ctx.send(content="Hello, World!")

    def cog_unload(self):
        self.slash.remove()


def setup(bot):
    bot.add_cog(Slash(bot))

```

## Installation
`pip install -U discord-py-slash-command`

## Simple note before you use this
Since slash commands are currently not officially released (They're in public beta),
there will be many breaking changes to this extension which may cause it to be unstable, 
so I'd recommend waiting until discord officially releases slash commands,
and waiting until Release 1.1.0, which I'm planning to finish implementing most of the features.  
Or you can wait until discord.py supports slash commands.

## DOCS
https://discord-py-slash-command.readthedocs.io/en/latest/  
See [discord-api-docs](https://discord.com/developers/docs/interactions/slash-commands) for some more information
about some formats.

## Any Questions?
[Discord Server](https://discord.gg/KkgMBVuEkx)  
Or you can ask at [Discussions](https://github.com/eunwoo1104/discord-py-slash-command/discussions).

## TODO
- Support subcommands
- Try supporting most of the features supported by discord.py commands extension
