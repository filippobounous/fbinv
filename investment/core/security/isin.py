from typing import ClassVar, Optional

from .base import BaseSecurity

class ISINSecurity(BaseSecurity):
    entity_type: ClassVar[str] = "isin"
    isin_code: Optional[str] = None
