from __future__ import annotations

from redis.asyncio import Redis


class RedisLoginThrottle:
    def __init__(self, redis: Redis, max_failures: int, window_seconds: int) -> None:
        self._redis = redis
        self._max = max_failures
        self._window = window_seconds

    def _key(self, username: str) -> str:
        return f"login:fail:{username}"

    async def is_locked(self, username: str) -> bool:
        raw = await self._redis.get(self._key(username))
        return raw is not None and int(raw) >= self._max

    async def record_failure(self, username: str) -> int:
        key = self._key(username)
        # MULTI/EXEC: INCR + EXPIRE NX are atomic — eliminates the race where
        # a crash between INCR and EXPIRE leaves the key with no TTL (permanent lockout).
        async with self._redis.pipeline(transaction=True) as pipe:
            pipe.incr(key)
            pipe.expire(key, self._window, nx=True)
            results = await pipe.execute()
        return int(results[0])

    async def reset(self, username: str) -> None:
        await self._redis.delete(self._key(username))
