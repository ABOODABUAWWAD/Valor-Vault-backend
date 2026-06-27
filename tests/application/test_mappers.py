from src.application.mappers import to_order_view, to_product_view
from src.domain.entities.order import Order
from src.domain.entities.product import Product


def _p() -> Product:
    return Product(id=4, title="Mystic Wand", description="x", price=200.0, location="SA")


def test_to_product_view_derives_fields():
    v = to_product_view(_p())
    assert v.currency == "SAR"
    assert v.rarity == "epic"
    assert v.icon == "Wand2"
    assert (v.id, v.title, v.price, v.location) == (4, "Mystic Wand", 200.0, "SA")


def test_to_order_view_matches_contract():
    p = _p()
    o = Order.create("u1", p)
    v = to_order_view(o, p)
    assert v.order_id == o.order_id
    assert v.product.id == 4
    assert v.price == 200.0
    assert v.currency == "SAR"
    assert v.location == "SA"
    assert v.status == "completed"
    assert v.created_at == o.created_at.isoformat()
