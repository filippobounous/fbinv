from dotenv import load_dotenv
import os

load_dotenv()

# api keys
TWELVE_DATA_API_KEY = os.getenv("TWELVE_DATA_API_KEY")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
OPEN_FIGI_API_KEY = os.getenv("OPEN_FIGI_API_KEY")
QUANDL_API_KEY = os.getenv("QUANDL_API_KEY")

# file paths with fallbacks for test environments
TRANSACTION_PATH = os.getenv("TRANSACTION_PATH", "transactions.xlsx")
TRANSACTION_SHEET_NAME = os.getenv("TRANSACTION_SHEET_NAME", "Sheet1")
DEFAULT_NAME = os.getenv("DEFAULT_NAME", "TEST")
BASE_PATH = os.getenv("BASE_PATH", "/tmp")

TIMESERIES_DATA_PATH = os.path.join(BASE_PATH, "timeseries_data")
PORTFOLIO_PATH = os.path.join(BASE_PATH, "portfolio")
