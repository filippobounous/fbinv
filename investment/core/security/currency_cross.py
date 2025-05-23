from typing import ClassVar, Optional

from .base import Security

class CurrencyCross(Security):
    entity_type: ClassVar[str] = "currency_cross"
    currency_vs: Optional[str] = None