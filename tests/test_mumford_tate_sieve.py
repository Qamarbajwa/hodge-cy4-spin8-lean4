"""Unit tests for Mumford-Tate Sieve and Self-Intersection Engine."""

import unittest
from toolkit.mumford_tate_sieve import MumfordTateSieve


class TestMumfordTateSieve(unittest.TestCase):
    def setUp(self):
        self.sieve1 = MumfordTateSieve(d=1)
        self.sieve3 = MumfordTateSieve(d=3)

    def test_poincare_intersection_matrix(self):
        for s in [self.sieve1, self.sieve3]:
            res = s.compute_poincare_intersection_matrix()
            self.assertAlmostEqual(res["Q_11"], 12.0, places=10)
            self.assertAlmostEqual(res["Q_12"], 0.0, places=10)
            self.assertAlmostEqual(res["Q_22"], 4.0, places=10)
            self.assertTrue(res["is_positive_definite"])
            self.assertTrue(res["hodge_riemann_satisfied"])
            self.assertEqual(res["eigenvalues"], [4.0, 12.0])

    def test_mohan_kumar_murthy_roy_obstruction(self):
        for s in [self.sieve1, self.sieve3]:
            res = s.evaluate_mohan_kumar_murthy_roy_obstruction()
            self.assertEqual(res["euler_characteristic_required"], 12)
            self.assertTrue(res["satisfies_noether_divisibility"])
            self.assertEqual(res["bmy_upper_bound_3_eS"], 36)
            self.assertEqual(res["admissible_K2_values"], [12, 24, 36])
            self.assertIn("OBSTRUCTED", res["albanese_endomorphism_obstruction"])


if __name__ == "__main__":
    unittest.main()
