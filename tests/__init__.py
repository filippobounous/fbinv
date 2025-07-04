"""Test suite configuration and environment variables."""

import os
import sys
from pathlib import Path

# Setup environment variables required for tests before importing config
os.environ.setdefault("BASE_PATH", "/tmp")
os.environ.setdefault("TRANSACTION_PATH", "/tmp")
os.environ.setdefault("DEFAULT_NAME", "TEST")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from investment import config

# Configure data path for test runs
config.TIMESERIES_DATA_PATH = "/tmp/data"
