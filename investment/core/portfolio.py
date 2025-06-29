"""Defines Portfolio class to manipulate multiple transactions together"""

from typing import ClassVar
import warnings

import pandas as pd
from pydantic import ConfigDict, Field

from ..config import PORTFOLIO_PATH, DEFAULT_NAME
from ..datasource.local import LocalDataSource, BaseDataSource
from .mapping import BaseMappingEntity
from .security.base import BaseSecurity
from .security.generic import Generic
from .transactions import Transactions
from ..utils.consts import OHLC, OC, DEFAULT_CURRENCY
from ..utils.date_utils import today_midnight
from ..utils.exceptions import TransactionsException

class Portfolio(BaseMappingEntity):
    """
    Portfolio.
    
    Groups together transactions made by a portfolio in order to perform
    further analysis on them as a whole. Initialised with:
        code (str), by default, if this is not provided it uses DEFAULT_NAME
    """
    entity_type: ClassVar[str] = "portfolio"
    owner: str | None = None
    has_cash: bool | None = None
    holdings: pd.DataFrame | None = Field(default=None, repr=False)
    cash: pd.DataFrame | None = Field(default=None, repr=False)
    account: str | None = None
    currency: str | None = None
    ignore_cash: bool | None = False

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, code: str | None = None, **kwargs) -> None:
        """Initialise portfolio data and load holdings."""
        if code is not None:
            kwargs["code"] = code
        if "code" not in kwargs:
            kwargs["code"] = DEFAULT_NAME

        super().__init__(**kwargs)

        self._load_cash_and_holdings()

    @property
    def transactions(self) -> pd.DataFrame:
        """Return cached transaction DataFrame."""
        return pd.read_csv(
            self._get_path(label="transactions"),
            parse_dates=['as_of_date'],
        )

    @property
    def all_securities(self) -> list["BaseSecurity"]:
        """List portfolio securities as class instances."""
        return [Generic(code) for code in self.holdings.code.unique()]

    def update(self) -> None:
        """Refresh transactions and reload holdings."""
        tr = Transactions()
        if self.code == tr.code:
            Transactions().update()
            self._load_cash_and_holdings()
        else:
            raise TransactionsException(f"Missing transactions updateable file for {self.code}")

    def _load_cash_and_holdings(self) -> None:
        """Populate holdings and cash attributes from disk."""
        self._get_holdings()
        if self.has_cash and not self.ignore_cash:
            self._get_cash()

    def _get_path(self, label: str) -> str:
        """Helper to construct a file path for portfolio data."""
        return f"{PORTFOLIO_PATH}/{self.code}-{label}.csv"

    def _get_cash(self) -> None:
        """Load cash positions from disk."""
        df = pd.read_csv(
            self._get_path(label="cash"),
            parse_dates=['as_of_date']
        )

        if self.account:
            df = df.loc[df.account == self.account]

        if self.currency:
            df = df.loc[df.currency == self.currency]

        self.cash = df

    def _get_holdings(self) -> None:
        """Load holdings derived from transactions."""
        df = self.transactions

        if self.account:
            df = df.loc[df['account'] == self.account]

        if self.currency:
            df = df.loc[df['currency'] == self.currency]

        df['cum_quantity'] = df.groupby('figi_code')['quantity'].cumsum()
        df['cum_value'] = df.groupby('figi_code')['value'].cumsum()
        df['average'] = df['cum_value'] / df['cum_quantity']

        result = df[
            ['as_of_date', 'figi_code', 'cum_quantity', 'average', 'currency']
        ].copy()
        result = result.rename(columns={
            'cum_quantity': 'quantity'
        })
        result["entry_value"] = result["quantity"] * result["average"]

        result = result.merge(
            LocalDataSource().get_security_mapping()[["figi_code", "code"]],
            on="figi_code", how="left"
        )

        self.holdings = result

    def get_price_history(
        self,
        datasource: "BaseDataSource" | None = None,
        local_only: bool = True,
        intraday: bool = False,
        currency: str = DEFAULT_CURRENCY,
    ) -> pd.DataFrame:
        """Return time series of portfolio value by currency."""
        if intraday:
            warnings.warn("Portfolio does not handle intraday, defaulting to single day.")

        df = self.get_holdings_price_history(
            datasource=datasource,
            local_only=local_only,
            currency=currency,
        )

        cols = OC + ["net", "entry"]
        df = df.groupby("as_of_date")[
            [f"{i}_value" for i in cols]
        ].sum().rename(columns={
            f"{i}_value": i for i in cols
        })

        return df

    def get_holdings_price_history(
        self,
        datasource: "BaseDataSource" | None = None,
        local_only: bool = True,
        currency: str | None = None
    ) -> pd.DataFrame:
        """Return time series of holdings values."""
        df_holdings = self._prepare_holdings_timeseries()

        df = self._combine_with_security_price_history(
            df=df_holdings,
            datasource=datasource,
            local_only=local_only,
            currency=currency,
        )

        for i in OHLC:
            df.loc[:, f"{i}_value"] = df[i] * df["quantity"]
        df.loc[:, "net_value"] = df["close_value"] - df["entry_value"]

        return df

    def _prepare_holdings_timeseries(self) -> pd.DataFrame:
        """Create a daily holdings DataFrame pivoted by currency and security."""
        df = self.holdings

        df_pivot = df.pivot(
            index="as_of_date",
            columns=["currency", "figi_code", "code"],
            values=["quantity", "average", "entry_value"]
        )

        full_date_range = pd.date_range(self.holdings['as_of_date'].min(), today_midnight())
        week_mask = full_date_range.to_series().dt.weekday < 5
        weekdays_only = full_date_range[week_mask]

        df_pivot = df_pivot.reindex(weekdays_only)
        df_pivot = df_pivot.ffill().fillna(0)
        df_pivot.index.name = "as_of_date"

        # flatten multiindex
        df_pivot.columns = ['-'.join(col).strip() for col in df_pivot.columns.values]

        # melt everything except 'as_of_date'
        df_pivot = df_pivot.reset_index()

        df_melted = df_pivot.melt(id_vars="as_of_date", var_name="key", value_name="value")

        # split 'key' into separate columns
        # ^(quantity|average|entry_value) → captures the value type
        # -(\w+) → captures the currency
        # -([^-]+) → captures the FIGI code (up to the next -)
        # -(.+)$ → captures the final code, which may contain underscores
        df_melted[['value_type', 'currency', 'figi_code', 'code']] = df_melted['key'].str.extract(
            r'^(quantity|average|entry_value)-(\w+)-([^-]+)-(.+)$'
        )

        # rearrange and format
        df = df_melted.drop(columns="key").pivot(
            index=["as_of_date", "currency", "figi_code", "code"],
            columns="value_type", values="value"
        ).reset_index()
        df.columns.name = ""

        return df[df.quantity != 0.0].reset_index(drop=True)

    def _combine_with_security_price_history(
        self,
        df: pd.DataFrame,
        datasource: "BaseDataSource" | None = None,
        local_only: bool = True,
        currency: str | None = None
    ) -> pd.DataFrame:
        "Combine holdings timeseries with security price history"
        security_ph_list = []

        for security in self.all_securities:
            _df_security = security.get_price_history(
                local_only=local_only,
                datasource=datasource,
                currency=currency,
            )
            if not _df_security.empty:
                _df_security.loc[:, "code"] = security.code
                security_ph_list.append(_df_security)

        df_security = pd.concat(security_ph_list).reset_index()

        df = df.merge(df_security, on=["as_of_date", "code"], how="left")

        # forward-filling values
        df.sort_values(by=["code", "figi_code", "as_of_date"], inplace=True)
        df = df.set_index(["code", "figi_code"]).groupby(level=0, group_keys=False).ffill()

        return df.set_index("as_of_date", append=True)
