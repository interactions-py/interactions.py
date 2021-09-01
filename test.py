# This is a written example used to test and debug the state of v4.0
import interactions

TOKEN = "no leak here :)"

client = interactions.Client(token=TOKEN)


@client.event
async def on_ready():
    print("hi")


client.start()
