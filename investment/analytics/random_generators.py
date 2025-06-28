"""Random generator utilities for Monte Carlo simulations."""

from typing import Optional, Tuple, Callable, Any, Dict

import numpy as np

from .base import _BaseAnalytics

class RandomGenerator(_BaseAnalytics):
    """Wrapper around ``numpy.random.Generator`` with helper methods."""

    @staticmethod
    def registry() -> Dict[str, Callable[[Any], np.ndarray]]:
        """Available random number generation routines."""
        return {
            "standard_normal": RandomGenerator.standard_normal,
            "antithetic_normal": RandomGenerator.antithetic_normal,
            "normal": RandomGenerator.normal,
            "uniform": RandomGenerator.uniform,
        }

    def __init__(self, seed: Optional[int] = None) -> None:
        self._rng = np.random.default_rng(seed)

    def standard_normal(self, size: Tuple[int, ...]) -> np.ndarray:
        """Return draws from a standard normal distribution."""
        return self._rng.standard_normal(size)

    def antithetic_normal(self, size: Tuple[int, int]) -> np.ndarray:
        """Return antithetic standard normal draws.

        Parameters
        ----------
        size : tuple of int
            Output shape ``(n_paths, n_assets)``. ``n_paths`` must be even.

        Returns
        -------
        ndarray
            Array where the second half is the negative of the first half.
        """
        if size[0] % 2 != 0:
            raise ValueError("First dimension must be even for antithetic sampling")
        half = size[0] // 2
        sample = self._rng.standard_normal((half, size[1]))
        return np.concatenate([sample, -sample], axis=0)

    def normal(self, mean: float, std: float, size: Tuple[int, ...]) -> np.ndarray:
        """Return draws from a normal distribution with mean and standard deviation.

        Parameters
        ----------
        mean : float
            Mean of the normal distribution.
        std : float
            Standard deviation of the distribution.
        size : tuple of int
            Desired output shape.

        Returns
        -------
        ndarray
            Draws from ``N(mean, std^2)``.
        """
        return self._rng.normal(loc=mean, scale=std, size=size)

    def uniform(
        self,
        low: float = 0.0, high: float = 1.0,
        size: Tuple[int, ...] | None = None
    ) -> np.ndarray:
        """Return draws from a uniform distribution.

        Parameters
        ----------
        low : float, default 0.0
            Lower bound of the distribution.
        high : float, default 1.0
            Upper bound of the distribution.
        size : tuple of int, optional
            Desired output shape.

        Returns
        -------
        ndarray
            Uniformly distributed random numbers in ``[low, high)``.
        """
        return self._rng.uniform(low=low, high=high, size=size)

    def set_seed(self, seed: Optional[int]) -> None:
        """Reset the underlying random number generator with a new seed."""
        self._rng = np.random.default_rng(seed)
