from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

import pandas as pd

from arbitrage_model.aggregator import load_book_quotes
from arbitrage_model.backtesting.schemas import MarketQuote, PredictionInput


def load_predictions(path: Path) -> List[PredictionInput]:
    """
    Load model predictions from CSV.
    Expected columns: player, market, line, prob_over (0-1), source (optional).
    """
    df = pd.read_csv(path)
    required = {"player", "market", "line", "prob_over"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"{path} missing required columns: {missing}")
    preds: List[PredictionInput] = []
    for _, row in df.iterrows():
        preds.append(
            PredictionInput(
                player=str(row["player"]).strip(),
                market=str(row["market"]).strip(),
                line=float(row["line"]),
                prob_over=float(row["prob_over"]),
                source=str(row.get("source", "model")),
            )
        )
    return preds


def load_quotes_from_dir(data_dir: Path, market: str = "points") -> List[MarketQuote]:
    """
    Load all sportsbook quotes in a directory into MarketQuote objects.
    Reuses aggregator.load_book_quotes to keep a single CSV schema.
    """
    quotes: List[MarketQuote] = []
    for csv_file in data_dir.glob("*.csv"):
        book_name = csv_file.stem.replace("_props_sample", "").replace("_", " ").title()
        offers = load_book_quotes(csv_file, book=book_name, market=market)
        for o in offers:
            quotes.append(
                MarketQuote(
                    book=o.book,
                    player=o.player,
                    market=o.market,
                    line=o.line,
                    over_odds=o.over_odds,
                    under_odds=o.under_odds,
                )
            )
    return quotes


def align_predictions_to_quotes(
    predictions: Iterable[PredictionInput], quotes: Iterable[MarketQuote]
) -> dict[tuple[str, float, str], list[MarketQuote]]:
    """
    Index quotes by (player, line, market) for quick matching during simulation.
    """
    index: dict[tuple[str, float, str], list[MarketQuote]] = {}
    for q in quotes:
        key = (q.player, q.line, q.market)
        index.setdefault(key, []).append(q)
    return index
