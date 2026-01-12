from __future__ import annotations

from typing import Optional

import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webdriver import WebDriver

from arbitrage_model.odds import normalize_american_odds


def scrape_draftkings(driver: WebDriver, url: str, wait_time: int = 12) -> pd.DataFrame:
    """
    Scrape DraftKings NBA player props (over/under) into a DataFrame with
    columns: players, line, over, under.

    The selectors are anchored on current DraftKings class names and may need
    refresh if the site changes; runs with explicit waits to reduce flakiness.
    """
    driver.get(url)
    wait = WebDriverWait(driver, wait_time)

    wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "sportsbook-row-name")))

    names = [el.text for el in driver.find_elements(By.CLASS_NAME, "sportsbook-row-name") if el.text]
    # Lines (duplicated for over/under; we keep every other as the prop number)
    raw_lines = [el.text for el in driver.find_elements(By.CLASS_NAME, "sportsbook-outcome-cell__line") if el.text]
    lines = [raw_lines[i] for i in range(len(raw_lines)) if i % 2 == 0]

    raw_odds = [el.text for el in driver.find_elements(By.CLASS_NAME, "sportsbook-outcome-cell__element") if el.text]
    overs, unders = _split_odds(raw_odds)

    rows = []
    for name, line, over, under in zip(names, lines, overs, unders):
        try:
            rows.append(
                {
                    "players": name.strip(),
                    "line": float(line),
                    "over": normalize_american_odds(over),
                    "under": normalize_american_odds(under),
                }
            )
        except Exception:
            # Skip malformed rows; log/debug in real runner
            continue
    return pd.DataFrame(rows)


def _split_odds(raw: list[str]) -> tuple[list[str], list[str]]:
    overs, unders = [], []
    odds = list(raw)
    while odds:
        if len(odds) < 2:
            break
        overs.append(odds[0])
        unders.append(odds[1])
        odds = odds[2:]
    return overs, unders
