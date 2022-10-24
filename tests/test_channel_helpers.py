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
