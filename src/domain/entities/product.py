from __future__ import annotations

from dataclasses import dataclass

from src.domain.value_objects.location import Location


@dataclass(frozen=True, slots=True)
class Product:
    id: int
    title: str
    description: str
    price: float
    location: Location
