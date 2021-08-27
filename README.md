<div align="center">
    <a href="https://pypi.org/project/discord-py-interactions/">
        <img src="https://raw.githubusercontent.com/muqshots/discord-py-interactions/master/.github/banner_transparent.png" alt="discord-py-interactions" height="128">
    </a>
    <h2>Your ultimate Discord interactions library for <a href="https://github.com/Rapptz/discord.py">discord.py</a>.</h2>
</div>

<div align="center">
        <a href="https://app.codacy.com/gh/eunwoo1104/discord-py-slash-command?utm_source=github.com&utm_medium=referral&utm_content=eunwoo1104/discord-py-slash-command&utm_campaign=Badge_Grade_Settings">
            <img src="https://api.codacy.com/project/badge/Grade/224bdbe58f8f43f28a093a33a7546456" alt="Codacy Badge">
        </a>
        <a href="https://discord.gg/KkgMBVuEkx">
            <img alt="Discord" src="https://img.shields.io/discord/789032594456576001">
        </a>
</div>

<p align="center">
    <a href="#about">About</a> |
    <a href="#installation">Installation</a> |
    <a href="#examples">Examples</a> |
    <a href="https://discord.gg/KkgMBVuEkx">Discord</a> |
    <a href="https://pypi.org/project/discord-py-interactions/">PyPI</a>
</p>

# About
## What is discord-py-interactions?
`discord-py-interactions` is, in the simplest terms, a library extension that builds off of the currently existing
discord.py API wrapper. While we do use our own basic class code for our own library, a large majority of
this library uses discord.py base events in order to make contextualization of interactions relatively easy
for us.

### When did this begin?
In mid-December of 2020, Discord released the very first type of components, **slash commands.** These were
relatively primitive at the time of their debut, however, over time they slowly came to grew more complex
and mutable. This library was created 2 days after the release of slash commands to Discord, and ever since
has been actively growing.

## What do we currently support?
At this time, we are able to provide you an non-exhaustive list (because Discord are actively
creating more interactions at this time) of all components integrated as interactions:

* Slash Commands
* Buttons
* Selects (also known as *dropdowns* or *menus*)

# Installation
We recommend using pip in order to install our library. You are able to do this by typing the following line below:

`pip install -U discord-py-interactions`

# Examples
## Slash Commands
This example shows a very quick and simplistic solution to implementing a slash command.

```py
from discord import Client, Intents, Embed
from discord_slash import SlashCommand, SlashContext

bot = Client(intents=Intents.default())
slash = SlashCommand(bot)

@slash.slash(name="test")
async def test(ctx: SlashContext):
    embed = Embed(title="Embed Test")
    await ctx.send(embed=embed)

bot.run("discord_token")
```

### Cogs
This example serves as an alternative method for using slash commands in a cog instead.

```py
# bot.py
from discord import Client, Intents, Embed
from discord_slash import SlashCommand, SlashContext

bot = Client(intents=Intents.default())
slash = SlashCommand(bot)

bot.load_extension("cog")
bot.run("discord_token")

# cog.py
from discord import Embed
from discord_slash import cog_ext, SlashContext

class Slash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(name="test")
    async def _test(self, ctx: SlashContext):
        embed = Embed(title="Embed Test")
        await ctx.send(embed=embed)
    
def setup(bot):
    bot.add_cog(Slash(bot))
```

## Buttons
This basic example shows how to easily integrate buttons into your commands. Buttons are not limited to
slash commands and may be used in regular discord.py commands as well.

```py
from discord_slash.utils.manage_components import create_button, create_actionrow
from discord_slash.model import ButtonStyle

buttons = [
    create_button(style=ButtonStyle.green, label="A green button"),
    create_button(style=ButtonStyle.blue, label="A blue button")
]
action_row = create_actionrow(*buttons)

await ctx.send(components=[action_row])
```

### Advanced
For more advanced use, please refer to our official documentation on [buttons here.](https://discord-interactions.readthedocs.io/en/latest/components.html#responding-to-interactions)

## Selects
This basic example shows how to add selects into our bot. Selects offer the same accessibility as buttons do
in premise of limitations.

```py
from discord_slash.utils.manage_components import create_select, create_select_option, create_actionrow

select = create_select(
    options=[
        create_select_option("Lab Coat", value="coat", emoji="🥼"),
        create_select_option("Test Tube", value="tube", emoji="🧪"),
        create_select_option("Petri Dish", value="dish", emoji="🧫")
    ],
    placeholder="Choose your option",
    min_values=1, # the minimum number of options a user must select
    max_values=2 # the maximum number of options a user can select
)
action_row = create_actionrow(select)

await ctx.send(components=[action_row])
```

### Advanced
For more advanced use, please refer to our official documentation on [selects here.](https://discord-interactions.readthedocs.io/en/latest/components.html#what-about-selects-dropdowns)

## Context Menus
This basic example shows how to add a message context menu.

```py
from discord_slash.context import MenuContext
from discord_slash.model import ContextMenuType

@slash.context_menu(target=ContextMenuType.MESSAGE,
                    name="commandname",
                    guild_ids=[789032594456576001])
async def commandname(ctx: MenuContext):
    await ctx.send(
        content=f"Responded! The content of the message targeted: {ctx.target_message.content}",
        hidden=True
    )
```

### Advanced
For more advanced use, please refer to our official documentation on [context menus here.](https://discord-interactions.readthedocs.io/en/latest/gettingstarted.html#adding-context-menus)

--------

- The discord-interactions library is based off of API gateway events. If you are looking for a library webserver-based, please consider:
    - [dispike](https://github.com/ms7m/dispike)
    - [discord-interactions-python](https://github.com/discord/discord-interactions-python)
- If you are looking for a similar library for other languages, please refer to here:
    - [discord-api-docs Community Resources: Interactions](https://discord.com/developers/docs/topics/community-resources#interactions)

