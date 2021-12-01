# This is a written example used to test and debug the state of v4.0
import interactions

TOKEN = open(".token").read().split("\n")[0]

client = interactions.Client(token=TOKEN, disable_sync=True)


@client.event
async def on_ready():
    print(f"{client.me.username}#{client.me.discriminator} logged in.")


cool_component = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY, label="hello world!", custom_id="test"
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
    name="cmd",
    description="just a basic testing description.",
    scope=852402668294766612,
    options=[
        interactions.Option(
            type=interactions.OptionType.STRING,
            name="arg",
            description="the argument to test",
            required=True,
        )
    ],
)
async def cmd_arg(ctx, arg):
    await ctx.send(f"You said: {arg}")


@client.component(component=cool_component)
async def test(ctx):
    await ctx.edit(f"hola. {'we are following up.' if ctx.responded else ''}")


client.start()
