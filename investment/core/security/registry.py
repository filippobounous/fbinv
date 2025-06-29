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
    i.entity_type: i
    for i in all_securities
}
