"""Configuration values loaded from environment variables."""

import os

from dotenv import load_dotenv

load_dotenv()

# External API keys
TWELVE_DATA_API_KEY = os.getenv("TWELVE_DATA_API_KEY")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
OPEN_FIGI_API_KEY = os.getenv("OPEN_FIGI_API_KEY")
QUANDL_API_KEY = os.getenv("QUANDL_API_KEY")

# Optional API key used to secure FastAPI endpoints
# If any of these are ``None`` the corresponding app will reject all requests.
FASTAPI_INVESTMENT_API_KEY = os.getenv("FASTAPI_INVESTMENT_API_KEY")

# File paths
TRANSACTION_PATH = os.getenv("INVESTMENT_TRANSACTION_PATH")
TRANSACTION_SHEET_NAME = os.getenv("INVESTMENT_TRANSACTION_SHEET_NAME")
DEFAULT_NAME = os.getenv("INVESTMENT_DEFAULT_NAME")
BASE_PATH = os.getenv("INVESTMENT_BASE_PATH")

REQUIRED_ENV_VARS = {
    "BASE_PATH": BASE_PATH,
    "TRANSACTION_PATH": TRANSACTION_PATH,
    "DEFAULT_NAME": DEFAULT_NAME,
}
missing_vars = [name for name, value in REQUIRED_ENV_VARS.items() if value is None]
if missing_vars:
    raise EnvironmentError(
        "Missing required environment variables: " + ", ".join(missing_vars)
    )

TIMESERIES_DATA_PATH = BASE_PATH + "/timeseries_data"
PORTFOLIO_PATH = BASE_PATH + "/portfolio"
