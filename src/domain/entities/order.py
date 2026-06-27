from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from src.domain.entities.product import Product
from src.domain.value_objects.derive import currency_for
from src.domain.value_objects.location import Location


@dataclass(frozen=True, slots=True)
class Order:
    order_id: str
    user_id: str
    product_id: int
    price: float
    currency: str
    location: Location
    status: str
    created_at: datetime

    @staticmethod
    def create(user_id: str, product: Product) -> Order:
        return Order(
            order_id=str(uuid.uuid4()),
            user_id=user_id,
            product_id=product.id,
            price=product.price,
            currency=currency_for(product.location),
            location=product.location,
            status="completed",
            created_at=datetime.now(UTC),
        )
