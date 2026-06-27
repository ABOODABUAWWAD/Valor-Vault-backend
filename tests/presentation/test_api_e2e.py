"""End-to-end API tests against the real app with fake adapters injected,
so they run fast without Docker. Verifies the exact wire contract."""

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from src.application.services.auth_service import AuthService
from src.application.services.order_service import OrderService
from src.application.services.product_service import ProductService
from src.domain.entities.product import Product
from src.domain.entities.user import User
from src.infrastructure.security.bcrypt_hasher import BcryptPasswordHasher
from src.infrastructure.security.jwt_token_service import JwtTokenService
from src.presentation.api.errors import register_error_handlers
from src.presentation.api.routers.auth import auth_router
from src.presentation.api.routers.orders import orders_router
from src.presentation.api.routers.products import products_router

from tests.fakes import (
    FakeLoginThrottle,
    FakeOrderRepository,
    FakeProductCache,
    FakeProductRepository,
    FakeUnitOfWork,
    FakeUserRepository,
)

PRODUCTS = [
    Product(id=i, title=f"Sword {i}", description="d", price=float(i * 10), location="JO")
    for i in range(1, 26)
] + [Product(id=99, title="Saudi Shield", description="d", price=120.0, location="SA")]


@pytest.fixture
def app() -> FastAPI:
    hasher = BcryptPasswordHasher(rounds=4)
    tokens = JwtTokenService(secret="s" * 32, ttl_seconds=3600)
    users = FakeUserRepository(
        [
            User(
                id="u1",
                username="demo",
                name="Demo Adventurer",
                password_hash=hasher.hash("demo123"),
            )
        ]
    )
    products = FakeProductRepository(PRODUCTS)

    app = FastAPI()
    register_error_handlers(app)
    app.state.token_service = tokens
    app.state.auth_service = AuthService(users, hasher, tokens, FakeLoginThrottle())
    app.state.product_service = ProductService(products, FakeProductCache())
    app.state.order_service = OrderService(
        lambda: FakeUnitOfWork(products=products, orders=FakeOrderRepository())
    )
    app.include_router(auth_router)
    app.include_router(products_router)
    app.include_router(orders_router)
    return app


async def _token(client: AsyncClient) -> str:
    res = await client.post("/auth/login", json={"username": "demo", "password": "demo123"})
    return res.json()["token"]


@pytest.fixture
async def client(app: FastAPI):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://t") as c:
        yield c


async def test_login_success(client):
    res = await client.post("/auth/login", json={"username": "demo", "password": "demo123"})
    assert res.status_code == 200
    body = res.json()
    assert body["user"] == {"id": "u1", "username": "demo", "name": "Demo Adventurer"}
    assert isinstance(body["token"], str)


async def test_login_bad_credentials(client):
    res = await client.post("/auth/login", json={"username": "demo", "password": "nope"})
    assert res.status_code == 401
    assert res.json()["error"]["code"] == "invalid_credentials"


async def test_products_requires_auth(client):
    res = await client.get("/products")
    assert res.status_code == 401
    assert res.json()["error"]["code"] == "unauthorized"


async def test_products_pagination_envelope(client):
    token = await _token(client)
    res = await client.get(
        "/products?page=2&page_size=12", headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200
    body = res.json()
    assert set(body) == {"items", "page", "page_size", "total", "total_pages"}
    assert body["page"] == 2 and body["page_size"] == 12 and body["total"] == 26
    assert body["total_pages"] == 3 and len(body["items"]) == 12
    assert set(body["items"][0]) == {
        "id",
        "title",
        "description",
        "price",
        "location",
        "currency",
        "rarity",
        "icon",
    }


async def test_products_location_filter(client):
    token = await _token(client)
    res = await client.get("/products?location=SA", headers={"Authorization": f"Bearer {token}"})
    assert res.json()["total"] == 1
    assert res.json()["items"][0]["id"] == 99


async def test_product_detail_and_404(client):
    token = await _token(client)
    headers = {"Authorization": f"Bearer {token}"}
    ok = await client.get("/products/99", headers=headers)
    assert ok.status_code == 200 and ok.json()["currency"] == "SAR"
    missing = await client.get("/products/123456", headers=headers)
    assert missing.status_code == 404 and missing.json()["error"]["code"] == "not_found"


async def test_buy_creates_order(client):
    token = await _token(client)
    headers = {"Authorization": f"Bearer {token}"}
    res = await client.post("/orders", json={"product_id": 1}, headers=headers)
    assert res.status_code == 201
    body = res.json()
    assert set(body) == {
        "order_id",
        "product",
        "price",
        "currency",
        "location",
        "status",
        "created_at",
    }
    assert body["status"] == "completed" and body["product"]["id"] == 1


async def test_buy_unknown_product_404(client):
    token = await _token(client)
    res = await client.post(
        "/orders", json={"product_id": 999}, headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 404 and res.json()["error"]["code"] == "not_found"
