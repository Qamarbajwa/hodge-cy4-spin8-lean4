"""Unit tests for Schoen-Prym Boundary and Cycle Deformation Analyzer."""

import unittest
from toolkit.schoen_prym import SchoenBoundaryAnalyzer


class TestSchoenPrymAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer1 = SchoenBoundaryAnalyzer(d=1)
        self.analyzer3 = SchoenBoundaryAnalyzer(d=3)

    def test_schoen_cycle_coefficients(self):
        for an in [self.analyzer1, self.analyzer3]:
            res = an.solve_schoen_cycle_coefficients()
            self.assertTrue(res["solution_found"])
            self.assertAlmostEqual(res["residual_norm"], 0.0, places=10)

            # Check the specific integer ratios: 2, -1, -1, -1, -1, 2
            coeffs = res["coefficients"]
            self.assertEqual(coeffs["S_12 (E_1 x E_2)"]["coefficient_rational_ratio"], 2)
            self.assertEqual(coeffs["S_13 (E_1 x E_3)"]["coefficient_rational_ratio"], -1)
            self.assertEqual(coeffs["S_14 (E_1 x E_4)"]["coefficient_rational_ratio"], -1)
            self.assertEqual(coeffs["S_23 (E_2 x E_3)"]["coefficient_rational_ratio"], -1)
            self.assertEqual(coeffs["S_24 (E_2 x E_4)"]["coefficient_rational_ratio"], -1)
            self.assertEqual(coeffs["S_34 (E_3 x E_4)"]["coefficient_rational_ratio"], 2)

    def test_kodaira_spencer_obstruction(self):
        for an in [self.analyzer1, self.analyzer3]:
            obs = an.compute_kodaira_spencer_obstruction()
            self.assertEqual(obs["moduli_tangent_dim"], 4)
            self.assertFalse(obs["cycle_deforms_first_order"])
            self.assertGreater(obs["obstruction_norm"], 0.0)
            self.assertEqual(obs["total_obstruction_vector"], [6.0, 6.0, 6.0, 6.0])


if __name__ == "__main__":
    unittest.main()
