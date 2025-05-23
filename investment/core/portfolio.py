import datetime
import pandas as pd
from pydantic import ConfigDict, Field
from typing import Optional

from ..config import PORTFOLIO_PATH, DEFAULT_NAME
from .mapping import BaseMappingEntity
from ..utils.date_utils import today_midnight

class Portfolio(BaseMappingEntity):
    entity_type: str = "portfolio"
    owner: Optional[str] = None
    has_cash: Optional[bool] = None
    
    portfolio: Optional[pd.DataFrame] = Field(default = None, repr=False)
    cash: Optional[pd.DataFrame] = Field(default = None, repr=False)
    
    account: Optional[str] = None
    currency: Optional[str] = None
    ignore_cash: Optional[bool] = False

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, **kwargs):

        if "code" not in kwargs:
            kwargs.update({"code": DEFAULT_NAME})

        super().__init__(**kwargs)

        self._get_portfolio()
        if self.has_cash and not self.ignore_cash:
            self._get_cash()
    
    def _get_cash(self) -> None:
        df = pd.read_csv(f"{PORTFOLIO_PATH}/{self.code}_cash.csv")

        if self.account:
            df = df.loc[df.account == self.account]

        if self.currency:
            df = df.loc[df.currency == self.currency]

        self.cash = df

    def _get_portfolio(self) -> None:
        df = pd.read_csv(f"{PORTFOLIO_PATH}/{self.code}_transactions.csv")

        if self.account:
            df = df.loc[df.account == self.account]

        if self.currency:
            df = df.loc[df.currency == self.currency]

        df['cum_quantity'] = df.groupby('code')['quantity'].cumsum()
        df['cum_value'] = df.groupby('code')['value'].cumsum()
        df['avg_price'] = df['cum_value'] / df['cum_quantity']

        result = df[
            ['as_of_date', 'code', 'cum_quantity', 'avg_price', 'currency']
        ].copy()
        result = result.rename(columns={
            'cum_quantity': 'quantity'
        })
        result["value"] = result["quantity"] * result["avg_price"]

        self.portfolio = result
