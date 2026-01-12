from __future__ import annotations

import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webdriver import WebDriver

from arbitrage_model.odds import normalize_american_odds


def scrape_bovada(driver: WebDriver, url: str, wait_time: int = 12) -> pd.DataFrame:
    """
    Scrape Bovada player props into a normalized DataFrame.

    Bovada's DOM is volatile; selectors below target over/under blocks and price cells.
    Verify selectors when running in your region/environment.
    """
    driver.get(url)
    wait = WebDriverWait(driver, wait_time)

    wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "over-under-block__title")))

    names = [el.text for el in driver.find_elements(By.CLASS_NAME, "over-under-block__title") if el.text]
    lines = [el.text for el in driver.find_elements(By.CLASS_NAME, "over-under-block__over-under") if el.text]
    price_cells = [el.text for el in driver.find_elements(By.CLASS_NAME, "bet-price") if el.text]

    overs, unders = _split_odds(price_cells)

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
