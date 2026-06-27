from __future__ import annotations

import builtins
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.application.services.auth_service import AuthService
from src.application.services.order_service import OrderService
from src.application.services.product_service import ProductService
from src.domain.entities.product import Product
from src.domain.entities.user import User
from src.domain.value_objects.location import Location
from src.infrastructure.cache.redis_client import make_redis
from src.infrastructure.cache.redis_login_throttle import RedisLoginThrottle
from src.infrastructure.cache.redis_product_cache import RedisProductCache
from src.infrastructure.config.settings import Settings, get_settings
from src.infrastructure.database.engine import make_engine, make_sessionmaker
from src.infrastructure.database.repositories.product_repo import SqlProductRepository
from src.infrastructure.database.repositories.user_repo import SqlUserRepository
from src.infrastructure.database.uow import SqlAlchemyUnitOfWork
from src.infrastructure.logging.setup import configure_logging
from src.infrastructure.security.bcrypt_hasher import BcryptPasswordHasher
from src.infrastructure.security.jwt_token_service import JwtTokenService
from src.presentation.api.errors import register_error_handlers
from src.presentation.api.routers.auth import auth_router
from src.presentation.api.routers.health import health_router
from src.presentation.api.routers.orders import orders_router
from src.presentation.api.routers.products import products_router


class SqlProductRepoProvider:
    """Adapts a sessionmaker into the ProductRepository port, opening a
    short-lived session per read (product data is read-only at runtime)."""

    def __init__(self, sessionmaker: async_sessionmaker[AsyncSession]) -> None:
        self._sessionmaker = sessionmaker

    async def list(
        self,
        location: Location | None,
        search: str | None,
        offset: int,
        limit: int,
        ids: builtins.list[int] | None = None,
    ) -> tuple[builtins.list[Product], int]:
        async with self._sessionmaker() as session:
            return await SqlProductRepository(session).list(location, search, offset, limit, ids)

    async def get(self, product_id: int) -> Product | None:
        async with self._sessionmaker() as session:
            return await SqlProductRepository(session).get(product_id)

    async def featured(self, limit: int = 4) -> builtins.list[Product]:
        async with self._sessionmaker() as session:
            return await SqlProductRepository(session).featured(limit)

    async def upsert_many(self, products: builtins.list[Product]) -> None:  # pragma: no cover
        raise NotImplementedError


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        engine = make_engine(settings.database_url)
        sm = make_sessionmaker(engine)
        redis = make_redis(settings.redis_url)

        hasher = BcryptPasswordHasher(rounds=settings.bcrypt_rounds)
        tokens = JwtTokenService(settings.jwt_secret, settings.jwt_ttl_seconds)
        cache = RedisProductCache(redis, settings.product_cache_ttl_seconds)
        throttle = RedisLoginThrottle(
            redis, settings.lockout_max_failures, settings.lockout_window_seconds
        )

        # AuthService needs a user repo bound to a live session for reads.
        # Reads are short-lived; open a session per login inside a tiny adapter.
        class _UserRepoProvider:
            async def find_by_username(self, username: str) -> User | None:
                async with sm() as session:
                    return await SqlUserRepository(session).find_by_username(username)

            async def add(self, user: User) -> None:  # pragma: no cover - unused at runtime
                raise NotImplementedError

        app.state.settings = settings
        app.state.engine = engine
        app.state.sessionmaker = sm
        app.state.redis = redis
        app.state.token_service = tokens
        app.state.auth_service = AuthService(_UserRepoProvider(), hasher, tokens, throttle)
        app.state.product_service = ProductService(SqlProductRepoProvider(sm), cache)
        app.state.order_service = OrderService(lambda: SqlAlchemyUnitOfWork(sm))  # type: ignore[arg-type, return-value]
        try:
            yield
        finally:
            await redis.aclose()
            await engine.dispose()

    app = FastAPI(title="Valor Vault API", version="0.1.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_error_handlers(app)
    app.include_router(auth_router)
    app.include_router(products_router)
    app.include_router(orders_router)
    app.include_router(health_router)
    return app
