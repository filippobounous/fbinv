"""Models for currency cross securities."""

from typing import ClassVar, Optional

from .base import Security

class CurrencyCross(Security):
    """Represents a currency pair used for conversion."""
    entity_type: ClassVar[str] = "currency_cross"
    currency_vs: Optional[str] = None
