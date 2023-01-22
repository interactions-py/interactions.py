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

    guild = bot.get_guild(701347683591389185)
    channel = guild.get_channel(1032200124732022835)

    # await channel.send("Hello", file=File(path, "colonelsanderskiss.png"))

    sticker = await guild.create_custom_sticker(
        "colonelsanderskiss",
        File("colonelsanderskiss.png"),
        tags=["flushed", "kiss", "colonel", "sanders"],
    )

    await channel.send("Hello", stickers=[sticker])

    # test files upload correctly
    await channel.send("image", file=File("colonelsanderskiss.png"))
    await channel.send("multiple", files=[File("colonelsanderskiss.png"), File("bman.png"), File("chubby.jpg")])
    await channel.send("python", files=File("main.py"))


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
