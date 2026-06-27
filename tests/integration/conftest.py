"""Integration fixtures — ephemeral Postgres/Redis via testcontainers.

Skips automatically when Docker is unavailable so the unit suite still runs.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncEngine
from src.infrastructure.database.engine import make_engine, make_sessionmaker
from src.infrastructure.database.models import Base

try:
    from testcontainers.postgres import PostgresContainer
    from testcontainers.redis import RedisContainer

    _HAS_DOCKER = True
except Exception:  # pragma: no cover
    _HAS_DOCKER = False


@pytest.fixture(scope="session")
def pg_url() -> Iterator[str]:
    if not _HAS_DOCKER:
        pytest.skip("Docker/testcontainers unavailable")
    with PostgresContainer("postgres:16-alpine", driver="asyncpg") as pg:
        yield pg.get_connection_url()


@pytest.fixture(scope="session")
def redis_url() -> Iterator[str]:
    if not _HAS_DOCKER:
        pytest.skip("Docker/testcontainers unavailable")
    with RedisContainer("redis:7-alpine") as r:
        host = r.get_container_host_ip()
        port = r.get_exposed_port(6379)
        yield f"redis://{host}:{port}/0"


@pytest_asyncio.fixture
async def engine(pg_url: str) -> AsyncIterator[AsyncEngine]:
    eng = make_engine(pg_url)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await eng.dispose()


@pytest_asyncio.fixture
async def sessionmaker(engine: AsyncEngine):  # type: ignore[return]
    return make_sessionmaker(engine)
