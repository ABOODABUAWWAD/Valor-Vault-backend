from __future__ import annotations

from types import TracebackType

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.infrastructure.database.repositories.order_repo import SqlOrderRepository
from src.infrastructure.database.repositories.product_repo import SqlProductRepository
from src.infrastructure.database.repositories.user_repo import SqlUserRepository


class SqlAlchemyUnitOfWork:
    def __init__(self, sessionmaker: async_sessionmaker[AsyncSession]) -> None:
        self._sessionmaker = sessionmaker
        self._session: AsyncSession | None = None

    async def __aenter__(self) -> SqlAlchemyUnitOfWork:
        self._session = self._sessionmaker()
        self.users = SqlUserRepository(self._session)
        self.products = SqlProductRepository(self._session)
        self.orders = SqlOrderRepository(self._session)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        assert self._session is not None
        try:
            if exc_type is not None:
                await self._session.rollback()
        finally:
            await self._session.close()
            self._session = None

    async def commit(self) -> None:
        assert self._session is not None
        await self._session.commit()

    async def rollback(self) -> None:
        assert self._session is not None
        await self._session.rollback()
