"""Type-safe application settings loaded from environment variables.

Centralized, fail-fast configuration (pydantic-settings). The rest of the app
receives a Settings instance via DI (presentation/api/deps.py) — never reads
os.environ directly.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "development"
    port: int = 8000

    database_url: str
    redis_url: str

    jwt_secret: str = Field(min_length=32)
    jwt_ttl_seconds: int = 86400
    bcrypt_rounds: int = 12

    lockout_max_failures: int = 5
    lockout_window_seconds: int = 900
    product_cache_ttl_seconds: int = 300

    cors_origins: Annotated[list[str], NoDecode] = ["http://localhost:3000"]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_origins(cls, raw: object) -> object:
        # NoDecode means pydantic-settings will NOT JSON-decode the env value,
        # so we always receive a plain string. Split on commas; a single value
        # with no comma yields a 1-element list, which is correct.
        if isinstance(raw, str):
            stripped = raw.strip()
            return [part.strip() for part in stripped.split(",") if part.strip()]
        return raw


@lru_cache
def get_settings() -> Settings:
    return Settings()
