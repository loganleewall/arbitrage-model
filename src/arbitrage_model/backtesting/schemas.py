from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional

MarketSide = Literal["over", "under"]


@dataclass(frozen=True)
class PredictionInput:
    """Model output for a single player prop."""

    player: str
    market: str
    line: float
    prob_over: float  # 0-1
    source: str = "model"


@dataclass(frozen=True)
class MarketQuote:
    """Snapshot of a book's offer for comparison with predictions."""

    book: str
    player: str
    market: str
    line: float
    over_odds: int
    under_odds: int


@dataclass(frozen=True)
class SimBet:
    """A simulated bet based on a prediction and a book quote."""

    player: str
    market: str
    line: float
    side: MarketSide
    book: str
    stake: float
    odds: int
    prob: float
    edge: float
    kelly_fraction: float


@dataclass(frozen=True)
class SimResult:
    """Aggregated simulation results."""

    bankroll_start: float
    bankroll_end: float
    total_staked: float
    expected_profit: float
    bets: list[SimBet]
    notes: Optional[str] = None
