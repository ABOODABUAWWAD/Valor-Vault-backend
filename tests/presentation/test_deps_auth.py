import pytest
from fastapi import Depends, FastAPI
from httpx import ASGITransport, AsyncClient
from src.domain.entities.user import User
from src.infrastructure.security.jwt_token_service import JwtTokenService
from src.presentation.api.deps import CurrentUser, get_current_user
from src.presentation.api.errors import register_error_handlers


def _app() -> tuple[FastAPI, JwtTokenService]:
    app = FastAPI()
    register_error_handlers(app)
    tokens = JwtTokenService(secret="s" * 32, ttl_seconds=3600)
    app.state.token_service = tokens

    @app.get("/whoami")
    async def whoami(user: CurrentUser = Depends(get_current_user)) -> dict[str, str]:  # noqa: B008
        return {"id": user.id, "username": user.username}

    return app, tokens


@pytest.mark.asyncio
async def test_valid_token_authenticates():
    app, tokens = _app()
    token = tokens.issue(User(id="u1", username="demo", name="Demo", password_hash="x"))
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://t") as client:
        res = await client.get("/whoami", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json() == {"id": "u1", "username": "demo"}


@pytest.mark.asyncio
async def test_missing_token_is_401_nested():
    app, _ = _app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://t") as client:
        res = await client.get("/whoami")
    assert res.status_code == 401
    assert res.json()["error"]["code"] == "unauthorized"
