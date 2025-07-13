"""Analytics calculators for performance and risk analysis.

This package exposes helpers for computing portfolio returns, realised
volatility, general performance metrics, Value-at-Risk estimates, and
a Monte-Carlo Engine.
"""

from .correlation import CorrelationCalculator
from .metrics import PerformanceMetrics
from .monte_carlo import BaseMonteCarloEngine, PricePathEngine, VolatilityEngine
from .random_generators import RandomGenerator
from .realised_volatility import RealisedVolatilityCalculator
from .returns import ReturnsCalculator
from .var import VaRCalculator

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
