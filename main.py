import asyncio
import logging
import os

import interactions
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

    while True:
        await asyncio.sleep(5)
        print(bot.latency)


@slash_command("ping")
async def ping(ctx):
    action_rows = [
        interactions.ActionRow(
            interactions.Button(
                style=interactions.ButtonStyles.DANGER,
                label="Danger Button",
            )
        )
    ]

    await ctx.send("Pong!", components=action_rows)


bot.start(os.environ["TOKEN"])
