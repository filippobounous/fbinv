"""Engines for generating correlated price or returns paths."""

from typing import Callable

import numpy as np

from . import BaseMonteCarloEngine

class PricePathEngine(BaseMonteCarloEngine):
    """Engine for generating correlated price or returns paths."""

    @staticmethod
    def registry() -> dict[str, Callable[..., np.ndarray]]:
        """Return available path generation methods."""
        return {
            "gbm": PricePathEngine.generate_paths,
            "jump_diffusion": PricePathEngine.generate_jump_diffusion_paths,
        }

    def generate_paths(
        self,
        spots: np.ndarray,
        drift: float | np.ndarray | Callable[[int], np.ndarray],
        vol: float | np.ndarray | Callable[[int], np.ndarray],
    ) -> np.ndarray:
        """Generate correlated geometric Brownian motion paths.

        Parameters
        ----------
        spots : ndarray
            Initial asset prices of shape ``(n_assets,)``.
        drift : float or ndarray or Callable[[int], ndarray]
            Drift terms which may be constant or vary by asset or time.
        vol : float or ndarray or Callable[[int], ndarray]
            Volatility specification which can be constant, an array of shape
            ``(n_assets,)`` or ``(n_steps, n_assets)``, or a callable returning a
            volatility vector for each step.

        Returns
        -------
        ndarray
            Simulated price paths of shape ``(n_steps + 1, n_paths, n_assets)``.
        """

        spots = np.asarray(spots, dtype=float)
        n_assets = len(spots)
        drift = np.asarray(drift, dtype=float) if not callable(drift) else drift

        paths = np.zeros((self.n_steps + 1, self.n_paths, n_assets))
        paths[0] = spots

        sqrt_dt = np.sqrt(self.dt)
        for t in range(1, self.n_steps + 1):
            sigma = self._prepare_vol(vol, t - 1, n_assets)
            mu = self._prepare_drift(drift, t - 1, n_assets)
            chol = self._prepare_corr(t - 1)
            z = self._get_random_shocks((self.n_paths, n_assets))
            if chol is not None:
                z = z @ chol.T
            drift_term = (mu - 0.5 * sigma ** 2) * self.dt
            diffusion = sigma * sqrt_dt * z
            paths[t] = paths[t - 1] * np.exp(drift_term + diffusion)

        return paths

    def generate_jump_diffusion_paths(
        self,
        spots: np.ndarray,
        drift: float | np.ndarray | Callable[[int], np.ndarray],
        vol: float | np.ndarray | Callable[[int], np.ndarray],
        jump_intensity: float,
        jump_mean: float,
        jump_std: float,
    ) -> np.ndarray:
        """Generate GBM paths with Merton-style jumps.

        Parameters
        ----------
        spots : ndarray
            Initial asset prices of shape ``(n_assets,)``.
        drift : float or ndarray or Callable[[int], ndarray]
            Drift specification for the underlying process.
        vol : float or ndarray or Callable[[int], ndarray]
            Volatility specification used for the diffusion part.
        jump_intensity : float
            Average number of jumps per unit time.
        jump_mean : float
            Mean of jump sizes in log space.
        jump_std : float
            Standard deviation of jump sizes.

        Returns
        -------
        ndarray
            Simulated price paths including jumps, of shape
            ``(n_steps + 1, n_paths, n_assets)``.
        """

        paths = self.generate_paths(spots=spots, drift=drift, vol=vol)

        for t in range(1, self.n_steps + 1):
            num_jumps = self.random_state.poisson(
                jump_intensity * self.dt, (self.n_paths, paths.shape[2])
            )
            if np.any(num_jumps > 0):
                jump_sizes = self._randn((self.n_paths, paths.shape[2])) * jump_std + jump_mean
                jump_factor = np.exp(jump_sizes * num_jumps)
                paths[t] *= jump_factor

        return paths

__all__ = [
    "PricePathEngine",
]
