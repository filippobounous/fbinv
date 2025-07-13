"""Unit tests for Monte Carlo engines in :mod:`investment.analytics.monte_carlo`."""

import unittest

import numpy as np

from investment.analytics import BaseMonteCarloEngine, PricePathEngine, VolatilityEngine


class MonteCarloTests(unittest.TestCase):
    """Test cases for Monte Carlo path generation."""

    def test_gbm_paths_and_jump_diffusion(self):
        """Generate GBM and jump-diffusion paths consistently."""
        engine = PricePathEngine(n_steps=1, n_paths=2, random_state=0)
        spots = np.array([1.0])
        paths = engine.generate_paths(
            spots=spots, drift=np.array([0.0]), vol=np.array([0.0])
        )
        self.assertEqual(paths.shape, (2, 2, 1))
        self.assertTrue(np.all(paths[0] == spots))

        jump_paths = engine.generate_jump_diffusion_paths(
            spots, np.array([0.0]), np.array([0.0]), 0.0, 0.0, 0.0
        )
        np.testing.assert_allclose(paths, jump_paths)

    def test_apply_control_variate(self):
        """Control variate adjustment should return sample mean."""
        sample = np.array([1.0, 2.0, 3.0, 4.0])
        control = sample + 1.0
        mean = control.mean()
        result = BaseMonteCarloEngine.apply_control_variate(sample, control, mean)
        self.assertAlmostEqual(result, sample.mean())

    def test_volatility_engine_methods(self):
        """Ensure deterministic volatility path generators."""
        engine = VolatilityEngine(n_steps=1, n_paths=2, dt=1.0, random_state=0)

        heston = engine.generate_heston_vol(vol0=0.2, kappa=1.0, theta=0.3, xi=0.0)
        self.assertEqual(heston.shape, (2, 2, 1))
        self.assertTrue(np.allclose(heston[0], 0.2))
        self.assertTrue(np.allclose(heston[1], 0.3))

        garch = engine.generate_garch_vol(vol0=0.1, omega=0.0, alpha=0.0, beta=1.0)
        self.assertEqual(garch.shape, (2, 2, 1))
        self.assertTrue(np.allclose(garch[1], 0.1))

        sabr = engine.generate_sabr_vol(vol0=0.05, nu=0.0)
        self.assertEqual(sabr.shape, (2, 2, 1))
        self.assertTrue(np.allclose(sabr, 0.05))
