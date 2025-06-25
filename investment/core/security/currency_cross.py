from typing import ClassVar, Optional

from .base import BaseSecurity

class CurrencyCross(BaseSecurity):
    entity_type: ClassVar[str] = "currency_cross"
    currency_vs: Optional[str] = None
