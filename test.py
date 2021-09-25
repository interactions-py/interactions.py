# This is a written example used to test and debug the state of v4.0
import interactions
from interactions.api.http import Route

TOKEN = "stop drinking gfuel it sucks"

client = interactions.Client(token=TOKEN)


@client.event
async def on_ready():
    print("Bot is online!")

    # await client.http.request(
    #     Route("POST", "/applications/883788893512683520/guilds/852402668294766612/commands"),
    #     json={"type": 1, "name": "digiorno", "description": "v4.0.0 baby!"},
    # )


@client.event
async def on_interaction_create(interaction):
    response = {
        "content": "pizza 🍕",
        "tts": False,
        "embeds": [],
        "allowed_mentions": None,
        "flags": None,
        "components": [],
    }
    path = f"/interactions/{interaction._json['id']}/{interaction._json['token']}/callback"
    await client.http.request(Route("POST", path), json={"type": 4, "data": response})


client.start()
