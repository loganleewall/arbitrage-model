from __future__ import annotations

import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webdriver import WebDriver

def scrape_rotowire(driver: WebDriver, url: str, wait_time: int = 12) -> pd.DataFrame:
    """
    Scrape Rotowire's aggregated props table (PointsBet view by default).

    Rotowire lists lines but not explicit American odds; we capture player and line
    for anomaly detection or cross-checking against books. Odds fields are left
    empty to avoid misleading the arbitrage engine.
    """
    driver.get(url)
    wait = WebDriverWait(driver, wait_time)

    wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "webix_ss_center_scroll")))

    raw_blocks = [el.text for el in driver.find_elements(By.CLASS_NAME, "webix_ss_center_scroll") if el.text]
    formatted = []
    for block in raw_blocks:
        chunk = [line for line in block.split("\n") if line]
        formatted.append(chunk)

    if len(formatted) < 2:
        return pd.DataFrame(columns=["players", "line", "over", "under"])

    players = formatted[0] + formatted[2] if len(formatted) > 2 else formatted[0]
    lines = formatted[1] if len(formatted) > 1 else []

    rows = []
    for name, line in zip(players, lines):
        try:
            rows.append({"players": name.strip(), "line": float(line), "over": None, "under": None})
        except Exception:
            continue
    return pd.DataFrame(rows)
