# syntax=docker/dockerfile:1

# ---- base: uv + python --------------------------------------------------
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS base
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
WORKDIR /app

# ---- deps: resolve + install into /app/.venv ----------------------------
FROM base AS deps
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# ---- test: install dev deps + run the unit suite (gate the image) -------
FROM base AS test
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen
COPY . .
# Integration tests need Docker (testcontainers) — skip here; CI runs them.
RUN uv run ruff check . && uv run mypy src && uv run pytest tests -m "not integration" -p no:cacheprovider \
    && touch /tmp/tests.passed

# ---- runtime: slim, non-root -------------------------------------------
FROM python:3.12-slim-bookworm AS runtime
ENV PATH="/app/.venv/bin:$PATH" PYTHONUNBUFFERED=1
WORKDIR /app
RUN groupadd -r app && useradd -r -g app app
COPY --from=test /tmp/tests.passed /tmp/tests.passed
COPY --from=deps /app/.venv /app/.venv
COPY src ./src
COPY migrations ./migrations
COPY alembic.ini ./
COPY scripts ./scripts
USER app
EXPOSE 8000
CMD ["sh", "scripts/init_db.sh"]
