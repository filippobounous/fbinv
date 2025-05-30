from typing import List, TYPE_CHECKING, Dict, Type

from .alpha_vantage import AlphaVantageDataSource
from .bloomberg import BloombergDataSource
from .financial_times import FinancialTimesDataSource
from .local import LocalDataSource
from .open_figi import OpenFigiDataSource
from .twelve_data import TwelveDataDataSource
from .yahoo_finance import YahooFinanceDataSource

if TYPE_CHECKING:
    from .base import BaseDataSource

all_datasource: List[Type["BaseDataSource"]] = [
    AlphaVantageDataSource,
    BloombergDataSource,
    FinancialTimesDataSource,
    LocalDataSource,
    OpenFigiDataSource,
    TwelveDataDataSource,
    YahooFinanceDataSource,
]

datasource_registry: Dict[str, Type["BaseDataSource"]] = {
    i.name: i for i in all_datasource
}

datasource_codes: List[str] = [f"{i.name}_code" for i in all_datasource] + [
    f"{FinancialTimesDataSource.name}_security_type"
]

default_timeseries_datasource: YahooFinanceDataSource = YahooFinanceDataSource()
