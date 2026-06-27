from __future__ import annotations

from dataclasses import dataclass

from src.domain.value_objects.location import Location


@dataclass(frozen=True, slots=True)
class ProductView:
    id: int
    title: str
    description: str
    price: float
    location: Location
    currency: str
    rarity: str
    icon: str


@dataclass(frozen=True, slots=True)
class OrderView:
    order_id: str
    product: ProductView
    price: float
    currency: str
    location: Location
    status: str
    created_at: str


@dataclass(frozen=True, slots=True)
class AuthView:
    token: str
    user_id: str
    username: str
    name: str
