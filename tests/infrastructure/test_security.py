from src.domain.entities.user import User
from src.infrastructure.security.bcrypt_hasher import BcryptPasswordHasher
from src.infrastructure.security.jwt_token_service import JwtTokenService


def test_bcrypt_hash_and_verify():
    hasher = BcryptPasswordHasher(rounds=4)  # low rounds = fast test
    h = hasher.hash("demo123")
    assert h != "demo123"
    assert hasher.verify("demo123", h) is True
    assert hasher.verify("wrong", h) is False


def test_jwt_roundtrip_and_claims():
    svc = JwtTokenService(secret="s" * 32, ttl_seconds=3600)
    user = User(id="u1", username="demo", name="Demo Adventurer", password_hash="x")
    token = svc.issue(user)
    claims = svc.verify(token)
    assert claims is not None
    assert claims["sub"] == "u1"
    assert claims["username"] == "demo"
    assert claims["name"] == "Demo Adventurer"


def test_jwt_rejects_tampered_and_expired():
    svc = JwtTokenService(secret="s" * 32, ttl_seconds=1)
    assert svc.verify("not.a.jwt") is None
    assert svc.verify("") is None
    user = User(id="u1", username="demo", name="Demo", password_hash="x")
    expired = JwtTokenService(secret="s" * 32, ttl_seconds=-1).issue(user)
    assert svc.verify(expired) is None
    # wrong secret
    other = JwtTokenService(secret="d" * 32, ttl_seconds=3600)
    assert svc.verify(other.issue(user)) is None
