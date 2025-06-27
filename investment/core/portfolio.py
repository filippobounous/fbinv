"""Defines Portfolio class to manipulate multiple transactions together"""

from typing import Optional, ClassVar, List

import pandas as pd
from pydantic import ConfigDict, Field

from ..config import PORTFOLIO_PATH, DEFAULT_NAME
from ..datasource.local import LocalDataSource
from .mapping import BaseMappingEntity
from .security.base import BaseSecurity
from .security.generic import Generic
from .transactions import Transactions
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
    owner: Optional[str] = None
    has_cash: Optional[bool] = None
    holdings: Optional[pd.DataFrame] = Field(default = None, repr=False)
    cash: Optional[pd.DataFrame] = Field(default = None, repr=False)
    account: Optional[str] = None
    currency: Optional[str] = None
    ignore_cash: Optional[bool] = False

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, code: Optional[str] = None, **kwargs) -> None:
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
    def all_security(self) -> List["BaseSecurity"]:
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
        df['avg_price'] = df['cum_value'] / df['cum_quantity']

        result = df[
            ['as_of_date', 'figi_code', 'cum_quantity', 'avg_price', 'currency']
        ].copy()
        result = result.rename(columns={
            'cum_quantity': 'quantity'
        })
        result["base_value"] = result["quantity"] * result["avg_price"]

        result = result.merge(
            LocalDataSource().get_security_mapping()[["figi_code", "code"]],
            on="figi_code", how="left"
        )

        self.holdings = result

    def get_price_history(
        self,
        convert_to_single_currency: bool = False,
        single_currency: Optional[str] = None,
    ) -> pd.DataFrame:
        """Return time series of holdings values."""
        df = self._prepare_holdings_timeseries()

        # TODO: Implement logic to get a full timeseries for a portfolio

        return df

    def _prepare_holdings_timeseries(self) -> pd.DataFrame:
        """Create a daily holdings DataFrame pivoted by currency and security."""
        df_pivot = self.holdings.pivot(
            index="as_of_date",
            columns=["currency", "figi_code"],
            values=["quantity", "avg_price", "base_value"]
        )

        full_date_range = pd.date_range(self.holdings['as_of_date'].min(), today_midnight())

        df_pivot = df_pivot.reindex(full_date_range)
        df_pivot = df_pivot.ffill().fillna(0)
        df_pivot.index.name = "as_of_date"

        # flatten multiindex
        df_pivot.columns = ['_'.join(col).strip() for col in df_pivot.columns.values]

        # melt everything except 'as_of_date'
        df_pivot = df_pivot.reset_index()
        df_melted = df_pivot.melt(id_vars="as_of_date", var_name="key", value_name="value")

        # split 'key' into separate columns
        df_melted[['value_type', 'currency', 'figi_code']] = df_melted['key'].str.extract(
            r'^(quantity|avg_price|base_value)_(\w+)_(.+)$'
        )

        # rearrange and format
        df = df_melted.drop(columns="key").pivot(
            index=["as_of_date", "currency", "figi_code"], columns="value_type", values="value"
        ).reset_index()
        df.columns.name = ""

        return df
