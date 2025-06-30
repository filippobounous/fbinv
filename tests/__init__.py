import os
from investment import config

# Setup environment variables required for tests
os.environ.setdefault("BASE_PATH", "/tmp")
os.environ.setdefault("TRANSACTION_PATH", "/tmp")
os.environ.setdefault("DEFAULT_NAME", "TEST")

# Configure data path for test runs
config.TIMESERIES_DATA_PATH = "/tmp/data"
