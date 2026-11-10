"""Unit tests for Constructive Cycle Hunt and Exterior Algebra Module."""

import unittest
import numpy as np
from toolkit.constructive_cycle_hunt import ExteriorAlgebraWeilFourfold


class TestConstructiveCycleHunt(unittest.TestCase):
    def setUp(self):
        self.ea = ExteriorAlgebraWeilFourfold()

    def test_dimensions_and_combinatorics(self):
        self.assertEqual(len(self.ea.comb_to_idx4), 70)
        self.assertEqual(len(self.ea.comb_to_idx2), 28)
        self.assertEqual(len(self.ea.V_plus_indices), 4)
        self.assertEqual(len(self.ea.V_minus_indices), 4)

    def test_theta2_nonzero_and_self_intersection(self):
        audit = self.ea.check_primitivity_and_orthogonality()
        self.assertTrue(audit["theta2_is_nonzero"])
        # Self-intersection of Theta^2 = int_A Theta^4 = 4! = 24
        self.assertEqual(audit["theta2_self_intersection"], 24)

    def test_weil_classes_primitivity(self):
        audit = self.ea.check_primitivity_and_orthogonality()
        self.assertTrue(audit["w1_is_primitive"])
        self.assertTrue(audit["w2_is_primitive"])

    def test_divisor_orthogonality(self):
        audit = self.ea.check_primitivity_and_orthogonality()
        self.assertEqual(audit["pairing_theta2_w1"], 0)
        self.assertEqual(audit["pairing_theta2_w2"], 0)
        self.assertTrue(audit["orthogonal_to_divisors"])

    def test_pontryagin_curve_products_zero_weil_projection(self):
        for a1, a2 in [(1, 1), (2, 3), (-1, 5)]:
            pont = self.ea.compute_pontryagin_product_curves(a1, a2)
            self.assertTrue(pont["cycle_class_in_polarization_span"])
            self.assertEqual(pont["projection_on_w1"], 0)
            self.assertEqual(pont["projection_on_w2"], 0)
            self.assertTrue(pont["projects_to_zero_on_weil"])

    def test_orthogonal_projector_W0(self):
        proj = self.ea.compute_orthogonal_projector_W0()
        self.assertEqual(proj["projector_rank"], 2)
        self.assertTrue(proj["theta2_in_projector_kernel"])

    def test_bogomolov_discriminant_criterion(self):
        # A candidate bundle with Delta(E) having non-zero projection in W_0
        # Let Delta = w1 (a Weil class)
        delta_vec = self.ea.w1
        proj = self.ea.compute_orthogonal_projector_W0()
        idx_plus, idx_minus = proj["W0_indices"]

        P = np.zeros((70, 70), dtype=int)
        P[idx_plus, idx_plus] = 1
        P[idx_minus, idx_minus] = 1

        delta_proj = P @ delta_vec
        self.assertFalse(np.all(delta_proj == 0))
        # Verify that such a Delta is orthogonal to Theta^2
        pair_theta2_delta = self.ea.poincare_pairing_H4(self.ea.theta2_vec, delta_vec)
        self.assertEqual(pair_theta2_delta, 0)


if __name__ == "__main__":
    unittest.main()
