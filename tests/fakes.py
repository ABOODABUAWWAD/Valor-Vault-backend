"""In-memory port implementations for fast application-layer tests."""

from __future__ import annotations

from types import TracebackType
from typing import Any

from src.domain.entities.order import Order
from src.domain.entities.product import Product
from src.domain.entities.user import User
from src.domain.value_objects.location import Location


class FakeUserRepository:
    def __init__(self, users: list[User] | None = None) -> None:
        self._users = {u.username: u for u in (users or [])}

    async def find_by_username(self, username: str) -> User | None:
        return self._users.get(username)

    async def add(self, user: User) -> None:
        self._users[user.username] = user


class FakeProductRepository:
    def __init__(self, products: list[Product]) -> None:
        self._products = list(products)

    async def list(
        self,
        location: Location | None,
        search: str | None,
        offset: int,
        limit: int,
        ids: list[int] | None = None,
    ) -> tuple[list[Product], int]:
        items = self._products
        if ids is not None:
            items = [p for p in items if p.id in ids]
        if location:
            items = [p for p in items if p.location == location]
        if search:
            q = search.lower()
            items = [p for p in items if q in p.title.lower()]
        total = len(items)
        return items[offset : offset + limit], total

    async def get(self, product_id: int) -> Product | None:
        return next((p for p in self._products if p.id == product_id), None)

    async def featured(self, limit: int = 4) -> list[Product]:
        return sorted(self._products, key=lambda p: p.price, reverse=True)[:limit]

    async def upsert_many(self, products: list[Product]) -> None:
        by_id = {p.id: p for p in self._products}
        for p in products:
            by_id[p.id] = p
        self._products = list(by_id.values())


class FakeOrderRepository:
    def __init__(self) -> None:
        self.saved: list[Order] = []

    async def add(self, order: Order) -> None:
        self.saved.append(order)


class FakePasswordHasher:
    def hash(self, plain: str) -> str:
        return f"hashed::{plain}"

    def verify(self, plain: str, hashed: str) -> bool:
        return hashed == f"hashed::{plain}"


class FakeTokenService:
    def issue(self, user: User) -> str:
        return f"token-for-{user.id}"

    def verify(self, token: str) -> dict[str, Any] | None:
        if token.startswith("token-for-"):
            uid = token.removeprefix("token-for-")
            return {"sub": uid, "username": uid, "name": "Fake User"}
        return None


class FakeProductCache:
    def __init__(self) -> None:
        self.store: dict[str, str] = {}

    async def get(self, key: str) -> str | None:
        return self.store.get(key)

    async def set(self, key: str, value: str) -> None:
        self.store[key] = value


class FakeLoginThrottle:
    def __init__(self, locked: bool = False) -> None:
        self._locked = locked
        self.failures: dict[str, int] = {}
        self.reset_called: list[str] = []

    async def is_locked(self, username: str) -> bool:
        return self._locked

    async def record_failure(self, username: str) -> int:
        self.failures[username] = self.failures.get(username, 0) + 1
        return self.failures[username]

    async def reset(self, username: str) -> None:
        self.reset_called.append(username)


class FakeUnitOfWork:
    def __init__(
        self,
        users: FakeUserRepository | None = None,
        products: FakeProductRepository | None = None,
        orders: FakeOrderRepository | None = None,
    ) -> None:
        self.users = users or FakeUserRepository()
        self.products = products or FakeProductRepository([])
        self.orders = orders or FakeOrderRepository()
        self.committed = False
        self.rolled_back = False

    async def __aenter__(self) -> FakeUnitOfWork:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if exc_type is not None:
            await self.rollback()

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True
