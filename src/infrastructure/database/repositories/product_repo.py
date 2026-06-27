from __future__ import annotations

import builtins

from sqlalchemy import ColumnElement, func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.product import Product
from src.domain.value_objects.location import Location
from src.infrastructure.database.mappers import product_to_domain
from src.infrastructure.database.models import ProductModel


class SqlProductRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list(
        self,
        location: Location | None,
        search: str | None,
        offset: int,
        limit: int,
        ids: builtins.list[int] | None = None,
    ) -> tuple[builtins.list[Product], int]:
        conditions: builtins.list[ColumnElement[bool]] = []
        if ids is not None:
            conditions.append(ProductModel.id.in_(ids))
        if location:
            conditions.append(ProductModel.location == location)
        if search:
            term = search.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            conditions.append(ProductModel.title.ilike(f"%{term}%", escape="\\"))

        total = await self._session.scalar(
            select(func.count()).select_from(ProductModel).where(*conditions)
        )
        rows = await self._session.scalars(
            select(ProductModel)
            .where(*conditions)
            .order_by(ProductModel.id)
            .offset(offset)
            .limit(limit)
        )
        return [product_to_domain(r) for r in rows], int(total or 0)

    async def get(self, product_id: int) -> Product | None:
        row = await self._session.get(ProductModel, product_id)
        return product_to_domain(row) if row else None

    async def featured(self, limit: int = 4) -> builtins.list[Product]:
        rows = await self._session.scalars(
            select(ProductModel).order_by(ProductModel.price.desc()).limit(limit)
        )
        return [product_to_domain(r) for r in rows]

    async def upsert_many(self, products: builtins.list[Product]) -> None:
        if not products:
            return
        stmt = pg_insert(ProductModel).values(
            [
                {
                    "id": p.id,
                    "title": p.title,
                    "description": p.description,
                    "price": p.price,
                    "location": p.location,
                }
                for p in products
            ]
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=[ProductModel.id],
            set_={
                "title": stmt.excluded.title,
                "description": stmt.excluded.description,
                "price": stmt.excluded.price,
                "location": stmt.excluded.location,
            },
        )
        await self._session.execute(stmt)
