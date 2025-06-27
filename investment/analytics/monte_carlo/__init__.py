"""Monte Carlo engine subpackage."""

from .base import BaseMonteCarloEngine
from .price_path import PricePathEngine
from .volatility import VolatilityEngine

__all__ = [
    "BaseMonteCarloEngine",
    "PricePathEngine",
    "VolatilityEngine",
]

# Ideas for further extensions:
#  - More exotic stochastic volatility models: incorporate jump volatility or
#    rough volatility frameworks.
#  - Path recycling and GPU acceleration: re-use generated shocks and leverage
#    GPU libraries such as CuPy for massive simulations.
#  - Quasi-random sampling methods for improved convergence: support Sobol or
#    Halton sequences to reduce simulation variance.
#  - Multi-threaded random number generation: parallelise RNG to better use
#    multi-core CPUs and speed up path creation.
#  - Calibration utilities for stochastic models: provide tools for parameter
#    estimation from historical data or market quotes.
#  - Asian and barrier option payoff helpers: build reusable payoff functions
#    for common exotic derivatives.
#  - Support for regime-switching dynamics: allow model parameters to change
#    according to a finite-state Markov chain.

