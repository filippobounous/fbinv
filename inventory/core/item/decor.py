"""Model for decorative items in the inventory."""

import datetime

from .base import BaseItem


class DecorItem(BaseItem):
    """Decorative inventory item with value and provenance."""

    entity_type: str = "decor"
    origin_region: str
    date_period: str
    material: str
    height_cm: float
    width_cm: float
    length_cm: float
    weight_kg: float
    condition: str
    provenance: str
    quantity: int
    acquisition_date: datetime.datetime
    acquisition_value: float
    acquisition_currency: str
    appraisal_date: datetime.datetime
    appraisal_value: float
    appraisal_currency: str
    appraisal_entity: str

__all__ = [
    "DecorItem",
]
