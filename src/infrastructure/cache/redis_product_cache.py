from __future__ import annotations

from redis.asyncio import Redis


class RedisProductCache:
    def __init__(self, redis: Redis, ttl_seconds: int) -> None:
        self._redis = redis
        self._ttl = ttl_seconds

    async def get(self, key: str) -> str | None:
        result = await self._redis.get(key)
        return str(result) if result is not None else None

    async def set(self, key: str, value: str) -> None:
        await self._redis.set(key, value, ex=self._ttl)
