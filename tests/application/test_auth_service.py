from src.application.services.auth_service import AuthService
from src.domain.entities.user import User

from tests.fakes import (
    FakeLoginThrottle,
    FakePasswordHasher,
    FakeTokenService,
    FakeUserRepository,
)


def _service(locked: bool = False, with_user: bool = True) -> tuple[AuthService, FakeLoginThrottle]:
    hasher = FakePasswordHasher()
    users = FakeUserRepository(
        [
            User(
                id="u1",
                username="demo",
                name="Demo Adventurer",
                password_hash=hasher.hash("demo123"),
            )
        ]
        if with_user
        else []
    )
    throttle = FakeLoginThrottle(locked=locked)
    return AuthService(users, hasher, FakeTokenService(), throttle), throttle


async def test_login_success_returns_authview_and_resets_throttle():
    svc, throttle = _service()
    r = await svc.login("demo", "demo123")
    assert r.is_ok()
    assert r.value.token == "token-for-u1"
    assert (r.value.user_id, r.value.username, r.value.name) == ("u1", "demo", "Demo Adventurer")
    assert throttle.reset_called == ["demo"]


async def test_login_bad_password_records_failure():
    svc, throttle = _service()
    r = await svc.login("demo", "wrong")
    assert r.is_fail()
    assert r.error.code == "invalid_credentials"
    assert throttle.failures["demo"] == 1


async def test_login_unknown_user_is_invalid_credentials():
    svc, _ = _service(with_user=False)
    r = await svc.login("ghost", "x")
    assert r.is_fail()
    assert r.error.code == "invalid_credentials"


async def test_login_locked_short_circuits():
    svc, throttle = _service(locked=True)
    r = await svc.login("demo", "demo123")
    assert r.is_fail()
    assert r.error.code == "too_many_attempts"
    assert "demo" not in throttle.failures  # no bcrypt work, no failure recorded
