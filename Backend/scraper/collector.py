import json
from pathlib import Path
from datetime import date, timedelta

from playwright.sync_api import sync_playwright


ORIGIN = "DEL"
DESTINATION = "BOM"
DAYS_AHEAD = 15


def collect_flight_page():
    departure_date = date.today() + timedelta(days=DAYS_AHEAD)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(viewport={"width": 1440, "height": 1000})

        page.goto(
            "https://www.google.com/travel/flights",
            wait_until="domcontentloaded",
            timeout=60000,
        )

        page.wait_for_timeout(5000)

        print("Page title:", page.title())
        print("Current URL:", page.url)

        # Page ka visible text save kar rahe hain.
        # Isse hum selectors identify kar sakte hain.
        visible_text = page.locator("body").inner_text()
        Path("data/raw/google_flights_page.txt").write_text(
            visible_text,
            encoding="utf-8",
        )

        print("Visible page text saved.")
        print("Departure date:", departure_date)

        browser.close()


if __name__ == "__main__":
    collect_flight_page()
