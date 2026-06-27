from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, Query

from src.application.services.product_service import ProductService
from src.presentation.api.deps import CurrentUser, get_current_user, get_product_service
from src.presentation.api.schemas import PaginatedProducts, ProductOut

products_router = APIRouter(prefix="/products", tags=["products"])


@products_router.get("", response_model=PaginatedProducts)
async def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=100),
    location: Literal["JO", "SA"] | None = Query(None),
    search: str | None = Query(None),
    ids: list[int] = Query(default=[]),  # noqa: B008
    _: CurrentUser = Depends(get_current_user),  # noqa: B008
    service: ProductService = Depends(get_product_service),  # noqa: B008
) -> PaginatedProducts:
    page_result = await service.list_products(
        page, page_size, location, search, ids or None
    )
    return PaginatedProducts.from_page(page_result)


@products_router.get("/featured", response_model=list[ProductOut])
async def featured_products(
    service: ProductService = Depends(get_product_service),  # noqa: B008
) -> list[ProductOut]:
    """Public endpoint — no auth required. Returns top products by price."""
    products = await service.featured_products()
    return [ProductOut.from_view(p) for p in products]


@products_router.get("/{product_id}", response_model=ProductOut)
async def get_product(
    product_id: int,
    _: CurrentUser = Depends(get_current_user),  # noqa: B008
    service: ProductService = Depends(get_product_service),  # noqa: B008
) -> ProductOut:
    result = await service.get_product(product_id)
    if result.is_fail():
        raise result.error
    return ProductOut.from_view(result.value)
