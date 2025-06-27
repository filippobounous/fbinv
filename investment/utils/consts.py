"""Project wide constants."""

import datetime

DATA_START_DATE = datetime.datetime(1900, 1, 1)
OC = ["open", "close"]
HL = ["high", "low"]
OHLC = OC + HL

DEFAULT_RET_WIN_SIZE = 1
DEFAULT_CORR_MODEL = "pearson"
DEFAULT_RV_WIN_SIZE = 20
DEFAULT_RV_MODEL = "close_to_close"
TRADING_DAYS = 252
