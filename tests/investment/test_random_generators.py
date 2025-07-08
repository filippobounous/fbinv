"""Unit tests for the :mod:`investment.analytics.random_generators` module."""

import unittest

import numpy as np

from investment.analytics import RandomGenerator

class RandomGeneratorTests(unittest.TestCase):
    """Test cases for :class:`RandomGenerator`."""

    def test_standard_and_antithetic_normal(self):
        """Standard draws should match antithetic pairings."""
        rng = RandomGenerator(seed=42)
        sample = rng.standard_normal((2, 3))
        self.assertEqual(sample.shape, (2, 3))

        anti = rng.antithetic_normal((4, 1))
        self.assertTrue(np.allclose(anti[:2], -anti[2:]))

    def test_other_distributions(self):
        """Check normal and uniform distribution helpers."""
        rng = RandomGenerator(seed=0)
        normal = rng.normal(0, 2, (10,))
        self.assertAlmostEqual(normal.mean(), 0, delta=1)
        self.assertEqual(normal.shape, (10,))

        uni = rng.uniform(low=1.0, high=2.0, size=(5,))
        self.assertTrue(np.all((uni >= 1.0) & (uni < 2.0)))

    def test_set_seed_and_antithetic_error(self):
        """Setting the seed resets RNG and invalid antithetic size errors."""
        rng = RandomGenerator(seed=123)
        sample1 = rng.standard_normal((1,))
        rng.set_seed(123)
        sample2 = rng.standard_normal((1,))
        np.testing.assert_allclose(sample1, sample2)

        with self.assertRaises(ValueError):
            rng.antithetic_normal((3, 1))
