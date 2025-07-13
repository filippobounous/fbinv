"""Model for decorative items in the inventory."""

import datetime

from .base import BaseItem

class Decor(BaseItem):
    """Decorative inventory item with value and provenance."""

    entity_type: str = "decor"
    origin_region: str
    date_period: str
    material: str
    height_cm: float
    width_cm: float
    depth_cm: float
    mass_kg: float
    provenance: str
    quantity: int
    acquisition_date: datetime.datetime
    acquisition_value: float
    acquisition_currency: str
    appraisal_date: datetime.datetime
    appraisal_value: float
    appraisal_currency: str
    appraisal_entity: str

    @property
    def required_fields(self) -> list[str]:
        """Return a list of required fields for the entity."""
        return super().required_fields + [
            "date_period",
            "quantity",
            "appraisal_date",
            "appraisal_value",
            "appraisal_currency",
            "appraisal_entity",
        ]

__all__ = [
    "Decor",
]
