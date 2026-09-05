import json
import re
from pathlib import Path
from datetime import date, timedelta, datetime, timezone


SOURCE = "Google Flights"
ORIGIN = "DEL"
DESTINATION = "BOM"
BOOKING_WINDOW = 15
DEPARTURE_DATE = date.today() + timedelta(days=BOOKING_WINDOW)

text_path = Path("data/raw/google_flights_results.txt")
output_path = Path("data/raw/google_fares.json")

text = text_path.read_text(encoding="utf-8")

airlines = [
    "IndiGo",
    "Air India",
    "Air India Express",
    "Akasa Air",
    "SpiceJet",
    "Vistara",
    "Alliance Air",
]

fare_pattern = re.compile(r"₹\s?([\d,]+)")

records = []

lines = [line.strip() for line in text.splitlines() if line.strip()]

for i, line in enumerate(lines):
    if line not in airlines:
        continue

    # Nearby lines mein fare search karo
    nearby = lines[i:i + 8]
    fare = None

    for nearby_line in nearby:
        match = fare_pattern.search(nearby_line)
        if match:
            fare = int(match.group(1).replace(",", ""))
            break

    if fare is None:
        continue

    records.append({
        "source": SOURCE,
        "airline": line,
        "origin": ORIGIN,
        "destination": DESTINATION,
        "departure_date": DEPARTURE_DATE.isoformat(),
        "booking_window": BOOKING_WINDOW,
        "fare": fare,
        "currency": "INR",
        "collected_at": datetime.now(timezone.utc).isoformat(),
    })

output_path.write_text(
    json.dumps(records, indent=2, ensure_ascii=False),
    encoding="utf-8",
)

print(f"Extracted records: {len(records)}")
print(f"Saved to: {output_path}")

for record in records:
    print(
        record["airline"],
        "₹" + f'{record["fare"]:,}'
    )
