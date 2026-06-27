import pytest
from src.domain.entities.order import Order
from src.domain.entities.product import Product
from src.domain.entities.user import User
from src.infrastructure.database.uow import SqlAlchemyUnitOfWork

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_user_and_product_and_order_roundtrip(sessionmaker):
    uow = SqlAlchemyUnitOfWork(sessionmaker)
    async with uow:
        await uow.users.add(User(id="u1", username="demo", name="Demo", password_hash="h"))
        await uow.products.upsert_many(
            [
                Product(id=1, title="Sword", description="d", price=150.0, location="JO"),
                Product(id=2, title="Saudi Shield", description="d", price=120.0, location="SA"),
            ]
        )
        await uow.commit()

    async with uow:
        found = await uow.users.find_by_username("demo")
        assert found is not None and found.id == "u1"

        items, total = await uow.products.list(location="SA", search=None, offset=0, limit=10)
        assert total == 1 and items[0].id == 2

        items, total = await uow.products.list(location=None, search="sword", offset=0, limit=10)
        assert total == 1 and items[0].id == 1

        product = await uow.products.get(1)
        assert product is not None
        order = Order.create("u1", product)
        await uow.orders.add(order)
        await uow.commit()


@pytest.mark.asyncio
async def test_list_search_escapes_like_wildcards(sessionmaker):
    uow = SqlAlchemyUnitOfWork(sessionmaker)
    async with uow:
        await uow.products.upsert_many(
            [
                Product(id=1, title="Sword", description="d", price=150.0, location="JO"),
                Product(id=2, title="Shield", description="d", price=120.0, location="SA"),
            ]
        )
        await uow.commit()
    async with uow:
        # '%' is a LIKE wildcard; escaped, it matches no literal '%' in any title -> 0
        items, total = await uow.products.list(location=None, search="%", offset=0, limit=50)
        # sanity: a real literal substring still matches
        sw_items, sw_total = await uow.products.list(
            location=None, search="word", offset=0, limit=50
        )
    assert total == 0 and items == []
    assert sw_total == 1 and sw_items[0].title == "Sword"


@pytest.mark.asyncio
async def test_upsert_many_is_idempotent(sessionmaker):
    uow = SqlAlchemyUnitOfWork(sessionmaker)
    p = Product(id=5, title="Wand", description="d", price=200.0, location="SA")
    async with uow:
        await uow.products.upsert_many([p])
        await uow.products.upsert_many([p])  # second time must not raise
        await uow.commit()
    async with uow:
        _, total = await uow.products.list(location=None, search=None, offset=0, limit=50)
    assert total == 1
