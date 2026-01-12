from __future__ import annotations

import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webdriver import WebDriver

from arbitrage_model.odds import normalize_american_odds


def scrape_fanduel(driver: WebDriver, url: str, wait_time: int = 15) -> pd.DataFrame:
    """
    Scrape FanDuel NBA player props into a normalized DataFrame.

    Notes:
    - FanDuel frequently changes class names; selectors may need updates.
    - We target generic sportsbook outcome classes (`sportsbook-outcome-cell__line`
      and `sportsbook-outcome-cell__element`) which tend to be stable.
    """
    driver.get(url)
    wait = WebDriverWait(driver, wait_time)

    wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "sportsbook-outcome-cell__line")))

    raw_lines = [el.text for el in driver.find_elements(By.CLASS_NAME, "sportsbook-outcome-cell__line") if el.text]
    # Every other element is the numeric line; odd indices are labels like "O/U"
    lines = [raw_lines[i] for i in range(len(raw_lines)) if i % 2 == 0]

    raw_odds = [el.text for el in driver.find_elements(By.CLASS_NAME, "sportsbook-outcome-cell__element") if el.text]
    overs, unders = _split_odds(raw_odds)

    # Player names are nested; target aria-label-based selector for resiliency
    name_elements = driver.find_elements(By.CSS_SELECTOR, "[data-test-id='event-title']") or driver.find_elements(
        By.CLASS_NAME, "event-title"
    )
    names = [el.text for el in name_elements if el.text]

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
