# This is a written example used to test and debug the state of v4.0
import interactions

TOKEN = open(".token").read().split("\n")[0]

client = interactions.Client(token=TOKEN)


@client.event
async def on_ready():
    print(f"{client.me.username}#{client.me.discriminator} logged in.")


@client.command(name="test", description="poggers desc", scope=852402668294766612)
async def command_name(ctx):
    await ctx.send("testing")


@client.command(type=2, name="test context menu", scope=852402668294766612)
async def context_command(ctx):
    await ctx.send("hi?")


client.start()
