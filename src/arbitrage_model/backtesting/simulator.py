from __future__ import annotations

from typing import Iterable, List

import pandas as pd

from arbitrage_model.backtesting.schemas import MarketQuote, PredictionInput, SimBet, SimResult
from arbitrage_model.odds import american_to_decimal


def simulate_expected_value(
    predictions: Iterable[PredictionInput],
    quote_index: dict[tuple[str, float, str], list[MarketQuote]],
    bankroll: float = 1000.0,
    kelly_clip: float = 0.25,
    min_edge_pct: float = 0.5,
    flat_stake: float | None = None,
) -> SimResult:
    """
    Simulate betting using model probabilities as ground truth (expected value simulation).
    This does NOT require actual outcomes—use this to score model quality vs available prices.

    Strategy:
    - For each prediction, find matching quotes (player, line, market).
    - Compute edge for over and under; pick the better side above `min_edge_pct`.
    - Size using fractional Kelly (clipped) or flat stake if provided.
    """
    bets: List[SimBet] = []
    total_staked = 0.0
    expected_profit = 0.0

    for pred in predictions:
        key = (pred.player, pred.line, pred.market)
        quotes = quote_index.get(key, [])
        if not quotes:
            continue
        quote = _best_edge_quote(pred, quotes)
        if not quote:
            continue

        side, odds, prob = quote
        edge = _edge(prob, odds)
        if edge * 100 < min_edge_pct:
            continue

        if flat_stake:
            stake = flat_stake
        else:
            kelly = _kelly_fraction(prob, odds)
            stake = bankroll * min(kelly, kelly_clip)

        exp_profit = stake * _expected_return(prob, odds)
        bets.append(
            SimBet(
                player=pred.player,
                market=pred.market,
                line=pred.line,
                side=side,
                book=_quote_book(quotes, side),
                stake=stake,
                odds=odds,
                prob=prob,
                edge=edge * 100,
                kelly_fraction=min(_kelly_fraction(prob, odds), kelly_clip),
            )
        )
        total_staked += stake
        expected_profit += exp_profit

    bankroll_end = bankroll + expected_profit
    notes = (
        "Expected-value simulation only; plug in realized outcomes to compute actual P&L. "
        "Selectors and matching are naive—tighten with IDs or timestamps as needed."
    )
    return SimResult(
        bankroll_start=bankroll,
        bankroll_end=bankroll_end,
        total_staked=total_staked,
        expected_profit=expected_profit,
        bets=bets,
        notes=notes,
    )


def _best_edge_quote(pred: PredictionInput, quotes: list[MarketQuote]):
    best = None
    best_edge = 0.0
    # Over
    for q in quotes:
        over_edge = _edge(pred.prob_over, q.over_odds)
        under_prob = 1 - pred.prob_over
        under_edge = _edge(under_prob, q.under_odds)
        if over_edge > best_edge:
            best_edge = over_edge
            best = ("over", q.over_odds, pred.prob_over)
        if under_edge > best_edge:
            best_edge = under_edge
            best = ("under", q.under_odds, under_prob)
    return best


def _edge(prob: float, odds: int) -> float:
    dec = american_to_decimal(odds)
    return prob * dec - 1


def _expected_return(prob: float, odds: int) -> float:
    dec = american_to_decimal(odds)
    return prob * (dec - 1) - (1 - prob)


def _kelly_fraction(prob: float, odds: int) -> float:
    b = american_to_decimal(odds) - 1
    q = 1 - prob
    return max((prob * b - q) / b, 0)


def _quote_book(quotes: list[MarketQuote], side: str) -> str:
    # Return the book for the first quote; extend to pick best book per side if needed.
    return quotes[0].book if quotes else "unknown"


def to_frame(result: SimResult) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "player": b.player,
                "market": b.market,
                "line": b.line,
                "side": b.side,
                "book": b.book,
                "stake": round(b.stake, 2),
                "odds": b.odds,
                "prob": round(b.prob, 3),
                "edge_pct": round(b.edge, 2),
                "kelly_fraction": round(b.kelly_fraction, 3),
            }
            for b in result.bets
        ]
    )
