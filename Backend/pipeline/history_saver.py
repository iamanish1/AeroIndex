import json
from pathlib import Path
from datetime import datetime, timezone


BASE_DIR = Path(__file__).resolve().parents[1]

CLEANED_FILE = (
    BASE_DIR
    / "data"
    / "cleaned"
    / "flights_cleaned.json"
)

ROUTE_FILE = (
    BASE_DIR
    / "data"
    / "raw"
    / "current_route.txt"
)

# Existing app compatibility ke liye
HISTORY_FILE = (
    BASE_DIR
    / "data"
    / "history"
    / "airfare_history.json"
)


def load_json(path, default):
    if not path.exists():
        return default

    try:
        with path.open(
            "r",
            encoding="utf-8"
        ) as file:
            return json.load(file)

    except (
        json.JSONDecodeError,
        OSError
    ):
        return default


def get_current_route():
    """
    current_route.txt ka format:
    DEL,GOI
    """

    if not ROUTE_FILE.exists():
        print(
            "⚠️ Route file nahi mili. "
            "Default route DEL_BOM use hoga."
        )
        return "DEL", "BOM"

    route_text = ROUTE_FILE.read_text(
        encoding="utf-8"
    ).strip()

    if "," not in route_text:
        print(
            "⚠️ Route format galat hai. "
            "Default route DEL_BOM use hoga."
        )
        return "DEL", "BOM"

    origin, destination = route_text.split(
        ",",
        1
    )

    return (
        origin.strip().upper(),
        destination.strip().upper()
    )


def get_route_history_file(origin, destination):
    """
    Example:
    data/routes/DEL_GOI/history.json
    """

    route_folder = (
        BASE_DIR
        / "data"
        / "routes"
        / f"{origin}_{destination}"
    )

    route_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    return route_folder / "history.json"


def calculate_fare_summary(flights):
    fares = []

    for item in flights:
        fare = item.get("fare")

        if fare is None:
            continue

        try:
            fare = float(fare)
        except (
            TypeError,
            ValueError
        ):
            continue

        if fare > 0:
            fares.append(fare)

    if not fares:
        return None

    return {
        "averageFare": round(
            sum(fares) / len(fares),
            2
        ),
        "lowestFare": round(
            min(fares),
            2
        ),
        "highestFare": round(
            max(fares),
            2
        ),
        "observations": len(fares)
    }


def save_history():
    origin, destination = get_current_route()

    print("\n" + "=" * 60)
    print("ROUTE-WISE HISTORY SAVER")
    print("=" * 60)
    print(f"Route: {origin} → {destination}")
    print("=" * 60)

    flights = load_json(
        CLEANED_FILE,
        []
    )

    if not flights:
        print("❌ No cleaned flight data found.")
        return

    summary = calculate_fare_summary(
        flights
    )

    if summary is None:
        print("❌ No valid fare values found.")
        return

    route_history_file = get_route_history_file(
        origin,
        destination
    )

    history = load_json(
        route_history_file,
        []
    )

    today = datetime.now(
        timezone.utc
    ).strftime("%Y-%m-%d")

    new_record = {
        "date": today,
        "averageFare": summary["averageFare"],
        "lowestFare": summary["lowestFare"],
        "highestFare": summary["highestFare"],
        "observations": summary["observations"]
    }

    existing_index = next(
        (
            index
            for index, item in enumerate(history)
            if item.get("date") == today
        ),
        None
    )

    if existing_index is not None:
        history[existing_index] = new_record
    else:
        history.append(new_record)

    history.sort(
        key=lambda item: item.get(
            "date",
            ""
        )
    )

    with route_history_file.open(
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            history,
            file,
            indent=2,
            ensure_ascii=False
        )

    # Existing app ke liye old history file bhi update hogi
    HISTORY_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with HISTORY_FILE.open(
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            history,
            file,
            indent=2,
            ensure_ascii=False
        )

    print("\nHistory saved successfully:")
    print(
        json.dumps(
            new_record,
            indent=2,
            ensure_ascii=False
        )
    )

    print(
        f"\nRoute history saved to:"
        f"\n{route_history_file}"
    )


if __name__ == "__main__":
    save_history()