"""Base class for initialisations from the mapping csv files available"""

from __future__ import annotations

from abc import abstractmethod
from typing import Any, TYPE_CHECKING

import pandas as pd
from pydantic import BaseModel, ConfigDict

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
    DEFAULT_VAR_MODEL,
    DEFAULT_METRIC_WIN_SIZE,
    DEFAULT_VAR_WIN_SIZE,
    TRADING_DAYS,
    DEFAULT_CURRENCY
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
    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    def __setattr__(self, name: str, value: Any) -> None:
        try:
            super().__setattr__(name, value)
        except ValueError:
            object.__setattr__(self, name, value)

    def __init__(self, **kwargs) -> None:
        """Initialise entity attributes from the local mapping files."""
        kwargs.setdefault(
            "entity_type", self.__class__.__fields__["entity_type"].default
        )
        super().__init__(**kwargs)

        lds: LocalDataSource = self._local_datasource()

        load_methods = {
            "composite": lds.load_composite_security,
            "currency_cross": lds.load_security,
            "equity": lds.load_security,
            "etf": lds.load_security,
            "fund": lds.load_security,
            "portfolio": lds.load_portfolio,
        }

        init_method = load_methods.get(self.entity_type)

        if init_method is None:
            raise KeyError(f"Entity type '{self.entity_type}' has not been configured.")

        di: dict[str, Any] = init_method(self)
        for key, el in di.items():
            if hasattr(self, key):
                setattr(self, key, el)

    @abstractmethod
    def get_price_history(
        self,
        datasource: "BaseDataSource" | None = None,
        local_only: bool = True,
        intraday: bool = False,
        currency: str = DEFAULT_CURRENCY,
    ) -> pd.DataFrame:
        """Returns time series of prices."""

    def get_returns(
        self,
        use_ln_ret: bool = True,
        ret_win_size: int | list[int] = DEFAULT_RET_WIN_SIZE,
        datasource: "BaseDataSource" | None = None,
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
        rv_model: str | list[str] = DEFAULT_RV_MODEL,
        rv_win_size: int | list[int] = DEFAULT_RV_WIN_SIZE,
        datasource: "BaseDataSource" | None = None,
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
        metric_win_size: int = DEFAULT_METRIC_WIN_SIZE,
        risk_free_rate: float = DEFAULT_RISK_FREE_RATE,
        periods_per_year: int = TRADING_DAYS,
        datasource: "BaseDataSource" | None = None,
        local_only: bool = True,
    ) -> pd.DataFrame:
        """Return common performance and risk metrics."""
        df = self.get_price_history(
            datasource=datasource, local_only=local_only,
        )

        metrics = [
            PerformanceMetrics.cumulative_return(df, metric_win_size=metric_win_size),
            PerformanceMetrics.annualised_return(
                df,
                periods_per_year=periods_per_year,
                metric_win_size=metric_win_size,
            ),
            PerformanceMetrics.max_drawdown(df, metric_win_size=metric_win_size),
            PerformanceMetrics.sharpe_ratio(
                df,
                risk_free_rate=risk_free_rate,
                periods_per_year=periods_per_year,
                metric_win_size=metric_win_size,
            ),
            PerformanceMetrics.sortino_ratio(
                df,
                risk_free_rate=risk_free_rate,
                periods_per_year=periods_per_year,
                metric_win_size=metric_win_size,
            ),
        ]
        return pd.concat(metrics).reset_index(drop=True)

    def get_var(
        self,
        var_win_size: int = DEFAULT_VAR_WIN_SIZE,
        confidence_level: float = DEFAULT_CONFIDENCE_LEVEL,
        method: str = DEFAULT_VAR_MODEL,
        datasource: "BaseDataSource" | None = None,
        local_only: bool = True,
    ) -> pd.DataFrame:
        """Return Value-at-Risk using the specified method."""
        df = self.get_price_history(
            datasource=datasource, local_only=local_only,
        )

        calc = VaRCalculator.registry().get(method)
        if calc is None:
            raise KeyError(f"VaR method '{method}' not recognised.")

        return calc(
            df,
            confidence_level=confidence_level,
            var_win_size=var_win_size,
        )
