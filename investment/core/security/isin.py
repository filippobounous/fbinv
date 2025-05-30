"""Security subclass identified by an ISIN."""

from typing import ClassVar, Optional

from .base import Security

class ISINSecurity(Security):
    """Security that has an ISIN code."""
    entity_type: ClassVar[str] = "isin"
    isin_code: Optional[str] = None
