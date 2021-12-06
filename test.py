# This is a written example used to test and debug the state of v4.0
import interactions

TOKEN = open(".token").read().split("\n")[0]

client = interactions.Client(token=TOKEN, disable_sync=True)


@client.event
async def on_ready():
    print(f"{client.me.name} ({client.me.id} {(type(client.me.id))}) logged in.")


cool_component = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY, label="shiny boi", custom_id="test_custom_id"
)

cool_modal = interactions.Modal(
    custom_id="test_custom_modal",
    title="modal title!",
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
    name="sub",
    description="let's make sure it works.",
    scope=852402668294766612,
    options=[
        interactions.Option(
            type=interactions.OptionType.SUB_COMMAND,
            name="command",
            description="cool name",
            required=False,
        )
    ],
)
async def sub_command(ctx: interactions.context.CommandContext):
    await ctx.popup(cool_modal)


@client.modal(modal=cool_modal)
async def modal_response(ctx):
    await ctx.send("Hello there!")


@client.command(
    name="command",
    description="just a basic testing description.",
    scope=852402668294766612,
    options=[
        interactions.Option(
            type=interactions.OptionType.STRING,
            name="arg",
            description="the argument to test",
            required=False,
        )
    ],
)
async def command_argument(ctx: interactions.context.CommandContext, arg):
    await ctx.send(f"You said: {arg}", components=cool_component)


@client.component(component=cool_component)
async def test(ctx: interactions.context.ComponentContext):
    await ctx.send(f"hola. {'we are following up.' if ctx.responded else 'first time?'}")


client.start()
