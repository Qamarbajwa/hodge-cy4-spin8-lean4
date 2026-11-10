"""Unit tests for Kummer Fourfold Obstruction Scan Engine."""

import unittest
from toolkit.kummer_scan import KummerFourfoldScanner


class TestKummerScanner(unittest.TestCase):
    def setUp(self):
        self.scanner1 = KummerFourfoldScanner(d=1)
        self.scanner3 = KummerFourfoldScanner(d=3)

    def test_singularities_count(self):
        for sc in [self.scanner1, self.scanner3]:
            res = sc.compute_fixed_torsion_subgroup()
            self.assertEqual(res["total_singularities"], 256)
            self.assertEqual(res["fixed_by_complex_structure"], 16)
            self.assertEqual(res["total_orbits_under_K"], 136)

    def test_exceptional_cycle_contraction(self):
        for sc in [self.scanner1, self.scanner3]:
            res = sc.verify_exceptional_cycle_contraction()
            self.assertEqual(res["num_exceptional_surfaces"], 256)
            self.assertTrue(res["pushforward_is_identically_zero"])
            self.assertEqual(res["max_pushforward_norm"], 0.0)

    def test_weil_orthogonality_to_exceptional(self):
        for sc in [self.scanner1, self.scanner3]:
            res = sc.verify_weil_orthogonality_to_exceptional_divisors()
            self.assertTrue(res["weil_class_pullback_is_hodge"])
            self.assertTrue(res["exceptional_pairing_all_zero"])
            self.assertFalse(res["escape_hatch_exists"])
            self.assertEqual(res["conclusion"], "EXCEPTIONAL_DIVISORS_CANNOT_PRODUCE_WEIL_CLASS")


if __name__ == "__main__":
    unittest.main()
