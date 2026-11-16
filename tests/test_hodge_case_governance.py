"""Tests for Four-Pillar Symbolic Hodge Architecture under MATH-GOV v0.6 Governance OS."""

import json
import sqlite3
import unittest
from pathlib import Path

from toolkit.governance import event_ledger
from toolkit.governance.lean_step_runner import check_step
from toolkit.governance.math_step_engine import audit, progress


class TestHodgeCaseGovernance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.case_path = Path("governance/hodge_four_pillars_case.json")
        cls.hashes_path = Path("governance/HODGE_CASE_HASHES.json")
        cls.db_path = Path("governance/hodge_governance_ledger.db")
        cls.lean_root = Path("examples/math_gov/LeanDemoProject").resolve()
        cls.case = json.loads(cls.case_path.read_text(encoding="utf-8"))
        cls.hashes = json.loads(cls.hashes_path.read_text(encoding="utf-8"))

    def test_01_structural_preflight_audit_passes(self):
        res = audit(
            self.case,
            trusted_original_digest=self.hashes["original"],
            trusted_formal_digest=self.hashes["formal"],
            trusted_contract_digest=self.hashes["contract"],
        )
        self.assertEqual(res["verdict"], "STRUCTURAL_PREFLIGHT_PASS_ONLY")
        self.assertEqual(res["errors"], [])
        self.assertFalse(res["formal_proof_verified"])
        self.assertFalse(res["release_authorized"])

    def test_02_scientific_honesty_progress_reporting(self):
        pr = progress(self.case)
        self.assertEqual(pr["verdict"], "DESCRIPTIVE_UNVERIFIED")
        self.assertFalse(pr["proof_verified"])
        self.assertEqual(pr["theorem_progress_percent"], "UNKNOWN")
        self.assertEqual(pr["tasks_execution_finished"], 4)
        self.assertEqual(pr["tasks_total"], 5)
        self.assertEqual(pr["steps_with_open_obligations"], 1)

    def test_03_event_ledger_hash_chain_validity(self):
        conn = sqlite3.connect(self.db_path)
        ver = event_ledger.verify(conn)
        conn.close()
        self.assertEqual(ver["verdict"], "LOCAL_CHAIN_VALID_UNAUTHENTICATED")
        self.assertGreaterEqual(ver["count"], 14)

    def test_04_lean_four_pillars_exactness(self):
        # Test Pillar 1: exact_chain_im_sub_ker
        res1 = check_step(
            str(self.lean_root),
            "HodgeVerification.lean",
            "exact_chain_im_sub_ker",
            "forall {α β γ : Type} (f : α → β) (g : β → γ) (zero_c : γ), (forall x : α, g (f x) = zero_c) → forall y : β, (exists x : α, f x = y) → g y = zero_c",
            self.hashes["lean_source"],
        )
        self.assertTrue(res1["lean_kernel_check_passed"])
        self.assertEqual(res1["axioms"], [])

        # Test Pillar 2: weil_w1_orthogonal_to_theta2
        res2 = check_step(
            str(self.lean_root),
            "HodgeVerification.lean",
            "weil_w1_orthogonal_to_theta2",
            "dot weil_w1 theta2 = 0",
            self.hashes["lean_source"],
        )
        self.assertTrue(res2["lean_kernel_check_passed"])
        self.assertEqual(res2["axioms"], [])

        # Test Pillar 3: zero_tuples_len
        res3 = check_step(
            str(self.lean_root),
            "HodgeVerification.lean",
            "zero_tuples_len",
            "zero_weight_tuples.length = 6",
            self.hashes["lean_source"],
        )
        self.assertTrue(res3["lean_kernel_check_passed"])
        self.assertEqual(res3["axioms"], [])

        # Test Pillar 4: plane_kernel_dim_eq
        res4 = check_step(
            str(self.lean_root),
            "HodgeVerification.lean",
            "plane_kernel_dim_eq",
            "plane_kernel_dim = 407",
            self.hashes["lean_source"],
        )
        self.assertTrue(res4["lean_kernel_check_passed"])
        self.assertEqual(res4["axioms"], [])

        # Test Pillar 4 Node 4 additions: saturation_three_count_eq, band3_partitions_satisfy_2_plus_4, fermat_four_band_closure_eq
        res5 = check_step(
            str(self.lean_root),
            "HodgeVerification.lean",
            "saturation_three_count_eq",
            "saturation_three_count = 20",
            self.hashes["lean_source"],
        )
        self.assertTrue(res5["lean_kernel_check_passed"])
        self.assertEqual(res5["axioms"], [])

        res6 = check_step(
            str(self.lean_root),
            "HodgeVerification.lean",
            "band3_partitions_satisfy_2_plus_4",
            "(has_2_plus_4_split [4, 2, 2, 2, 1, 1] && has_2_plus_4_split [3, 3, 2, 2, 2, 0]) = true",
            self.hashes["lean_source"],
        )
        self.assertTrue(res6["lean_kernel_check_passed"])
        self.assertEqual(res6["axioms"], [])

        res7 = check_step(
            str(self.lean_root),
            "HodgeVerification.lean",
            "fermat_four_band_closure_eq",
            "fermat_four_band_total = h22_prim",
            self.hashes["lean_source"],
        )
        self.assertTrue(res7["lean_kernel_check_passed"])
        self.assertEqual(res7["axioms"], [])

        res8 = check_step(
            str(self.lean_root),
            "HodgeVerification.lean",
            "f_p3_surface_h11_prim_eq",
            "f_p3_surface_h11_prim = 85",
            self.hashes["lean_source"],
        )
        self.assertTrue(res8["lean_kernel_check_passed"])
        self.assertEqual(res8["axioms"], [])

        res9 = check_step(
            str(self.lean_root),
            "HodgeVerification.lean",
            "min_ivhs_codimension_pos",
            "(min_ivhs_codimension >= 19 && min_ivhs_codimension > 0) = true",
            self.hashes["lean_source"],
        )
        self.assertTrue(res9["lean_kernel_check_passed"])
        self.assertEqual(res9["axioms"], [])

        res10 = check_step(
            str(self.lean_root),
            "HodgeVerification.lean",
            "clifford_even_dim_eq",
            "(clifford_even_dim == 128 && chevalley_spinor_end_dim == 128) = true",
            self.hashes["lean_source"],
        )
        self.assertTrue(res10["lean_kernel_check_passed"])
        self.assertEqual(res10["axioms"], [])

        res11 = check_step(
            str(self.lean_root),
            "HodgeVerification.lean",
            "d4_triality_zero_triples_len",
            "triality_zero_triples.length = 32",
            self.hashes["lean_source"],
        )
        self.assertTrue(res11["lean_kernel_check_passed"])
        self.assertEqual(res11["axioms"], [])

        res12 = check_step(
            str(self.lean_root),
            "HodgeVerification.lean",
            "max_ivhs_monomial_rank_eq",
            "(max_ivhs_monomial_rank == 141 && min_ivhs_monomial_kernel == 285) = true",
            self.hashes["lean_source"],
        )
        self.assertTrue(res12["lean_kernel_check_passed"])
        self.assertEqual(res12["axioms"], [])

        res13 = check_step(
            str(self.lean_root),
            "HodgeVerification.lean",
            "canonical_fixed_plane_subspace_dim_eq",
            "canonical_fixed_plane_subspace_dim = 56",
            self.hashes["lean_source"],
        )
        self.assertTrue(res13["lean_kernel_check_passed"])
        self.assertEqual(res13["axioms"], [])

        res14 = check_step(
            str(self.lean_root),
            "HodgeVerification.lean",
            "macaulay_annihilator_dim_bound",
            "(r1_monomials.length == 6 && macaulay_m1_rank_pi == 3 && macaulay_ann_r1_pi == 3) = true",
            self.hashes["lean_source"],
        )
        self.assertTrue(res14["lean_kernel_check_passed"])
        self.assertEqual(res14["axioms"], [])

        res15 = check_step(
            str(self.lean_root),
            "HodgeVerification.lean",
            "signed_difference_ideal_intersection",
            "(r2_monomials.length == 21 && pi_plus_ideal_r1.length == 3 && pi_minus_ideal_r1.length == 3 && "
            "cross_product_quadrics.length == 9 && signed_ann_r1_dim == 0 && signed_ann_r2_dim == 9 && "
            "cross_quadrics_annihilate_both) = true",
            self.hashes["lean_source"],
        )
        self.assertTrue(res15["lean_kernel_check_passed"])
        self.assertEqual(res15["axioms"], [])

        res16 = check_step(
            str(self.lean_root),
            "HodgeVerification.lean",
            "quadratic_moving_plane_directions_count_eq",
            "(r_exps_deg4.length == 6 && quadratic_moving_plane_directions.length == 18 && "
            "quadratic_moving_plane_directions.all (fun u => "
            "u.1 + u.2.1 + u.2.2.1 == 2 && u.2.2.2.1 + u.2.2.2.2.1 + u.2.2.2.2.2 == 4 && "
            "Nat.ble u.2.2.2.1 2 && Nat.ble u.2.2.2.2.1 2 && Nat.ble u.2.2.2.2.2 2)) = true",
            self.hashes["lean_source"],
        )
        self.assertTrue(res16["lean_kernel_check_passed"])
        self.assertEqual(res16["axioms"], [])

        res17 = check_step(
            str(self.lean_root),
            "HodgeVerification.lean",
            "deformed_macaulay_flat_hilbert_sum_eq",
            "(deformed_macaulay_flat_hilbert.foldr Nat.add 0 == 72 && "
            "deformed_macaulay_flat_hilbert.take 5 == binomial_2_plane_hilbert && "
            "[0, 1, 2, 3, 4].map (fun m => binom (m + 2) 2) == binomial_2_plane_hilbert) = true",
            self.hashes["lean_source"],
        )
        self.assertTrue(res17["lean_kernel_check_passed"])
        self.assertEqual(res17["axioms"], [])

        res18 = check_step(
            str(self.lean_root),
            "HodgeVerification.lean",
            "cyclotomic_plane_wavepacket_support_eq",
            "(pair_sums_4.length == 5 && cyclotomic_plane_wavepacket_count == 125 && "
            "pair_sums_4.all (fun p => p.1 + p.2 == 4 && Nat.ble p.1 4 && Nat.ble p.2 4)) = true",
            self.hashes["lean_source"],
        )
        self.assertTrue(res18["lean_kernel_check_passed"])
        self.assertEqual(res18["axioms"], [])

        res19 = check_step(
            str(self.lean_root),
            "HodgeVerification.lean",
            "telescoping_cyclotomic_annihilator_eq",
            "(telescope_lhs_exp6 1 1 1 1 1 == telescope_rhs_exp6 1 1 1 1 1) = true",
            self.hashes["lean_source"],
        )
        self.assertTrue(res19["lean_kernel_check_passed"])
        self.assertEqual(res19["axioms"], [])

        res20 = check_step(
            str(self.lean_root),
            "HodgeVerification.lean",
            "spinor_to_weil_su22_branching_eq",
            "(d3_zero_weight_tuples.length == 8 && pure_weil_tuples.length == 2 && "
            "mixed_d4_zero_tuples.length == 6 && mixed_d4_zero_tuples.length == zero_weight_tuples.length && "
            "pure_weil_tuples.length + mixed_d4_zero_tuples.length == d3_zero_weight_tuples.length) = true",
            self.hashes["lean_source"],
        )
        self.assertTrue(res20["lean_kernel_check_passed"])
        self.assertEqual(res20["axioms"], [])

        res21 = check_step(
            str(self.lean_root),
            "HodgeVerification.lean",
            "tangential_leibniz_annihilator_eq",
            "(bivar_d_plus [1, -1], bivar_d_plus [1, 0, 0, 0, 0, -1], "
            "bivar_eval_diag (bivar_d_plus [1, -1, 0, 0, 0, 0]), "
            "bivar_eval_diag (bivar_d_minus [1, -1, 0, 0, 0, 0])) = ([0], [5, 0, 0, 0, -5], 0, 2)",
            self.hashes["lean_source"],
        )
        self.assertTrue(res21["lean_kernel_check_passed"])
        self.assertEqual(res21["axioms"], [])

        res22 = check_step(
            str(self.lean_root),
            "HodgeVerification.lean",
            "recombination_kernel_dim_gain_eq",
            "(deg6_triples_le4.length == 19 && shared_deg6_triples.length == 3 && "
            "cancel_deg2_pairs.length == 3 && shared_ker_dim == 391 && recomb_rank == 32 && "
            "recomb_ker_dim == 394 && recomb_ker_dim - shared_ker_dim == 3) = true",
            self.hashes["lean_source"],
        )
        self.assertTrue(res22["lean_kernel_check_passed"])
        self.assertEqual(res22["axioms"], [])

        res23 = check_step(
            str(self.lean_root),
            "HodgeVerification.lean",
            "weyl_d4_conjugate_weil_axes_eq",
            "(coord_pure_weil_tuples.length == 8 && hadamard_pure_weil_tuples.length == 8 && "
            "coord_pure_weil_tuples.length + hadamard_pure_weil_tuples.length == 16 && "
            "binom 8 2 == 28 && binom 6 2 + 1 == 16 && shimura_coset_dim == 12 && "
            "k22_pair0_count == 2 && k22_pair1_count == 2 && k22_pair2_count == 2 && "
            "k22_pair0_count + k22_pair1_count + k22_pair2_count == zero_weight_tuples.length) = true",
            self.hashes["lean_source"],
        )
        self.assertTrue(res23["lean_kernel_check_passed"])
        self.assertEqual(res23["axioms"], [])

        res24 = check_step(
            str(self.lean_root),
            "HodgeVerification.lean",
            "universal_band_obstruction_cancellation_bounds_eq",
            "(universal_total_ker_bound == 1325 && universal_band1_ker_bound == 575 && "
            "universal_band2_ker_bound == 204 && turan_max_obstructed_planes == 4 && "
            "turan_min_surviving_planes == 16 && turan_max_obstructed_planes + 1 == 5) = true",
            self.hashes["lean_source"],
        )
        self.assertTrue(res24["lean_kernel_check_passed"])
        self.assertEqual(res24["axioms"], [])

        res25 = check_step(
            str(self.lean_root),
            "HodgeVerification.lean",
            "gorenstein_moduli_rank_extremes_eq",
            "(gorenstein_min_rank_deg12 == 155 && gorenstein_min_rank_deg6_dual == 155 && "
            "gorenstein_max_ker_dim == 1596 && gorenstein_max_rank_deg12 == 336 && "
            "gorenstein_max_rank_deg6_dual == 336 && gorenstein_min_ker_dim == 1415) = true",
            self.hashes["lean_source"],
        )
        self.assertTrue(res25["lean_kernel_check_passed"])
        self.assertEqual(res25["axioms"], [])

        res27 = check_step(
            str(self.lean_root),
            "HodgeVerification.lean",
            "nine_partition_cokernel_dims_eq",
            "(nine_partition_moduli_ranks.map (fun r => 426 - r) == nine_partition_cokernels && "
            "nine_gorenstein_exact_ranks.map (fun r => 426 - r) == nine_gorenstein_exact_cokernels) = true",
            self.hashes["lean_source"],
        )
        self.assertTrue(res27["lean_kernel_check_passed"])
        self.assertEqual(res27["axioms"], [])

        res28 = check_step(
            str(self.lean_root),
            "HodgeVerification.lean",
            "twenty_plane_target_and_collision_counts_eq",
            "(twenty_plane_total_incidences == 380 && twenty_plane_target_dim == 245 && "
            "twenty_plane_three_4_targets * 1 + twenty_plane_four_4_targets * 4 == 380 && "
            "twenty_plane_collision_excess == 135 && "
            "twenty_plane_target_dim + high_support_moduli_dim == h31_prim && "
            "high_support_moduli_counts == [150, 30, 1] && high_support_moduli_dim == 181 && "
            "9 + 11 == saturation_three_count && 15 == saturation_three_count - 5 && "
            "15 - 11 == 4) = true",
            self.hashes["lean_source"],
        )
        self.assertTrue(res28["lean_kernel_check_passed"])
        self.assertEqual(res28["axioms"], [])

        res29 = check_step(
            str(self.lean_root),
            "HodgeVerification.lean",
            "fifteen_matching_band1_block_incidence_eq",
            "(fifteen_perfect_matchings == 15 && modes_per_matching_block == 125 && "
            "band1_block_total_incidences == 1875 && "
            "band1_mult_mode_sum == fermat_band1_planes && "
            "band1_mult_incidence_sum == band1_block_total_incidences && "
            "band1_block_total_incidences - fermat_band1_planes == 874 && "
            "band1_multiplicity_pairs.map (fun p => p.2) == [360, 540, 60, 40, 1]) = true",
            self.hashes["lean_source"],
        )
        self.assertTrue(res29["lean_kernel_check_passed"])
        self.assertEqual(res29["axioms"], [])

        res30 = check_step(
            str(self.lean_root),
            "HodgeVerification.lean",
            "recomb_and_collision_flat_hilbert_eq",
            "(recomb_flat_target == [8, 18, 32, 48, 60, 64] && "
            "list_diff_nat recomb_ua_naive_ranks recomb_flat_target == [0, 1, 4, 8, 11, 12] && "
            "list_diff_nat recomb_ub_naive_ranks recomb_flat_target == [0, 1, 4, 8, 12, 14] && "
            "list_diff_nat quad_collision_naive_ranks recomb_flat_target == [1, 5, 13, 23, 31, 34] && "
            "list_head_nat recomb_ua_naive_ranks == 8 && "
            "list_head_nat quad_collision_naive_ranks == 9 && "
            "h31_prim - 32 == 394) = true",
            self.hashes["lean_source"],
        )
        self.assertTrue(res30["lean_kernel_check_passed"])
        self.assertEqual(res30["axioms"], [])

        res31 = check_step(
            str(self.lean_root),
            "HodgeVerification.lean",
            "finite_non_fermat_pair_milnor_and_ranks_eq",
            "(nf_pair_milnor == 25 && "
            "nf_total_milnor == milnor_number && "
            "1 :: nf_plane_ranks == deformed_macaulay_flat_hilbert && "
            "([1, 2, 3, 4, 5, 6].map nf_sum_pairs == [6, 21, 56, 126, 246, 426]) && "
            "nf_sum_pairs 12 == h22_prim && "
            "nf_sum_pairs 18 == h31_prim && "
            "6 - 3 == 3 && 6 - 4 == 2) = true",
            self.hashes["lean_source"],
        )
        self.assertTrue(res31["lean_kernel_check_passed"])
        self.assertEqual(res31["axioms"], [])


if __name__ == "__main__":
    unittest.main()
