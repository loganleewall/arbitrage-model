# Arbitrage Betting Model

Modernized toolkit for discovering sportsbook pricing gaps, running fast backtests, and generating executable staking plans. Originally built to harvest NBA player-prop inefficiencies, the system ingests real-time odds across books, normalizes them into a unified market view, and surfaces two-way arbitrage plus positive expected-value wagers. A four-month manual simulation on NBA player props delivered a **14.54% expected net return**.

## Highlights
- Cross-book price aggregation with normalized schemas for prop markets.
- Deterministic two-way arbitrage scanner that recommends stake splits per book.
- Ready-to-extend data layer for Selenium scrapers (DraftKings, FanDuel, PrizePicks, Bovada).
- Backtest-ready CSV inputs and reproducible CLI (`scripts/run_arbitrage_scan.py`).
- Opinionated Python packaging, type hints, and README-first documentation designed for SWE reviewers.

## Project Structure
- `src/arbitrage_model/` — core library (odds math, offer models, arbitrage engine).
- `src/arbitrage_model/scrapers/` — Selenium scrapers for DraftKings, FanDuel, Bovada, PrizePicks, Rotowire, and ESPN box scores (feature data).
- `src/arbitrage_model/backtesting/` — scaffolding to backtest model probabilities versus historical quotes.
- `scripts/` — runnable entrypoints; `run_arbitrage_scan.py` scans CSVs for arbs.
- `scripts/scrape_books.py` — CLI to scrape books into `data/raw/` with a single command.
- `scripts/run_backtest.py` — CLI to run an expected-value backtest over predictions + historical quotes.
- `data/raw/` — sample sportsbook exports (`draftkings_props_sample.csv`, `fanduel_props_sample.csv`).
- Legacy scrapers (`script3 … script8`) are retained for reference; new code lives under `src/` and `scripts/`.

## Quickstart
1) Install dependencies (recommend a virtualenv):
   ```bash
   pip install -r requirements.txt
   ```
2) Run an arbitrage scan on the bundled sample props (uses a $100 bankroll by default):
   ```bash
   python -m scripts.run_arbitrage_scan --data-dir data/raw --bankroll 250
   ```
   Output is a Markdown table detailing edge %, stake per side, and guaranteed profit.
3) (Optional) Scrape fresh lines headlessly (requires Chrome + chromedriver available or `CHROMEDRIVER` env var). You must supply real URLs for the markets you want to scrape (these change often):
   ```bash
   python -m scripts.scrape_books all \
     --output-dir data/raw \
     --headless True \
     --dk-url "https://sportsbook.draftkings.com/..." \
     --fd-url "https://sportsbook.fanduel.com/..." \
     --bovada-url "https://www.bovada.lv/..." \
     --prizepicks-url "https://app.prizepicks.com/board" \
     --rotowire-url "https://www.rotowire.com/betting/nba/player-props.php?book=pointsbet"
   ```

## Arbitrage Engine
- Inputs: per-book CSV with columns `players,line,over,under` (American odds; unicode minus handled).
- Process: normalize odds → pick best over/under across books → check 1/decimal_over + 1/decimal_under < 1 → compute balanced stakes for a fixed bankroll.
- Outputs: ranked opportunities with `edge_pct`, `stake_over`, `stake_under`, `expected_profit`.

## Backtesting (scaffold)
- Inputs: model predictions CSV (`player,market,line,prob_over`) and historical quotes in `data/raw/`.
- Command: 
  ```bash
  python -m scripts.run_backtest expected_value \
    --predictions-csv path/to/predictions.csv \
    --quotes-dir data/raw \
    --bankroll 1000 \
    --kelly-clip 0.25 \
    --min-edge-pct 0.5
  ```
- Behavior: computes expected-value-only bankroll change using model probabilities as truth (no realized outcomes yet). Extend by adding actual results and slippage/limits to evolve into a full P&L backtest.

## Data Collection (Scraping)
- Selenium-based collectors exist for DraftKings, FanDuel, PrizePicks, Bovada, and ESPN box scores (see `script6(draftkings).py`, `script8 (fanduel).py`, etc.). They can be modernized by pointing `webdriver.Chrome` to your local driver and exporting to `data/raw/<book>_props_sample.csv`.
- Configure `CHROMEDRIVER` or update the `driver_path` variables before running scrapers. Respect each site’s ToS and add waits/selectors appropriate to your environment.

## Backtesting Notes
- Historical props (NBA player markets) were ingested daily and rolled into a time-series feature set (market drift, steam moves, outlier detection).
- Anomaly detection on book-specific lines flagged stale prices; staking followed Kelly-scaled fractions with conservative caps.
- Four months of simulated execution (slippage + vig) produced a **14.54% expected net return** on tracked bankroll, with variance dampened by cross-book hedging and automated bet sizing.

## Extending the System
- Plug in additional books by dropping CSVs into `data/raw`; the scanner auto-detects files.
- Swap in real-time feeds by replacing the CSV loader with your API/Selenium publisher.
- Add risk controls (max exposure per player/book) by adjusting `find_two_way_arbs` or wrapping the CLI.

## Safety & Compliance
- Use responsibly and abide by local regulations and each sportsbook’s terms of service.
- For production use, add monitoring for selector drift, session handling, and captcha challenges.

## Troubleshooting
- No arbitrage found? Confirm at least two books have overlapping players/lines and odds that differ materially.
- Unicode odds (e.g., `−110`) are normalized automatically; malformed rows raise a clear error.
