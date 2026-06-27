from src.domain.entities.order import Order
from src.domain.entities.product import Product
from src.infrastructure.database.mappers import (
    order_to_model,
    product_to_domain,
    product_to_model,
)
from src.infrastructure.database.models import ProductModel


def test_product_roundtrip():
    p = Product(id=1, title="Sword", description="d", price=150.0, location="JO")
    model = product_to_model(p)
    assert isinstance(model, ProductModel)
    assert model.id == 1 and model.location == "JO"
    back = product_to_domain(model)
    assert back == p


def test_order_to_model_snapshots():
    p = Product(id=2, title="Shield", description="d", price=120.0, location="SA")
    o = Order.create("u1", p)
    m = order_to_model(o)
    assert m.order_id == o.order_id
    assert m.currency == "SAR"
    assert m.status == "completed"
    assert m.created_at.tzinfo is not None
