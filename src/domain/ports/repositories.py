from __future__ import annotations

import builtins
from typing import Protocol, runtime_checkable

from src.domain.entities.order import Order
from src.domain.entities.product import Product
from src.domain.entities.user import User
from src.domain.value_objects.location import Location


@runtime_checkable
class UserRepository(Protocol):
    async def find_by_username(self, username: str) -> User | None: ...
    async def add(self, user: User) -> None: ...


@runtime_checkable
class ProductRepository(Protocol):
    async def list(
        self,
        location: Location | None,
        search: str | None,
        offset: int,
        limit: int,
        ids: builtins.list[int] | None = None,
    ) -> tuple[builtins.list[Product], int]: ...
    async def get(self, product_id: int) -> Product | None: ...
    async def upsert_many(self, products: builtins.list[Product]) -> None: ...
    async def featured(self, limit: int = 4) -> builtins.list[Product]: ...


@runtime_checkable
class OrderRepository(Protocol):
    async def add(self, order: Order) -> None: ...
