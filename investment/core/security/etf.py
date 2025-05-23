from typing import ClassVar

from .isin import ISINSecurity

class ETF(ISINSecurity):
    entity_type: ClassVar[str] = "etf"