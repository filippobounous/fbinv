"""Placeholder entities for future inventory mappings."""

from typing import Optional
from pydantic import BaseModel


class BaseMappingEntity(BaseModel):
    """Basic placeholder for mapping entities."""

    code: Optional[str] = None

    def get_price_history(self, *args, **kwargs):
        """Return price history for the entity when implemented."""
        raise NotImplementedError
