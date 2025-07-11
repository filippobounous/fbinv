"""Local-only inventory datasource."""

from __future__ import annotations

from typing import Any, ClassVar, TYPE_CHECKING

import pandas as pd

from .base import BaseDataSource
from investment.utils.exceptions import SecurityMappingError

if TYPE_CHECKING:
    from ..core import (
        House, Photo, Room, Book, Decor, Music
    )
    from ..core.item import BaseItem
    from ..core.mapping import BaseMappingEntity

class LocalDataSource(BaseDataSource):
    """Data source that reads from local CSV files."""

    name: ClassVar[str] = "local"

    def get_mapping(self, name: str) -> pd.DataFrame:
        """Load a mapping table from disk."""
        return pd.read_csv(self.mapping_path(name))

    def write_mapping(self, name: str, df: pd.DataFrame) -> None:
        """Persist a mapping table to disk."""
        df.to_csv(self.mapping_path(name), index=False)

    @staticmethod
    def _load(df: pd.DataFrame, entity: "BaseMappingEntity" | None = None) -> dict[str, Any]:
        """Convert a single CSV row to a dictionary."""
        if len(df) > 1:
            raise SecurityMappingError(
                f"Duplicate {entity.entity_type} for code '{entity.code}'" if entity else "Duplicate data."
            )
        if len(df) == 0:
            raise SecurityMappingError(
                f"No {entity.entity_type} for code '{entity.code}'" if entity else "Missing data."
            )

        di = df.iloc[0].to_dict()
        return {k: v for k, v in di.items() if not pd.isna(v)}

    def load_entity(self, entity: "BaseMappingEntity") -> dict[str, Any]:
        """Return mapping data for the given entity."""
        df = self.get_mapping(entity.entity_type)
        row = df.loc[df.code == entity.code]
        return self._load(df=row, entity=entity)

__all__ = [
    "LocalDataSource",
]
