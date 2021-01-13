# discord-py-slash-command

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/224bdbe58f8f43f28a093a33a7546456)](https://app.codacy.com/gh/eunwoo1104/discord-py-slash-command?utm_source=github.com&utm_medium=referral&utm_content=eunwoo1104/discord-py-slash-command&utm_campaign=Badge_Grade_Settings)
<a href="https://discord.gg/KkgMBVuEkx"> <img alt="Discord" src="https://img.shields.io/discord/789032594456576001" /> </a>

A simple Discord Slash Command extension for [discord.py](https://github.com/Rapptz/discord.py).

[**Discussions**](https://github.com/eunwoo1104/discord-py-slash-command/discussions).

## About
Discord Slash Commands are a new implementation for the Bot API that utilize the forward-slash "/" symbol.
Released on 15 December 2020, many bot developers are still learning to learn how to implement this into
their very own bots. This extension aims to help serve as a guidance for those looking into wanting to add
these new slash commands into their bots for those that use discord.py, building off of the current library
code and substituting its own for where it's needed. *discord-py-slash-command* stands as the first public
slash command extension library to be made for Discord Bot API libraries.

## Installation
You are able to easily install the *discord-py-slash-command* library by using the given PIP line below:

`pip install -U discord-py-slash-command`

## Disclaimer
Since slash commands are currently not officially released (They're in public beta), there will be many breaking
changes to this extension which may cause it to become unstable. It is recommended to wait until discord officially
releases slash commands. Waiting until Release 1.1.0, which is planned to have most features implemented in the code, is also recommended.
At this time, the developer of *discord.py* has no plans to officially support slash commands for their library.

## Examples
### Quick Startup
This is a quick startup method towards using slash commands.
```py
import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
slash = SlashCommand(bot)

@slash.slash(name="test")
async def _test(ctx: SlashContext):
    embed = discord.Embed(title="embed test")
    await ctx.send(content="test", embeds=[embed])

bot.run("discord_token")
```

### Advanced
This offers implementation of the slash command library in the usage of a cog.
```py
import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashCommand, SlashContext

class Slash(commands.Cog):
    def __init__(self, bot):
        if not hasattr(bot, "slash"):
            # Creates new SlashCommand instance to bot if bot doesn't have.
            bot.slash = SlashCommand(bot, override_type=True)
        self.bot = bot
        self.bot.slash.get_cog_commands(self)

    def cog_unload(self):
        self.bot.slash.remove_cog_commands(self)

    @cog_ext.cog_slash(name="test")
    async def _test(self, ctx: SlashContext):
        embed = discord.Embed(title="embed test")
        await ctx.send(content="test", embeds=[embed])

def setup(bot):
    bot.add_cog(Slash(bot))
```

## Documentation
See the official [docs](https://discord-py-slash-command.readthedocs.io/en/latest/) for library usage here.

See [discord-api-docs](https://discord.com/developers/docs/interactions/slash-commands) for some more information
about some formats.
