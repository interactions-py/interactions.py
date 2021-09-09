# This is a written example used to test and debug the state of v4.0
import interactions
from interactions.api.http import Route

TOKEN = "guess we'll never be commiting this again."

client = interactions.Client(token=TOKEN)


@client.event
async def on_ready():
    print("Bot is online!")

    await client.http.request(
        Route("POST", "/applications/883788893512683520/guilds/852402668294766612/commands"),
        json={"type": 1, "name": "digiorno", "description": "v4.0.0 baby!"},
    )


@client.event
async def on_message_create(message):
    response = {
        "content": "yeah, message commands are still supported.",
        "tts": False,
        "embeds": [],
        "allowed_mentions": None,
        "components": [],
    }

    args = message.content.split(" ")
    if args[0] == "!digiorno":
        await client.http.request(
            Route("POST", "/channels/852402668294766615/messages"), json=response
        )


@client.event
async def on_interaction_create(interaction):
    # working slash command response.
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
