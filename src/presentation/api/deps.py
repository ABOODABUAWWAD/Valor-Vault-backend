from __future__ import annotations

from dataclasses import dataclass

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.application.services.auth_service import AuthService
from src.application.services.order_service import OrderService
from src.application.services.product_service import ProductService
from src.domain.ports.security import TokenService
from src.domain.shared.exceptions import UnauthenticatedError

_bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True, slots=True)
class CurrentUser:
    id: str
    username: str
    name: str


def get_token_service(request: Request) -> TokenService:
    return request.app.state.token_service  # type: ignore[no-any-return]


def get_auth_service(request: Request) -> AuthService:
    return request.app.state.auth_service  # type: ignore[no-any-return]


def get_product_service(request: Request) -> ProductService:
    return request.app.state.product_service  # type: ignore[no-any-return]


def get_order_service(request: Request) -> OrderService:
    return request.app.state.order_service  # type: ignore[no-any-return]


def get_current_user(
    tokens: TokenService = Depends(get_token_service),  # noqa: B008
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),  # noqa: B008
) -> CurrentUser:
    if credentials is None:
        raise UnauthenticatedError("Authentication required")
    claims = tokens.verify(credentials.credentials)
    if claims is None:
        raise UnauthenticatedError("Authentication required")
    return CurrentUser(id=claims["sub"], username=claims["username"], name=claims["name"])
