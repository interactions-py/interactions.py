import logging
import os

from interactions import Client, listen, slash_command

logging.basicConfig()
logging.getLogger("interactions").setLevel(logging.DEBUG)

bot = Client()


@listen()
async def on_startup():
    print(f"Logged in as {bot.user}")


@bot.event()
async def on_ready():
    print("Im ready!")


@slash_command("ping")
async def ping(ctx):
    await ctx.send("Pong!")


bot.start(os.environ["TOKEN"])
