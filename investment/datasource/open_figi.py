import pandas as pd
import requests
from time import sleep
from typing import TYPE_CHECKING, ClassVar, List

from .base import BaseDataSource
from ..config import OPEN_FIGI_API_KEY, BASE_PATH
from .local import LocalDataSource

if TYPE_CHECKING:
    from ..core.security.registry import CurrencyCross, Equity, ETF, Fund

# https://github.com/OpenFIGI/api-examples
# https://www.openfigi.com/api/documentation

class OpenFigiDataSource(BaseDataSource):
    name: ClassVar[str] = "open_figi"
    base_url: str = "https://api.openfigi.com/v3/mapping"

    def _get_currency_cross_ts_from_remote(self, security: 'CurrencyCross', intraday: bool) -> pd.DataFrame:
        raise NotImplementedError(f"No remote source for {self.name} datasource.")

    def _get_equity_ts_from_remote(self, security: 'Equity', intraday: bool) -> pd.DataFrame:
        raise NotImplementedError(f"No remote source for {self.name} datasource.")

    def _get_etf_ts_from_remote(self, security: 'ETF', intraday: bool) -> pd.DataFrame:
        raise NotImplementedError(f"No remote source for {self.name} datasource.")

    def _get_fund_ts_from_remote(self, security: 'Fund', intraday: bool) -> pd.DataFrame:
        raise NotImplementedError(f"No remote source for {self.name} datasource.")
    
    @staticmethod
    def _format_ts_from_remote(df: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError(f"Not implemented.")

    def _update_security_mapping(
        self,
        figis: List[str],
        batch_size: int = 100,
        pause: float = 1.0,
    ) -> pd.DataFrame:
        headers = {
            "Content-Type": "application/json",
            "X-OPENFIGI-APIKEY": OPEN_FIGI_API_KEY
        }

        results = []

        for i in range(0, len(figis), batch_size):
            batch = figis[i:i + batch_size]
            payload = [{"idType": "ID_BB_GLOBAL", "idValue": figi} for figi in batch]

            try:
                resp = requests.post(self.base_url, json=payload, headers=headers, timeout=10)
                resp.raise_for_status()
                batch_results = resp.json()
            except Exception as e:
                raise RuntimeError(f"OpenFIGI batch failed for batch {i // batch_size + 1}: {e}")

            for j in range(len(batch)):
                entry = batch_results[j] if j < len(batch_results) else {}
                data = entry.get("data", [])
                if data:
                    row = data[0]
                    row["figi"] = batch[j]
                    results.append(row)
                else:
                    results.append({"figi": batch[j]})

            sleep(pause)  # Respect API rate limits

        df = pd.DataFrame(results)

        return df