import logging

import interactions

logging.basicConfig(level=logging.DEBUG)


bot = interactions.Client(token=open("bot.token").read(), disable_sync=True)


@bot.event
async def on_ready():
    print("bot is now online.")


@bot.command(name="intent", description="h")
async def intent(ctx):
    await ctx.send("hola")


bot.start()
