from .base import Security

class CurrencyCross(Security):
    entity_type: str = "currency_cross"
    currency_vs: str