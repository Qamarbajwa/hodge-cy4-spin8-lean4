"""Adversarial Reviewer Test Suite for DeformedMacaulayTransportEngine (Event 22)."""

from __future__ import annotations

import sys
import unittest
from fractions import Fraction
from pathlib import Path

_REPO_ROOT = str(Path(__file__).resolve().parent.parent)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from toolkit.deformed_macaulay_transport_engine import DeformedMacaulayTransportEngine
from toolkit.integrity import scan_forbidden


class TestDeformedMacaulayTransportEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(_REPO_ROOT)
        cls.engine = DeformedMacaulayTransportEngine()
        cls.audit = cls.engine.run_full_audit()

    def test_01_deformed_jacobian_ring_dual_arithmetic_and_nilpotence(self) -> None:
        """Verifies exact reduction mod (J(F_t), t^2) including x_i^5 * x_j^5 === 0 mod t^2."""
        u = {(2, 0, 0, 2, 2, 0): Fraction(1, 1)}
        # x_0^5 + 0*t === -2 t x_0 x_3^2 x_4^2
        r0, r1 = self.engine.jet.reduce_mod_deformed_jacobian(
            {(5, 0, 0, 0, 0, 0): Fraction(1, 1)}, {}, u
        )
        self.assertEqual(r0, {})
        self.assertEqual(r1, {(1, 0, 0, 2, 2, 0): Fraction(-2, 1)})

        # Two coordinates >= 5 vanish identically mod t^2
        r0_dbl, r1_dbl = self.engine.jet.reduce_mod_deformed_jacobian(
            {(5, 0, 0, 5, 0, 0): Fraction(1, 1)}, {}, u
        )
        self.assertEqual(r0_dbl, {})
        self.assertEqual(r1_dbl, {})

        # Coordinate >= 10 vanishes identically mod t^2
        r0_ten, r1_ten = self.engine.jet.reduce_mod_deformed_jacobian(
            {(10, 0, 0, 0, 0, 0): Fraction(1, 1)}, {}, u
        )
        self.assertEqual(r0_ten, {})
        self.assertEqual(r1_ten, {})

    def test_02_all_18_quadratic_moving_plane_directions_cancel_and_stay_flat(self) -> None:
        """Confirms 18/18 moving directions fail statically yet cancel & stay flat in R(F_t)."""
        q = self.audit["quadratic_moving_plane_audit"]
        self.assertEqual(q["total_directions"], 18)
        self.assertEqual(q["static_xi_lam1_nonzero_count"], 18)
        self.assertEqual(q["deformed_x012_exact_cancellation_count"], 18)
        self.assertEqual(q["full_m1_to_m6_flat_count"], 18)
        self.assertEqual(q["direct_full_rref_witness_count"], 3)

        expected_double_ranks = {1: 6, 2: 12, 3: 20, 4: 30, 5: 36, 6: 38}
        for w in q["direct_rref_witnesses"]:
            self.assertTrue(w["all_degrees_flat"])
            self.assertEqual(w["deformed_ranks"], expected_double_ranks)

    def test_03_fixed_ideal_359_diagonal_and_56_canonical_flatness(self) -> None:
        """Verifies 359/359 diagonal transport, 56/56 canonical fixed-plane & 260+54 full flatness."""
        f = self.audit["fixed_ideal_audit"]
        self.assertEqual(f["fixed_s2_directions_total"], 359)
        self.assertEqual(f["diagonal_u_dot_lam0_vanishes_count"], 359)
        self.assertEqual(f["canonical_fixed_56_total"], 56)
        self.assertEqual(f["canonical_fixed_56_flat_count"], 56)
        self.assertEqual(f["full_m1_to_m6_flat_with_lam1_zero_count"], 260)
        self.assertEqual(f["one_axis_u_ge_2_flat_with_explicit_lam1_count"], 54)
        self.assertEqual(f["linear_u_eq_1_monomial_nonflat_count"], 45)
        self.assertEqual(
            f["canonical_witness_deformed_ranks"],
            {1: 6, 2: 12, 3: 20, 4: 30, 5: 36, 6: 38},
        )

    def test_04_obstructed_stealth_and_chain_provably_unliftable_in_R12(self) -> None:
        """Proves NO lambda_1 in R^12(F_0) preserves deformed kernel for obstructed directions."""
        o = self.audit["artificial_obstruction_audit"]
        self.assertTrue(o["both_provably_unliftable_in_R12"])

        ch = o["lambda_chain"]
        self.assertTrue(ch["no_lam1_in_R12_preserves_kernel"])
        self.assertGreater(ch["deformed_rank_m6_lam1_zero"], ch["expected_flat_double_rank_m6"])

        st = o["lambda_stealth"]
        self.assertTrue(st["no_lam1_in_R12_preserves_kernel"])
        self.assertGreater(st["deformed_rank_m6_lam1_zero"], st["expected_flat_double_rank_m6"])

    def test_05_gotzmann_persistence_and_honest_millennium_boundary(self) -> None:
        """Confirms G_t = 1 Hilbert (1,3,6,10,15,18,19) sum 72 while Bridge A stays open."""
        g = self.audit["gotzmann_persistence_audit"]
        self.assertTrue(g["infinitesimal_macaulay_flatness_verified"])
        self.assertTrue(g["gotzmann_persistence_gt_1_verified"])
        self.assertTrue(g["quadratic_moving_flat_18_of_18"])
        self.assertTrue(g["canonical_fixed_flat_56_of_56"])
        self.assertEqual(g["total_full_ideal_flat_directions_verified"], 332)
        self.assertEqual(g["gotzmann_deformed_witness"]["hilbert_vector"], (1, 3, 6, 10, 15, 18, 19))
        self.assertEqual(g["gotzmann_deformed_witness"]["hilbert_sum"], 72)
        self.assertEqual(g["gotzmann_deformed_witness"]["gotzmann_constant_Gt"], 1)

        # Strict Millennium Honesty Guardrails
        self.assertEqual(g["bridge_a_status"], "ADVERSARIALLY_BLOCKED_OPEN_BRIDGE")
        self.assertEqual(g["global_hodge_conjecture_status"], "OPEN")
        self.assertFalse(g["release_authorized"])
        self.assertEqual(g["theorem_progress"], "UNKNOWN")
        self.assertFalse(g["effective_hilbert_degree_bound_known"])
        self.assertFalse(g["disconnected_hodge_loci_solved"])

    def test_06_cyclotomic_125_wavepacket_band1_and_ideal(self) -> None:
        """Event 23: 125-monomial Band-1 cyclotomic wavepacket recovers true plane ideal and G=1."""
        audit = self.audit["cyclotomic_wavepacket_audit"]
        self.assertEqual(audit["monomial_count"], 125)
        self.assertEqual(audit["band1_pairable_count"], 125)
        self.assertEqual(audit["pair_sum_4_count"], 125)
        self.assertEqual(
            audit["annihilator_generators"],
            ["x_0 - x_3", "x_1 - x_4", "x_2 - x_5"],
        )
        self.assertEqual(audit["ann_R1_dim"], 3)
        self.assertTrue(audit["ann_R1_exact_plane_ideal_match"])
        self.assertEqual(audit["ideal_deg6_dim"], 407)
        self.assertEqual(tuple(audit["macaulay_rank_vector"]), (3, 6, 10, 15, 18, 19))
        self.assertEqual(tuple(audit["hilbert_vector"]), (1, 3, 6, 10, 15, 18, 19))
        self.assertEqual(audit["hilbert_sum"], 72)
        self.assertEqual(audit["gotzmann_G"], 1)

    def test_07_joint_generator_shadow_transport_gain_and_tilting(self) -> None:
        """Event 23: Joint generator-shadow transport gains +6 rank/subspace on wavepacket vs +0 on nilpotent."""
        jt = self.audit["joint_generator_transport_audit"]
        self.assertEqual(jt["wavepacket_stat_operator_rank"], 1750)
        self.assertEqual(jt["wavepacket_joint_operator_rank"], 1756)
        self.assertEqual(jt["wavepacket_operator_rank_gain"], 6)
        self.assertEqual(jt["wavepacket_ker6_dim"], 407)
        self.assertEqual(jt["wavepacket_stationary_subspace_dim"], 353)
        self.assertEqual(jt["wavepacket_joint_subspace_dim"], 359)
        self.assertEqual(jt["wavepacket_subspace_gain_by_tilting"], 6)
        self.assertEqual(jt["wavepacket_remaining_higher_deg_normal_gap"], 48)
        self.assertEqual(jt["nilpotent_stat_operator_rank"], 1750)
        self.assertEqual(jt["nilpotent_joint_operator_rank"], 1750)
        self.assertEqual(jt["nilpotent_tilting_gain"], 0)
        witnesses = jt["tilting_witnesses"]
        self.assertEqual(len(witnesses), 3)
        for w in witnesses:
            self.assertFalse(w["stationary_solvable"])
            self.assertTrue(w["joint_solvable"])
        self.assertEqual(
            witnesses[0]["full_m1_to_m6_deformed_ranks"],
            {1: 6, 2: 12, 3: 20, 4: 30, 5: 36, 6: 38},
        )
        self.assertTrue(witnesses[0]["all_degrees_flat"])

    def test_08_zero_floating_point_violations(self) -> None:
        """Zero floating-point constructs in deformed_macaulay_transport_engine.py."""
        hits = scan_forbidden(
            self.root / "toolkit" / "deformed_macaulay_transport_engine.py"
        )
        self.assertEqual(hits, [])


if __name__ == "__main__":
    unittest.main()
