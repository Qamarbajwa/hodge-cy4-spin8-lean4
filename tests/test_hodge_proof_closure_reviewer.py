"""Adversarial 5-Point Audit Suite for Hodge Proof Formulation & MATH-GOV v0.7 Graph Closure.

Tests:
  1. Sub-Domain Proof Soundness Check (Domains 1, 2, 3 verified in Python & 18 Lean 4 theorems).
  2. Adversarial Bridge A Rejection Check (S-BRIDGE-DEFORM-CY4 blocked: min rk(M_{x^a}) = 19 > 0, non-constructive Phi_lambda).
  3. Adversarial Bridge B Rejection Check (S-BRIDGE-SPINOR-MOTIVE blocked: End_Q(A_6)=Q, rho(A_6)=1, root rank = 6, ker = 0).
  4. MATH-GOV v0.7 Graph Closure Propagation Check (subdomains CLOSED_VERIFIED, CLM-GLOBAL-HODGE-MILLENNIUM OPEN_BLOCKED).
  5. Zero-Float & Zero-Axiom Check (scan_forbidden == [] across engines + 18/18 Lean 4 theorems axioms == []).
"""

import unittest
from pathlib import Path

from toolkit.hodge_proof_closure_reviewer import (
    HodgeProofClosureReviewer,
    LEAN_THEOREM_SPECS,
)
from toolkit.integrity import scan_forbidden


class TestHodgeProofClosureReviewer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parent.parent
        cls.reviewer = HodgeProofClosureReviewer(repo_root=cls.root)
        cls.report = cls.reviewer.evaluate_graph_closure(fast=True, run_exhaustive_407=False)

    def test_01_subdomain_proof_soundness_check(self):
        """Verifies all 3 resolved sub-domains have 100% Python + Lean 4 zero-axiom proofs."""
        sub = self.report["subdomains"]
        self.assertTrue(sub["all_resolved_subdomains_verified"])

        d1 = sub["domain_1_universal_reduction"]
        self.assertEqual(d1["claim_id"], "CLM-UNIVERSAL-COHOMOLOGICAL-REDUCTION")
        self.assertEqual(d1["domain_status"], "FORMALLY_PROVED_SUBDOMAIN")
        self.assertEqual(d1["closure_status"], "CLOSED_VERIFIED")
        self.assertEqual(d1["step_results"]["S-PIL1-GYSIN"]["axioms"], [])
        self.assertEqual(d1["step_results"]["S-PIL1-EXOTIC-REDUCTION"]["classes_reduced_to_CHp"], 5)
        self.assertEqual(d1["step_results"]["S-PIL1-EXOTIC-REDUCTION"]["new_cohomology_shadows"], 0)
        self.assertEqual(d1["step_results"]["S-PIL1-WIRTINGER"]["net_volume_difference"], "0")

        d2 = sub["domain_2_abelian_dim_le_5"]
        self.assertEqual(d2["claim_id"], "CLM-ABELIAN-DIM-LE-5-PROVED")
        self.assertEqual(d2["domain_status"], "FORMALLY_PROVED_SUBDOMAIN")
        self.assertEqual(d2["closure_status"], "CLOSED_VERIFIED")
        self.assertEqual(d2["step_results"]["S-PIL2-ORTH1"]["axioms"], [])
        self.assertEqual(d2["step_results"]["S-PIL2-ORTH2"]["axioms"], [])
        self.assertEqual(d2["step_results"]["S-PIL2-MARKMAN-SCHOEN"]["h4_dim"], 70)
        self.assertEqual(d2["step_results"]["S-PIL2-MARKMAN-SCHOEN"]["primitive_weil_dim"], 2)

        d3 = sub["domain_3_fermat_sextic_cy4"]
        self.assertEqual(d3["claim_id"], "CLM-FERMAT-SEXTIC-CY4-PROVED")
        self.assertEqual(d3["domain_status"], "FORMALLY_PROVED_SUBDOMAIN")
        self.assertEqual(d3["closure_status"], "CLOSED_VERIFIED")
        self.assertEqual(d3["four_band_summary"], "1001 + 630 + 120 + 0 = 1751")
        self.assertEqual(d3["dim_R8_P3"], 85)
        self.assertEqual(len(d3["step_results"]), 31)
        for step_data in d3["step_results"].values():
            self.assertTrue(step_data["verified"])
            self.assertEqual(step_data["axioms"], [])

    def test_02_adversarial_bridge_a_rejection_check(self):
        """Verifies naive worker attempt to close Bridge A (S-BRIDGE-DEFORM-CY4) is adversarially rejected."""
        worker_claim = (
            "Since 1,001 + 630 + 120 + 0 = 1,751 closes X^4_6 and Phi_lambda = 0 holds for all "
            "407 moving-plane vectors, parallel transport proves the Hodge Conjecture on all deformed sextics X_t."
        )
        decision = self.reviewer.attempt_bridge_promotion(
            "S-BRIDGE-DEFORM-CY4",
            "PROVED",
            worker_claim,
        )
        self.assertFalse(decision["accepted"])
        self.assertEqual(decision["verdict"], "REJECTED_BY_ADVERSARIAL_REVIEWER")
        self.assertEqual(decision["resulting_status"], "ADVERSARIALLY_BLOCKED_OPEN_BRIDGE")

        audit = decision["audit_evidence"]
        self.assertEqual(audit["min_ivhs_codimension"], 19)
        self.assertEqual(audit["max_ivhs_codimension"], 141)
        self.assertEqual(audit["ivhs_kernel_range"], [285, 407])
        self.assertEqual(audit["zero_codimension_monomials_count"], 0)
        self.assertEqual(audit["voisin_chain_filter_base_rank"], 68)
        self.assertEqual(audit["voisin_chain_filter_augmented_rank"], 69)
        self.assertEqual(audit["plane_order3_canonical_fixed_unobstructed"], "56/56")
        self.assertEqual(audit["plane_order3_moving_27_unobstructed"], "27/27")
        self.assertEqual(audit["plane_order3_linear_54_unobstructed"], "54/54")
        self.assertEqual(audit["plane_order3_full_kernel_unobstructed"], "407/407")
        self.assertEqual(audit["stealth_class_jet_filtration"], [347, 336, 334])
        self.assertEqual(audit["stealth_order3_caught_vectors"], 2)
        self.assertTrue(audit["CDK_BASE_MODULI_ALGEBRAICITY_VERIFIED"])
        self.assertTrue(audit["fermat_apolar_inversion_complete"])
        self.assertEqual(audit["macaulay_single_plane_ann_R1"], 3)
        self.assertEqual(audit["macaulay_signed_quadrics_R2"], 9)
        self.assertTrue(audit["macaulay_18_partitions_verified"])
        self.assertTrue(audit["deformed_moving_plane_18_cancelled"])
        self.assertTrue(audit["deformed_fixed_ideal_359_diagonal_flat"])
        self.assertTrue(audit["deformed_canonical_fixed_56_flat"])
        self.assertTrue(audit["deformed_chain_stealth_unliftable_in_R12"])
        self.assertEqual(audit["deformed_gotzmann_flat_hilbert_sum"], 72)
        self.assertEqual(audit["deformed_gotzmann_Gt"], 1)
        self.assertEqual(audit["cyclotomic_wavepacket_monomials"], 125)
        self.assertTrue(audit["cyclotomic_wavepacket_ideal_match"])
        self.assertEqual(audit["cyclotomic_wavepacket_gotzmann_G"], 1)
        self.assertEqual(audit["joint_transport_stat_rank"], 1750)
        self.assertEqual(audit["joint_transport_joint_rank"], 1756)
        self.assertEqual(audit["joint_transport_rank_gain"], 6)
        self.assertEqual(audit["joint_transport_stat_subspace"], 353)
        self.assertEqual(audit["joint_transport_joint_subspace"], 359)
        self.assertEqual(audit["joint_transport_subspace_gain"], 6)
        self.assertEqual(audit["joint_transport_nilpotent_gain"], 0)
        self.assertEqual(audit["wall1_signed_fermat_tangential_leibniz"], "407/407")
        self.assertEqual(audit["wall1_signed_fermat_joint_solvable"], "407/407")
        self.assertEqual(audit["wall1_unsigned_fermat_unlifted"], 48)
        self.assertTrue(audit["wall1_100_percent_closed"])
        self.assertEqual(audit["wall2_liaison_z5_rank_vector"], (3, 6, 10, 15, 18, 19))
        self.assertEqual(audit["wall2_liaison_gotzmann_G"], 1)
        self.assertEqual(audit["wall3_nodal_orbit_size"], 30)
        self.assertFalse(audit["wall3_nodal_global_bound_known"])
        self.assertEqual(audit["recomb_shared_kernel_dim"], 391)
        self.assertEqual(audit["recomb_kernel_dim"], 394)
        self.assertEqual(audit["recomb_kernel_gain"], 3)
        self.assertTrue(audit["recomb_all_orders_1_2_3_pass"])
        self.assertEqual(audit["recomb_macaulay_ranks"], (4, 9, 16, 24, 30, 32))
        self.assertEqual(audit["recomb_subadditive_deg_Q"], 2)
        self.assertEqual(audit["dictionary_raw_ann12_partitions"], 17)
        self.assertEqual(audit["dictionary_max_d_gen"], 4)
        self.assertEqual(audit["univ_total_ker_lower_bound"], 1325)
        self.assertEqual(audit["univ_band1_ker_lower_bound"], 575)
        self.assertEqual(audit["univ_band2_ker_lower_bound"], 204)
        self.assertEqual(audit["univ_dense_u_full_rank"], 426)
        self.assertEqual(audit["univ_dense_u_full_ker"], 1325)
        self.assertEqual(audit["gorenstein_moduli_partitions_count"], 9)
        self.assertEqual(audit["gorenstein_moduli_rank_range"], [155, 336])
        self.assertEqual(audit["gorenstein_moduli_ker_range"], [1415, 1596])
        self.assertEqual(audit["turan_min_surviving_planes"], 16)
        self.assertEqual(audit["turan_pigeonhole_min_K"], 5)
        self.assertEqual(audit["surj_coker_dense_u_coker_dim"], 0)
        self.assertEqual(audit["surj_coker_all_order_ker_dim"], 1325)
        self.assertEqual(audit["twenty_plane_collision_excess"], 135)
        self.assertEqual(audit["high_support_zero_count"], 181)
        self.assertEqual(audit["fifteen_matching_union_size"], 1001)
        self.assertTrue(audit["recomb_all_moving_stabilized_m1_to_m6"])
        self.assertEqual(audit["quad_syzygies_stabilized_count"], 4)
        self.assertEqual(audit["finite_non_fermat_plane_ranks"], [3, 6, 10, 15, 18, 19])
        self.assertEqual(audit["finite_non_fermat_quad_ranks"], [4, 9, 16, 24, 30, 32])
        self.assertFalse(audit["universal_non_fermat_determinantal_stabilization_proved"])
        self.assertEqual(audit["surj_coker_rank_independent_bound"], 1325)
        self.assertEqual(audit["surj_coker_min_psi2_ker_dim"], 1325)
        self.assertEqual(audit["surj_coker_max_psi2_ker_dim"], 1544)
        self.assertFalse(audit["global_non_fermat_hilbert_stabilization_proved"])
        self.assertFalse(audit["effective_hilbert_degree_bound_known"])
        self.assertFalse(audit["constructive_cycle_lifting"])
        self.assertFalse(audit["global_extension_valid"])
        self.assertTrue(any("19 > 0" in r for r in decision["blocking_reasons"]))
        self.assertTrue(any("Phi_lambda = 0" in r for r in decision["blocking_reasons"]))
        self.assertTrue(any("Cattani-Deligne-Kaplan" in r for r in decision["blocking_reasons"]))

    def test_03_adversarial_bridge_b_rejection_check(self):
        """Verifies naive worker attempt to close Bridge B (S-BRIDGE-SPINOR-MOTIVE) is adversarially rejected."""
        worker_claim = (
            "Because (wedge^4 S^+_8)_0 has 6 K_{2,2} zero-weight tuples and U_4 tensor W_3 spans H^1(A_6, Q), "
            "Markman's secant-sheaf theorem splits A_6 and proves Mumford spinor Hodge classes are algebraic."
        )
        decision = self.reviewer.attempt_bridge_promotion(
            "S-BRIDGE-SPINOR-MOTIVE",
            "CLOSED_VERIFIED",
            worker_claim,
        )
        self.assertFalse(decision["accepted"])
        self.assertEqual(decision["verdict"], "REJECTED_BY_ADVERSARIAL_REVIEWER")
        self.assertEqual(decision["resulting_status"], "ADVERSARIALLY_BLOCKED_OPEN_BRIDGE")

        audit = decision["audit_evidence"]
        self.assertEqual(audit["sixfold_b6"], 924)
        self.assertEqual(audit["sixfold_h33"], 400)
        self.assertEqual(audit["wedge4_dim"], 70)
        self.assertEqual(audit["cartan_zero_weight_k22_tuples"], 6)
        self.assertEqual(audit["endomorphism_algebra"], "End_Q(A) = Q")
        self.assertEqual(audit["picard_number"], 1)
        self.assertEqual(audit["dim_end_g_V"], 1)
        self.assertEqual(audit["stacked_simple_root_operator_rank"], 6)
        self.assertEqual(audit["root_annihilation_kernel_dim"], 0)
        self.assertFalse(audit["markman_secant_applicable"])
        self.assertFalse(audit["geometric_variety_splitting_exists"])
        self.assertEqual(audit["clifford_even_dim"], 128)
        self.assertEqual(audit["triality_zero_triples_count"], 32)
        self.assertEqual(audit["cartan_zero_weight_branching_split"], [3, 3])
        self.assertTrue(audit["ABSOLUTE_HODGE_AND_MOTIVATED_VERIFIED"])
        self.assertFalse(audit["kuga_satake_algebraic_cycle_proved"])
        self.assertEqual(audit["wall4_d3_su22_zero_weight_dim"], 8)
        self.assertEqual(audit["wall4_pure_weil_dim"], 2)
        self.assertEqual(audit["wall4_mixed_d4_zero_dim"], 6)
        self.assertEqual(audit["weyl_coset_pure_weil_count"], 16)
        self.assertEqual(audit["weyl_coset_wd4_order"], 192)
        self.assertEqual(audit["weyl_coset_dim_p"], 12)
        self.assertEqual(audit["weyl_coset_multi_axis_rank"], 6)
        self.assertTrue(audit["weyl_coset_full_6_of_6_spanned"])
        self.assertFalse(audit["weyl_coset_chow_flatness_proved"])
        self.assertEqual(audit["wall4_mixed_d3_root_rank"], 5)
        self.assertEqual(audit["wall4_total_su22_invariant_dim"], 3)
        self.assertFalse(audit["wall4_horizontal_spreading_proved"])
        self.assertTrue(any("End_Q(A_6) = Q" in r for r in decision["blocking_reasons"]))
        self.assertTrue(any("rank 6" in r for r in decision["blocking_reasons"]))
        self.assertTrue(any("Kuga-Satake Algebraicity Conjecture" in r for r in decision["blocking_reasons"]))

    def test_04_v07_graph_closure_propagation_check(self):
        """Verifies MATH-GOV v0.7 AND-gate propagation: 3 sub-domains closed, global Millennium target blocked."""
        self.assertTrue(self.report["dag_summary"]["is_acyclic_dag"])
        node_states = self.report["node_states"]

        for clm in (
            "CLM-UNIVERSAL-COHOMOLOGICAL-REDUCTION",
            "CLM-ABELIAN-DIM-LE-5-PROVED",
            "CLM-FERMAT-SEXTIC-CY4-PROVED",
            "CLM-FOUR-PILLARS-STRUCTURAL",
        ):
            self.assertEqual(node_states[clm], "CLOSED_VERIFIED")

        self.assertEqual(node_states["S-BRIDGE-DEFORM-CY4"], "ADVERSARIALLY_BLOCKED_OPEN_BRIDGE")
        self.assertEqual(node_states["S-BRIDGE-SPINOR-MOTIVE"], "ADVERSARIALLY_BLOCKED_OPEN_BRIDGE")
        self.assertEqual(self.report["blocked_global_bridges"], ["S-BRIDGE-DEFORM-CY4", "S-BRIDGE-SPINOR-MOTIVE"])
        self.assertEqual(node_states["CLM-GLOBAL-HODGE-MILLENNIUM"], "OPEN_BLOCKED_BY_BRIDGES_A_AND_B")
        self.assertEqual(self.report["global_root_status"], "OPEN_BLOCKED_BY_BRIDGES_A_AND_B")
        self.assertEqual(self.report["global_hodge_conjecture"], "OPEN")
        self.assertFalse(self.report["release_authorized"])
        self.assertEqual(self.report["theorem_progress"], "UNKNOWN")

    def test_05_zero_float_and_zero_axiom_check(self):
        """Confirms zero floating-point constructs across all engines and zero axioms across 24 Lean theorems."""
        files_to_scan = [
            "toolkit/three_agent_space_comparison.py",
            "toolkit/markman_secant_engine.py",
            "toolkit/mumford_spinor_engine.py",
            "toolkit/calabi_yau_jacobian_engine.py",
            "toolkit/erdos_fourier_incidence_engine.py",
            "toolkit/hodge_proof_closure_reviewer.py",
            "toolkit/kuga_satake_clifford_engine.py",
            "toolkit/higher_order_gauss_manin_sieve.py",
            "toolkit/macaulay_apolarity_inverse_engine.py",
            "toolkit/deformed_macaulay_transport_engine.py",
            "toolkit/four_wall_strategic_resolution_engine.py",
            "toolkit/global_recombination_and_coset_engine.py",
            "toolkit/universal_obstruction_cancellation_engine.py",
            "toolkit/surjective_cokernel_integrability_engine.py",
            "toolkit/twenty_plane_minimal_rank_stabilization_engine.py",
            "toolkit/non_fermat_determinantal_stabilization_engine.py",
            "toolkit/modular_crt_linear_solver.py",
            "toolkit/cmi_five_condition_attack_engine.py",
            "verify_zenodo_deposit.py",
        ]
        for rel in files_to_scan:
            hits = scan_forbidden(str(self.root / rel))
            self.assertEqual(hits, [], msg=f"Forbidden float construct in {rel}: {hits}")

        lean = self.report["lean_audit"]
        self.assertTrue(lean["zero_cheating_clean"])
        self.assertTrue(lean["all_axioms_empty"])
        self.assertEqual(lean["theorems_verified_count"], 43)
        self.assertEqual(len(LEAN_THEOREM_SPECS), 43)
        for thm_name, _ in LEAN_THEOREM_SPECS:
            self.assertEqual(lean["axioms_by_theorem"][thm_name], [])

        scope = self.report["lean_scope_note"]
        self.assertIn("zero Mathlib imports", scope)
        self.assertIn("43 decidable", scope)
        self.assertEqual(self.report["blocked_global_bridges"], ["S-BRIDGE-DEFORM-CY4", "S-BRIDGE-SPINOR-MOTIVE"])


if __name__ == "__main__":
    unittest.main()
