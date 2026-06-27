from __future__ import annotations

from typing import cast

from src.domain.entities.order import Order
from src.domain.entities.product import Product
from src.domain.entities.user import User
from src.domain.value_objects.location import Location
from src.infrastructure.database.models import OrderModel, ProductModel, UserModel


def user_to_domain(m: UserModel) -> User:
    return User(id=m.id, username=m.username, name=m.name, password_hash=m.password_hash)


def product_to_domain(m: ProductModel) -> Product:
    return Product(
        id=m.id,
        title=m.title,
        description=m.description,
        price=float(m.price),
        location=cast(Location, m.location),
    )


def product_to_model(p: Product) -> ProductModel:
    return ProductModel(
        id=p.id, title=p.title, description=p.description, price=p.price, location=p.location
    )


def order_to_model(o: Order) -> OrderModel:
    return OrderModel(
        order_id=o.order_id,
        user_id=o.user_id,
        product_id=o.product_id,
        price=o.price,
        currency=o.currency,
        location=o.location,
        status=o.status,
        created_at=o.created_at,
    )
