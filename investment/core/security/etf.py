"""Exchange traded fund security types."""

from typing import ClassVar

from .isin import ISINSecurity

class ETF(ISINSecurity):
    """ETF security identified by an ISIN."""
    entity_type: ClassVar[str] = "etf"
