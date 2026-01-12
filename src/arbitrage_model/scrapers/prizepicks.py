from __future__ import annotations

import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webdriver import WebDriver

from arbitrage_model.odds import normalize_american_odds


def scrape_prizepicks(driver: WebDriver, url: str, wait_time: int = 20) -> pd.DataFrame:
    """
    Scrape PrizePicks player props.

    PrizePicks presents flex odds rather than American odds; to keep compatibility
    with the arbitrage pipeline, we treat over/under payout multipliers as
    pseudo-odds. Update selectors if the React app changes.
    """
    driver.get(url)
    wait = WebDriverWait(driver, wait_time)

    wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class,'player-name')]")))

    names = [el.text for el in driver.find_elements(By.XPATH, "//div[contains(@class,'player-name')]") if el.text]
    lines = [el.text for el in driver.find_elements(By.XPATH, "//div[contains(@class,'player-projection')]") if el.text]

    # PrizePicks uses multipliers; capture both over and under payout strings.
    payouts = [el.text for el in driver.find_elements(By.XPATH, "//div[contains(@class,'pp-over-under')]//div") if el.text]
    overs, unders = _split_odds(payouts)

    rows = []
    for name, line, over, under in zip(names, lines, overs, unders):
        try:
            rows.append(
                {
                    "players": name.strip(),
                    "line": float(line),
                    "over": _to_fake_american(over),
                    "under": _to_fake_american(under),
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


def _to_fake_american(multiplier_text: str) -> int:
    """
    Convert a PrizePicks multiplier string to a pseudo-American odds for compatibility.
    Example: "1.25x" -> +125, "0.9x" -> -111 (approx).
    """
    m = multiplier_text.lower().replace("x", "").strip()
    mult = float(m)
    # approximate: convert decimal to american
    if mult >= 1:
        return int(round((mult - 1) * 100))
    return -int(round(100 / mult - 100))
