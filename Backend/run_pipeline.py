import subprocess
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


def run_step(title, command):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

    result = subprocess.run(
        command,
        cwd=BASE_DIR,
        check=False
    )

    if result.returncode != 0:
        print(f"\n❌ Step failed: {title}")
        sys.exit(result.returncode)

    print(f"✅ Completed: {title}")


def main():
    python = sys.executable

    # Command se route receive hoga
    # Example:
    # python run_pipeline.py DEL BLR

    if len(sys.argv) >= 3:
        origin = sys.argv[1].upper()
        destination = sys.argv[2].upper()
    else:
        origin = "DEL"
        destination = "BOM"

    print("\n" + "=" * 60)
    print("AEROINDEX ROUTE PIPELINE")
    print("=" * 60)
    print(f"Selected route: {origin} → {destination}")
    print("=" * 60)

    run_step(
        "1. Google Flights Scraper",
        [
            python,
            "scraper/search_flights.py",
            origin,
            destination
        ]
    )

    run_step(
        "2. Extract Google Flight Fares",
        [
            python,
            "scraper/extract_google_fares.py"
        ]
    )

    run_step(
        "3. Deduplicate Google Fares",
        [
            python,
            "scraper/deduplicate_google_fares.py"
        ]
    )

    run_step(
        "4. Clean Fare Data",
        [
            python,
            "pipeline/cleaner.py"
        ]
    )

    run_step(
        "5. Save Historical Data",
        [
            python,
            "pipeline/history_saver.py"
        ]
    )

    print("\n" + "=" * 60)
    print("🎉 COMPLETE PIPELINE FINISHED SUCCESSFULLY")
    print(f"Route completed: {origin} → {destination}")
    print("=" * 60)


if __name__ == "__main__":
    main()