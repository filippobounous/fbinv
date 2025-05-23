from typing import ClassVar

from .base import Security

class ETF(Security):
    entity_type: ClassVar[str] = "etf"