from typing import ClassVar

from .isin import ISINSecurity

class Equity(ISINSecurity):
    entity_type: ClassVar[str] = "equity"
