from __future__ import annotations

import time
from typing import Any

import jwt

from src.domain.entities.user import User

_ALG = "HS256"


class JwtTokenService:
    def __init__(self, secret: str, ttl_seconds: int) -> None:
        self._secret = secret
        self._ttl = ttl_seconds

    def issue(self, user: User) -> str:
        now = int(time.time())
        payload = {
            "sub": user.id,
            "username": user.username,
            "name": user.name,
            "iat": now,
            "exp": now + self._ttl,
        }
        return jwt.encode(payload, self._secret, algorithm=_ALG)

    def verify(self, token: str) -> dict[str, Any] | None:
        try:
            return jwt.decode(token, self._secret, algorithms=[_ALG])
        except jwt.PyJWTError:
            return None
