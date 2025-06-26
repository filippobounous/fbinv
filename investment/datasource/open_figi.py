"""Data source that interfaces with the OpenFIGI API."""

import datetime
from time import sleep
from typing import TYPE_CHECKING, ClassVar

import pandas as pd
import requests

from .base import BaseDataSource
from ..config import OPEN_FIGI_API_KEY
from ..utils.exceptions import DataSourceMethodException

if TYPE_CHECKING:
    from ..core.security.registry import CurrencyCross, Equity, ETF, Fund

# https://github.com/OpenFIGI/api-examples
# https://www.openfigi.com/api/documentation

class OpenFigiDataSource(BaseDataSource):
    """Data source for mapping codes via the OpenFIGI API."""

    name: ClassVar[str] = "open_figi"
    base_url: str = "https://api.openfigi.com/v3/mapping"
    batch_size: int = 100
    timeout: float = 1.0

    def _get_currency_cross_price_history_from_remote(
        self,
        security: 'CurrencyCross', intraday: bool,
        start_date: datetime.datetime, end_date: datetime.datetime,
    ) -> pd.DataFrame:
        """OpenFIGI does not provide price history."""
        raise DataSourceMethodException(
            f"No remote series for {self.name} datasource for {security.code}."
        )

    def _get_equity_price_history_from_remote(
        self,
        security: 'Equity', intraday: bool,
        start_date: datetime.datetime, end_date: datetime.datetime,
    ) -> pd.DataFrame:
        """OpenFIGI does not provide price history."""
        raise DataSourceMethodException(
            f"No remote series for {self.name} datasource for {security.code}."
        )

    def _get_etf_price_history_from_remote(
        self,
        security: 'ETF', intraday: bool,
        start_date: datetime.datetime, end_date: datetime.datetime,
    ) -> pd.DataFrame:
        """OpenFIGI does not provide price history."""
        raise DataSourceMethodException(
            f"No remote series for {self.name} datasource for {security.code}."
        )

    def _get_fund_price_history_from_remote(
        self,
        security: 'Fund', intraday: bool,
        start_date: datetime.datetime, end_date: datetime.datetime,
    ) -> pd.DataFrame:
        """OpenFIGI does not provide price history."""
        raise DataSourceMethodException(
            f"No remote series for {self.name} datasource for {security.code}."
        )

    @staticmethod
    def _format_price_history_from_remote(df: pd.DataFrame) -> pd.DataFrame:
        """Return the input DataFrame unchanged."""
        return df

    def _update_security_mapping(self, df: pd.DataFrame) -> pd.DataFrame:
        """Retrieve additional information for securities from OpenFIGI."""
        figis = df["figi_code"].to_list()

        headers = {
            "Content-Type": "application/json",
            "X-OPENFIGI-APIKEY": OPEN_FIGI_API_KEY
        }

        results = []

        for idx in range(0, len(figis), self.batch_size):
            batch = figis[idx:idx + self.batch_size]
            payload = [{"idType": "ID_BB_GLOBAL", "idValue": figi} for figi in batch]

            try:
                resp = requests.post(self.base_url, json=payload, headers=headers, timeout=10)
                resp.raise_for_status()
                batch_results = resp.json()
            except Exception as e:
                raise RuntimeError(
                    f"OpenFIGI batch failed for batch {idx // self.batch_size + 1}: {e}"
                ) from e

            for jdx, batch_el in enumerate(batch):
                entry = batch_results[jdx] if jdx < len(batch_results) else {}
                data = entry.get("data", [])
                if data:
                    row = data[0]
                    row["figi"] = batch_el
                    results.append(row)
                else:
                    results.append({"figi": batch_el})

            sleep(self.timeout)  # Respect API rate limits

        df = pd.DataFrame(results)

        return df
