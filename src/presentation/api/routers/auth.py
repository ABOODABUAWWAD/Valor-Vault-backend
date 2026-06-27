from __future__ import annotations

from fastapi import APIRouter, Depends

from src.application.services.auth_service import AuthService
from src.presentation.api.deps import get_auth_service
from src.presentation.api.schemas import LoginRequest, LoginResponse

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/login", response_model=LoginResponse)
async def login(
    body: LoginRequest,
    service: AuthService = Depends(get_auth_service),  # noqa: B008
) -> LoginResponse:
    result = await service.login(body.username, body.password)
    if result.is_fail():
        raise result.error
    return LoginResponse.from_view(result.value)
