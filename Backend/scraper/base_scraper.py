from datetime import datetime, timezone


class BaseScraper:
    source_name = "Unknown"

    def make_record(
        self,
        airline,
        origin,
        destination,
        departure_date,
        booking_window,
        fare,
        currency="INR",
    ):
        return {
            "source": self.source_name,
            "airline": airline,
            "origin": origin,
            "destination": destination,
            "departure_date": departure_date,
            "booking_window": booking_window,
            "fare": float(fare),
            "currency": currency,
            "collected_at": datetime.now(timezone.utc).isoformat(),
        }
