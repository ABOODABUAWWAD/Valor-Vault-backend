from __future__ import annotations

from types import TracebackType
from typing import Protocol

from src.domain.ports.repositories import (
    OrderRepository,
    ProductRepository,
    UserRepository,
)


class UnitOfWork(Protocol):
    users: UserRepository
    products: ProductRepository
    orders: OrderRepository

    async def __aenter__(self) -> UnitOfWork: ...
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None: ...
    async def commit(self) -> None: ...
    async def rollback(self) -> None: ...
