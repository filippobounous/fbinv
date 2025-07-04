"""Full registy of BaseSecuirty subclasses"""

from typing import TYPE_CHECKING

from .composite import Composite
from .currency_cross import CurrencyCross
from .equity import Equity
from .etf import ETF
from .fund import Fund

if TYPE_CHECKING:
    from .base import BaseSecurity

all_securities: list['BaseSecurity']= [
    Composite,
    CurrencyCross,
    Equity,
    ETF,
    Fund,
]

security_registry: dict[str, 'BaseSecurity'] = {
    i.__fields__["entity_type"].default: i
    for i in all_securities
}
