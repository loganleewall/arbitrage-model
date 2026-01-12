from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

MarketSide = Literal["over", "under"]


@dataclass(frozen=True)
class BookOffer:
    """Quote for a single player prop from a specific sportsbook."""

    book: str
    player: str
    market: str
    line: float
    over_odds: int
    under_odds: int


@dataclass(frozen=True)
class ArbitrageOpportunity:
    """Represents a two-way arbitrage opportunity between two books."""

    player: str
    market: str
    line: float
    over_book: str
    under_book: str
    over_odds: int
    under_odds: int
    edge_pct: float
    stake_over: float
    stake_under: float
    expected_profit: float
