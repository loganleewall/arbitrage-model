from __future__ import annotations

from pathlib import Path

import typer

from arbitrage_model.backtesting.loader import align_predictions_to_quotes, load_predictions, load_quotes_from_dir
from arbitrage_model.backtesting.simulator import simulate_expected_value, to_frame

app = typer.Typer(help="Backtest model predictions against historical sportsbook quotes (expected-value only).")


@app.command()
def expected_value(
    predictions_csv: Path = typer.Option(..., help="CSV with columns: player, market, line, prob_over."),
    quotes_dir: Path = typer.Option(Path("data/raw"), help="Directory of sportsbook CSVs (players,line,over,under)."),
    bankroll: float = typer.Option(1000.0, help="Starting bankroll."),
    kelly_clip: float = typer.Option(0.25, help="Max Kelly fraction to stake per bet."),
    min_edge_pct: float = typer.Option(0.5, help="Minimum edge %% to place a bet."),
    flat_stake: float = typer.Option(None, help="Override Kelly with a fixed stake amount."),
) -> None:
    preds = load_predictions(predictions_csv)
    quotes = load_quotes_from_dir(quotes_dir)
    index = align_predictions_to_quotes(preds, quotes)
    result = simulate_expected_value(
        preds, index, bankroll=bankroll, kelly_clip=kelly_clip, min_edge_pct=min_edge_pct, flat_stake=flat_stake
    )
    typer.echo(f"Bankroll start: {result.bankroll_start:.2f}")
    typer.echo(f"Bankroll end (expected): {result.bankroll_end:.2f}")
    typer.echo(f"Total staked: {result.total_staked:.2f}")
    typer.echo(f"Expected profit: {result.expected_profit:.2f}")
    typer.echo(f"Notes: {result.notes}")
    typer.echo("\nTop bets (expected-value):")
    typer.echo(to_frame(result).head(25).to_markdown(index=False))


if __name__ == "__main__":
    app()
