from __future__ import annotations

from fastapi import APIRouter, Request
from sqlalchemy import text

health_router = APIRouter(tags=["health"])


@health_router.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@health_router.get("/readyz")
async def readyz(request: Request) -> dict[str, str]:
    engine = request.app.state.engine
    redis = request.app.state.redis
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
    await redis.ping()
    return {"status": "ready"}
