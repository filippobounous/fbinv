import pandas as pd
from pydantic import ConfigDict, Field
from typing import Optional, ClassVar

from ..config import PORTFOLIO_PATH, DEFAULT_NAME
from .mapping import BaseMappingEntity
from .transactions import Transactions
from ..utils.exceptions import TransactionsException


class Portfolio(BaseMappingEntity):
    entity_type: ClassVar[str] = "portfolio"
    owner: Optional[str] = None
    has_cash: Optional[bool] = None
    holdings: Optional[pd.DataFrame] = Field(default=None, repr=False)
    cash: Optional[pd.DataFrame] = Field(default=None, repr=False)
    account: Optional[str] = None
    currency: Optional[str] = None
    ignore_cash: Optional[bool] = False

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, code: Optional[str] = None, **kwargs) -> None:

        if code is not None:
            kwargs["code"] = code
        if "code" not in kwargs:
            kwargs["code"] = DEFAULT_NAME

        super().__init__(**kwargs)

        self._load_cash_and_holdings()

    @property
    def transactions(self) -> pd.DataFrame:
        return pd.read_csv(
            self._get_path(label="transactions"),
            parse_dates=["as_of_date"],
        )

    def update(self) -> None:
        tr = Transactions()
        if self.code == tr.code:
            Transactions().update()
            self._load_cash_and_holdings()
        else:
            raise TransactionsException(
                f"Missing transactions updateable file for {self.code}"
            )

    def _load_cash_and_holdings(self) -> None:
        self._get_holdings()
        if self.has_cash and not self.ignore_cash:
            self._get_cash()

    def _get_path(self, label: str) -> str:
        return f"{PORTFOLIO_PATH}/{self.code}-{label}.csv"

    def _get_cash(self) -> None:
        df = pd.read_csv(self._get_path(label="cash"), parse_dates=["as_of_date"])

        if self.account:
            df = df.loc[df.account == self.account]

        if self.currency:
            df = df.loc[df.currency == self.currency]

        self.cash = df

    def _get_holdings(self) -> None:
        df = self.transactions

        if self.account:
            df = df.loc[df["account"] == self.account]

        if self.currency:
            df = df.loc[df["currency"] == self.currency]

        df["cum_quantity"] = df.groupby("figi_code")["quantity"].cumsum()
        df["cum_value"] = df.groupby("figi_code")["value"].cumsum()
        df["avg_price"] = df["cum_value"] / df["cum_quantity"]

        result = df[
            ["as_of_date", "figi_code", "cum_quantity", "avg_price", "currency"]
        ].copy()
        result = result.rename(columns={"cum_quantity": "quantity"})
        result["base_value"] = result["quantity"] * result["avg_price"]

        self.holdings = result

    def get_price_history(self) -> None:
        pass
