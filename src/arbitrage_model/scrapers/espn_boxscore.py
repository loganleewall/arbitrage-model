from __future__ import annotations

import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webdriver import WebDriver

def scrape_boxscore(driver: WebDriver, game_url: str, wait_time: int = 5) -> pd.DataFrame:
    """
    Scrape an ESPN NBA box score page into a player-level stats DataFrame.
    Used for feature engineering/backtests, not directly for odds.
    """
    driver.get(game_url)
    wait = WebDriverWait(driver, wait_time)
    wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "Table__TD")))

    cells = [el.text for el in driver.find_elements(By.CLASS_NAME, "Table__TD")]
    caps = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    players, minutes, points = [], [], []
    # Simple heuristic: ESPN tables list player names with initials and periods
    for idx, cell in enumerate(cells):
        if cell and cell[0] in caps and "." in cell:
            players.append(cell.split("\n")[0])
            # offsets: minutes at idx+1, points at idx+13 in standard layout
            try:
                minutes.append(cells[idx + 1])
                points.append(cells[idx + 13])
            except Exception:
                minutes.append(None)
                points.append(None)

    return pd.DataFrame({"players": players, "minutes": minutes, "points": points})
