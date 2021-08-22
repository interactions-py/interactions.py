<div align="center">
    <a href="https://pypi.org/project/discord-py-slash-command/">
        <img src="https://raw.githubusercontent.com/discord-py-slash-commands/discord-py-interactions/goverfl0w-new-readme/.github/banner_transparent.png" alt="discord-py-interactions" height="128">
    </a>
    <h2>A simple API wrapper for Discord interactions.</h2>
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
    <a href="https://pypi.org/project/discord-py-slash-command/">PyPI</a>
</p>

# About
## What is discord-interactions?
discord-interactions is, in the simplest terms, a 3rd party library that allows the integration of Discord
interactions of all types to be implemented alongside your discord.py code or separate.

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
* Context Menus

# Installation
We recommend using pip in order to install our library. You are able to do this by typing the following line below:

`pip install -U discord-py-interactions`

# Examples
## Slash Commands
This example shows a very quick and simplistic solution to implementing a slash command.

```py
from interactions import Client

bot = Client(token="...")

# /test
@bot.slash_command(
    name="test",
    description="Your slash command."
)
async def test(ctx):
    await ctx.send("Hello world!")

# /example ping
# We handle subcommands as of v4.0 under the slash decorator.
# All subcommand kwargs are optionals to avoid conflicts.
@bot.slash_command(
    base="example",
    name="ping",
    description="This gives back a ping."
)
async def example_ping(ctx):
    await ctx.send(f"Pong! {bot.latency}")

bot.start()
```

### Cogs
This example serves as an alternative method for using slash commands in a cog instead.

**TBA.**

## Buttons
This basic example shows how to easily integrate buttons into your commands. Buttons are not limited to
slash commands and may be used in regular discord.py commands as well.

**TBA.**

### Advanced
For more advanced use, please refer to our official documentation on [buttons here.](https://discord-py-slash-command.readthedocs.io/en/latest/components.html#responding-to-interactions)

## Selects
This basic example shows how to add selects into our bot. Selects offer the same accessibility as buttons do
in premise of limitations.

**TBA.**

### Advanced
For more advanced use, please refer to our official documentation on [selects here.](https://discord-py-slash-command.readthedocs.io/en/latest/components.html#what-about-selects-dropdowns)

--------

- The discord-interactions library is based off of API gateway events. If you are looking for a library that is webserver-based, please consider:
    - [dispike](https://github.com/ms7m/dispike)
    - [discord-interactions-python](https://github.com/discord/discord-interactions-python)
- If you are looking for a similar library for other languages, please refer to here:
    - [discord-api-docs Community Resources: Interactions](https://discord.com/developers/docs/topics/community-resources#interactions)

