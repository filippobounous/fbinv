"Composite security class to convert between currencies"

from typing import Optional, TYPE_CHECKING, ClassVar

import pandas as pd

from .base import BaseSecurity
from .currency_cross import CurrencyCross
from ..utils import get_currency_cross
from ...utils.consts import OC

if TYPE_CHECKING:
    from ...datasource.base import BaseDataSource

class Composite(BaseSecurity):
    """
    Composite Security.
    
    Converts a given security (Security) with currency to a different
    currency using a CurrencyCross Security. Initalialised with:
        security (Security): The base security to convert
        currency_cross (opt, str): The currency to convert to
        composite_currency (opt, CurrencyCross): The conversion security 
    """
    entity_type: ClassVar[str] = "composite"
    security: BaseSecurity
    currency_cross: CurrencyCross

    def __init__(self, **kwargs) -> None:
        security: "BaseSecurity" = kwargs.get("security")
        currency_cross: "CurrencyCross" = kwargs.get("currency_cross")
        composite_currency: str = kwargs.get("composite_currency")

        if currency_cross:
            kwargs["composite_currency"] = currency_cross.currency
        elif composite_currency:
            kwargs["currency_cross"] = get_currency_cross(
                origin_currency=security.currency,
                result_currency=composite_currency
            )

        kwargs["code"] = f"{security.code}_{kwargs.get('composite_currency')}"

        super().__init__(**kwargs)

    def __repr__(self):
        pa = f"security={self.security.code}, currency_cross={self.currency_cross.code}"
        string = f"""Composite(entity_type={self.entity_type}, {pa})"""
        return string

    def get_price_history(
        self,
        datasource: Optional["BaseDataSource"] = None,
        local_only: bool = True,
        intraday: bool = False,
    ) -> pd.DataFrame:
        kwargs = {
            "datasource": datasource,
            "local_only": local_only,
            "intraday": intraday,
        }

        ph_security = self.security.get_price_history(**kwargs)[OC]
        ph_currency_cross = self.currency_cross.get_price_history(**kwargs)[OC]

        ph_security.columns = [f"{i}_sec" for i in ph_security.columns]
        ph_currency_cross.columns = [f"{i}_ccy" for i in ph_currency_cross.columns]

        df = pd.merge(
            left=ph_security, right=ph_currency_cross,
            how="inner", left_index=True, right_index=True,
        ).dropna()

        df["open"] = df["open_sec"] * df["open_ccy"]
        df["close"] = df["close_sec"] * df["close_ccy"]

        return df[["open", "close"]]
