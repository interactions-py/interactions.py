import asyncio
import logging
import os
import uuid

from thefuzz import process

import interactions
from interactions import Client, listen, slash_command, BrandColours, FlatUIColours, MaterialColours, File
from interactions.models.internal.application_commands import global_autocomplete, slash_option

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


@slash_command("record", description="Record audio in your voice channel")
@slash_option("duration", "The duration of the recording", opt_type=interactions.OptionType.NUMBER, required=True)
async def record(ctx: interactions.SlashContext, duration: int):
    if ctx.author.voice.channel is None:
        return await ctx.send("You must be in a voice channel to use this command.")
    voice_channel = ctx.author.voice.channel
    voice_state = await voice_channel.connect()

    recorder = voice_state.start_recording()
    await ctx.send(f"Recording for {duration} seconds")
    await asyncio.sleep(duration)
    voice_state.stop_recording()

    await ctx.send(
        "Here is your recording", files=[File(f, file_name=f"{user_id}.mp3") for user_id, f in recorder.output.items()]
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


@slash_command("multi_image")
async def multi_image_embed_test(ctx: interactions.SlashContext):
    images = [
        "https://cdn.discordapp.com/attachments/1024794413710458980/1066808750519885974/Batman_Stellar_Derp.png",
        "https://cdn.discordapp.com/attachments/1024794413710458980/1066808761626402836/Batman_Derp.jpg",
    ]

    embed = interactions.Embed(url="https://github.com/interactions-py/interactions.py", color=BrandColours.BLURPLE)
    embed.set_images(*images)

    await ctx.send(embeds=embed)

    embed = interactions.Embed("Standard embed")
    embed.set_image(images[0])
    await ctx.send(embeds=embed)


def get_colour(colour: str):
    if colour in interactions.MaterialColors.__members__:
        return interactions.MaterialColors[colour]
    elif colour in interactions.BrandColors.__members__:
        return interactions.BrandColors[colour]
    elif colour in interactions.FlatUIColours.__members__:
        return interactions.FlatUIColours[colour]
    else:
        return interactions.BrandColors.BLURPLE


@slash_command("test")
@slash_option("colour", "The colour to use", autocomplete=True, opt_type=interactions.OptionType.STRING, required=True)
@slash_option("text", "some text", autocomplete=True, opt_type=interactions.OptionType.STRING, required=True)
async def test(ctx: interactions.SlashContext, colour: str, text: str):
    embed = interactions.Embed(f"{text} {colour.title()}", color=get_colour(colour))
    await ctx.send(embeds=embed)


@global_autocomplete("colour")
async def colour_autocomplete(ctx: interactions.AutocompleteContext):
    colours = list((BrandColours.__members__ | FlatUIColours.__members__ | MaterialColours.__members__).keys())

    if not ctx.input_text:
        colours = colours[:25]
    else:
        results = process.extract(ctx.input_text, colours, limit=25)
        colour_match = sorted([result for result in results if result[1] > 50], key=lambda x: x[1], reverse=True)
        colours = [colour[0] for colour in colour_match]

    await ctx.send([{"name": colour.title(), "value": colour} for colour in colours])


@test.autocomplete("text")
async def text_autocomplete(ctx: interactions.AutocompleteContext):
    await ctx.send([{"name": c, "value": c} for c in ["colour", "color", "shade", "hue"]])


bot.start(os.environ["TOKEN"])
