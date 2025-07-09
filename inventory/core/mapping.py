"""Base classes for mapping entities used in the inventory module."""

from pydantic import BaseModel, ConfigDict

from ..datasource import LocalDataSource

class BaseMappingEntity(BaseModel):
    """Base object populated from local mapping data."""

    entity_type: str
    id: int
    code: str
    name: str
    description: str = ""
    notes: str = ""

    _local_datasource: LocalDataSource = LocalDataSource

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    def __setattr__(self, name: str, value):
        """Allow setting undefined attributes without raising."""
        try:
            super().__setattr__(name, value)
        except ValueError:
            object.__setattr__(self, name, value)

    def __init__(self, **kwargs) -> None:
        """Initialise the object from local mapping files."""
        kwargs.setdefault(
            "entity_type", self.__class__.__fields__["entity_type"].default
        )
        super().__init__(**kwargs)

        lds = self._local_datasource()
        try:
            data = lds.load_entity(self)
        except Exception:
            data = {}

        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

__all__ = [
    "BaseMappingEntity",
]
