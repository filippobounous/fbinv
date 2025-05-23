from typing import ClassVar

from .base import Security

class CurrencyCross(Security):
    entity_type: ClassVar[str] = "currency_cross"
    currency_vs: str