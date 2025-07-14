"""Full registy of BaseSecurity subclasses"""

from typing import TYPE_CHECKING

from .composite import Composite
from .currency_cross import CurrencyCross
from .equity import Equity
from .etf import ETF
from .fund import Fund
from .isin import ISINSecurity

if TYPE_CHECKING:
    from .base import BaseSecurity

all_securities: list["BaseSecurity"] = [
    Composite,
    CurrencyCross,
    Equity,
    ETF,
    Fund,
    ISINSecurity,
]

security_registry: dict[str, "BaseSecurity"] = {
    i.model_fields["entity_type"].default: i for i in all_securities
}

__all__ = [
    "all_securities",
    "security_registry",
]
