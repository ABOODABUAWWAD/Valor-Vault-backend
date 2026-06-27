import pytest
from sqlalchemy import text

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_metadata_creates_all_tables(engine):
    async with engine.connect() as conn:
        rows = await conn.execute(
            text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
        )
        names = {r[0] for r in rows}
    assert {"users", "products", "orders"}.issubset(names)
