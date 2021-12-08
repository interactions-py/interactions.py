import interactions

TOKEN = open(".token").read().split("\n")[0]

client = interactions.Client(
    token=TOKEN,
    disable_sync=False,
)


@client.event
async def on_ready():
    print(f"{client.me.name} ({client.me.id}) logged in.")


@client.command(name="normal-command", description="testing in da root.", scope=852402668294766612)
async def normal_command(ctx):
    await ctx.send("cool normal man.")


client.load("test_2")
client.start()
