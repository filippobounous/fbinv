"""Configuration values loaded from environment variables."""

import os

from dotenv import load_dotenv

load_dotenv()

FASTAPI_INVENTORY_API_KEY = os.getenv("FASTAPI_INVENTORY_API_KEY")
BASE_PATH = os.getenv("BASE_PATH")

REQUIRED_ENV_VARS = {
    "BASE_PATH": BASE_PATH,
}

missing_vars = [name for name, value in REQUIRED_ENV_VARS.items() if value is None]
if missing_vars:
    raise EnvironmentError(
        "Missing required environment variables: " + ", ".join(missing_vars)
    )

INVENTORY_DATA_PATH = f"{BASE_PATH}/inventory"

__all__ = [
    "FASTAPI_INVENTORY_API_KEY",
    "BASE_PATH",
    "INVENTORY_DATA_PATH",
]
