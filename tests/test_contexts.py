import interactions
from interactions.client.client import Client
from interactions.models.discord.application import Application
from interactions.models.discord.guild import Guild
from tests.consts import SAMPLE_APPLICATION_DATA, SAMPLE_CHANNEL_DATA, SAMPLE_GUILD_DATA, SAMPLE_USER_DATA
from tests.utils import generate_dummy_context

from discord_typings import UserData
import pytest


__all__ = ()


@pytest.fixture()
def owner() -> UserData:
    return SAMPLE_USER_DATA()


@pytest.fixture()
def bot(owner: UserData) -> Client:
    bot = Client()
    u = bot.cache.place_user_data(owner)
    bot._app = Application.from_dict(SAMPLE_APPLICATION_DATA(owner), bot)
    bot.owner_ids.add(u.id)
    assert bot.owner is not None
    assert bot.owner is u
    return bot


@pytest.fixture()
def guild(bot: Client) -> Guild:
    return bot.cache.place_guild_data(SAMPLE_GUILD_DATA(guild_id=1234123412341234))


@pytest.mark.asyncio
async def test_checks(bot: Client, guild: Guild) -> None:
    user_id = 121216789012345678
    assert bot.owner is not None
    assert user_id != bot.owner.id

    is_owner = interactions.is_owner()
    assert await is_owner(generate_dummy_context(user_id=bot.owner.id, client=bot)) is True
    assert await is_owner(generate_dummy_context(user_id=user_id, client=bot)) is False

    has_id = interactions.has_id(user_id)
    assert await has_id(generate_dummy_context(user_id=user_id, client=bot)) is True
    assert await has_id(generate_dummy_context(user_id=bot.owner.id, client=bot)) is False

    guild_only = interactions.guild_only()
    bot.cache.place_channel_data(SAMPLE_CHANNEL_DATA(guild_id=guild.id))
    assert await guild_only(generate_dummy_context(guild_id=guild.id, client=bot)) is True
    assert await guild_only(generate_dummy_context(dm=True)) is False

    dm_only = interactions.dm_only()
    assert await dm_only(generate_dummy_context(guild_id=guild.id, client=bot)) is False
    assert await dm_only(generate_dummy_context(dm=True)) is True
