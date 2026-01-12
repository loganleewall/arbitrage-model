from __future__ import annotations

from pathlib import Path

import typer

from arbitrage_model.aggregator import detect_arbitrage_from_dir, opportunities_to_frame

app = typer.Typer(help="Scan sportsbook CSVs for two-way arbitrage opportunities.")


@app.command()
def scan(
    data_dir: Path = typer.Option(
        Path("data/raw"), "--data-dir", "-d", help="Directory containing sportsbook CSVs."
    ),
    bankroll: float = typer.Option(100.0, "--bankroll", "-b", help="Total stake to deploy per market."),
) -> None:
    opportunities = detect_arbitrage_from_dir(data_dir, bankroll=bankroll)
    if not opportunities:
        typer.echo("No arbitrage opportunities detected with current inputs.")
        raise typer.Exit()
    frame = opportunities_to_frame(opportunities)
    typer.echo(frame.to_markdown(index=False))


if __name__ == "__main__":
    app()
