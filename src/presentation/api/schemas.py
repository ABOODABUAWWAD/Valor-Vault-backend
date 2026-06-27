from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from src.application.dtos import AuthView, OrderView, ProductView
from src.domain.shared.pagination import Page


class LoginRequest(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: str
    username: str
    name: str


class LoginResponse(BaseModel):
    token: str
    user: UserOut

    @classmethod
    def from_view(cls, v: AuthView) -> LoginResponse:
        return cls(token=v.token, user=UserOut(id=v.user_id, username=v.username, name=v.name))


class ProductOut(BaseModel):
    id: int
    title: str
    description: str
    price: float
    location: Literal["JO", "SA"]
    currency: str
    rarity: str
    icon: str

    @classmethod
    def from_view(cls, v: ProductView) -> ProductOut:
        return cls(
            id=v.id,
            title=v.title,
            description=v.description,
            price=v.price,
            location=v.location,
            currency=v.currency,
            rarity=v.rarity,
            icon=v.icon,
        )


class PaginatedProducts(BaseModel):
    items: list[ProductOut]
    page: int
    page_size: int
    total: int
    total_pages: int

    @classmethod
    def from_page(cls, page: Page[ProductView]) -> PaginatedProducts:
        return cls(
            items=[ProductOut.from_view(v) for v in page.items],
            page=page.page,
            page_size=page.page_size,
            total=page.total,
            total_pages=page.total_pages,
        )


class OrderRequest(BaseModel):
    product_id: int


class OrderOut(BaseModel):
    order_id: str
    product: ProductOut
    price: float
    currency: str
    location: Literal["JO", "SA"]
    status: str
    created_at: str

    @classmethod
    def from_view(cls, v: OrderView) -> OrderOut:
        return cls(
            order_id=v.order_id,
            product=ProductOut.from_view(v.product),
            price=v.price,
            currency=v.currency,
            location=v.location,
            status=v.status,
            created_at=v.created_at,
        )
