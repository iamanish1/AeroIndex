import json
from pathlib import Path
from collections import defaultdict

INPUT_FILE = Path("data/raw/google_fares.json")
OUTPUT_FILE = Path("data/raw/google_fares_cleaned.json")

with INPUT_FILE.open("r", encoding="utf-8") as f:
    records = json.load(f)

grouped = defaultdict(list)

for record in records:
    key = (
        record["source"],
        record["airline"],
        record["origin"],
        record["destination"],
        record["departure_date"],
        record["booking_window"],
    )

    grouped[key].append(record)

cleaned_records = []

for key, items in grouped.items():
    # Same airline/route/window ke duplicate fares hatao
    unique_fares = sorted(
        set(item["fare"] for item in items)
    )

    base_record = items[0]

    for fare in unique_fares:
        new_record = base_record.copy()
        new_record["fare"] = fare
        new_record["observations"] = items.count(
            next(item for item in items if item["fare"] == fare)
        )
        cleaned_records.append(new_record)

with OUTPUT_FILE.open("w", encoding="utf-8") as f:
    json.dump(cleaned_records, f, indent=2, ensure_ascii=False)

print(f"Original records: {len(records)}")
print(f"Cleaned records: {len(cleaned_records)}")
print(f"Saved to: {OUTPUT_FILE}")

print("\nCleaned fares:")
for record in cleaned_records:
    print(
        f'{record["airline"]}: ₹{record["fare"]:,} '
        f'({record["observations"]} observations)'
    )


