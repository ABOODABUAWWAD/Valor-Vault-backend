from src.application.services.order_service import OrderService
from src.domain.entities.product import Product

from tests.fakes import (
    FakeOrderRepository,
    FakeProductRepository,
    FakeUnitOfWork,
)


def _uow_factory(uow: FakeUnitOfWork):
    def factory() -> FakeUnitOfWork:
        return uow

    return factory


async def test_buy_persists_order_and_returns_view():
    products = FakeProductRepository(
        [Product(id=1, title="Sword of Valor", description="x", price=150.0, location="JO")]
    )
    orders = FakeOrderRepository()
    uow = FakeUnitOfWork(products=products, orders=orders)
    svc = OrderService(_uow_factory(uow))

    r = await svc.buy(user_id="u1", product_id=1)

    assert r.is_ok()
    assert r.value.product.id == 1
    assert r.value.currency == "JOD"
    assert r.value.status == "completed"
    assert len(orders.saved) == 1
    assert uow.committed is True


async def test_buy_unknown_product_is_not_found():
    uow = FakeUnitOfWork(products=FakeProductRepository([]))
    svc = OrderService(_uow_factory(uow))
    r = await svc.buy(user_id="u1", product_id=999)
    assert r.is_fail()
    assert r.error.code == "not_found"
    assert uow.committed is False
