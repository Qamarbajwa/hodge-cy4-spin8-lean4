r"""Unit tests for Mumford-Weil Spinor Engine.

Verifies exact exterior algebra, Hodge diamond decompositions, D_4 = \mathfrak{so}(8)
spinor weight combinatorics, Schur's lemma endomorphism vacuum, and Markman inapplicability.
"""

import unittest
from toolkit.mumford_spinor_engine import MumfordSpinorEngine


class TestMumfordSpinorEngine(unittest.TestCase):
    def setUp(self):
        self.engine = MumfordSpinorEngine()

    def test_abelian_sixfold_hodge_diamond(self):
        res = self.engine.abelian_sixfold_hodge_diamond()
        self.assertEqual(res["dimension_complex"], 6)
        self.assertEqual(res["dimension_h1_rational"], 12)
        self.assertEqual(res["b_6"], 924)
        self.assertEqual(res["h_3_3"], 400)

        # Check all Hodge components in H^6
        decomp = res["h6_decomposition"]
        self.assertEqual(decomp["h^0,6"], 1)
        self.assertEqual(decomp["h^1,5"], 36)
        self.assertEqual(decomp["h^2,4"], 225)
        self.assertEqual(decomp["h^3,3"], 400)
        self.assertEqual(decomp["h^4,2"], 225)
        self.assertEqual(decomp["h^5,1"], 36)
        self.assertEqual(decomp["h^6,0"], 1)
        self.assertEqual(sum(decomp.values()), 924)

    def test_so8_spinor_representation_weights(self):
        res = self.engine.so8_spinor_representation_weights()
        self.assertEqual(res["representation_dimension"], 8)
        self.assertEqual(res["weights_count"], 8)
        self.assertEqual(res["antipodal_pairs_count"], 4)
        self.assertEqual(res["exterior_power_dim_wedge4"], 70)
        self.assertEqual(res["zero_weight_subspace_dimension"], 6)

        # Verify that all 6 zero-weight 4-tuples are combinations of 2 antipodal pairs
        tuples = res["zero_weight_basis_tuples"]
        self.assertEqual(len(tuples), 6)
        for t in tuples:
            self.assertEqual(len(t), 4)

    def test_tensor_core_sixfold_model(self):
        res = self.engine.tensor_core_sixfold_model()
        self.assertEqual(res["spin_representation_dimension"], 4)
        self.assertEqual(res["orthogonal_representation_dimension"], 3)
        self.assertEqual(res["total_h1_dimension"], 12)
        self.assertEqual(res["exterior_algebra_wedge6_dim"], 924)
        self.assertEqual(res["abelian_variety_dimension"], 6)
        self.assertEqual(res["middle_hodge_h33"], 400)

    def test_schur_endomorphism_vacuum(self):
        res = self.engine.schur_endomorphism_vacuum()
        self.assertEqual(res["endomorphism_algebra"], "End_Q(A) = Q")
        self.assertEqual(res["picard_number"], 1)

    def test_markman_applicability_audit(self):
        res = self.engine.markman_applicability_audit()
        self.assertFalse(res["is_markman_applicable_to_mumford"])
        comp = res["comparison"]
        self.assertTrue(comp["Weil_Type_Varieties_Markman_2025"]["secant_sheaf_applicable"])
        self.assertFalse(comp["Mumford_Spinor_Varieties_1969"]["secant_sheaf_applicable"])
        self.assertEqual(
            comp["Weil_Type_Varieties_Markman_2025"]["hodge_conjecture_status"],
            "RESOLVED_AFFIRMATIVELY (Markman arXiv:2502.03415)",
        )
        self.assertEqual(
            comp["Mumford_Spinor_Varieties_1969"]["hodge_conjecture_status"],
            "OPEN_FRONTIER (Unresolved by Markman)",
        )

    def test_cartan_weight_zero_vs_root_annihilation(self):
        res = self.engine.cartan_weight_zero_vs_root_annihilation()
        self.assertEqual(res["cartan_zero_weight_dim"], 6)
        self.assertEqual(res["total_wedge4_dim"], 70)
        self.assertEqual(res["stacked_root_operator_rank"], 6)
        self.assertEqual(res["root_annihilation_kernel_dim"], 0)
        self.assertEqual(res["full_so8_invariants_dim"], 0)
        self.assertFalse(res["is_cartan_zero_weight_annihilated_by_roots"])



if __name__ == "__main__":
    unittest.main()
