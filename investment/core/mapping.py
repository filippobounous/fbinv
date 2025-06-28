"""Base class for initialisations from the mapping csv files available"""

from abc import abstractmethod
from typing import Dict, Any, Optional, TYPE_CHECKING, List, Union

import pandas as pd
from pydantic import BaseModel

from ..analytics.metrics import PerformanceMetrics
from ..analytics.var import VaRCalculator
from ..analytics.realised_volatility import RealisedVolatilityCalculator
from ..analytics.returns import ReturnsCalculator
from ..datasource import LocalDataSource
from ..utils.consts import (
    DEFAULT_RET_WIN_SIZE,
    DEFAULT_RV_WIN_SIZE,
    DEFAULT_RV_MODEL,
    DEFAULT_RISK_FREE_RATE,
    DEFAULT_CONFIDENCE_LEVEL,
    DEFAULT_VAR_METHOD,
    TRADING_DAYS,
)

if TYPE_CHECKING:
    from ..datasource import BaseDataSource

class BaseMappingEntity(BaseModel):
    """
    BaseMappingEntity.
    
    Returns required attributes to a class from the base csv mapping files.
    Initialised with:
        entity_type (str): The entity type to select the correct load_method.
        code (str): The code for the entity to select the correct parameters.
    """
    entity_type: str
    code: str
    _local_datasource: LocalDataSource = LocalDataSource

    def __init__(self, **kwargs) -> None:
        """Initialise entity attributes from the local mapping files."""
        super().__init__(**kwargs)

        lds: LocalDataSource = self._local_datasource()

        load_methods = {
            "composite": lds.load_composite_security,
            "currency_cross": lds.load_security,
            "etf": lds.load_security,
            "fund": lds.load_security,
            "portfolio": lds.load_portfolio,
        }

        init_method = load_methods.get(self.entity_type)

        if init_method is None:
            raise KeyError(f"Entity type '{self.entity_type}' has not been configured.")

        di: Dict[str, Any] = init_method(self)
        for key, el in di.items():
            if hasattr(self, key):
                setattr(self, key, el)

    @abstractmethod
    def get_price_history(
        self,
        datasource: Optional["BaseDataSource"] = None,
        local_only: bool = True,
        intraday: bool = False,
    ) -> pd.DataFrame:
        """Returns time series of prices."""

    def get_returns(
        self,
        use_ln_ret: bool = True,
        ret_win_size: Union[int, List[int]] = DEFAULT_RET_WIN_SIZE,
        datasource: Optional["BaseDataSource"] = None,
        local_only: bool = True,
    ) -> pd.DataFrame:
        """Return the returns series."""
        df = self.get_price_history(
            datasource=datasource, local_only=local_only, intraday=False
        )

        return ReturnsCalculator(
            ret_win_size=ret_win_size, use_ln_ret=use_ln_ret
        ).calculate(df=df)

    def get_realised_volatility(
        self,
        rv_model: Union[str, List[str]] = DEFAULT_RV_MODEL,
        rv_win_size: Union[int, List[int]] = DEFAULT_RV_WIN_SIZE,
        datasource: Optional["BaseDataSource"] = None,
        local_only: bool = True,
    ) -> pd.DataFrame:
        """Return the realised volatility series."""
        df = self.get_price_history(
            datasource=datasource, local_only=local_only, intraday=False
        )

        return RealisedVolatilityCalculator(
            rv_win_size=rv_win_size, rv_model=rv_model
        ).calculate(df=df)

    def get_performance_metrics(
        self,
        risk_free_rate: float = DEFAULT_RISK_FREE_RATE,
        periods_per_year: int = TRADING_DAYS,
        confidence_level: float = DEFAULT_CONFIDENCE_LEVEL,
        datasource: Optional["BaseDataSource"] = None,
        local_only: bool = True,
    ) -> Dict[str, float]:
        """Return common performance and risk metrics."""
        df = self.get_price_history(
            datasource=datasource, local_only=local_only,
        )

        return {
            "cumulative_return": PerformanceMetrics.cumulative_return(df),
            "annualised_return": PerformanceMetrics.annualised_return(
                df, periods_per_year
            ),
            "max_drawdown": PerformanceMetrics.max_drawdown(df),
            "sharpe_ratio": PerformanceMetrics.sharpe_ratio(
                df,
                risk_free_rate=risk_free_rate,
                periods_per_year=periods_per_year,
            ),
            "sortino_ratio": PerformanceMetrics.sortino_ratio(
                df,
                risk_free_rate=risk_free_rate,
                periods_per_year=periods_per_year,
            ),
        }

    def get_value_at_risk(
        self,
        confidence_level: float = DEFAULT_CONFIDENCE_LEVEL,
        method: str = DEFAULT_VAR_METHOD,
        datasource: Optional["BaseDataSource"] = None,
        local_only: bool = True,
    ) -> float:
        """Return Value-at-Risk using the specified method."""
        df = self.get_price_history(
            datasource=datasource, local_only=local_only, **price_history_kwargs
        )

        methods = {
            "historical": VaRCalculator.value_at_risk,
            "parametric": VaRCalculator.parametric_var,
            "conditional": VaRCalculator.conditional_var,
        }

        calc = methods.get(method)
        if calc is None:
            raise KeyError(f"VaR method '{method}' not recognised.")

        return calc(df, confidence_level=confidence_level)
