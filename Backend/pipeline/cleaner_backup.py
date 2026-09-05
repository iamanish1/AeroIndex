import json
from pathlib import Path
from datetime import datetime


RAW_FILE = Path("data/raw/flights.json")
CLEANED_FILE = Path("data/cleaned/flights_cleaned.json")


REQUIRED_FIELDS = [
    "airline",
    "from",
    "to",
    "departure_date",
    "booking_date",
    "booking_window",
    "fare",
    "currency",
    "source",
    "collected_at",
]


def load_raw_data():
    with open(RAW_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def is_valid_date(date_value):
    try:
        datetime.strptime(date_value, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def clean_record(record):
    # Required fields check
    for field in REQUIRED_FIELDS:
        if field not in record:
            return None

    # Text cleaning
    record["airline"] = str(record["airline"]).strip()
    record["from"] = str(record["from"]).strip().title()
    record["to"] = str(record["to"]).strip().title()
    record["currency"] = str(record["currency"]).strip().upper()

    # Fare validation
    try:
        record["fare"] = float(record["fare"])
    except (ValueError, TypeError):
        return None

    if record["fare"] <= 0:
        return None

    # Abnormal fare filter
    if record["fare"] > 100000:
        return None

    # Booking window validation
    try:
        record["booking_window"] = int(record["booking_window"])
    except (ValueError, TypeError):
        return None

    if record["booking_window"] <= 0:
        return None

    # Currency validation
    if record["currency"] != "INR":
        return None

    # Date validation
    if not is_valid_date(record["departure_date"]):
        return None

    if not is_valid_date(record["booking_date"]):
        return None

    # Collection timestamp validation
    try:
        datetime.fromisoformat(record["collected_at"])
    except ValueError:
        return None

    return record


def remove_duplicates(records):
    unique_records = []
    seen = set()

    for record in records:
        unique_key = (
            record["airline"],
            record["from"],
            record["to"],
            record["departure_date"],
            record["booking_date"],
            record["booking_window"],
            record["fare"],
        )

        if unique_key not in seen:
            seen.add(unique_key)
            unique_records.append(record)

    return unique_records


def main():
    raw_records = load_raw_data()

    cleaned_records = []

    for record in raw_records:
        cleaned_record = clean_record(record)

        if cleaned_record is not None:
            cleaned_records.append(cleaned_record)

    cleaned_records = remove_duplicates(cleaned_records)

    CLEANED_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(CLEANED_FILE, "w", encoding="utf-8") as file:
        json.dump(cleaned_records, file, indent=2, ensure_ascii=False)

    print(f"Raw records: {len(raw_records)}")
    print(f"Cleaned records: {len(cleaned_records)}")
    print(f"Saved to: {CLEANED_FILE}")


if __name__ == "__main__":
    main()