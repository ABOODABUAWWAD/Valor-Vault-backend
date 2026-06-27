from __future__ import annotations

import pytest
import pytest_asyncio
from redis.asyncio import Redis
from src.infrastructure.cache.redis_login_throttle import RedisLoginThrottle
from src.infrastructure.cache.redis_product_cache import RedisProductCache

pytestmark = pytest.mark.integration


@pytest_asyncio.fixture
async def redis(redis_url: str) -> Redis:  # type: ignore[misc]
    client = Redis.from_url(redis_url, decode_responses=True)
    await client.flushdb()
    yield client  # type: ignore[misc]
    await client.aclose()


@pytest.mark.asyncio
async def test_product_cache_set_get(redis: Redis) -> None:
    cache = RedisProductCache(redis, ttl_seconds=60)
    assert await cache.get("k") is None
    await cache.set("k", '{"x":1}')
    assert await cache.get("k") == '{"x":1}'


@pytest.mark.asyncio
async def test_login_throttle_locks_after_max(redis: Redis) -> None:
    throttle = RedisLoginThrottle(redis, max_failures=3, window_seconds=60)
    assert await throttle.is_locked("demo") is False
    await throttle.record_failure("demo")
    await throttle.record_failure("demo")
    assert await throttle.is_locked("demo") is False
    n = await throttle.record_failure("demo")
    assert n == 3
    assert await throttle.is_locked("demo") is True
    await throttle.reset("demo")
    assert await throttle.is_locked("demo") is False
