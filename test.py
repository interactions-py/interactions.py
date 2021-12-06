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
async def sub_command(ctx):
    await ctx.send("just some proof, subcommands *do* in fact work.")


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
async def command_argument(ctx, arg):
    await ctx.send(f"You said: {arg}", components=cool_component)


@client.component(component=cool_component)
async def test(ctx):
    await ctx.send(f"hola. {'we are following up.' if ctx.responded else 'first time?'}")


client.start()
