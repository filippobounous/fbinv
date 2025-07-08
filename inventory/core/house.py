from .mapping import BaseMappingEntity


class House(BaseMappingEntity):
    """A physical property that can contain rooms."""

    entity_type: str = "house"
    address: str
    city: str
    country: str
    postal_code: str
    beneficiary: str
    latitude: float
    longitude: float

__all__ = [
    "House",
]
