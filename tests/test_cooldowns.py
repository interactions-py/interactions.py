import asyncio

import pytest

from interactions import Client, MaxConcurrency, Buckets, CooldownSystem, Cooldown
from tests.consts import SAMPLE_CHANNEL_DATA
from tests.utils import generate_dummy_context

__all__ = ()


@pytest.mark.asyncio
async def test_cooldowns() -> None:
    user_id = 903968203779215401
    context = generate_dummy_context(user_id=user_id)
    rate = 2

    cooldown = Cooldown(Buckets.USER, 1, rate)

    # test cooldown locks
    assert await cooldown.get_cooldown(context) is not None
    assert await cooldown.on_cooldown(context) is False
    assert await cooldown.acquire_token(context) is True
    assert await cooldown.acquire_token(context) is False
    assert await cooldown.on_cooldown(context) is True

    # test cooldown unlock
    await asyncio.sleep(rate)
    assert await cooldown.get_cooldown_time(context) == 0
    assert await cooldown.on_cooldown(context) is False
    assert await cooldown.acquire_token(context) is True

    assert isinstance(await cooldown.get_cooldown(context), CooldownSystem)

    # test cooldown time
    await cooldown.acquire_token(context)
    assert await cooldown.get_cooldown_time(context) >= 0

    # test reset
    await cooldown.acquire_token(context)
    assert await cooldown.on_cooldown(context) is True
    await cooldown.reset(context)
    assert await cooldown.on_cooldown(context) is False
    await cooldown.acquire_token(context)
    assert await cooldown.on_cooldown(context) is True
    await cooldown.reset_all()
    assert await cooldown.on_cooldown(context) is False


@pytest.mark.asyncio
async def test_max_concurrency() -> None:
    user_id = 903968203779215401
    context = generate_dummy_context(user_id=user_id)
    concurrent = 1

    max_conc = MaxConcurrency(concurrent, Buckets.USER, False)

    assert isinstance(await max_conc.get_semaphore(context), asyncio.Semaphore)

    assert await max_conc.acquire(context) is True
    assert await max_conc.acquire(context) is False
    await max_conc.release(context)
    assert await max_conc.acquire(context) is True
    await max_conc.release(context)


@pytest.mark.asyncio
async def test_buckets() -> None:
    context = generate_dummy_context()
    _ = (await bucket.get_key(context) for bucket in Buckets)


@pytest.mark.asyncio
async def test_category_bucket() -> None:
    client = Client()
    guild_id = "123456789012345670"
    channel_id = "123456789012345671"
    category_id = "123456789012345672"

    channel_data = SAMPLE_CHANNEL_DATA(channel_id=channel_id, guild_id=guild_id)
    channel_data["parent_id"] = category_id
    client.cache.place_channel_data(channel_data)

    # guild channel in a category -> keyed by the category
    context = generate_dummy_context(channel_id=channel_id, guild_id=guild_id, client=client)
    assert await Buckets.CATEGORY.get_key(context) == int(category_id)

    # thread in that channel -> keyed by the parent channel's category
    thread_id = "123456789012345674"
    thread_data = SAMPLE_CHANNEL_DATA(channel_id=thread_id, guild_id=guild_id)
    thread_data["type"] = 11
    thread_data["parent_id"] = channel_id
    client.cache.place_channel_data(thread_data)
    context = generate_dummy_context(channel_id=thread_id, guild_id=guild_id, client=client)
    assert await Buckets.CATEGORY.get_key(context) == int(category_id)

    # guild channel without a category -> keyed by the channel itself
    other_channel_id = "123456789012345673"
    client.cache.place_channel_data(SAMPLE_CHANNEL_DATA(channel_id=other_channel_id, guild_id=guild_id))
    context = generate_dummy_context(channel_id=other_channel_id, guild_id=guild_id, client=client)
    assert await Buckets.CATEGORY.get_key(context) == int(other_channel_id)

    # DMs have no category -> keyed by the channel
    context = generate_dummy_context(dm=True)
    assert await Buckets.CATEGORY.get_key(context) == context.channel.id
