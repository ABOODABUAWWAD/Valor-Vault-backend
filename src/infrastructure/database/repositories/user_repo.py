from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.user import User
from src.infrastructure.database.mappers import user_to_domain
from src.infrastructure.database.models import UserModel


class SqlUserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_username(self, username: str) -> User | None:
        row = await self._session.scalar(select(UserModel).where(UserModel.username == username))
        return user_to_domain(row) if row else None

    async def add(self, user: User) -> None:
        self._session.add(
            UserModel(
                id=user.id,
                username=user.username,
                name=user.name,
                password_hash=user.password_hash,
            )
        )
