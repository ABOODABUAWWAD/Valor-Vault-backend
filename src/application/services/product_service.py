from __future__ import annotations

import json
from dataclasses import asdict

from src.application.dtos import ProductView
from src.application.mappers import to_product_view
from src.domain.ports.cache import ProductCache
from src.domain.ports.repositories import ProductRepository
from src.domain.shared.exceptions import NotFoundError
from src.domain.shared.pagination import Page
from src.domain.shared.result import Result
from src.domain.value_objects.location import Location

_MAX_PAGE_SIZE = 100


class ProductService:
    def __init__(self, products: ProductRepository, cache: ProductCache) -> None:
        self._products = products
        self._cache = cache

    async def list_products(
        self,
        page: int,
        page_size: int,
        location: Location | None,
        search: str | None,
        ids: list[int] | None = None,
    ) -> Page[ProductView]:
        page = max(1, page)
        page_size = min(max(1, page_size), _MAX_PAGE_SIZE)
        offset = (page - 1) * page_size
        key = self._key(page, page_size, location, search, ids)

        cached = await self._cache.get(key)
        if cached is not None:
            return self._deserialize(cached)

        items, total = await self._products.list(location, search, offset, page_size, ids)
        views = [to_product_view(p) for p in items]
        result = Page(items=views, page=page, page_size=page_size, total=total)
        await self._cache.set(key, self._serialize(result))
        return result

    async def featured_products(self, limit: int = 4) -> list[ProductView]:
        key = f"products:featured:{limit}"
        cached = await self._cache.get(key)
        if cached is not None:
            return [ProductView(**v) for v in json.loads(cached)]
        products = await self._products.featured(limit)
        views = [to_product_view(p) for p in products]
        await self._cache.set(key, json.dumps([asdict(v) for v in views]))
        return views

    async def get_product(self, product_id: int) -> Result[ProductView]:
        product = await self._products.get(product_id)
        if product is None:
            return Result.fail(NotFoundError(f"Product {product_id} not found"))
        return Result.ok(to_product_view(product))

    @staticmethod
    def _key(
        page: int,
        size: int,
        loc: Location | None,
        search: str | None,
        ids: list[int] | None,
    ) -> str:
        ids_part = ",".join(str(i) for i in sorted(ids)) if ids else ""
        q_part = (search or "").lower()
        return f"products:p={page}:s={size}:loc={loc or ''}:q={q_part}:ids={ids_part}"

    @staticmethod
    def _serialize(page: Page[ProductView]) -> str:
        return json.dumps(
            {
                "items": [asdict(v) for v in page.items],
                "page": page.page,
                "page_size": page.page_size,
                "total": page.total,
            }
        )

    @staticmethod
    def _deserialize(raw: str) -> Page[ProductView]:
        data = json.loads(raw)
        return Page(
            items=[ProductView(**v) for v in data["items"]],
            page=data["page"],
            page_size=data["page_size"],
            total=data["total"],
        )
