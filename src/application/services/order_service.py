from __future__ import annotations

from collections.abc import Callable

from src.application.dtos import OrderView
from src.application.mappers import to_order_view
from src.domain.entities.order import Order
from src.domain.ports.unit_of_work import UnitOfWork
from src.domain.shared.exceptions import NotFoundError
from src.domain.shared.result import Result


class OrderService:
    def __init__(self, uow_factory: Callable[[], UnitOfWork]) -> None:
        self._uow_factory = uow_factory

    async def buy(self, user_id: str, product_id: int) -> Result[OrderView]:
        async with self._uow_factory() as uow:
            product = await uow.products.get(product_id)
            if product is None:
                return Result.fail(NotFoundError(f"Product {product_id} not found"))
            order = Order.create(user_id=user_id, product=product)
            await uow.orders.add(order)
            await uow.commit()
            return Result.ok(to_order_view(order, product))
