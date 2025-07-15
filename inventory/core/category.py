"""Mapping model for item category within the inventory."""

from .mapping import BaseMappingEntity


class Category(BaseMappingEntity):
    """An item category that can contain subcategories."""

    entity_type: str = "category"
    related_entity_type: str | None = None

    @property
    def required_fields(self) -> list[str]:
        """Return a list of required fields for the entity."""
        return self.base_required_fields + [
            "related_entity_type",
        ]


__all__ = [
    "Category",
]
