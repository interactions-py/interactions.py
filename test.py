# This is a written example used to test and debug the state of v4.0
import logging

import interactions

TOKEN = open(".token").read().split("\n")[0]

client = interactions.Client(token=TOKEN, disable_sync=True, log_level=logging.INFO)


@client.event
async def on_ready():
    print(f"{client.me.name} ({client.me.id} {(type(client.me.id))}) logged in.")


cool_modal = interactions.Modal(
    custom_id="test_custom_modal",
    title="Vent to me.",
    components=[
        interactions.ModalInput(
            style=interactions.TextStyleType.PARAGRAPH,
            custom_id="input_custom_id",
            label="Tell me about your life.",
            placeholder="Well, it started ever since I was born, and...",
        )
    ],
)


@client.command(
    type=interactions.ApplicationCommandType.USER, name="Vent to Digiorno", scope=852402668294766612
)
async def context_print_name(ctx: interactions.context.CommandContext):
    # user_mention = interactions.Format.stylize(interactions.Format.USER, id=ctx.target.id)
    # await ctx.send(f"Okay, {user_mention}! Nice to see you here.")
    await ctx.popup(cool_modal)


@client.modal(cool_modal)
async def context_modal_response(ctx: interactions.context.CommandContext):
    await ctx.send(
        f"I see, I see... talking about ||{ctx.data.components[0].components[0]['value']}|| is very serious. I'm sorry to hear that."
    )


client.start()
