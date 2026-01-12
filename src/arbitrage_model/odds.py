from __future__ import annotations

import re

_UNICODE_MINUS = "\u2212"
_AMERICAN_ODDS_PATTERN = re.compile(r"^([+-]?)(\d+)$")


def normalize_american_odds(raw: str | int) -> int:
    """Normalize American odds to an int, handling unicode minus signs."""
    if isinstance(raw, int):
        return raw
    cleaned = raw.strip().replace(_UNICODE_MINUS, "-")
    match = _AMERICAN_ODDS_PATTERN.match(cleaned)
    if not match:
        raise ValueError(f"Unable to parse American odds value: {raw!r}")
    sign, digits = match.groups()
    value = int(digits)
    return value if sign != "-" else -value


def american_to_decimal(odds: int) -> float:
    """Convert American odds to decimal odds."""
    if odds == 0:
        raise ValueError("American odds cannot be zero")
    if odds > 0:
        return odds / 100 + 1
    return 100 / abs(odds) + 1


def american_to_implied_prob(odds: int) -> float:
    """Convert American odds to implied probability (vig included)."""
    if odds > 0:
        return 100 / (odds + 100)
    return abs(odds) / (abs(odds) + 100)
