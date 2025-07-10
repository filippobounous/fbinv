"""Base class definitions for inventory data sources."""

from typing import ClassVar, Any

from pydantic import BaseModel, ConfigDict

class BaseDataSource(BaseModel):
    """Minimal base class for inventory data sources."""

    name: ClassVar[str] = "base"
    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    def __setattr__(self, name: str, value: Any) -> None:
        """Set an attribute, allowing for ValueError exceptions."""
        try:
            super().__setattr__(name, value)
        except ValueError:
            object.__setattr__(self, name, value)

__all__ = [
    "BaseDataSource",
]
