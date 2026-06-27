from datetime import UTC, datetime

from src.domain.entities.order import Order
from src.domain.entities.product import Product


def _product() -> Product:
    return Product(id=1, title="Sword of Valor", description="x", price=150.0, location="JO")


def test_order_create_snapshots_product():
    p = _product()
    o = Order.create(user_id="u1", product=p)

    assert o.product_id == 1
    assert o.price == 150.0
    assert o.currency == "JOD"  # derived from JO
    assert o.location == "JO"
    assert o.status == "completed"
    assert o.user_id == "u1"
    # order_id is a uuid4 string (36 chars, 4 hyphens)
    assert len(o.order_id) == 36 and o.order_id.count("-") == 4
    assert o.created_at.tzinfo == UTC
    assert isinstance(o.created_at, datetime)


def test_two_orders_get_distinct_ids():
    p = _product()
    assert Order.create("u1", p).order_id != Order.create("u1", p).order_id
