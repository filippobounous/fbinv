from typing import ClassVar

from .base import Security

class Fund(Security):
    entity_type: ClassVar[str] = "fund"