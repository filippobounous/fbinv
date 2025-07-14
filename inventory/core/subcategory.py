"""Mapping model for item subcategory within the inventory."""

from .mapping import BaseMappingEntity


class Subcategory(BaseMappingEntity):
    """An item subcategory."""

    entity_type: str = "subcategory"
    category_code: str | None = None

    @property
    def required_fields(self) -> list[str]:
        """Return a list of required fields for the entity."""
        return self.base_required_fields + [
            "category_code",
        ]


__all__ = [
    "Subcategory",
]
