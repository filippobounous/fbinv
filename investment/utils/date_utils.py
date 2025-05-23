import datetime

def today_midnight() -> datetime.datetime:
    return datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0, 0, 0))
