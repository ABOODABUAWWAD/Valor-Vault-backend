from __future__ import annotations

from typing import Literal

Location = Literal["JO", "SA"]
_VALID: frozenset[str] = frozenset({"JO", "SA"})


def parse_location(raw: str | None) -> Location | None:
    if raw in _VALID:
        return raw  # type: ignore[return-value]
    return None
