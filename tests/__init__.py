"""Test suite configuration and environment variables."""

import os

# Setup environment variables required for tests before importing config
os.environ.setdefault("BASE_PATH", "/tmp")
os.environ.setdefault("TRANSACTION_PATH", "/tmp")
os.environ.setdefault("DEFAULT_NAME", "TEST")

from investment import config

# Configure data path for test runs
config.TIMESERIES_DATA_PATH = "/tmp/data"
