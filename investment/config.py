"""Configuration values sourced from environment variables."""

from dotenv import load_dotenv
import os

load_dotenv()

# api keys
TWELVE_DATA_API_KEY = os.getenv("TWELVE_DATA_API_KEY")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
OPEN_FIGI_API_KEY = os.getenv("OPEN_FIGI_API_KEY")
QUANDL_API_KEY = os.getenv("QUANDL_API_KEY")

# file paths
TRANSACTION_PATH = os.getenv("TRANSACTION_PATH")
TRANSACTION_SHEET_NAME = os.getenv("TRANSACTION_SHEET_NAME")
DEFAULT_NAME = os.getenv("DEFAULT_NAME")
BASE_PATH = os.getenv("BASE_PATH")

TIMESERIES_DATA_PATH = BASE_PATH + "/timeseries_data"
PORTFOLIO_PATH = BASE_PATH + "/portfolio"
