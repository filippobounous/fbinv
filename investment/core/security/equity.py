"""Equity security types."""

from typing import ClassVar

from .isin import ISINSecurity

class Equity(ISINSecurity):
    """Equity security identified by an ISIN."""
    entity_type: ClassVar[str] = "equity"
