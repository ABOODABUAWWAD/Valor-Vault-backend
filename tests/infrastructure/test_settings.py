from src.infrastructure.config.settings import Settings


def test_settings_reads_env(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://u:p@db:5432/x")
    monkeypatch.setenv("REDIS_URL", "redis://cache:6379/0")
    monkeypatch.setenv("JWT_SECRET", "y" * 40)
    monkeypatch.setenv("JWT_TTL_SECONDS", "3600")

    s = Settings()

    assert s.database_url.endswith("/x")
    assert s.jwt_ttl_seconds == 3600
    assert s.bcrypt_rounds == 12  # default
    assert s.cors_origins == ["http://localhost:3000"]


def test_settings_parses_comma_separated_cors(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://u:p@db:5432/x")
    monkeypatch.setenv("REDIS_URL", "redis://cache:6379/0")
    monkeypatch.setenv("JWT_SECRET", "y" * 40)
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:3000, https://app.example.com")

    s = Settings()

    assert s.cors_origins == ["http://localhost:3000", "https://app.example.com"]


def test_settings_rejects_short_secret(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://u:p@db:5432/x")
    monkeypatch.setenv("REDIS_URL", "redis://cache:6379/0")
    monkeypatch.setenv("JWT_SECRET", "tooshort")
    import pytest
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        Settings()
