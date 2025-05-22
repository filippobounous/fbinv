from typing import List, TYPE_CHECKING

from .alpha_vantage import AlphaVantageDataSource
from .bloomberg import BloombergDataSource
from .local import LocalDataSource
from .twelve_data import TwelveDataDataSource
from .yahoo_finance import YahooFinanceDataSource

if TYPE_CHECKING:
    from .base import BaseDataSource

all_data_source: List["BaseDataSource"] = [
    AlphaVantageDataSource,
    BloombergDataSource,
    LocalDataSource,
    TwelveDataDataSource,
    YahooFinanceDataSource,
]

data_source_registry = {
    i.name: i
    for i in all_data_source
}