from __future__ import annotations

from src.application.dtos import AuthView
from src.domain.ports.cache import LoginThrottle
from src.domain.ports.repositories import UserRepository
from src.domain.ports.security import PasswordHasher, TokenService
from src.domain.shared.exceptions import InvalidCredentialsError, TooManyAttemptsError
from src.domain.shared.result import Result

_INVALID = "Invalid username or password"


class AuthService:
    def __init__(
        self,
        users: UserRepository,
        hasher: PasswordHasher,
        tokens: TokenService,
        throttle: LoginThrottle,
    ) -> None:
        self._users = users
        self._hasher = hasher
        self._tokens = tokens
        self._throttle = throttle

    async def login(self, username: str, password: str) -> Result[AuthView]:
        # Lockout check first: a locked account does no bcrypt work and the
        # generic message never confirms whether the account exists.
        if await self._throttle.is_locked(username):
            return Result.fail(TooManyAttemptsError(_INVALID))

        user = await self._users.find_by_username(username)
        ok = user is not None and self._hasher.verify(password, user.password_hash)
        if user is None or not ok:
            await self._throttle.record_failure(username)
            return Result.fail(InvalidCredentialsError(_INVALID))

        await self._throttle.reset(username)
        token = self._tokens.issue(user)
        return Result.ok(
            AuthView(token=token, user_id=user.id, username=user.username, name=user.name)
        )
