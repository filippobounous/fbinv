import pandas as pd
from typing import TYPE_CHECKING
import yfinance as yf

from .base import BaseDataSource

if TYPE_CHECKING:
    from ..core import Security

class YahooFinanceDataSource(BaseDataSource):
    name: str = "yahoo_finance"

    def _get_ts_from_remote(self, security: Security) -> pd.DataFrame:
        pass