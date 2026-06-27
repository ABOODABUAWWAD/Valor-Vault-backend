#!/usr/bin/env python3
"""CSV import script: parse scripts/seeds/items.csv into the DB + seed the demo user.

Run: uv run python scripts/import_csv.py
"""

from __future__ import annotations

import asyncio
import csv as csv_module
import io
import sys
from pathlib import Path

# Standalone-script bootstrap: `python scripts/import_csv.py` puts scripts/ on sys.path,
# not the backend root, so make `src` importable.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import structlog
from src.domain.entities.product import Product
from src.domain.entities.user import User
from src.domain.ports.security import PasswordHasher
from src.domain.value_objects.location import parse_location
from src.infrastructure.config.settings import get_settings
from src.infrastructure.database.engine import make_engine, make_sessionmaker
from src.infrastructure.database.uow import SqlAlchemyUnitOfWork
from src.infrastructure.security.bcrypt_hasher import BcryptPasswordHasher

_DEMO_ID = "u1"
_DEMO_USERNAME = "demo"
_DEMO_NAME = "Demo Adventurer"

_DEFAULT_CSV = Path(__file__).resolve().parent / "seeds" / "items.csv"
log = structlog.get_logger()


def parse_products(csv_text: str) -> list[Product]:
    reader = csv_module.DictReader(io.StringIO(csv_text))
    products: list[Product] = []
    for row in reader:
        location = parse_location(row["location"].strip())
        if location is None:
            continue
        products.append(
            Product(
                id=int(row["id"]),
                title=row["title"].strip(),
                description=row["description"].strip(),
                price=float(row["price"]),
                location=location,
            )
        )
    return products


async def import_data(
    uow: SqlAlchemyUnitOfWork,
    hasher: PasswordHasher,
    csv_path: str,
    demo_password: str = "demo123",
) -> tuple[int, bool]:
    products = parse_products(Path(csv_path).read_text(encoding="utf-8"))
    async with uow:
        await uow.products.upsert_many(products)
        existing = await uow.users.find_by_username(_DEMO_USERNAME)
        created = existing is None
        if created:
            await uow.users.add(
                User(
                    id=_DEMO_ID,
                    username=_DEMO_USERNAME,
                    name=_DEMO_NAME,
                    password_hash=hasher.hash(demo_password),
                )
            )
        await uow.commit()
    return len(products), created


async def _run() -> None:
    settings = get_settings()
    engine = make_engine(settings.database_url)
    try:
        sessionmaker = make_sessionmaker(engine)
        hasher = BcryptPasswordHasher(rounds=settings.bcrypt_rounds)
        count, created = await import_data(
            SqlAlchemyUnitOfWork(sessionmaker), hasher, str(_DEFAULT_CSV)
        )
        log.info("import complete", products=count, demo_user_created=created)
    finally:
        await engine.dispose()


def main() -> None:
    asyncio.run(_run())


if __name__ == "__main__":
    main()
