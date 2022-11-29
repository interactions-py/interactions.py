import random
from string import printable

import pytest

import interactions

client = interactions.Client(
    "ODIzMTQxMTE3ODUxMjA1Njgy.G8pIon.3WZzfl6W-C5HO-E_rAHfCojJKeG6aq3keFvjGw"
)  # this token is invalidated
client._http = interactions.HTTPClient(client._http, client._cache)


def pytest_sessionstart(session):
    class _Request:
        async def request(self, route, **kwargs):
            if route.method == "POST" and route.path == "/channels/123456789/messages":
                kwargs["json"]["author"] = {}

            if route.method == "PATCH":
                if route.path == "/guilds/987654321":
                    kwargs["json"] = {"id": 987654321, **kwargs["json"]}
                elif route.path.endswith("/roles"):
                    kwargs["json"] = [{"id": 987654321, "position": 1}, {"id": 98437893445445}]

            elif route.method == "POST":
                if route.path.endswith("/channels"):
                    kwargs["json"].pop("recipient_id", None)
                    kwargs["json"] = {"id": random.randint(1, 1000)}

            elif route.method == "GET":
                if route.path.startswith("/channels/"):
                    kwargs["json"] = {
                        "name": "owo",
                        "type": 0,
                        "id": f"{route.path.split('channels/')[-1]}",
                    }

                elif "/threads/active" in route.path:
                    kwargs["json"] = {"threads": [{"id": "8920370479428"}], "members": []}

                elif "/bans" in route.path:
                    kwargs["json"] = [{"user": {"id": 4124121452420}}]

                elif route.path == "/sticker-packs":
                    kwargs["json"] = {"sticker_packs": []}

                elif route.path.endswith("/members"):
                    kwargs["json"] = [{"user": {"id": 82093740240392}}]

                elif route.path.endswith("/members") or route.path.endswith("/members/search"):
                    kwargs["json"] = [{"user": {"id": 128093209}}, {"user": {"id": 125418155}}]

                elif "/members/" in route.path:
                    kwargs["json"] = {"user": {"id": "8432795240"}}

                elif "auto-moderation/rules/" in route.path:
                    kwargs["json"] = {}

                elif route.path.endswith("/preview"):
                    kwargs["json"] = {}

                elif route.path.endswith("/prune"):
                    kwargs["json"] = {"prune": "hi"}

                elif "/guilds/" in route.path and "/emojis/" in route.path:
                    kwargs["json"] = {}

                elif route.path.endswith("/guilds/987654321"):
                    kwargs["json"] = {"id": 987654321}

                elif route.path.startswith("/invites/"):
                    kwargs["json"] = {}

                else:
                    kwargs["json"] = [{"id": 128093209}, {"id": 125418155}]

            if (
                not (json := kwargs.get("json", {}))
                and not isinstance(json, list)
                and not json.get("id")
            ):
                if not json:
                    kwargs["json"] = {"id": random.randint(0, 1000)}
                else:
                    kwargs["json"]["id"] = random.randint(0, 1000)

            return kwargs.get("json", {})

    interactions.api.http.request._Request.request = _Request.request


def pytest_sessionfinish(session):
    del client._http._req._session


@pytest.fixture(scope="session")
def fake_client():
    return client


@pytest.fixture(autouse=True)
def clear_commands(fake_client):
    fake_client._commands = []


@pytest.fixture(autouse=True)
def ensure_no_stdout(capfd):
    yield
    out, _ = capfd.readouterr()
    assert all(letter not in out for letter in printable)


@pytest.fixture(scope="session")
def channel(fake_client):
    ch = interactions.Channel(id=123456789, guild_id=987654321, _client=fake_client._http)
    ch.available_tags = []
    fake_client._http.cache[interactions.Channel].add(ch)

    fake_client._http.cache[interactions.VoiceState][
        interactions.Snowflake(77)
    ] = interactions.VoiceState(user_id=77, channel_id=123456789, guild_id=987654321)
    fake_client._http.cache[interactions.VoiceState][
        interactions.Snowflake(88)
    ] = interactions.VoiceState(user_id=88, channel_id=123456789, guild_id=987654321)
    fake_client._http.cache[interactions.VoiceState][
        interactions.Snowflake(99)
    ] = interactions.VoiceState(user_id=99, channel_id=123456789, guild_id=777)
    fake_client._http.cache[interactions.VoiceState][
        interactions.Snowflake(111)
    ] = interactions.VoiceState(user_id=111, channel_id=777, guild_id=987654321)
    return ch


@pytest.fixture(scope="session")
def guild(fake_client, channel):
    g = interactions.Guild(
        id=987654321,
        roles=[
            interactions.Role(id=987654321),
            interactions.Role(id=987654321, emoji=":bleh:"),
            interactions.Role(id=987654321, name="hi"),
            interactions.Role(id=8974894372054),
        ],
        _client=fake_client._http,
        channels=[
            channel,
            interactions.Channel(
                id=777, type=interactions.ChannelType.GUILD_VOICE, name="stepbro?"
            ),
        ],
    )
    fake_client._http.cache[interactions.Guild].add(g)
    return g


# todo test get func
# todo test every model
# todo "test" every http func?
# todo test gateway (events (-> AND CACHE)) as good as possible with fake data
# todo run every get request func in a sep file to ensure 0 printouts
