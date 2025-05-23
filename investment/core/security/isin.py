from typing import ClassVar, Optional

from .base import Security

class ISINSecurity(Security):
    entity_type: ClassVar[str] = "isin"
    isin_code: Optional[str] = None