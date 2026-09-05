from datetime import date, timedelta
from pathlib import Path
import sys
from playwright.sync_api import sync_playwright


# Default route agar koi route provide na kiya jaye
DEFAULT_ORIGIN = "DEL"
DEFAULT_DESTINATION = "BOM"

DAYS_AHEAD = 15


def get_route():
    """
    Command line se airport codes leta hai.

    Example:
    python search_flights.py DEL BLR
    """

    if len(sys.argv) >= 3:
        origin = sys.argv[1].upper()
        destination = sys.argv[2].upper()
    else:
        origin = DEFAULT_ORIGIN
        destination = DEFAULT_DESTINATION

    return origin, destination


def main():
    origin, destination = get_route()

    departure_date = date.today() + timedelta(days=DAYS_AHEAD)

    search_url = (
        "https://www.google.com/travel/flights"
        f"?q=Flights%20from%20{origin}%20to%20{destination}"
        f"%20on%20{departure_date.isoformat()}"
    )

    print("\n" + "=" * 60)
    print("GOOGLE FLIGHTS SEARCH")
    print("=" * 60)
    print(f"Origin: {origin}")
    print(f"Destination: {destination}")
    print(f"Departure date: {departure_date}")
    print(f"Search URL: {search_url}")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True
        )

        page = browser.new_page(
            viewport={
                "width": 1440,
                "height": 1000,
            }
        )

        try:
            page.goto(
                search_url,
                wait_until="domcontentloaded",
                timeout=60000,
            )

            # Google Flights ko results load karne ka time
            page.wait_for_timeout(10000)

            print("Title:", page.title())
            print("URL:", page.url)

            text = page.locator("body").inner_text()

            output_path = Path(
                "data/raw/google_flights_results.txt"
            )

            output_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            output_path.write_text(
                text,
                encoding="utf-8",
            )

            # Route information save karna
            route_path = Path(
                "data/raw/current_route.txt"
            )

            route_path.write_text(
                f"{origin},{destination}",
                encoding="utf-8",
            )

            print("\nResults text saved.")
            print(f"Route saved: {origin} → {destination}")
            print("\nFirst 3000 characters:\n")
            print(text[:3000])

            page.wait_for_timeout(3000)

        except Exception as error:
            print(
                "\n❌ Google Flights scraping error:",
                error
            )
            sys.exit(1)

        finally:
            browser.close()
            print("\nBrowser closed.")


if __name__ == "__main__":
    main()