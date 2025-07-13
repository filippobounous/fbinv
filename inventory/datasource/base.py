"""Base class definitions for inventory data sources."""

import datetime
from pathlib import Path
from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict

from ..config import BASE_PATH


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

    @staticmethod
    def _get_file_names_in_path(path: str) -> dict[str, datetime.datetime]:
        """Return mapping of file names to last modified datetime."""
        folder = Path(path)

        di: dict[str, datetime.datetime] = {}
        if not folder.exists():
            return di
        if not folder.is_dir():
            raise NotADirectoryError(f"{path} is not a directory")
        for file_path in folder.iterdir():
            if file_path.is_file() and not file_path.name.startswith("."):
                file_stem = file_path.stem
                last_modified_timestamp = file_path.stat().st_mtime
                last_modified_datetime = datetime.datetime.fromtimestamp(
                    last_modified_timestamp
                )
                di[file_stem] = last_modified_datetime

        return di

    @staticmethod
    def mapping_path(name: str) -> str:
        """Return the CSV path for a given mapping name."""
        return f"{BASE_PATH}/{name}_mapping.csv"


__all__ = [
    "BaseDataSource",
]
