import logging
import os
import uuid

import interactions
from interactions import Client, listen, slash_command, BrandColours, File

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


@slash_command("components")
async def components(ctx):
    selects = [
        [interactions.ChannelSelectMenu()],
        [interactions.RoleSelectMenu()],
        [interactions.UserSelectMenu()],
        [interactions.MentionableSelectMenu()],
        [interactions.StringSelectMenu("test", "test 2", "test 3")],
    ]
    await ctx.send("Select menus", components=selects)
    await ctx.send(
        "Buttons",
        components=[interactions.Button(label="test", style=interactions.ButtonStyles.PRIMARY)],
    )


@slash_command("modal")
async def modal(ctx):
    _modal = interactions.Modal(
        interactions.ShortText(
            label="Input Text",
            placeholder="Placeholder",
            required=True,
            min_length=5,
            max_length=10,
        ),
        interactions.ParagraphText(
            label="Paragraph Text",
            placeholder="Placeholder",
            required=True,
            min_length=5,
            max_length=10,
        ),
        title="Modal",
    )
    await ctx.send_modal(_modal)


@listen()
async def on_component(event: interactions.events.Component):
    ctx: interactions.ComponentContext = event.ctx

    if ctx.values:
        await ctx.send(f"Selected {ctx.values}")
    else:
        await ctx.send(f"Clicked {ctx.custom_id}")


bot.start(os.environ["TOKEN"])
