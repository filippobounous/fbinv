import alpha_vantage
import pandas as pd

from .base import BaseDataSource
from ..config import ALPHA_VANTAGE_API_KEY
from ..core import Security
from ..core.security.currency_cross import CurrencyCross

# https://alpha-vantage.readthedocs.io/en/latest/

class AlphaVantageDataSource(BaseDataSource):
    name: str = "alpha_vantage"

    def _get_ts_from_remote(self, security: Security) -> pd.DataFrame:
        pass