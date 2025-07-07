"""Equity class for single stock securities"""

from .isin import ISINSecurity

class Equity(ISINSecurity):
    """
    Equity Security.
    
    A single stock equity. Initialised with:
        code (str): The Bloomberg ticker for the equity
    """
    entity_type: str = "equity"

__all__ = [
    "Equity",
]
