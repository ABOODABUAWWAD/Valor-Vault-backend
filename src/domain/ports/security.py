from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from src.domain.entities.user import User


@runtime_checkable
class PasswordHasher(Protocol):
    def hash(self, plain: str) -> str: ...
    def verify(self, plain: str, hashed: str) -> bool: ...


@runtime_checkable
class TokenService(Protocol):
    def issue(self, user: User) -> str: ...
    def verify(self, token: str) -> dict[str, Any] | None: ...
