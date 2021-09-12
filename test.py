# This is a written example used to test and debug the state of v4.0
import interactions

TOKEN = "stop drinking gfuel it sucks"

client = interactions.Client(token=TOKEN)


@client.event
async def on_ready():
    print(f"{client.me._json['username']}#{client.me._json['discriminator']} logged in.")

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
        "allowed_mentions": {},
        "components": [],
    }
    json_data = {"type": 4, "data": response}
    _id = interaction._json["id"]  # id of interaction
    _token = interaction._json["token"]
    await client.http._create_interaction_response(_token, _id, json_data)
    await client.http._edit_interaction_response({}, _token, "")


client.start()
