"""Mapping model for houses within the inventory."""

from .mapping import BaseMappingEntity


class House(BaseMappingEntity):
    """A physical property that can contain rooms."""

    entity_type: str = "house"
    address: str | None = None
    city: str | None = None
    country: str | None = None
    postal_code: str | None = None
    beneficiary: str | None = None
    latitude: float | None = None
    longitude: float | None = None

    @property
    def required_fields(self) -> list[str]:
        """Return a list of required fields for the entity."""
        return self.base_required_fields + [
            "address",
            "city",
            "country",
            "postal_code",
            "beneficiary",
        ]


__all__ = [
    "House",
]
