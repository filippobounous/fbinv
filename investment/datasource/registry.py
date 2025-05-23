from typing import List, TYPE_CHECKING, Dict

from .alpha_vantage import AlphaVantageDataSource
from .bloomberg import BloombergDataSource
from .financial_times import FinancialTimesDataSource
from .local import LocalDataSource
from .twelve_data import TwelveDataDataSource
from .yahoo_finance import YahooFinanceDataSource

if TYPE_CHECKING:
    from .base import BaseDataSource

all_data_source: List["BaseDataSource"] = [
    AlphaVantageDataSource,
    BloombergDataSource,
    FinancialTimesDataSource,
    LocalDataSource,
    TwelveDataDataSource,
    YahooFinanceDataSource,
]

data_source_registry: Dict[str, "BaseDataSource"] = {
    i.name: i
    for i in all_data_source
}

data_source_codes: List[str] = [
    f"{i.name}_code"
    for i in  all_data_source
] + [f"{FinancialTimesDataSource.name}_security_type"]