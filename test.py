# This is a written example used to test and debug the state of v4.0
import interactions

TOKEN = open(".token").read().split("\n")[0]

client = interactions.Client(token=TOKEN)


@client.event
async def on_ready():
    print(f"{client.me.username}#{client.me.discriminator} logged in.")

    # await client.http.request(
    #     Route("POST", "/applications/883788893512683520/guilds/852402668294766612/commands"),
    #     json={"type": 1, "name": "digiorno", "description": "v4.0.0 baby!"},
    # )


@client.command(name="test", description="new descc", scope=789032594456576001)
async def command_name(ctx):
    await ctx.send("testing")


client.start()
