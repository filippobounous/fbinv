import pandas as pd

from .base import BaseDataSource
from ..core import Security

class AlphaVantageDataSource(BaseDataSource):
    name: str = "alpha_vantage"

    def _get_ts_from_remote(self, security: Security) -> pd.DataFrame:
        pass