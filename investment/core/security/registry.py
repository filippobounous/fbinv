from typing import TYPE_CHECKING, List, Dict

from .currency_cross import CurrencyCross
from .equity import Equity
from .etf import ETF
from .fund import Fund

if TYPE_CHECKING:
    from .base import Security

all_securities: List['Security']= [
    CurrencyCross,
    Equity,
    ETF,
    Fund,
]

security_registry: Dict[str, 'Security'] = {
    i.entity_type: i
    for i in all_securities
}
