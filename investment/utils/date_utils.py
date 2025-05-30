"""Date and time helper functions."""

import datetime

def today_midnight() -> datetime.datetime:
    """Return ``datetime`` representing today's midnight UTC."""

    return datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0, 0, 0))
