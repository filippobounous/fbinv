from typing import ClassVar

from .isin import ISINSecurity

class Fund(ISINSecurity):
    entity_type: ClassVar[str] = "fund"