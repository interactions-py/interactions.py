import logging

import interactions

logging.basicConfig(level=logging.DEBUG)


bot = interactions.Client(token=open("bot.token").read())


@bot.event
async def on_ready():
    print("bot is now online.")


@bot.command(
    type=interactions.ApplicationCommandType.MESSAGE,
    name="simple testing command",
    scope=852402668294766612,
)
async def simple_testing_command(ctx):
    await ctx.send("Hello world!")


bot.start()
