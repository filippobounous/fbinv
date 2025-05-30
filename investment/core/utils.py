"""Helper functions used across the core package."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .security.currency_cross import CurrencyCross


def get_currency_cross(origin_currency: str, result_currency: str) -> "CurrencyCross":
    """Return a ``CurrencyCross`` instance for the given currency pair."""

    from .security.currency_cross import CurrencyCross

    ccy = CurrencyCross(code=f"{origin_currency}{result_currency}")
    return ccy
