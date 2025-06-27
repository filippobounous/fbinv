"""Intermediate ISIN class for ISIN-required securities"""

from typing import ClassVar, Optional

from .base import BaseSecurity


class ISINSecurity(BaseSecurity):
    """
    ISIN Security.
    
    Intermediate class to require isin_code across subclasses.
    """
    entity_type: ClassVar[str] = "isin"
    isin_code: Optional[str] = None
