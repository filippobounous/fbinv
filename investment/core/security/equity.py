"""Equity class for single stock securities"""

from typing import ClassVar

from .isin import ISINSecurity

class Equity(ISINSecurity):
    """
    Equity Security.
    
    A single stock equity. Initialised with:
        code (str): The Bloomberg ticker for the equity
    """
    entity_type: ClassVar[str] = "equity"
