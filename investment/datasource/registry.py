"""Registry of available data sources."""

from typing import TYPE_CHECKING

from .alpha_vantage import AlphaVantageDataSource
from .bloomberg import BloombergDataSource
from .financial_times import FinancialTimesDataSource
from .local import LocalDataSource
from .open_figi import OpenFigiDataSource
from .twelve_data import TwelveDataDataSource
from .yahoo_finance import YahooFinanceDataSource

if TYPE_CHECKING:
    from .base import BaseDataSource

all_datasource: list["BaseDataSource"] = [
    AlphaVantageDataSource,
    BloombergDataSource,
    FinancialTimesDataSource,
    LocalDataSource,
    OpenFigiDataSource,
    TwelveDataDataSource,
    YahooFinanceDataSource,
]

datasource_registry: dict[str, "BaseDataSource"] = {i.name: i for i in all_datasource}

datasource_codes: list[str] = [f"{i.name}_code" for i in all_datasource] + [
    f"{FinancialTimesDataSource.name}_security_type"
]

default_timeseries_datasource = YahooFinanceDataSource()

__all__ = [
    "all_datasource",
    "datasource_registry",
    "datasource_codes",
    "default_timeseries_datasource",
]
