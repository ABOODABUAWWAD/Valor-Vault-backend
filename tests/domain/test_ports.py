from src.domain.ports.cache import ProductCache
from src.domain.ports.repositories import ProductRepository
from src.domain.ports.security import PasswordHasher, TokenService

from tests.fakes import (
    FakePasswordHasher,
    FakeProductCache,
    FakeProductRepository,
    FakeTokenService,
)


def test_fakes_satisfy_protocols():
    assert isinstance(FakeProductRepository([]), ProductRepository)
    assert isinstance(FakeProductCache(), ProductCache)
    assert isinstance(FakePasswordHasher(), PasswordHasher)
    assert isinstance(FakeTokenService(), TokenService)
