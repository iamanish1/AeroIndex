from flask import Flask, jsonify, request
from flask_cors import CORS
from pathlib import Path
from collections import defaultdict
from urllib.parse import quote
import json
import statistics
import subprocess
import sys
import threading


app = Flask(__name__)
CORS(app)


# --------------------------------------------------
# PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

DATA_FILE = (
    BASE_DIR
    / "data"
    / "cleaned"
    / "flights_cleaned.json"
)

HISTORY_FILE = (
    BASE_DIR
    / "data"
    / "history"
    / "airfare_history.json"
)


# --------------------------------------------------
# PIPELINE STATUS
# --------------------------------------------------

pipeline_running = False
pipeline_lock = threading.Lock()

current_pipeline_route = {
    "from": "",
    "to": ""
}


def run_refresh_pipeline(origin, destination):
    global pipeline_running

    try:
        print("\n" + "=" * 60)
        print("STARTING FRESH AIRFARE PIPELINE")
        print("=" * 60)
        print(f"Route: {origin} → {destination}")
        print("=" * 60)

        python_path = sys.executable

        result = subprocess.run(
            [
                python_path,
                "run_pipeline.py",
                origin,
                destination
            ],
            cwd=BASE_DIR,
            check=False
        )

        if result.returncode == 0:
            print(
                f"Fresh pipeline completed successfully "
                f"for {origin} → {destination}"
            )
        else:
            print(
                f"Pipeline failed with exit code: "
                f"{result.returncode}"
            )

    except Exception as error:
        print(f"Pipeline error: {error}")

    finally:
        pipeline_running = False
        current_pipeline_route["from"] = ""
        current_pipeline_route["to"] = ""

        print("Pipeline status: stopped")


# --------------------------------------------------
# CITY NORMALIZATION
# --------------------------------------------------

CITY_ALIASES = {
    "delhi": "DEL",
    "new delhi": "DEL",
    "del": "DEL",

    "mumbai": "BOM",
    "bombay": "BOM",
    "bom": "BOM",

    "bangalore": "BLR",
    "bengaluru": "BLR",
    "blr": "BLR",

    "hyderabad": "HYD",
    "hyd": "HYD",

    "chennai": "MAA",
    "madras": "MAA",
    "maa": "MAA",

    "kolkata": "CCU",
    "calcutta": "CCU",
    "ccu": "CCU",

    "pune": "PNQ",
    "pnq": "PNQ",

    "goa": "GOI",
    "goi": "GOI",

    "ahmedabad": "AMD",
    "amd": "AMD",

    "jaipur": "JAI",
    "jai": "JAI",

    "lucknow": "LKO",
    "lko": "LKO",

    "patna": "PAT",
    "pat": "PAT",

    "kochi": "COK",
    "cochin": "COK",
    "cok": "COK",

    "guwahati": "GAU",
    "gau": "GAU",

    "chandigarh": "IXC",
    "ixc": "IXC",

    "srinagar": "SXR",
    "sxr": "SXR",
}


CITY_NAMES = {
    "DEL": "Delhi",
    "BOM": "Mumbai",
    "BLR": "Bengaluru",
    "HYD": "Hyderabad",
    "MAA": "Chennai",
    "CCU": "Kolkata",
    "PNQ": "Pune",
    "GOI": "Goa",
    "AMD": "Ahmedabad",
    "JAI": "Jaipur",
    "LKO": "Lucknow",
    "PAT": "Patna",
    "COK": "Kochi",
    "GAU": "Guwahati",
    "IXC": "Chandigarh",
    "SXR": "Srinagar",
}


# --------------------------------------------------
# AIRLINE CODES
# --------------------------------------------------

AIRLINE_CODES = {
    "IndiGo": "6E",
    "Air India": "AI",
    "Air India Express": "IX",
    "Akasa Air": "QP",
    "Vistara": "UK",
    "SpiceJet": "SG",
    "Go First": "G8",
    "Alliance Air": "9I",
}


# --------------------------------------------------
# ROUTE DISTANCES
# --------------------------------------------------

ROUTE_DISTANCES = {
    ("DEL", "BOM"): "1,148 km",
    ("BOM", "DEL"): "1,148 km",

    ("DEL", "BLR"): "1,740 km",
    ("BLR", "DEL"): "1,740 km",

    ("DEL", "HYD"): "1,260 km",
    ("HYD", "DEL"): "1,260 km",

    ("DEL", "MAA"): "1,760 km",
    ("MAA", "DEL"): "1,760 km",

    ("DEL", "CCU"): "1,300 km",
    ("CCU", "DEL"): "1,300 km",

    ("DEL", "GOI"): "1,510 km",
    ("GOI", "DEL"): "1,510 km",

    ("DEL", "AMD"): "755 km",
    ("AMD", "DEL"): "755 km",

    ("DEL", "PNQ"): "1,175 km",
    ("PNQ", "DEL"): "1,175 km",

    ("DEL", "JAI"): "235 km",
    ("JAI", "DEL"): "235 km",

    ("DEL", "LKO"): "425 km",
    ("LKO", "DEL"): "425 km",

    ("DEL", "PAT"): "850 km",
    ("PAT", "DEL"): "850 km",

    ("DEL", "COK"): "2,080 km",
    ("COK", "DEL"): "2,080 km",

    ("DEL", "GAU"): "1,450 km",
    ("GAU", "DEL"): "1,450 km",

    ("DEL", "IXC"): "245 km",
    ("IXC", "DEL"): "245 km",

    ("DEL", "SXR"): "645 km",
    ("SXR", "DEL"): "645 km",

    ("BOM", "BLR"): "840 km",
    ("BLR", "BOM"): "840 km",

    ("BOM", "HYD"): "620 km",
    ("HYD", "BOM"): "620 km",

    ("BOM", "MAA"): "1,030 km",
    ("MAA", "BOM"): "1,030 km",

    ("BOM", "GOI"): "430 km",
    ("GOI", "BOM"): "430 km",

    ("BLR", "HYD"): "500 km",
    ("HYD", "BLR"): "500 km",

    ("BLR", "MAA"): "290 km",
    ("MAA", "BLR"): "290 km",

    ("BLR", "GOI"): "480 km",
    ("GOI", "BLR"): "480 km",

    ("BLR", "CCU"): "1,560 km",
    ("CCU", "BLR"): "1,560 km",

    ("HYD", "MAA"): "520 km",
    ("MAA", "HYD"): "520 km",

    ("HYD", "GOI"): "530 km",
    ("GOI", "HYD"): "530 km",
}


# --------------------------------------------------
# FILE HELPERS
# --------------------------------------------------

def load_json_file(file_path, default):
    if not file_path.exists():
        return default

    try:
        with file_path.open(
            "r",
            encoding="utf-8"
        ) as file:
            return json.load(file)

    except Exception as error:
        print(
            f"Error loading {file_path}: {error}"
        )
        return default


def get_route_file(origin, destination):
    return (
        BASE_DIR
        / "data"
        / "routes"
        / f"{origin}_{destination}"
        / "flights_cleaned.json"
    )


def get_route_history_file(origin, destination):
    return (
        BASE_DIR
        / "data"
        / "routes"
        / f"{origin}_{destination}"
        / "history.json"
    )


def load_fares(origin, destination):
    route_file = get_route_file(
        origin,
        destination
    )

    data = load_json_file(
        route_file,
        []
    )

    if isinstance(data, list) and data:
        return data

    # Reverse route fallback
    reverse_file = get_route_file(
        destination,
        origin
    )

    reverse_data = load_json_file(
        reverse_file,
        []
    )

    if isinstance(reverse_data, list):
        return reverse_data

    # Old common file fallback
    old_data = load_json_file(
        DATA_FILE,
        []
    )

    if isinstance(old_data, list):
        return old_data

    return []


def load_history(origin, destination):
    route_history_file = get_route_history_file(
        origin,
        destination
    )

    data = load_json_file(
        route_history_file,
        []
    )

    if isinstance(data, list) and data:
        return data

    reverse_history_file = get_route_history_file(
        destination,
        origin
    )

    reverse_data = load_json_file(
        reverse_history_file,
        []
    )

    if isinstance(reverse_data, list):
        return reverse_data

    old_data = load_json_file(
        HISTORY_FILE,
        []
    )

    if isinstance(old_data, list):
        return old_data

    return []


# --------------------------------------------------
# CITY HELPERS
# --------------------------------------------------

def normalize_city(value):
    value = str(
        value or ""
    ).strip().lower()

    if not value:
        return ""

    return CITY_ALIASES.get(
        value,
        value.upper()
    )


def city_name(code):
    return CITY_NAMES.get(
        code,
        code
    )


def route_distance(origin, destination):
    return ROUTE_DISTANCES.get(
        (origin, destination),
        "Distance unavailable"
    )


# --------------------------------------------------
# BOOKING URL
# --------------------------------------------------

def booking_url(origin, destination):
    origin_name = quote(
        city_name(origin)
    )

    destination_name = quote(
        city_name(destination)
    )

    return (
        "https://www.google.com/travel/flights?"
        f"q=Flights%20from%20{origin_name}%20to%20"
        f"{destination_name}"
    )


# --------------------------------------------------
# NUMBER HELPERS
# --------------------------------------------------

def safe_float(value):
    try:
        number = float(value)

        if number > 0:
            return number

        return 0.0

    except (
        TypeError,
        ValueError
    ):
        return 0.0


def percentage_difference(value, reference):
    if reference <= 0:
        return 0.0

    return round(
        (
            (value - reference)
            / reference
        ) * 100,
        1
    )


# --------------------------------------------------
# HOME API
# --------------------------------------------------

@app.get("/")
def home():
    return jsonify({
        "app": "AeroIndex API",
        "status": "running",
        "version": "5.0"
    })


# --------------------------------------------------
# REFRESH API
# --------------------------------------------------

@app.post("/api/refresh")
def refresh_pipeline():
    global pipeline_running

    body = request.get_json(
        silent=True
    ) or {}

    origin = normalize_city(
        body.get("from")
        or request.args.get("from")
        or "DEL"
    )

    destination = normalize_city(
        body.get("to")
        or request.args.get("to")
        or "BOM"
    )

    if not origin or not destination:
        return jsonify({
            "error": "Both from and to cities are required."
        }), 400

    if origin == destination:
        return jsonify({
            "error": "From and to cities cannot be same."
        }), 400

    with pipeline_lock:
        if pipeline_running:
            return jsonify({
                "status": "already_running",
                "message": (
                    "Fresh airfare data is already being collected."
                ),
                "from": origin,
                "to": destination
            }), 202

        pipeline_running = True

        current_pipeline_route["from"] = origin
        current_pipeline_route["to"] = destination

    thread = threading.Thread(
        target=run_refresh_pipeline,
        args=(
            origin,
            destination
        ),
        daemon=True
    )

    thread.start()

    return jsonify({
        "status": "started",
        "message": (
            "Fresh airfare data collection has started."
        ),
        "from": origin,
        "to": destination
    }), 202


@app.get("/api/refresh-status")
def refresh_status():
    return jsonify({
        "running": pipeline_running,
        "from": current_pipeline_route["from"],
        "to": current_pipeline_route["to"]
    })


# --------------------------------------------------
# AIRFARE API
# --------------------------------------------------

@app.get("/api/airfare")
def airfare():
    origin = normalize_city(
        request.args.get("from")
    )

    destination = normalize_city(
        request.args.get("to")
    )

    if not origin or not destination:
        return jsonify({
            "error": "Both from and to cities are required."
        }), 400

    if origin == destination:
        return jsonify({
            "error": (
                "Departure and arrival cities "
                "cannot be the same."
            )
        }), 400

    all_fares = load_fares(
        origin,
        destination
    )

    if not all_fares:
        return jsonify({
            "error": (
                f"No fare data found for "
                f"{city_name(origin)} to "
                f"{city_name(destination)}."
            ),
            "from": city_name(origin),
            "to": city_name(destination)
        }), 404

    route_fares = [
        item
        for item in all_fares
        if (
            normalize_city(item.get("origin"))
            == origin
            and
            normalize_city(item.get("destination"))
            == destination
        )
    ]

    is_reverse_route = False

    if not route_fares:
        route_fares = [
            item
            for item in all_fares
            if (
                normalize_city(item.get("origin"))
                == destination
                and
                normalize_city(item.get("destination"))
                == origin
            )
        ]

        if route_fares:
            is_reverse_route = True

    # Route folder ke data mein origin/destination missing
    # ho toh us route folder ke saare fares use honge.
    if not route_fares:
        route_fares = all_fares

    valid_records = []

    for item in route_fares:
        fare = safe_float(
            item.get("fare")
        )

        if fare <= 0:
            continue

        valid_records.append({
            **item,
            "fare": fare
        })

    if not valid_records:
        return jsonify({
            "error": "Fare values are unavailable for this route."
        }), 404

    fare_values = [
        item["fare"]
        for item in valid_records
    ]

    current_average = round(
        statistics.mean(fare_values),
        2
    )

    current_lowest = round(
        min(fare_values),
        2
    )

    current_highest = round(
        max(fare_values),
        2
    )

    base_fare = current_lowest if current_lowest > 0 else current_average

    index_value = round(
        (
            current_average
            / base_fare
        ) * 100,
        2
    )

    # --------------------------------------------------
    # AIRLINE DATA
    # --------------------------------------------------

    airline_groups = defaultdict(list)

    for item in valid_records:
        airline = (
            item.get("airline")
            or "Unknown airline"
        )

        airline_groups[airline].append(
            item["fare"]
        )

    airline_average_values = {
        airline: statistics.mean(fares)
        for airline, fares
        in airline_groups.items()
    }

    cheapest_airline_average = min(
        airline_average_values.values()
    )

    airline_data = []

    for airline, fares in airline_groups.items():
        airline_lowest = round(
            min(fares),
            2
        )

        airline_average = round(
            statistics.mean(fares),
            2
        )

        difference_percent = percentage_difference(
            airline_average,
            current_average
        )

        is_best_value = (
            airline_average
            == cheapest_airline_average
        )

        if is_best_value:
            change_text = "Best value"
        elif difference_percent > 0:
            change_text = f"+{difference_percent}%"
        else:
            change_text = f"{difference_percent}%"

        airline_data.append({
            "name": airline,
            "code": AIRLINE_CODES.get(
                airline,
                airline[:2].upper()
            ),
            "lowestFare": airline_lowest,
            "averageFare": airline_average,
            "fare": airline_lowest,
            "change": change_text,
            "differencePercent": difference_percent,
            "observations": len(fares)
        })

    airline_data.sort(
        key=lambda item: item["lowestFare"]
    )

    # --------------------------------------------------
    # HISTORY
    # --------------------------------------------------

    saved_history = load_history(
        origin,
        destination
    )

    history = []

    for item in saved_history:
        average_fare = safe_float(
            item.get("averageFare")
        )

        lowest_fare = safe_float(
            item.get("lowestFare")
        )

        highest_fare = safe_float(
            item.get("highestFare")
        )

        if average_fare <= 0:
            continue

        history.append({
            "name": item.get(
                "date",
                "Unknown"
            ),
            "avg": round(
                average_fare,
                2
            ),
            "low": round(
                lowest_fare,
                2
            ),
            "high": round(
                highest_fare,
                2
            ),
            "observations": item.get(
                "observations",
                0
            )
        })

    if not history:
        history = [{
            "name": "Latest",
            "avg": current_average,
            "low": current_lowest,
            "high": current_highest,
            "observations": len(valid_records)
        }]

    return jsonify({
        "index": index_value,

        "averageFare": current_average,
        "lowestFare": current_lowest,
        "highestFare": current_highest,

        "baseFare": base_fare,
        "currency": "INR",

        "from": city_name(origin),
        "to": city_name(destination),

        "fromCode": origin,
        "toCode": destination,

        "route": (
            f"{city_name(origin)}-"
            f"{city_name(destination)}"
        ),

        "distance": route_distance(
            origin,
            destination
        ),

        "bestBookingWindow": "15–30 days",
        "priceChange": "Live data",
        "observations": len(valid_records),
        "source": "Google Flights",
        "isReverseRoute": is_reverse_route,

        "bookingUrl": booking_url(
            origin,
            destination
        ),

        "airlines": airline_data,
        "history": history
    })


# --------------------------------------------------
# SERVER START
# --------------------------------------------------

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
        use_reloader=False
    )
