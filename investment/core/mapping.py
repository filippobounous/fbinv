"Base class for initialisations from the mapping csv files available"

from typing import Dict, Any, Optional

from abc import ABC, abstractmethod
import pandas as pd

from ..analytics.metrics import PerformanceMetrics
from ..analytics.var import VaRCalculator
from ..utils.consts import TRADING_DAYS

from pydantic import BaseModel

from ..datasource.local import LocalDataSource

class BaseMappingEntity(BaseModel, ABC):
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

    def __init__(self, **kwargs):
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
    def get_price_history(self, **kwargs) -> pd.DataFrame:
        """Return price history for the entity."""
        raise NotImplementedError

    def get_performance_metrics(
        self,
        risk_free_rate: float = 0.0,
        periods_per_year: int = TRADING_DAYS,
        confidence_level: float = 0.95,
        **price_history_kwargs,
    ) -> Dict[str, float]:
        """Return common performance and risk metrics."""
        df = self.get_price_history(**price_history_kwargs)

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
            "value_at_risk": VaRCalculator.value_at_risk(
                df, confidence_level=confidence_level
            ),
        }
