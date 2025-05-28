import pandas as pd
from typing import Optional, ClassVar, TYPE_CHECKING, Union, List

from ...analytics.realised_volatility import RealisedVolatilityCalculator
from ...analytics.returns import ReturnsCalculator
from ...config import TIMESERIES_DATA_PATH
from ...datasource.utils import get_datasource
from ..mapping import BaseMappingEntity
from ...utils.consts import DEFAULT_RET_WIN_SIZE, DEFAULT_RV_WIN_SIZE, DEFAULT_RV_MODEL

if TYPE_CHECKING:
    from ...datasource.base import BaseDataSource

class Security(BaseMappingEntity):
    entity_type: ClassVar[str] = "security"
    name: Optional[str] = None
    figi_code: Optional[str] = None
    reporting_currency: Optional[str] = None
    currency: Optional[str] = None
    financial_times_code: Optional[str] = None
    financial_times_security_type: Optional[str] = None
    bloomberg_code: Optional[str] = None
    yahoo_finance_code: Optional[str] = None
    twelve_data_code: Optional[str] = None
    alpha_vantage_code: Optional[str] = None
    multiplier: Optional[float] = None

    def __init__(self, code: Optional[str] = None, **kwargs) -> None:
        from ...datasource.registry import datasource_codes
        
        if code is not None:
            kwargs["code"] = code

        super().__init__(**kwargs)

        missing = [
            k
            for k, v in self.__dict__.items()
            if v is None and k not in ["entity_type"] + datasource_codes
        ]
        if missing:
            raise ValueError(f"{self.code} is missing required values for: {missing}.")

    def get_file_path(self, datasource_name: str, intraday: bool, series_type: str) -> str:
        from ...datasource.registry import LocalDataSource, OpenFigiDataSource

        if datasource_name == LocalDataSource.name:
            _file_name = "code"
        elif datasource_name == OpenFigiDataSource.name:
            _file_name = "figi_code"
        else:
            _file_name = getattr(self, f"{datasource_name}_code", None)
        
        file_name = _file_name.replace("/", "") if _file_name else _file_name

        data_frequency = "intraday" if intraday else "daily"
        return f"{TIMESERIES_DATA_PATH}/{series_type}/{datasource_name}/{self.entity_type}/{file_name}-{data_frequency}-{series_type}.csv"

    def get_price_history(self, datasource: Optional["BaseDataSource"] = None, local_only: bool = True, intraday: bool = False) -> pd.DataFrame:
        datasource = get_datasource(datasource=datasource)
        return datasource.get_price_history(security=self, intraday=intraday, local_only=local_only)

    def get_returns(
        self,
        use_ln_ret: bool = True,
        ret_win_size: Union[int, List[int]] = DEFAULT_RET_WIN_SIZE,
        datasource: Optional["BaseDataSource"] = None,
        local_only: bool = True,
    ) -> pd.DataFrame:
        df = self.get_price_history(datasource=datasource, local_only=local_only, intraday=False)

        return ReturnsCalculator(ret_win_size=ret_win_size, ln_ret=use_ln_ret).calculate(df=df)

    def get_realised_volatility(
        self,
        rv_model: Union[str, List[str]] = DEFAULT_RV_MODEL,
        rv_win_size: Union[int, List[int]] = DEFAULT_RV_WIN_SIZE,
        datasource: Optional["BaseDataSource"] = None,
        local_only: bool = True,
    ) -> pd.DataFrame:
        df = self.get_price_history(datasource=datasource, local_only=local_only, intraday=False)

        return RealisedVolatilityCalculator(rv_win_size=rv_win_size, rv_model=rv_model).calculate(df=df)
