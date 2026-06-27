"""Functional Result — services return it instead of throwing across the
application boundary, keeping error paths explicit in the type system."""

from __future__ import annotations

from typing import TypeVar

from src.domain.shared.exceptions import DomainError

T = TypeVar("T")


class Result[T]:
    __slots__ = ("_error", "_ok", "_value")

    def __init__(self, ok: bool, value: T | None, error: DomainError | None) -> None:
        self._ok = ok
        self._value = value
        self._error = error

    @staticmethod
    def ok(value: T) -> Result[T]:
        return Result(True, value, None)

    @staticmethod
    def fail(error: DomainError) -> Result[T]:
        return Result(False, None, error)

    def is_ok(self) -> bool:
        return self._ok

    def is_fail(self) -> bool:
        return not self._ok

    @property
    def value(self) -> T:
        if not self._ok:
            raise RuntimeError("Result.value accessed on a failed Result")
        return self._value  # type: ignore[return-value]

    @property
    def error(self) -> DomainError:
        if self._ok:
            raise RuntimeError("Result.error accessed on an ok Result")
        assert self._error is not None
        return self._error
