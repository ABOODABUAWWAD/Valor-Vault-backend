import pytest


@pytest.fixture(autouse=True)
def _base_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Minimal env so get_settings() constructs in unit tests."""
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://t:t@localhost:5432/t")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("JWT_SECRET", "x" * 32)
