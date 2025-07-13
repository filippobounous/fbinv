"""Core helper functions."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .security.currency_cross import CurrencyCross


def get_currency_cross(origin_currency: str, result_currency: str) -> "CurrencyCross":
    """Create a :class:`CurrencyCross` from two currency codes."""
    from .security.currency_cross import CurrencyCross

    ccy = CurrencyCross(code=f"{origin_currency}{result_currency}")
    return ccy


__all__ = [
    "get_currency_cross",
]
