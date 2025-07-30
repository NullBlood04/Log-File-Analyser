from datetime import datetime, timezone
import logging


def sanitise_datetime(timestamp: str) -> datetime:
    # Converts a .NET JSON date format to a timezone-aware datetime object.
    try:
        in_milliseconds = int(timestamp.strip("/Date()"))
        return datetime.fromtimestamp(in_milliseconds / 1000, tz=timezone.utc)
    except (ValueError, TypeError):
        logging.warning(f"Could not parse timestamp: {timestamp}. Using current time.")
        return datetime.now(timezone.utc)
