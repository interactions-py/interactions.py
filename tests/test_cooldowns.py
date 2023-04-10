import asyncio

import pytest

from interactions import MaxConcurrency, Buckets, CooldownSystem, Cooldown
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
