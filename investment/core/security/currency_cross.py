"""CurrencyCross class for exchange rates"""

from .base import BaseSecurity

class CurrencyCross(BaseSecurity):
    """
    Currency Cross Security.
    
    An exchange rate between two given currencies. Initialised with:
        code (str): The currency code given as XXXYYY 
    """
    entity_type: str = "currency_cross"
    currency_vs: str | None = None
