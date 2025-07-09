"""Local-only inventory datasource."""

from __future__ import annotations

from typing import Any, ClassVar

import pandas as pd

from ..config import INVENTORY_DATA_PATH
from .base import BaseDataSource

if False:  # pragma: no cover - for type checkers
    from ..core.mapping import BaseMappingEntity


class LocalDataSource(BaseDataSource):
    """Data source that reads from local CSV files."""

    name: ClassVar[str] = "local"

    def mapping_path(self, entity_type: str) -> str:
        """Return CSV path for ``entity_type`` mapping."""
        return f"{INVENTORY_DATA_PATH}/{entity_type}.csv"

    def load_entity(self, entity: "BaseMappingEntity") -> dict[str, Any]:
        """Load attributes for ``entity`` from disk if possible."""
        path = self.mapping_path(entity.entity_type)
        try:
            df = pd.read_csv(path)
        except FileNotFoundError:
            return {}

        rows = df.loc[df.code == entity.code]
        if rows.empty:
            return {}

        if "is_deleted" in rows.columns:
            rows = rows.loc[~rows["is_deleted"].astype(bool)]
        if rows.empty:
            return {}

        if "version" in rows.columns:
            rows = rows.sort_values("version", ascending=False)

        di = rows.iloc[0].to_dict()
        return {k: v for k, v in di.items() if pd.notna(v)}


__all__ = [
    "LocalDataSource",
]
