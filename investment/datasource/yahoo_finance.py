import pandas as pd
from typing import TYPE_CHECKING, ClassVar
import yfinance as yf

from .base import BaseDataSource
from ..utils.consts import DATA_START_DATE
from ..utils.date_utils import today_midnight

if TYPE_CHECKING:
    from ..core import Security

class YahooFinanceDataSource(BaseDataSource):
    name: ClassVar[str] = "yahoo_finance"

    def _get_ts_from_remote(self, security: 'Security') -> pd.DataFrame:
        ticker = yf.Ticker(security.yahoo_finance_code)
        df = ticker.history()
        return df
    
    def update_all_securities(self):
        pass