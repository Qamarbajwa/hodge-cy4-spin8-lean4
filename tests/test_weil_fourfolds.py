"""Unit tests for Weil-Type Abelian Fourfold Analysis Engine."""

import unittest
import numpy as np
from toolkit.weil_fourfolds import WeilAbelianFourfold, wedge_product_sign


class TestWeilAbelianFourfold(unittest.TestCase):
    def setUp(self):
        self.af1 = WeilAbelianFourfold(d=1)
        self.af3 = WeilAbelianFourfold(d=3)

    def test_wedge_product_sign(self):
        # (0, 1) and (2, 3) -> sorted union is (0, 1, 2, 3) (0 inversions -> +1)
        self.assertEqual(wedge_product_sign((0, 1), (2, 3)), 1)
        # (2, 3) and (0, 1) -> (2, 3, 0, 1) -> 4 inversions -> +1
        self.assertEqual(wedge_product_sign((2, 3), (0, 1)), 1)
        # Overlapping indices -> 0
        self.assertEqual(wedge_product_sign((0, 1), (1, 2)), 0)

    def test_dimensions(self):
        self.assertEqual(len(self.af1.comb2), 28)
        self.assertEqual(len(self.af1.comb4), 70)
        self.assertEqual(len(self.af1.comb6), 28)

    def test_primitiveness(self):
        for af in [self.af1, self.af3]:
            res = af.verify_primitiveness()
            self.assertTrue(res["is_primitive"])
            self.assertAlmostEqual(res["w1_wedge_omega_norm"], 0.0, places=10)
            self.assertAlmostEqual(res["w2_wedge_omega_norm"], 0.0, places=10)

    def test_divisor_orthogonality(self):
        for af in [self.af1, self.af3]:
            divisors = [af.omega]
            res = af.verify_divisor_orthogonality(divisors)
            self.assertTrue(res["strictly_orthogonal_to_all_divisor_products"])
            self.assertEqual(res["conclusion"], "DIVISORS_CANNOT_SPAN_WEIL_CLASSES")
            self.assertAlmostEqual(res["max_poincare_intersection"], 0.0, places=10)


if __name__ == "__main__":
    unittest.main()
