import math

import pytest
from src.domain.shared.exceptions import (
    DomainError,
    InvalidCredentialsError,
    NotFoundError,
)
from src.domain.shared.pagination import Page
from src.domain.shared.result import Result


def test_result_ok_carries_value():
    r = Result.ok(42)
    assert r.is_ok() and not r.is_fail()
    assert r.value == 42


def test_result_fail_carries_error():
    err = NotFoundError("nope")
    r: Result[int] = Result.fail(err)
    assert r.is_fail()
    assert r.error is err
    with pytest.raises(RuntimeError):
        _ = r.value


def test_domain_errors_have_codes():
    assert NotFoundError("x").code == "not_found"
    assert InvalidCredentialsError("x").code == "invalid_credentials"
    assert isinstance(NotFoundError("x"), DomainError)


@pytest.mark.parametrize(
    "total,size,expected",
    [(0, 12, 1), (12, 12, 1), (13, 12, 2), (100, 12, math.ceil(100 / 12))],
)
def test_page_total_pages(total, size, expected):
    p = Page(items=[], page=1, page_size=size, total=total)
    assert p.total_pages == expected
