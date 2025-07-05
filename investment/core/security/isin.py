"""Intermediate ISIN class for ISIN-required securities"""

from .base import BaseSecurity

class ISINSecurity(BaseSecurity):
    """
    ISIN Security.
    
    Intermediate class to require isin_code across subclasses.
    """
    entity_type: str = "isin"
    isin_code: str | None = None
