"""Constant values used across the investment package."""

import datetime

DATA_START_DATE = datetime.datetime(1900, 1, 1)
OHLC = ["open", "high", "low", "close"]
OC = ["open", "close"]

DEFAULT_RET_WIN_SIZE = 1
DEFAULT_RV_WIN_SIZE = 20
DEFAULT_RV_MODEL = "close_to_close"
TRADING_DAYS = 252
