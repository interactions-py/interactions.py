import asyncio
import logging
import os
import uuid

import interactions
from interactions import Client, listen, slash_command, BrandColours

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
    action_rows = [
        interactions.ActionRow(
            interactions.Button(
                style=interactions.ButtonStyles.DANGER,
                label="Danger Button",
            )
        )
    ]

    embed = interactions.Embed("Pong!", description="Pong!", color=BrandColours.BLURPLE)
    for i in range(5):
        embed.add_field(name=f"Field {i}", value=f"Value {uuid.uuid4()}")

    await ctx.send("Pong!", components=action_rows, embeds=embed)


bot.start(os.environ["TOKEN"])
