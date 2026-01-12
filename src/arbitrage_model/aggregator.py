from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Iterable, List, Sequence

import pandas as pd

from arbitrage_model.models import ArbitrageOpportunity, BookOffer
from arbitrage_model.odds import american_to_decimal, normalize_american_odds


def load_book_quotes(csv_path: Path, book: str, market: str = "points") -> List[BookOffer]:
    """
    Load a sportsbook CSV into normalized BookOffer objects.

    Expected columns: players, line, over, under
    """
    df = pd.read_csv(csv_path)
    missing = {"players", "line", "over", "under"} - set(df.columns)
    if missing:
        raise ValueError(f"{csv_path} missing required columns: {missing}")

    offers: List[BookOffer] = []
    for _, row in df.iterrows():
        offers.append(
            BookOffer(
                book=book,
                player=str(row["players"]).strip(),
                market=market,
                line=float(row["line"]),
                over_odds=normalize_american_odds(row["over"]),
                under_odds=normalize_american_odds(row["under"]),
            )
        )
    return offers


def group_by_player_line(offers: Sequence[BookOffer]):
    grouped: dict[tuple[str, float], list[BookOffer]] = defaultdict(list)
    for offer in offers:
        grouped[(offer.player, offer.line)].append(offer)
    return grouped


def _best_offer(offers: Iterable[BookOffer], side: str) -> BookOffer:
    key = (
        (lambda o: american_to_decimal(o.over_odds))
        if side == "over"
        else (lambda o: american_to_decimal(o.under_odds))
    )
    return max(offers, key=key)


def find_two_way_arbs(
    offers: Sequence[BookOffer],
    bankroll: float = 100.0,
) -> List[ArbitrageOpportunity]:
    """Identify two-way arbitrage opportunities across books for each player line."""
    opportunities: List[ArbitrageOpportunity] = []
    for (player, line), quotes in group_by_player_line(offers).items():
        if len(quotes) < 2:
            continue

        best_over = _best_offer(quotes, "over")
        best_under = _best_offer(quotes, "under")

        over_decimal = american_to_decimal(best_over.over_odds)
        under_decimal = american_to_decimal(best_under.under_odds)
        inverse_sum = 1 / over_decimal + 1 / under_decimal

        if inverse_sum >= 1:
            continue

        stake_over = bankroll * (1 / over_decimal) / inverse_sum
        stake_under = bankroll * (1 / under_decimal) / inverse_sum
        guaranteed_payout = bankroll / inverse_sum
        expected_profit = guaranteed_payout - bankroll
        edge_pct = (1 / inverse_sum - 1) * 100

        opportunities.append(
            ArbitrageOpportunity(
                player=player,
                market=quotes[0].market,
                line=line,
                over_book=best_over.book,
                under_book=best_under.book,
                over_odds=best_over.over_odds,
                under_odds=best_under.under_odds,
                edge_pct=edge_pct,
                stake_over=stake_over,
                stake_under=stake_under,
                expected_profit=expected_profit,
            )
        )
    return sorted(opportunities, key=lambda o: o.edge_pct, reverse=True)


def detect_arbitrage_from_dir(data_dir: Path, bankroll: float = 100.0) -> List[ArbitrageOpportunity]:
    """Load every CSV in a directory and run arbitrage detection."""
    all_offers: List[BookOffer] = []
    for csv_file in data_dir.glob("*.csv"):
        book_name = csv_file.stem.replace("_props_sample", "").replace("_", " ").title()
        all_offers.extend(load_book_quotes(csv_file, book=book_name))
    return find_two_way_arbs(all_offers, bankroll=bankroll)


def opportunities_to_frame(opportunities: Sequence[ArbitrageOpportunity]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "player": o.player,
                "market": o.market,
                "line": o.line,
                "over_book": o.over_book,
                "under_book": o.under_book,
                "over_odds": o.over_odds,
                "under_odds": o.under_odds,
                "edge_pct": round(o.edge_pct, 2),
                "stake_over": round(o.stake_over, 2),
                "stake_under": round(o.stake_under, 2),
                "expected_profit": round(o.expected_profit, 2),
            }
            for o in opportunities
        ]
    )
