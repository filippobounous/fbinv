"""Monte Carlo path generation utilities."""

from abc import abstractmethod
from typing import Callable

import numpy as np

from ..base import BaseAnalytics
from ..random_generators import RandomGenerator

class BaseMonteCarloEngine(BaseAnalytics):
    """Base class providing common Monte Carlo helpers.

    Parameters
    ----------
    n_steps : int
        Number of time steps to simulate.
    n_paths : int
        Number of simulation paths to generate.
    dt : float, default ``1 / 252``
        Time increment per step.
    corr_matrix : array-like or Callable[[int], ndarray], optional
        Correlation matrix between asset returns. If ``None`` assets are
        independent.
    random_state : int, optional
        Seed for the random number generator.
    random_generator : RandomGenerator or Callable[[tuple], ndarray], optional
        Custom random number generator used for drawing normal shocks.
    use_antithetic : bool
        If ``True`` use antithetic variates for variance reduction.
    """

    def __init__(
        self,
        n_steps: int,
        n_paths: int,
        dt: float = 1 / 252,
        corr_matrix: np.ndarray | Callable[[int], np.ndarray] | None = None,
        random_state: int | None = None,
        random_generator: RandomGenerator | Callable[[tuple], np.ndarray] | None = None,
        use_antithetic: bool = False,
    ) -> None:
        """Base init class for the MonteCarlo engine"""
        self.n_steps = n_steps
        self.n_paths = n_paths
        self.dt = dt
        self.random_state = np.random.default_rng(random_state)
        self.corr_matrix = corr_matrix
        if corr_matrix is not None and not callable(corr_matrix):
            self._chol = np.linalg.cholesky(np.asarray(corr_matrix))
        else:
            self._chol = None
        self.random_generator = random_generator
        self.use_antithetic = use_antithetic

    @staticmethod
    @abstractmethod
    def registry() -> dict[str, Callable[..., np.ndarray]]:
        """Registry of MonteCarlo methods"""

    def _randn(self, size: tuple) -> np.ndarray:
        """Return random draws using either a custom or NumPy generator.

        Parameters
        ----------
        size : tuple
            Desired output shape of the sample.

        Returns
        -------
        ndarray
            Standard normal draws of the requested shape.
        """

        if isinstance(self.random_generator, RandomGenerator):
            return self.random_generator.standard_normal(size)
        if callable(self.random_generator):
            return np.asarray(self.random_generator(size))
        return self.random_state.standard_normal(size)

    def _get_random_shocks(self, size: tuple) -> np.ndarray:
        """Generate random shocks, optionally using antithetic variates.

        Parameters
        ----------
        size : tuple
            Desired output shape ``(n_paths, n_assets)``.

        Returns
        -------
        ndarray
            Array of normal shocks, doubled when antithetic variates are used.
        """

        if not self.use_antithetic:
            return self._randn(size)
        if size[0] % 2 != 0:
            raise ValueError("n_paths must be even when using antithetic variates")
        half = size[0] // 2
        base = self._randn((half, size[1]))
        return np.concatenate([base, -base], axis=0)

    def _prepare_vol(
        self,
        vol: float | np.ndarray | Callable[[int], np.ndarray],
        step: int,
        n_assets: int,
    ) -> np.ndarray:
        """Return the volatility for a given simulation step.

        Parameters
        ----------
        vol : float or ndarray or Callable[[int], ndarray]
            Volatility specification which may be scalar, time dependent array or
            callable returning an array for the step.
        step : int
            Index of the current step.
        n_assets : int
            Number of assets being simulated.

        Returns
        -------
        ndarray
            Volatility values for each asset at ``step``.
        """

        if callable(vol):
            sigma = np.asarray(vol(step))
        elif np.isscalar(vol):
            sigma = np.full(n_assets, float(vol))
        else:
            vol = np.asarray(vol)
            if vol.ndim == 1:
                if len(vol) == n_assets:
                    sigma = vol
                else:
                    sigma = np.full(n_assets, vol[step])
            else:
                sigma = vol[step]
        return sigma

    def _prepare_drift(
        self, drift: float | np.ndarray | Callable[[int], np.ndarray], step: int, n_assets: int
    ) -> np.ndarray:
        """Return the drift for a given simulation step.

        Parameters
        ----------
        drift : float or ndarray or Callable[[int], ndarray]
            Drift specification that may vary with time or asset.
        step : int
            Index of the current step.
        n_assets : int
            Number of assets being simulated.

        Returns
        -------
        ndarray
            Drift values for each asset at ``step``.
        """

        if callable(drift):
            mu = np.asarray(drift(step))
        elif np.isscalar(drift):
            mu = np.full(n_assets, float(drift))
        else:
            drift = np.asarray(drift)
            if drift.ndim == 1:
                if len(drift) == n_assets:
                    mu = drift
                else:
                    mu = np.full(n_assets, drift[step])
            else:
                mu = drift[step]
        return mu

    def _prepare_corr(self, step: int) -> np.ndarray | None:
        """Return Cholesky factor for correlations at a given step.

        Parameters
        ----------
        step : int
            Index of the current step.

        Returns
        -------
        ndarray or None
            Cholesky factor of the correlation matrix or ``None`` if no
            correlations are specified.
        """

        if self.corr_matrix is None:
            return None
        if callable(self.corr_matrix):
            matrix = np.asarray(self.corr_matrix(step))
            return np.linalg.cholesky(matrix)
        if self._chol is not None:
            return self._chol
        return None

    @staticmethod
    def apply_control_variate(
        sample: np.ndarray,
        control: np.ndarray,
        control_expectation: float,
    ) -> float:
        """Return mean of ``sample`` adjusted with a control variate.

        Parameters
        ----------
        sample : ndarray
            Sample observations of the payoff or quantity of interest.
        control : ndarray
            Control variate values correlated with ``sample``.
        control_expectation : float
            Known expectation of the control variate.

        Returns
        -------
        float
            Variance-reduced estimate of ``sample``'s expectation.
        """

        sample = np.asarray(sample, dtype=float)
        control = np.asarray(control, dtype=float)
        cov = np.cov(sample, control)[0, 1]
        var = np.var(control)
        if var == 0:
            return sample.mean()
        beta = cov / var
        return sample.mean() - beta * (control.mean() - control_expectation)

__all__ = [
    "BaseMonteCarloEngine",
]
