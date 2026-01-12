from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd
import typer

from arbitrage_model.scrapers.base import chrome_driver
from arbitrage_model.scrapers.bovada import scrape_bovada
from arbitrage_model.scrapers.draftkings import scrape_draftkings
from arbitrage_model.scrapers.fanduel import scrape_fanduel
from arbitrage_model.scrapers.prizepicks import scrape_prizepicks
from arbitrage_model.scrapers.rotowire import scrape_rotowire

app = typer.Typer(help="Scrape sportsbook lines into normalized CSVs.")


@app.command()
def all(
    output_dir: Path = typer.Option(Path("data/raw"), "--output-dir", "-o"),
    headless: bool = typer.Option(True, help="Run Chrome in headless mode."),
    dk_url: str = typer.Option(..., help="DraftKings NBA props URL."),
    fd_url: str = typer.Option(..., help="FanDuel NBA props URL."),
    bovada_url: str = typer.Option(..., help="Bovada player props URL."),
    prizepicks_url: str = typer.Option(..., help="PrizePicks board URL."),
    rotowire_url: str = typer.Option(..., help="Rotowire props page URL."),
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    with chrome_driver(headless=headless) as driver:
        _write(scrape_draftkings(driver, url=dk_url), output_dir / "draftkings_props_latest.csv")
        _write(scrape_fanduel(driver, url=fd_url), output_dir / "fanduel_props_latest.csv")
        _write(scrape_bovada(driver, url=bovada_url), output_dir / "bovada_props_latest.csv")
        _write(scrape_prizepicks(driver, url=prizepicks_url), output_dir / "prizepicks_props_latest.csv")
        _write(scrape_rotowire(driver, url=rotowire_url), output_dir / "rotowire_props_latest.csv")
    typer.echo(f"Wrote scraped props to {output_dir}")


@app.command()
def draftkings(
    output: Path = typer.Option(Path("data/raw/draftkings_props_latest.csv"), "--output", "-o"),
    headless: bool = typer.Option(True),
    url: str = typer.Option(..., help="DraftKings NBA props URL."),
) -> None:
    with chrome_driver(headless=headless) as driver:
        df = scrape_draftkings(driver, url=url)
        _write(df, output)
        typer.echo(f"Wrote DraftKings props to {output}")


@app.command()
def fanduel(
    output: Path = typer.Option(Path("data/raw/fanduel_props_latest.csv"), "--output", "-o"),
    headless: bool = typer.Option(True),
    url: str = typer.Option(..., help="FanDuel NBA props URL."),
) -> None:
    with chrome_driver(headless=headless) as driver:
        df = scrape_fanduel(driver, url=url)
        _write(df, output)
        typer.echo(f"Wrote FanDuel props to {output}")


@app.command()
def bovada(
    output: Path = typer.Option(Path("data/raw/bovada_props_latest.csv"), "--output", "-o"),
    headless: bool = typer.Option(True),
    url: str = typer.Option(..., help="Bovada player props URL."),
) -> None:
    with chrome_driver(headless=headless) as driver:
        df = scrape_bovada(driver, url=url)
        _write(df, output)
        typer.echo(f"Wrote Bovada props to {output}")


@app.command()
def prizepicks(
    output: Path = typer.Option(Path("data/raw/prizepicks_props_latest.csv"), "--output", "-o"),
    headless: bool = typer.Option(True),
    url: str = typer.Option(..., help="PrizePicks board URL."),
) -> None:
    with chrome_driver(headless=headless) as driver:
        df = scrape_prizepicks(driver, url=url)
        _write(df, output)
        typer.echo(f"Wrote PrizePicks props to {output}")


@app.command()
def rotowire(
    output: Path = typer.Option(Path("data/raw/rotowire_props_latest.csv"), "--output", "-o"),
    headless: bool = typer.Option(True),
    url: str = typer.Option(..., help="Rotowire props page URL."),
) -> None:
    with chrome_driver(headless=headless) as driver:
        df = scrape_rotowire(driver, url=url)
        _write(df, output)
        typer.echo(f"Wrote Rotowire props to {output}")


def _write(df: pd.DataFrame, path: Path) -> None:
    if df.empty:
        typer.echo(f"Warning: no rows scraped for {path.name}")
    df.to_csv(path, index=False)


if __name__ == "__main__":
    app()
