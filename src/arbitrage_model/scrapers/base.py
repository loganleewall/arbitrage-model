from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Iterator

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


def _resolve_driver_path() -> str | None:
    """Resolve chromedriver path from env or system default."""
    return os.environ.get("CHROMEDRIVER")


def build_chrome(headless: bool = True) -> webdriver.Chrome:
    """
    Create a Chrome driver with sensible defaults.

    Notes:
    - Requires CHROMEDRIVER env var pointing to chromedriver binary, or chromedriver on PATH.
    - Headless by default; set headless=False for interactive debugging.
    """
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver_path = _resolve_driver_path()
    service = Service(executable_path=driver_path) if driver_path else Service()
    return webdriver.Chrome(service=service, options=options)


@contextmanager
def chrome_driver(headless: bool = True) -> Iterator[webdriver.Chrome]:
    driver = build_chrome(headless=headless)
    try:
        yield driver
    finally:
        driver.quit()
