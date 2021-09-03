# This is a written example used to test and debug the state of v4.0
import interactions

TOKEN = "Mzc5MzQzMzIyNTQ1NzgyNzg0.WgiY_w.ApUS8sm9kdsnqgkiGyJJvOaiXbY"

client = interactions.Client(token=TOKEN)


@client.event
async def on_ready():
    print("hi")


@client.event
async def on_guild_create(guild):
    print("helo")


client.start()
