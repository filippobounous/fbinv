from typing import TYPE_CHECKING, List, Dict

from .composite import Composite
from .currency_cross import CurrencyCross
from .equity import Equity
from .etf import ETF
from .fund import Fund

if TYPE_CHECKING:
    from .base import BaseSecurity

all_securities: List['BaseSecurity']= [
    Composite,
    CurrencyCross,
    Equity,
    ETF,
    Fund,
]

security_registry: Dict[str, 'BaseSecurity'] = {
    i.entity_type: i
    for i in all_securities
}
