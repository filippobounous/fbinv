from typing import ClassVar

from pydantic import BaseModel, ConfigDict


class BaseDataSource(BaseModel):
    """Minimal base class for inventory data sources."""

    name: ClassVar[str] = "base"
    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)


__all__ = [
    "BaseDataSource",
]
