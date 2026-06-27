from __future__ import annotations

from fastapi import APIRouter, Depends

from src.application.services.order_service import OrderService
from src.presentation.api.deps import CurrentUser, get_current_user, get_order_service
from src.presentation.api.schemas import OrderOut, OrderRequest

orders_router = APIRouter(prefix="/orders", tags=["orders"])


@orders_router.post("", response_model=OrderOut, status_code=201)
async def create_order(
    body: OrderRequest,
    user: CurrentUser = Depends(get_current_user),  # noqa: B008
    service: OrderService = Depends(get_order_service),  # noqa: B008
) -> OrderOut:
    result = await service.buy(user.id, body.product_id)
    if result.is_fail():
        raise result.error
    return OrderOut.from_view(result.value)
