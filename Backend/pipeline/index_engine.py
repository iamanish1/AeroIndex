import json
from pathlib import Path
from collections import defaultdict


CLEANED_FILE = Path("data/cleaned/flights_cleaned.json")


BASE_FARES = {
    "Delhi-Mumbai": 7000,
    "Mumbai-Bangalore": 6500,
    "Delhi-Bangalore": 8000,
    "Delhi-Kolkata": 7200,
    "Mumbai-Kolkata": 8500,
    "Bangalore-Hyderabad": 4500,
}


ROUTE_WEIGHTS = {
    "Delhi-Mumbai": 0.25,
    "Mumbai-Bangalore": 0.20,
    "Delhi-Bangalore": 0.15,
    "Delhi-Kolkata": 0.15,
    "Mumbai-Kolkata": 0.15,
    "Bangalore-Hyderabad": 0.10,
}


ROUTE_NAMES = {
    "DEL-BOM": "Delhi-Mumbai",
    "BOM-BLR": "Mumbai-Bangalore",
    "DEL-BLR": "Delhi-Bangalore",
    "DEL-CCU": "Delhi-Kolkata",
    "BOM-CCU": "Mumbai-Kolkata",
    "BLR-HYD": "Bangalore-Hyderabad",
}


def load_data():
    with open(CLEANED_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def calculate_weighted_index(records):
    route_fares = defaultdict(list)

    for record in records:
        raw_route = f'{record["origin"]}-{record["destination"]}'
        route = ROUTE_NAMES.get(raw_route, raw_route)

        route_fares[route].append(float(record["fare"]))

    route_results = []
    weighted_index = 0
    total_weight_used = 0

    for route, fares in route_fares.items():
        current_fare = sum(fares) / len(fares)
        base_fare = BASE_FARES.get(route)

        if base_fare is None:
            continue

        route_index = (current_fare / base_fare) * 100
        weight = ROUTE_WEIGHTS.get(route, 0)

        weighted_index += route_index * weight
        total_weight_used += weight

        route_results.append({
            "route": route,
            "currentFare": round(current_fare, 2),
            "baseFare": base_fare,
            "index": round(route_index, 2),
            "weight": weight,
            "observations": len(fares)
        })

    if total_weight_used == 0:
        return {
            "index": 0,
            "averageFare": 0,
            "routes": []
        }

    final_index = weighted_index / total_weight_used

    total_fares = [
        float(record["fare"])
        for record in records
    ]

    return {
        "index": round(final_index, 2),
        "averageFare": round(sum(total_fares) / len(total_fares), 2),
        "routes": route_results
    }


if __name__ == "__main__":
    records = load_data()
    result = calculate_weighted_index(records)

    print(json.dumps(result, indent=2))