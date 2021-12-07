# This is a written example used to test and debug the state of v4.0
import interactions

TOKEN = open(".token").read().split("\n")[0]

client = interactions.Client(
    token=TOKEN,
    disable_sync=False,
    # TODO: Fix "member_descriptor" non-JSON serializable type error.
    # presence=interactions.Presence(
    #     status="idle",
    #     afk=False,
    #     activities=[
    #         interactions.PresenceActivity(
    #             name="you.",
    #             type=3,
    #             created_at=int(datetime.utcnow().timestamp())
    #         )._json
    #     ],
    #     client_status = interactions.ClientStatus(desktop="idle", mobile="idle", web="idle")._json
    # )
)


@client.event
async def on_ready():
    print(f"{client.me.name} ({client.me.id} {(type(client.me.id))}) logged in.")


cool_modal = interactions.Modal(
    custom_id="test_custom_modal",
    title="Vent to me.",
    components=[
        interactions.TextInput(
            style=interactions.TextStyleType.PARAGRAPH,
            custom_id="custom_id_one",
            label="Tell me about your life.",
            placeholder="Well, it started ever since I was born, and...",
        ),
        interactions.TextInput(
            style=interactions.TextStyleType.SHORT,
            custom_id="custom_id_two",
            label="How?",
            placeholder="Well...",
            min_length=0,
        ),
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
async def context_modal_response(ctx: interactions.context.CommandContext, argOne, argTwo):
    await ctx.send(
        f"I see, I see... talking about ||{argOne}|| is very serious. I'm sorry to hear that."
    )
    await ctx.send(f"Wow, even more so with ||{argTwo}||? Yikes! That must be really bad then.")


client.start()
