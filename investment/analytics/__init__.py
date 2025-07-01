"""Analytics calculators for performance and risk analysis.

This package exposes helpers for computing portfolio returns, realised
volatility, general performance metrics, Value-at-Risk estimates, and
a Monte-Carlo Engine.
"""

from .correlation import CorrelationCalculator
from .realised_volatility import RealisedVolatilityCalculator
from .returns import ReturnsCalculator
from .metrics import PerformanceMetrics
from .var import VaRCalculator
from .monte_carlo import (
    BaseMonteCarloEngine,
    PricePathEngine,
    VolatilityEngine,
)
from .random_generators import RandomGenerator

__all__ = [
    "CorrelationCalculator",
    "RealisedVolatilityCalculator",
    "ReturnsCalculator",
    "PerformanceMetrics",
    "VaRCalculator",
    "BaseMonteCarloEngine",
    "PricePathEngine",
    "VolatilityEngine",
    "RandomGenerator",
]
# TODO: add analytics such as:
#   realised volatility forecasting
#   portfolio rebalancing
#   portfolio optimisation
#   suggest portfolio trades
#   .....sugest more
