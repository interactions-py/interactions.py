import asyncio

import pytest
from multidict import CIMultiDict, CIMultiDictProxy

from interactions.api.http.http_client import BucketLock

__all__ = ()


def make_header(limit: int = 5) -> CIMultiDictProxy:
    return CIMultiDictProxy(
        CIMultiDict(
            {
                "x-ratelimit-bucket": "bucket",
                "x-ratelimit-limit": str(limit),
                "x-ratelimit-remaining": str(limit - 1),
                "x-ratelimit-reset-after": "1.0",
            }
        )
    )


@pytest.mark.asyncio
async def test_bucket_lock_does_not_strand_queued_requests() -> None:
    """A request queued on a full bucket must run once a slot is released, even though responses were ingested."""
    limit = 5
    lock = BucketLock(make_header(limit))

    async def request(index: int) -> None:
        # same shape as HTTPClient.request: hold the bucket, make the call, ingest the response headers
        async with lock:
            await asyncio.sleep(0.01 + index * 0.005)
            lock.ingest_ratelimit_header(make_header(limit))

    tasks = [asyncio.create_task(request(i)) for i in range(limit * 3)]
    _, pending = await asyncio.wait(tasks, timeout=5)

    for task in pending:
        task.cancel()
    assert not pending, f"{len(pending)} of {len(tasks)} requests never acquired the bucket"


@pytest.mark.asyncio
async def test_bucket_lock_resizes_when_limit_changes() -> None:
    lock = BucketLock(make_header(5))

    lock.ingest_ratelimit_header(make_header(3))

    assert lock.limit == 3
    assert lock._semaphore is not None
    assert lock._semaphore._value == 3
