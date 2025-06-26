"""Date utilities used across the project."""

import datetime

def today_midnight() -> datetime.datetime:
    """Return today's date at midnight."""
    return datetime.datetime.combine(
        datetime.date.today(), datetime.time(0, 0, 0, 0)
    )
