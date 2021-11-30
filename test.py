# This is a written example used to test and debug the state of v4.0
import interactions

TOKEN = open(".token").read().split("\n")[0]

client = interactions.Client(token=TOKEN)


@client.event
async def on_ready():
    print(f"{client.me.username}#{client.me.discriminator} logged in.")


cool_component = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY, label="hello world!", custom_id="test"
)


@client.command(name="test", description="poggers desc", scope=852402668294766612)
async def command_name(ctx):
    # row = interactions.ActionRow(
    #     components=[

    #     ]
    # )
    await ctx.send("testing", components=cool_component)


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


@client.component(component=cool_component)
async def test(ctx):
    await ctx.edit("hola")


@client.command(
    type=interactions.ApplicationCommandType.MESSAGE,
    name="test context menu",
    scope=852402668294766612,
)
async def context_command(ctx):
    await ctx.send("hi?")


client.start()
