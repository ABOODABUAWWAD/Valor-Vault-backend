# Valor Vault Backend

FastAPI backend for the Valor Vault game-item store. This service owns the
database, CSV import, authentication, product listing, product details, and order
creation APIs consumed by the frontend repository.

## Stack

- FastAPI + Uvicorn
- PostgreSQL — relational store (users, products, orders)
- SQLAlchemy 2.0 with asyncpg
- Alembic migrations
- Redis — product list cache (5 min TTL) and login-failure throttle
- uv for environment and dependency management

## What it provides

- Public featured-products endpoint (no auth) — used by the landing page.
- JWT login endpoint with brute-force protection (5 failures / 15 min window).
- Auth-protected product listing with pagination, search, and location filtering.
- Product detail endpoint.
- Single-item purchase endpoint that creates an order record.
- CSV import script for seeding the catalog and demo user (`demo` / `demo123`).
- OpenAPI docs at `/docs`.

## Setup

```bash
cd backend
cp .env.example .env
```

Set a strong `JWT_SECRET` in `.env` (minimum 32 characters):

```bash
JWT_SECRET=$(openssl rand -hex 32)
```

## Run with Docker

```bash
cd backend
docker compose up --build
```

This starts PostgreSQL, Redis, and the API. `scripts/init_db.sh` runs as the
container entrypoint: it applies Alembic migrations, seeds `scripts/seeds/items.csv`,
then starts Uvicorn.

For production, pass a real secrets file:

```bash
docker compose --env-file .env.prod up -d --build
```

To run only the backing infrastructure (PostgreSQL + Redis) and serve the API on
the host:

```bash
docker compose -f docker-compose.server.yaml up -d
```

Then follow the **Run on the host** steps below.

## Run on the host

```bash
cd backend
uv sync --frozen
uv run alembic upgrade head
uv run python scripts/import_csv.py
uv run uvicorn src.main:app --reload
```

API docs are available at http://localhost:8000/docs.

## Scripts

- `scripts/init_db.sh` — Docker entrypoint: migrate → seed → start Uvicorn.
- `scripts/import_csv.py` — imports `scripts/seeds/items.csv` and seeds the demo user.
- `scripts/setup_db.py` — host helper: creates the Postgres database, migrates, and seeds.

## API contract

Errors always use this shape:

```json
{ "error": { "code": "...", "message": "..." } }
```

| Method | Path | Auth | Success |
|---|---|---|---|
| POST | `/auth/login` | none | `200 { token, user_id, username, name }` |
| GET | `/products/featured` | none | `200 Product[]` (top 4 by price) |
| GET | `/products?page=&page_size=&location=JO\|SA&search=` | Bearer | `200 { items, page, page_size, total, total_pages }` |
| GET | `/products/{id}` | Bearer | `200 Product` |
| POST | `/orders` | Bearer | `201 { order_id, product, price, currency, location, status, created_at }` |
| GET | `/healthz` | none | `200 { status: "ok" }` |
| GET | `/readyz` | none | `200 { status: "ready" }` (checks DB + Redis) |

`Product` shape:

```ts
Product = { id, title, description, price, location: "JO" | "SA", currency, rarity, icon }
```

## Database and migrations

- Alembic migration files live under `migrations/`.
- The initial schema is in `migrations/versions/0001_initial_schema.py`.

## Repository layout

```
src/
  domain/         entities, value objects, ports, shared primitives
  application/    services, DTOs, mappers
  infrastructure/ database, cache (Redis), security, config, logging
  presentation/   FastAPI app factory, deps, schemas, routers, error handlers
migrations/       Alembic env + version files
scripts/
  init_db.sh      Docker entrypoint
  import_csv.py   CSV importer + demo-user seeder
  setup_db.py     host first-run helper
  seeds/
    items.csv     100-row product catalogue
```

## Testing

```bash
cd backend
uv run pytest -v                      # unit + integration (integration needs Docker)
uv run pytest -m "not integration"    # unit only
uv run ruff check .
uv run ruff format --check .
uv run mypy src
```

## Notes

- `currency`, `rarity`, and `icon` are derived on read from `price` and `location`; they are not stored in the database.
- The frontend cart is client-side; the backend creates one order per purchase request.
- The demo user (`demo` / `demo123`) is seeded by `scripts/import_csv.py`.
- JWT tokens are stateless (HS256, 24 h). There is no logout endpoint.
