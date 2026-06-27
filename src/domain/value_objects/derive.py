"""Presentation fields derived from raw CSV columns. NOT stored in the DB.
Mirrors web/src/lib/derive.ts exactly so the existing UI renders identically."""

from __future__ import annotations

import re

from src.domain.value_objects.location import Location


def currency_for(loc: Location) -> str:
    return "JOD" if loc == "JO" else "SAR"


def rarity_for(price: float) -> str:
    if price <= 25:
        return "common"
    if price <= 75:
        return "uncommon"
    if price <= 125:
        return "rare"
    if price <= 200:
        return "epic"
    return "legendary"


# Title keyword -> lucide-react icon key. First match wins; fallback "Package".
_ICON_MAP: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"sword", re.I), "Sword"),
    (re.compile(r"shield", re.I), "Shield"),
    (re.compile(r"potion", re.I), "FlaskConical"),
    (re.compile(r"wand", re.I), "Wand2"),
    (re.compile(r"ring", re.I), "Gem"),
    (re.compile(r"helmet", re.I), "HardHat"),
    (re.compile(r"armor", re.I), "Shirt"),
    (re.compile(r"boots", re.I), "Footprints"),
    (re.compile(r"gloves", re.I), "Hand"),
    (re.compile(r"cape|shadow", re.I), "Ghost"),
)


def icon_for(title: str) -> str:
    for pattern, name in _ICON_MAP:
        if pattern.search(title):
            return name
    return "Package"
