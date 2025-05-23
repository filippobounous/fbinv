from typing import ClassVar

from .base import Security

class Equity(Security):
    entity_type: ClassVar[str] = "equity"