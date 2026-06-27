#!/usr/bin/env python3
"""
First-time setup: create the Postgres database, run Alembic migrations,
and seed the demo data + user.

Usage:
    DATABASE_URL=postgresql+asyncpg://valor:valor@localhost:5432/valor \\
    uv run python scripts/setup_db.py
"""

from __future__ import annotations

import asyncio
import os
import subprocess
import sys
from urllib.parse import urlparse


def _parse_url(database_url: str) -> tuple[str, str]:
    """Return (admin_dsn, db_name) for the given asyncpg DATABASE_URL."""
    # Strip SQLAlchemy dialect prefix so urlparse works.
    plain = database_url.replace("postgresql+asyncpg://", "postgresql://", 1)
    parsed = urlparse(plain)
    db_name = parsed.path.lstrip("/")
    if not db_name:
        print("[setup] DATABASE_URL has no database name.", file=sys.stderr)
        sys.exit(1)
    # Build admin DSN pointing at the maintenance 'postgres' database.
    admin = plain.replace(f"/{db_name}", "/postgres", 1)
    return admin, db_name


async def _ensure_database(database_url: str) -> None:
    try:
        import asyncpg
    except ImportError:
        print("[setup] asyncpg not installed — run inside uv.", file=sys.stderr)
        sys.exit(1)

    admin_dsn, db_name = _parse_url(database_url)
    conn = await asyncpg.connect(admin_dsn)
    try:
        exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1", db_name
        )
        if exists:
            print(f"[setup] Database '{db_name}' already exists — skipping CREATE.")
        else:
            # Can't use parameters for identifiers; db_name came from the URL we own.
            await conn.execute(f'CREATE DATABASE "{db_name}"')
            print(f"[setup] Database '{db_name}' created.")
    finally:
        await conn.close()


def _run(cmd: list[str], label: str) -> None:
    print(f"[setup] {label}…")
    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        print(f"[setup] {label} failed (exit {result.returncode}).", file=sys.stderr)
        sys.exit(result.returncode)
    print(f"[setup] {label} done.")


async def main() -> None:
    database_url = os.environ.get("DATABASE_URL", "")
    if not database_url:
        print("[setup] DATABASE_URL is not set.", file=sys.stderr)
        sys.exit(1)

    await _ensure_database(database_url)
    _run(["uv", "run", "alembic", "upgrade", "head"], "Alembic migrations")
    _run(["uv", "run", "python", "scripts/import_csv.py"], "Seed data")

    print("[setup] Setup complete. Run the server with:")
    print("  uv run uvicorn src.main:app --host 0.0.0.0 --port 8000")


if __name__ == "__main__":
    asyncio.run(main())
