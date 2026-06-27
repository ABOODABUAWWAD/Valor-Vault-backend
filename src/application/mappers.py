from __future__ import annotations

from src.application.dtos import OrderView, ProductView
from src.domain.entities.order import Order
from src.domain.entities.product import Product
from src.domain.value_objects.derive import currency_for, icon_for, rarity_for


def to_product_view(p: Product) -> ProductView:
    return ProductView(
        id=p.id,
        title=p.title,
        description=p.description,
        price=p.price,
        location=p.location,
        currency=currency_for(p.location),
        rarity=rarity_for(p.price),
        icon=icon_for(p.title),
    )


def to_order_view(o: Order, p: Product) -> OrderView:
    return OrderView(
        order_id=o.order_id,
        product=to_product_view(p),
        price=o.price,
        currency=o.currency,
        location=o.location,
        status=o.status,
        created_at=o.created_at.isoformat(),
    )
