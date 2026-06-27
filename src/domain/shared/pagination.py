from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TypeVar

T = TypeVar("T")


@dataclass(slots=True)
class Page[T]:
    items: list[T]
    page: int
    page_size: int
    total: int

    @property
    def total_pages(self) -> int:
        return max(1, math.ceil(self.total / self.page_size))
