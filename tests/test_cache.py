import discord_typings
import pytest

from interactions.client.client import Client
from interactions.models.discord.channel import DM, GuildText
from interactions.models.discord.snowflake import to_snowflake
from tests.consts import SAMPLE_DM_DATA, SAMPLE_GUILD_DATA, SAMPLE_USER_DATA

__all__ = ("bot", "test_dm_channel", "test_get_user_from_dm", "test_guild_channel", "test_update_guild")


@pytest.fixture()
def bot() -> Client:
    return Client()


def test_dm_channel(bot: Client) -> None:
    channel = bot.cache.place_channel_data(SAMPLE_DM_DATA())
    assert isinstance(channel, DM)
    assert channel.recipient.id == to_snowflake(SAMPLE_USER_DATA()["id"])
    channel2 = bot.cache.get_channel(channel.id)
    assert channel2 is channel


def test_get_user_from_dm(bot: Client) -> None:
    bot.cache.place_channel_data(SAMPLE_DM_DATA())
    user = bot.cache.get_user(to_snowflake(SAMPLE_USER_DATA()["id"]))
    assert user is not None
    assert user.username == SAMPLE_USER_DATA()["username"]


def test_guild_channel(bot: Client) -> None:
    bot.cache.place_guild_data(SAMPLE_GUILD_DATA())
    data: discord_typings.TextChannelData = {
        "id": "12345",
        "type": 0,
        "guild_id": SAMPLE_GUILD_DATA()["id"],
        "position": 0,
        "last_message_id": None,
        "permission_overwrites": [],
        "name": "general",
        "topic": None,
        "nsfw": False,
        "parent_id": None,
        "rate_limit_per_user": 0,
    }
    channel = bot.cache.place_channel_data(data)
    assert isinstance(channel, GuildText)
    assert channel.guild.id == to_snowflake(SAMPLE_GUILD_DATA()["id"])


def test_update_guild(bot: Client) -> None:
    guild = bot.cache.place_guild_data(SAMPLE_GUILD_DATA())
    assert guild.mfa_level == 0
    data = SAMPLE_GUILD_DATA()
    data["mfa_level"] = 1
    bot.cache.place_guild_data(data)
    assert guild.mfa_level == 1
