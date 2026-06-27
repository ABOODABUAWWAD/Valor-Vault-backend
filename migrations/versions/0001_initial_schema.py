"""initial schema — users, products, orders

Revision ID: 0001
Revises:
Create Date: 2026-06-26
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("username", sa.String(64), nullable=False, unique=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
    )
    op.create_table(
        "products",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.String(1024), nullable=False),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        sa.Column("location", sa.String(2), nullable=False),
    )
    op.create_index("ix_products_title", "products", ["title"])
    op.create_index("ix_products_location", "products", ["location"])

    op.create_table(
        "orders",
        sa.Column("order_id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("product_id", sa.Integer, sa.ForeignKey("products.id"), nullable=False),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("location", sa.String(2), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("orders")
    op.drop_index("ix_products_location", table_name="products")
    op.drop_index("ix_products_title", table_name="products")
    op.drop_table("products")
    op.drop_table("users")
