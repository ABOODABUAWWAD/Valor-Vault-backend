import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from src.domain.shared.exceptions import NotFoundError
from src.presentation.api.errors import STATUS_BY_CODE, register_error_handlers


def _app() -> FastAPI:
    app = FastAPI()
    register_error_handlers(app)

    @app.get("/boom")
    async def boom():
        raise NotFoundError("Product 5 not found")

    return app


@pytest.mark.asyncio
async def test_domain_error_becomes_nested_envelope():
    transport = ASGITransport(app=_app())
    async with AsyncClient(transport=transport, base_url="http://t") as client:
        res = await client.get("/boom")
    assert res.status_code == 404
    assert res.json() == {"error": {"code": "not_found", "message": "Product 5 not found"}}


@pytest.mark.asyncio
async def test_unhandled_exception_becomes_internal_envelope():
    app = FastAPI()
    register_error_handlers(app)

    @app.get("/kaboom")
    async def kaboom():
        raise RuntimeError("secret internal detail")

    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://t") as client:
        res = await client.get("/kaboom")
    assert res.status_code == 500
    assert res.json() == {"error": {"code": "internal", "message": "Internal server error"}}
    # the leaked detail must NOT appear
    assert "secret internal detail" not in res.text


def test_status_map_covers_codes():
    for code in (
        "invalid_credentials",
        "not_found",
        "validation",
        "too_many_attempts",
        "unauthorized",
    ):
        assert code in STATUS_BY_CODE
