import pandas as pd

from .base import BaseDataSource
from ..core import Security

class BloombergDataSource(BaseDataSource):
    name: str = "bloomberg"

    def _get_ts_from_remote(self, security: Security) -> pd.DataFrame:
        pass