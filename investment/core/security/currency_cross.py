"""CurrencyCross class for exchange rates"""

from typing import ClassVar, Optional

from .base import BaseSecurity


class CurrencyCross(BaseSecurity):
    """
    Currency Cross Security.
    
    An exchange rate between two given currencies. Initialised with:
        code (str): The currency code given as XXXYYY 
    """
    entity_type: ClassVar[str] = "currency_cross"
    currency_vs: Optional[str] = None
