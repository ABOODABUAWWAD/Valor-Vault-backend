from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.order import Order
from src.infrastructure.database.mappers import order_to_model


class SqlOrderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, order: Order) -> None:
        self._session.add(order_to_model(order))
