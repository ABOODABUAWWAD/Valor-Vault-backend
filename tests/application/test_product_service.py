from src.application.services.product_service import ProductService
from src.domain.entities.product import Product

from tests.fakes import FakeProductCache, FakeProductRepository


def _repo() -> FakeProductRepository:
    return FakeProductRepository(
        [
            Product(id=i, title=f"Sword {i}", description="x", price=float(i * 10), location="JO")
            for i in range(1, 26)
        ]
        + [Product(id=99, title="Saudi Shield", description="x", price=120.0, location="SA")]
    )


async def test_list_paginates_and_wraps_envelope():
    svc = ProductService(_repo(), FakeProductCache())
    page = await svc.list_products(page=2, page_size=12, location=None, search=None)
    assert page.page == 2
    assert page.page_size == 12
    assert page.total == 26
    assert page.total_pages == 3
    assert len(page.items) == 12
    assert page.items[0].rarity in {"common", "uncommon", "rare", "epic", "legendary"}


async def test_list_filters_by_location():
    svc = ProductService(_repo(), FakeProductCache())
    page = await svc.list_products(page=1, page_size=12, location="SA", search=None)
    assert page.total == 1
    assert page.items[0].id == 99


async def test_list_search_is_case_insensitive_on_title():
    svc = ProductService(_repo(), FakeProductCache())
    page = await svc.list_products(page=1, page_size=50, location=None, search="saudi")
    assert page.total == 1
    assert page.items[0].id == 99


async def test_list_clamps_invalid_pagination():
    svc = ProductService(_repo(), FakeProductCache())
    page = await svc.list_products(page=0, page_size=999, location=None, search=None)
    assert page.page == 1
    assert page.page_size == 100


async def test_list_uses_cache_on_repeat():
    cache = FakeProductCache()
    repo = _repo()
    svc = ProductService(repo, cache)
    await svc.list_products(page=1, page_size=12, location=None, search=None)
    assert len(cache.store) == 1  # one cached envelope
    # second call served from cache — sabotage the repo to prove it isn't hit
    repo._products = []
    page = await svc.list_products(page=1, page_size=12, location=None, search=None)
    assert page.total == 26


async def test_get_product_found_and_missing():
    svc = ProductService(_repo(), FakeProductCache())
    ok = await svc.get_product(99)
    assert ok.is_ok() and ok.value.currency == "SAR"
    missing = await svc.get_product(123456)
    assert missing.is_fail() and missing.error.code == "not_found"


async def test_featured_products_cached_on_repeat():
    cache = FakeProductCache()
    repo = _repo()
    svc = ProductService(repo, cache)
    first = await svc.featured_products(limit=4)
    assert len(first) == 4
    assert "products:featured:4" in cache.store
    # sabotage repo — second call must come from cache
    repo._products = []
    second = await svc.featured_products(limit=4)
    assert [v.id for v in second] == [v.id for v in first]
