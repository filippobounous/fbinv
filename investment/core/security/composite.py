from typing import Optional, TYPE_CHECKING, ClassVar

import pandas as pd

from .base import Security
from .currency_cross import CurrencyCross
from ..utils import get_currency_cross
from ...utils.consts import OC

if TYPE_CHECKING:
    from ...datasource.base import BaseDataSource


class Composite(Security):
    entity_type: ClassVar[str] = "composite"
    security: Security
    currency_cross: CurrencyCross
    composite_currency: str

    def __init__(self, **kwargs) -> None:
        security: "Security" = kwargs.get("security")
        currency_cross: "CurrencyCross" = kwargs.get("currency_cross")
        composite_currency: str = kwargs.get("composite_currency")

        if currency_cross:
            kwargs["composite_currency"] = currency_cross.currency
        elif composite_currency:
            kwargs["currency_cross"] = get_currency_cross(
                origin_currency=security.currency, result_currency=composite_currency
            )

        kwargs["code"] = f"{security.code}_{kwargs.get('composite_currency')}"

        super().__init__(**kwargs)

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

        ph_security.columns = [f"{i}_origin" for i in ph_security.columns]
        ph_currency_cross.columns = [
            f"{i}_conversion" for i in ph_currency_cross.columns
        ]

        df = pd.concat([ph_security, ph_currency_cross], axis=1, join="inner")

        df["open"] = df["open_origin"] * df["open_conversion"]
        df["close"] = df["close_origin"] * df["close_conversion"]

        return df[["open", "close"]]
