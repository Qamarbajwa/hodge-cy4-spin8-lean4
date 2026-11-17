"""Adversarial Reviewer Test Suite for the Macaulay Apolarity Inverse Engine.

Verifies Role 2 mandates:
  1. Exact graded Macaulay tower dimensions R^m(F_0) -> R^{12+m}(F_0) for m=1..6
     and exact rational multiplication matrix vs sparse nullspace agreement.
  2. Annihilator Recovery Check: single 2-plane lambda_Pi = x_0^4 x_1^4 x_2^4 recovers
     the exact linear ideal (x_0, x_1, x_2) of dimension 3 without false positives.
  3. Signed Decomposition & Quadric Factorization Check: lambda_signed = lambda_+ - lambda_-
     yields dim Ann_{R^1} = 0, dim Ann_{R^2} = 9, decomposes back into (lambda_+, lambda_-)
     maximizing Score = 36, and factorizes Ann_{R^2} into exact cross-product ideal I_+ * I_-.
  4. All-18-Partition Decomposition Audit: every Band-1 (10 partitions / 1,001 modes) and
     Band-2 Shioda join (6 partitions / 630 modes) shadow factors into primary geometric equations.
  5. Effective Degree Bound & Honesty Boundary: verifies Macaulay Growth Theorem
     r_{m+1} <= r_m^{<m>} and Gotzmann bounds while preserving general_fiber_hilbert_bound_known = False.
  6. Zero-Float & 24/24 Zero-Axiom Lean 4 Check: scan_forbidden == [] and all 24 Lean theorems axioms == [].
"""

from __future__ import annotations

import unittest
from fractions import Fraction
from pathlib import Path

from toolkit.exact_linalg import exact_kernel_basis, exact_matrix_rank
from toolkit.hodge_proof_closure_reviewer import HodgeProofClosureReviewer, LEAN_THEOREM_SPECS
from toolkit.integrity import scan_forbidden
from toolkit.macaulay_apolarity_inverse_engine import MacaulayApolarityInverseEngine


class TestMacaulayApolarityInverseEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parent.parent
        cls.engine = MacaulayApolarityInverseEngine()
        cls.reviewer = HodgeProofClosureReviewer(repo_root=cls.root)
        cls.audit = cls.engine.run_full_audit()

    def test_01_graded_tower_dimensions_and_dense_sparse_agreement(self) -> None:
        """Confirms exact domain/codomain dims for m=1..6 and dense/sparse RREF agreement."""
        tower = self.engine.tower
        expected_dom = {1: 6, 2: 21, 3: 56, 4: 126, 5: 246, 6: 426}
        expected_cod = {1: 1686, 2: 1506, 3: 1246, 4: 951, 5: 666, 6: 426}
        for m in range(1, 7):
            self.assertEqual(len(tower.bases[m]), expected_dom[m])
            self.assertEqual(len(tower.bases[12 + m]), expected_cod[m])

        # Cross-check dense multiplication_matrix against sparse solver on mixed polynomial at m=1,2,3
        test_poly = {
            (4, 3, 3, 2, 0, 0): Fraction(1, 1),
            (0, 3, 4, 1, 4, 0): Fraction(-2, 1),
        }
        for m in (1, 2, 3):
            dense = tower.multiplication_matrix(test_poly, m)
            self.assertEqual(len(dense), expected_cod[m])
            self.assertEqual(len(dense[0]), expected_dom[m])
            sparse_res = tower.annihilator_at_degree(test_poly, m)
            self.assertEqual(sparse_res["rank"], exact_matrix_rank(dense))
            self.assertEqual(sparse_res["kernel_vectors"], exact_kernel_basis(dense))

    def test_02_annihilator_recovery_single_2_plane_no_false_positives(self) -> None:
        """Verifies lambda_Pi = x_0^4 x_1^4 x_2^4 recovers exact ideal (x_0, x_1, x_2) with zero false positives."""
        pi = {(4, 4, 4, 0, 0, 0): Fraction(1, 1)}
        res_m1 = self.engine.tower.annihilator_at_degree(pi, 1)
        self.assertEqual(res_m1["rank"], 3)
        self.assertEqual(res_m1["annihilator_dim"], 3)

        recovered_exps = set()
        for poly in res_m1["basis_polys"]:
            self.assertEqual(len(poly), 1)
            mon, coeff = next(iter(poly.items()))
            self.assertEqual(coeff, Fraction(1, 1))
            recovered_exps.add(mon)

        expected = {(1, 0, 0, 0, 0, 0), (0, 1, 0, 0, 0, 0), (0, 0, 1, 0, 0, 0)}
        forbidden = {(0, 0, 0, 1, 0, 0), (0, 0, 0, 0, 1, 0), (0, 0, 0, 0, 0, 1)}
        self.assertEqual(recovered_exps, expected)
        self.assertTrue(recovered_exps.isdisjoint(forbidden))

        full_t = self.engine.tower.compute_tower(pi, max_degree=6)
        self.assertEqual(full_t["ranks"], (3, 6, 10, 15, 18, 19))
        self.assertEqual(full_t["annihilator_dims"], (3, 15, 46, 111, 228, 407))

    def test_03_signed_decomposition_separation_and_9_cross_quadrics(self) -> None:
        """Verifies lambda_signed recovers 9 cross quadrics x_i x_j and factorizes into primary ideals."""
        pi_plus = {(4, 4, 4, 0, 0, 0): Fraction(1, 1)}
        pi_minus = {(0, 0, 0, 4, 4, 4): Fraction(1, 1)}
        lam_signed = {(4, 4, 4, 0, 0, 0): Fraction(1, 1), (0, 0, 0, 4, 4, 4): Fraction(-1, 1)}

        qf = self.engine.decomposer.factor_signed_quadrics(lam_signed)
        self.assertEqual(qf["lambda_ann_R1_dim"], 0)
        self.assertEqual(qf["lambda_ann_R2_dim"], 9)
        self.assertEqual(qf["primary_I_plus_dim"], 3)
        self.assertEqual(qf["primary_I_minus_dim"], 3)
        self.assertEqual(qf["product_ideal_dim"], 9)
        self.assertTrue(qf["exact_product_factorization_matches_ann_R2"])

        dec = qf["decomposition"]
        self.assertEqual(dec["lambda_plus"], pi_plus)
        self.assertEqual(dec["lambda_minus"], pi_minus)
        self.assertEqual(dec["score"], 36)
        self.assertTrue(dec["exact_reconstruction_verified"])
        self.assertTrue(dec["wirtinger_primitive_balanced"])

        # Adversarial negative check: confirm non-cross-product quadrics (x_0^2, x_3 x_4) are excluded
        ann2 = self.engine.tower.annihilator_at_degree(lam_signed, 2)
        recovered_m2 = {next(iter(p.keys())) for p in ann2["basis_polys"]}
        self.assertNotIn((2, 0, 0, 0, 0, 0), recovered_m2)
        self.assertNotIn((0, 0, 0, 1, 1, 0), recovered_m2)

    def test_04_all_18_partitions_band1_and_band2_factorization(self) -> None:
        """Confirms signed decomposition and geometric factorization across all 18 partitions (1,751 modes)."""
        p18 = self.audit["all_18_partitions_audit"]
        self.assertEqual(p18["total_partitions_tested"], 18)
        self.assertEqual(p18["band1_partitions_verified"], 10)
        self.assertEqual(p18["band2_partitions_verified"], 6)
        self.assertEqual(p18["band3_partitions_verified"], 2)
        self.assertEqual(p18["signed_pair_recoveries_verified"], 18)
        self.assertTrue(p18["all_18_partitions_verified"])

    def test_05_macaulay_growth_bounds_and_bridge_a_honesty(self) -> None:
        """Verifies Macaulay growth theorem on Gorenstein Hilbert vectors and preserves Bridge A honesty."""
        deg_pi = self.audit["effective_degree_bounds"]["single_plane"]
        deg_sig = self.audit["effective_degree_bounds"]["signed_disjoint_planes"]

        self.assertTrue(deg_pi["macaulay_growth_satisfied"])
        self.assertTrue(deg_sig["macaulay_growth_satisfied"])
        self.assertEqual(deg_pi["gorenstein_hilbert_vector_0_to_12"], [1, 3, 6, 10, 15, 18, 19, 18, 15, 10, 6, 3, 1])
        self.assertEqual(deg_sig["gorenstein_hilbert_vector_0_to_12"], [1, 6, 12, 20, 30, 36, 38, 36, 30, 20, 12, 6, 1])
        self.assertEqual(deg_pi["minimal_generation_cutoff_d_gen"], 1)
        self.assertEqual(deg_sig["minimal_generation_cutoff_d_gen"], 2)
        self.assertEqual(deg_pi["gotzmann_surface_fit"]["gotzmann_number_G"], 1)
        self.assertEqual(deg_sig["gotzmann_surface_fit"]["gotzmann_number_G"], 5)
        self.assertEqual(deg_pi["gotzmann_persistence_degrees"], [1, 2, 3])
        self.assertTrue(deg_pi["fermat_apolar_regularity_bounded"])
        self.assertFalse(deg_pi["general_fiber_hilbert_bound_known"])
        self.assertFalse(self.audit["effective_hilbert_degree_bound_known"])
        self.assertEqual(self.audit["bridge_a_status"], "ADVERSARIALLY_BLOCKED_OPEN_BRIDGE")

    def test_06_zero_floats_and_24_zero_axiom_lean4_theorems(self) -> None:
        """Confirms zero floats in macaulay_apolarity_inverse_engine.py and 24/24 zero-axiom Lean 4 proofs."""
        hits = scan_forbidden(str(self.root / "toolkit" / "macaulay_apolarity_inverse_engine.py"))
        self.assertEqual(hits, [])

        lean_audit = self.reviewer.verify_lean_blueprint(fast=True)
        self.assertTrue(lean_audit["zero_cheating_clean"])
        self.assertTrue(lean_audit["all_axioms_empty"])
        self.assertGreaterEqual(lean_audit["theorems_verified_count"], 24)
        self.assertGreaterEqual(len(LEAN_THEOREM_SPECS), 24)
        self.assertEqual(lean_audit["axioms_by_theorem"]["macaulay_annihilator_dim_bound"], [])
        self.assertEqual(lean_audit["axioms_by_theorem"]["signed_difference_ideal_intersection"], [])


if __name__ == "__main__":
    unittest.main()
