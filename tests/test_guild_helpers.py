#  import pytest

import interactions


async def test_guild_in_cache(fake_client, guild):
    assert fake_client._http.cache[interactions.Guild][guild.id]._json == dict(
        id="987654321",
        verification_level=0,
        default_message_notifications=0,
        explicit_content_filter=0,
        roles=[],
        emojis=[],
        mfa_level=0,
        channels=[
            {
                "id": "123456789",
                "_guild_id": "987654321",
                "position": 2160,
                "permission_overwrites": [],
                "name": "nya~",
                "topic": "nya~",
                "nsfw": False,
                "rate_limit_per_user": 2160,
                "parent_id": "223784",
                "available_tags": [],
            },
            {"id": "777", "permission_overwrites": [], "name": "", "type": 2},
        ],
        premium_tier=0,
        nsfw_level=0,
    )


def test_get_voice_state(fake_client, guild):
    assert [v._json for v in guild.voice_states] == [
        {"channel_id": "123456789", "user_id": "77", "guild_id": "987654321"},
        {"channel_id": "123456789", "user_id": "88", "guild_id": "987654321"},
        {"channel_id": "777", "user_id": "111", "guild_id": "987654321"},
    ]
    assert {k: [v._json for v in states] for k, states in guild.mapped_voice_states.items()} == {
        123456789: [
            {"channel_id": "123456789", "guild_id": "987654321", "user_id": "77"},
            {"channel_id": "123456789", "guild_id": "987654321", "user_id": "88"},
        ],
        777: [{"channel_id": "777", "guild_id": "987654321", "user_id": "111"}],
    }

    assert [v._json for v in guild.channels[1].voice_states] == [
        {"channel_id": "777", "guild_id": "987654321", "user_id": "111"}
    ]
