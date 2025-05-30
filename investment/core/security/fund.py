"""Fund security types."""

from typing import ClassVar

from .isin import ISINSecurity

class Fund(ISINSecurity):
    """Fund security identified by an ISIN."""
    entity_type: ClassVar[str] = "fund"
