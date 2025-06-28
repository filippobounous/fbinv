"""Project wide constants."""

import datetime

DATA_START_DATE = datetime.datetime(1900, 1, 1)
OC = ["open", "close"]
HL = ["high", "low"]
OHLC = OC + HL

DEFAULT_CURRENCY = "GBP"
DEFAULT_RET_WIN_SIZE = 1
DEFAULT_RV_WIN_SIZE = 20
DEFAULT_RV_MODEL = "close_to_close"
DEFAULT_RISK_FREE_RATE = 0.0
DEFAULT_CONFIDENCE_LEVEL = 0.95
DEFAULT_VAR_MODEL = "historical"
DEFAULT_CORR_MODEL = "pearson"
TRADING_DAYS = 252

DEFAULT_TIMEOUT = 60 # 60 seconds
