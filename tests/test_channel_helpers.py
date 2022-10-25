import pytest

import interactions


async def test_http_get_channel_messages_failure(fake_client):
    with pytest.raises(interactions.LibraryException):
        await fake_client._http.get_channel_messages(1, around=2, before=3)


async def test_channel_mention(channel):
    assert channel.mention == "<#123456789>"


async def test_channel_send_text(channel):
    msg = await channel.send("hi")
    msg._json["author"].pop("_client")

    assert isinstance(msg, interactions.Message) and msg._json == dict(
        content="hi",
        tts=False,
        attachments=[],
        embeds=[],
        allowed_mentions={},
        components=[],
        sticker_ids=[],
        author={"id": None, "username": None, "discriminator": None},
    )


async def test_channel_send_embeds_and_components(channel):
    embed1 = interactions.Embed(title="hi", description="hey")
    embed1.add_field(name="hi", value="bye")
    embed2 = interactions.Embed(title="OwO", description="nya~")
    embed2.set_image(url="https://127.0.0.1/images/illegal/1837392.png")
    embed2.set_author(name="hello")
    msg = await channel.send(
        embeds=[embed1, embed2],
        components=[
            interactions.Button(style=1, label="purr"),
            interactions.Button(style=2, label="hi"),
        ],
    )
    msg._json["author"].pop("_client")

    assert isinstance(msg, interactions.Message) and msg._json == dict(
        content="",
        tts=False,
        attachments=[],
        embeds=[
            {
                "title": "hi",
                "description": "hey",
                "fields": [{"name": "hi", "value": "bye", "inline": False}],
            },
            {
                "title": "OwO",
                "description": "nya~",
                "image": {
                    "url": "https://127.0.0.1/images/illegal/1837392.png",
                    "proxy_url": None,
                    "height": None,
                    "width": None,
                },
                "author": {"name": "hello", "url": None, "icon_url": None, "proxy_icon_url": None},
            },
        ],
        allowed_mentions={},
        components=[{"type": 1, "components": [[], []]}],
        sticker_ids=[],
        author={"id": None, "username": None, "discriminator": None},
    )


async def test_channel_modify_not_a_thread_failure(channel):
    with pytest.raises(interactions.LibraryException):
        await channel.archive(True)
    with pytest.raises(interactions.LibraryException):
        await channel.lock(True)
    with pytest.raises(interactions.LibraryException):
        await channel.set_auto_archive_duration(25)
    with pytest.raises(interactions.LibraryException):
        await channel.add_member(24320875439028)
    with pytest.raises(interactions.LibraryException):
        await channel.remove_member(24320875439028)


async def test_channel_set_name(channel):
    await channel.set_name("hello!")
    assert channel._json["name"] == "hello!" and channel.name == "hello!"
    await channel.modify(name="nya~")
    assert channel._json["name"] == "nya~" and channel.name == "nya~"


async def test_channel_set_topic(channel):
    await channel.set_topic("hello!")
    assert channel._json["topic"] == "hello!" and channel.topic == "hello!"
    await channel.modify(topic="nya~")
    assert channel._json["topic"] == "nya~" and channel.topic == "nya~"


async def test_set_bitrate_fail(channel):
    with pytest.raises(interactions.LibraryException):
        await channel.set_bitrate(1)


async def test_set_user_limit_fail(channel):
    with pytest.raises(interactions.LibraryException):
        await channel.set_user_limit(3)


async def test_set_ratelimit_per_user(channel):
    await channel.set_rate_limit_per_user(1000)
    assert channel._json["rate_limit_per_user"] == 1000 and channel.rate_limit_per_user == 1000
    await channel.modify(rate_limit_per_user=2160)
    assert channel._json["rate_limit_per_user"] == 2160 and channel.rate_limit_per_user == 2160


async def test_set_position(channel):
    await channel.set_position(82)
    assert channel._json["position"] == 82 and channel.position == 82
    await channel.modify(position=2160)
    assert channel._json["position"] == 2160 and channel.position == 2160


async def test_set_parent_id(channel):
    await channel.set_parent_id(82)
    assert channel._json["parent_id"] == 82 and channel.parent_id == 82
    await channel.modify(parent_id=223784)
    assert channel._json["parent_id"] == 223784 and channel.parent_id == 223784


async def test_set_nsfw(channel):
    await channel.set_nsfw(True)
    assert channel._json["nsfw"] is True and channel.nsfw is True
    await channel.modify(nsfw=False)
    assert channel._json["nsfw"] is False and channel.nsfw is False


async def test_create_thread(channel):
    assert True
