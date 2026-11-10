"""Unit tests for Higher Normal Function & Singular Cycle Sieve."""

import unittest
from toolkit.normal_function_sieve import NormalFunctionSieve


class TestNormalFunctionSieve(unittest.TestCase):
    def setUp(self):
        self.sieve1 = NormalFunctionSieve(d=1)
        self.sieve3 = NormalFunctionSieve(d=3)

    def test_ivhs_action(self):
        for s in [self.sieve1, self.sieve3]:
            res = s.compute_ivhs_tangent_action()
            self.assertEqual(res["dim_moduli_space"], 4)
            self.assertEqual(res["ivhs_action_rank"], 4)
            self.assertTrue(res["ivhs_is_non_degenerate"])
            self.assertEqual(res["contraction_vector"], [6.0, 6.0, 6.0, 6.0])
            self.assertAlmostEqual(res["obstruction_norm"], 12.0, places=10)

    def test_green_griffiths_kerr_curvature(self):
        for s in [self.sieve1, self.sieve3]:
            res = s.compute_green_griffiths_kerr_curvature()
            self.assertTrue(res["is_strictly_positive_definite"])
            self.assertAlmostEqual(res["minimal_curvature"], 9.0, places=10)
            self.assertEqual(res["curvature_tensor_dimension"], (4, 4))
            self.assertFalse(res["higher_normal_function_vanishes"])
            self.assertFalse(res["deformation_integrability_satisfied"])

    def test_singular_cycle_obstruction(self):
        for s in [self.sieve1, self.sieve3]:
            res = s.evaluate_singular_cycle_obstruction()
            self.assertTrue(res["fourfold_is_absolutely_simple"])
            self.assertTrue(res["albanese_is_surjective_for_all_components"])
            self.assertEqual(res["minimal_albanese_dimension"], 4)
            self.assertFalse(res["singular_cancellation_possible"])
            self.assertGreaterEqual(res["net_cycle_deformation_obstruction"], 12.0)

    def test_chow_rank_defect_certification(self):
        for s in [self.sieve1, self.sieve3]:
            res = s.verify_chow_rank_defect()
            self.assertEqual(res["lemma_id"], "LBL-HODGE-006")
            self.assertEqual(res["dim_Hdg4"], 3)
            self.assertEqual(res["dim_polarization_span"], 1)
            self.assertEqual(res["dim_primitive_weil_space"], 2)
            self.assertEqual(res["dim_chow_image_cl"], 1)
            self.assertEqual(res["primitive_weil_algebraic_cycles"], 0)
            self.assertTrue(res["is_certified"])
            self.assertIn("sha256_seal", res)
            self.assertEqual(len(res["sha256_seal"]), 64)


if __name__ == "__main__":
    unittest.main()
