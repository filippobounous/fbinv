"""ETF class for exchange-traded funds"""

from typing import ClassVar

from .isin import ISINSecurity

class ETF(ISINSecurity):
    """
    ETF Security.
    
    An exchange-traded fund. Initialised with:
        code (str): The Bloomberg ticker for the etf (ticker and exchange)
    """
    entity_type: ClassVar[str] = "etf"
