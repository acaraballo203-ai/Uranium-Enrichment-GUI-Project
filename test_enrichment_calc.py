"""
Simple tests for enrichment_calc.py.

Run them from this folder with:
    py -m unittest
"""

import unittest

import enrichment_calc as calc


class TestEnrichmentCalc(unittest.TestCase):

    # A common textbook case: 1 kg of 4.5 % product from natural
    # uranium (0.711 %) with 0.3 % tails.

    def test_feed_needed(self):
        feed = calc.feed_needed(1, 4.5, 0.711, 0.3)
        # (4.5 - 0.3) / (0.711 - 0.3) = 10.219...
        self.assertAlmostEqual(feed, 10.219, places=3)

    def test_tails_mass(self):
        tails = calc.tails_mass(1, 4.5, 0.711, 0.3)
        self.assertAlmostEqual(tails, 9.219, places=3)

    def test_swu_needed(self):
        swu = calc.swu_needed(1, 4.5, 0.711, 0.3)
        # Worked by hand: 1*V(4.5%) + 9.219*V(0.3%) - 10.219*V(0.711%) = about 6.23
        self.assertAlmostEqual(swu, 6.23, places=2)

    def test_swu_scales_with_mass(self):
        one_kg = calc.swu_needed(1, 4.5, 0.711, 0.3)
        ten_kg = calc.swu_needed(10, 4.5, 0.711, 0.3)
        self.assertAlmostEqual(ten_kg, 10 * one_kg)

    def test_total_cost(self):
        results = calc.calculate_all(1, 4.5, 0.711, 0.3,
                                     feed_cost_per_kg=100,
                                     swu_cost=150,
                                     conversion_cost_per_kg=10)
        expected = (results["feed_mass"] * 100
                    + results["feed_mass"] * 10
                    + results["swu"] * 150)
        self.assertAlmostEqual(results["total_cost"], expected)

    def test_bad_assay_order_raises(self):
        # tails higher than feed makes no sense
        with self.assertRaises(ValueError):
            calc.feed_needed(1, 4.5, 0.711, 1.0)


if __name__ == "__main__":
    unittest.main()
