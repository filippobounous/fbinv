"""Stochastic volatility model generators."""

from typing import Callable

import numpy as np

from .base import BaseMonteCarloEngine

class VolatilityEngine(BaseMonteCarloEngine):
    """Engine for generating stochastic volatility paths."""

    @staticmethod
    def registry() -> dict[str, Callable[..., np.ndarray]]:
        """Return available volatility generation methods."""
        return {
            "heston": VolatilityEngine.generate_heston_vol,
            "garch": VolatilityEngine.generate_garch_vol,
            "sabr": VolatilityEngine.generate_sabr_vol,
        }

    def generate_heston_vol(
        self,
        vol0: float | np.ndarray,
        kappa: float,
        theta: float,
        xi: float,
    ) -> np.ndarray:
        """Generate volatility paths using a simple Heston model.

        Parameters
        ----------
        vol0 : float or ndarray
            Initial volatility levels for each asset.
        kappa : float
            Mean reversion rate of the variance process.
        theta : float
            Long-run mean variance.
        xi : float
            Volatility of volatility.

        Returns
        -------
        ndarray
            Volatility paths of shape ``(n_steps + 1, n_paths, n_assets)``.
        """

        vol0 = np.asarray(vol0, dtype=float)
        n_assets = vol0.size
        vols = np.zeros((self.n_steps + 1, self.n_paths, n_assets))
        vols[0] = vol0
        sqrt_dt = np.sqrt(self.dt)

        for t in range(1, self.n_steps + 1):
            z = self._get_random_shocks((self.n_paths, n_assets))
            prev = vols[t - 1]
            d_var = kappa * (theta - prev) * self.dt + xi * sqrt_dt * z
            vols[t] = np.abs(prev + d_var)

        return vols

    def generate_garch_vol(
        self,
        vol0: float | np.ndarray,
        omega: float,
        alpha: float,
        beta: float,
    ) -> np.ndarray:
        """Generate volatility paths using a basic GARCH(1,1) model.

        Parameters
        ----------
        vol0 : float or ndarray
            Initial volatility levels for each asset.
        omega : float
            Constant term of the variance recursion.
        alpha : float
            Coefficient for lagged squared returns.
        beta : float
            Coefficient for lagged variance.

        Returns
        -------
        ndarray
            Volatility paths of shape ``(n_steps + 1, n_paths, n_assets)``.
        """

        vol0 = np.asarray(vol0, dtype=float)
        n_assets = vol0.size
        vols = np.zeros((self.n_steps + 1, self.n_paths, n_assets))
        vols[0] = vol0

        z_prev = self._get_random_shocks((self.n_paths, n_assets))
        epsilon_prev = vol0 * z_prev
        var_prev = vol0 ** 2

        for t in range(1, self.n_steps + 1):
            var_t = omega + alpha * epsilon_prev ** 2 + beta * var_prev
            vol_t = np.sqrt(np.maximum(var_t, 0))
            vols[t] = vol_t
            z = self._get_random_shocks((self.n_paths, n_assets))
            epsilon_prev = vol_t * z
            var_prev = var_t

        return vols

    def generate_sabr_vol(
        self,
        vol0: float | np.ndarray,
        nu: float,
    ) -> np.ndarray:
        """Generate volatility paths using a lognormal SABR volatility process.

        Parameters
        ----------
        vol0 : float or ndarray
            Initial volatility levels for each asset.
        nu : float
            Volatility of volatility parameter.

        Returns
        -------
        ndarray
            Volatility paths of shape ``(n_steps + 1, n_paths, n_assets)``.
        """

        vol0 = np.asarray(vol0, dtype=float)
        n_assets = vol0.size
        vols = np.zeros((self.n_steps + 1, self.n_paths, n_assets))
        vols[0] = vol0
        sqrt_dt = np.sqrt(self.dt)

        for t in range(1, self.n_steps + 1):
            z = self._get_random_shocks((self.n_paths, n_assets))
            vols[t] = vols[t - 1] * np.exp(-0.5 * nu ** 2 * self.dt + nu * sqrt_dt * z)

        return vols
