"""Adversarial Tests for Non-Fermat Determinantal Stabilization & Higher-Degree Recombination (Event 29)."""

from pathlib import Path
import unittest

from toolkit.governance.lean_step_runner import check_step, sha as sha_bytes
from toolkit.integrity import scan_forbidden
from toolkit.non_fermat_determinantal_stabilization_engine import (
    NonFermatDeterminantalStabilizationEngine,
)


class TestNonFermatDeterminantalStabilizationEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parent.parent
        cls.engine = NonFermatDeterminantalStabilizationEngine()
        cls.audit = cls.engine.run_full_audit()
        cls.lean_dir = cls.root / "examples" / "math_gov" / "LeanDemoProject"
        cls.lean_sha = sha_bytes((cls.lean_dir / "HodgeVerification.lean").read_bytes())

    def test_01_recombined_m1_vs_higher_degree_stabilization(self) -> None:
        rc = self.audit["recombined_higher_degree"]
        self.assertEqual(rc["base_ranks"], [4, 9, 16, 24, 30, 32])
        self.assertEqual(rc["u_flat_ranks"], [8, 18, 32, 48, 60, 64])
        self.assertTrue(rc["u_flat_all_degrees_flat"])
        self.assertTrue(rc["m2_offender_static_zero"])
        self.assertTrue(rc["m2_offender_u_a_obstruction_nonzero"])
        self.assertTrue(rc["u_a_order2_obstruction_absorbed"])
        self.assertTrue(rc["all_moving_stabilized"])

        expected_naive = {
            "u_A": ([8, 19, 36, 56, 71, 76], [0, 1, 4, 8, 11, 12]),
            "u_B": ([8, 19, 36, 56, 72, 78], [0, 1, 4, 8, 12, 14]),
            "u_C": ([8, 19, 36, 56, 71, 76], [0, 1, 4, 8, 11, 12]),
        }
        self.assertEqual(len(rc["directions"]), 3)
        for d in rc["directions"]:
            exp_ranks, exp_excess = expected_naive[d["direction"]]
            self.assertTrue(d["gm1_satisfied"])
            self.assertTrue(d["naive_m1_flat"])
            self.assertFalse(d["naive_all_degrees_flat"])
            self.assertEqual(d["naive_ranks"], exp_ranks)
            self.assertEqual(d["naive_excess"], exp_excess)
            self.assertEqual(d["stabilized_ranks"], [8, 18, 32, 48, 60, 64])
            self.assertTrue(d["stabilized_all_degrees_flat"])

    def test_02_quadruple_collision_syzygies_stabilize_all_degrees(self) -> None:
        qs = self.audit["quadruple_collision_syzygies"]
        self.assertEqual(qs["num_syzygies"], 4)
        self.assertTrue(qs["all_naive_jump_from_m1"])
        self.assertTrue(qs["all_stabilized_flat"])
        for syz in qs["syzygies"]:
            self.assertTrue(syz["gm1_satisfied"])
            self.assertEqual(syz["base_ranks"], [4, 9, 16, 24, 30, 32])
            self.assertEqual(syz["naive_ranks"], [9, 23, 45, 71, 91, 98])
            self.assertEqual(syz["naive_excess"], [1, 5, 13, 23, 31, 34])
            self.assertFalse(syz["naive_all_degrees_flat"])
            self.assertEqual(syz["stabilized_ranks"], [8, 18, 32, 48, 60, 64])
            self.assertTrue(syz["stabilized_all_degrees_flat"])

    def test_03_finite_non_fermat_smooth_cy4_macaulay_apolarity(self) -> None:
        fnf = self.audit["finite_non_fermat"]
        self.assertTrue(fnf["smooth_zero_deg9"])
        self.assertEqual(fnf["pair_milnors"], [25, 25, 25])
        self.assertEqual(fnf["total_milnor"], 15625)
        for h in fnf["pair_hilberts"]:
            self.assertEqual(h, fnf["expected_pair_hilbert_0_to_9"])
        self.assertEqual(
            fnf["six_var_graded_dims"],
            {1: 6, 2: 21, 3: 56, 4: 126, 5: 246, 6: 426, 12: 1751, 18: 426},
        )
        self.assertEqual(fnf["plane_nf_ranks"], [3, 6, 10, 15, 18, 19])
        self.assertEqual(fnf["plane_nf_ann1_dim"], 3)
        self.assertTrue(fnf["plane_nf_linear_ideal_verified"])
        self.assertEqual(fnf["quad_nf_ranks"], [4, 9, 16, 24, 30, 32])
        self.assertEqual(fnf["quad_nf_ann1_dim"], 2)
        self.assertEqual(fnf["quad_nf_ann6_dim"], 394)
        self.assertTrue(fnf["quad_nf_linear_ideal_verified"])
        self.assertTrue(fnf["quad_nf_quadratic_generator_verified"])

    def test_04_honesty_boundary_and_zero_float_guardrail(self) -> None:
        hb = self.audit["honesty_boundary"]
        self.assertFalse(hb["universal_non_fermat_determinantal_stabilization_proved"])
        self.assertFalse(hb["effective_hilbert_degree_bound_known"])
        self.assertFalse(hb["non_separable_dense_non_fermat_universal_bound_proved"])
        self.assertEqual(hb["global_hodge_conjecture_status"], "OPEN")
        self.assertEqual(self.audit["scan_forbidden_hits"], 0)
        eng_path = self.root / "toolkit" / "non_fermat_determinantal_stabilization_engine.py"
        self.assertEqual(scan_forbidden(str(eng_path)), [])
        self.assertEqual(scan_forbidden(__file__), [])

    def test_05_lean4_theorems_39_and_40_zero_axioms(self) -> None:
        bp_bytes = (self.root / "lean_blueprint" / "HodgeVerification.lean").read_bytes()
        demo_bytes = (self.lean_dir / "HodgeVerification.lean").read_bytes()
        self.assertEqual(bp_bytes, demo_bytes)

        r39 = check_step(
            str(self.lean_dir),
            "HodgeVerification.lean",
            "recomb_and_collision_flat_hilbert_eq",
            "(recomb_flat_target == [8, 18, 32, 48, 60, 64] && "
            "list_diff_nat recomb_ua_naive_ranks recomb_flat_target == [0, 1, 4, 8, 11, 12] && "
            "list_diff_nat recomb_ub_naive_ranks recomb_flat_target == [0, 1, 4, 8, 12, 14] && "
            "list_diff_nat quad_collision_naive_ranks recomb_flat_target == [1, 5, 13, 23, 31, 34] && "
            "list_head_nat recomb_ua_naive_ranks == 8 && "
            "list_head_nat quad_collision_naive_ranks == 9 && "
            "h31_prim - 32 == 394) = true",
            self.lean_sha,
        )
        self.assertTrue(r39["lean_kernel_check_passed"], msg=str(r39))
        self.assertEqual(r39["axioms"], [])

        r40 = check_step(
            str(self.lean_dir),
            "HodgeVerification.lean",
            "finite_non_fermat_pair_milnor_and_ranks_eq",
            "(nf_pair_milnor == 25 && "
            "nf_total_milnor == milnor_number && "
            "1 :: nf_plane_ranks == deformed_macaulay_flat_hilbert && "
            "([1, 2, 3, 4, 5, 6].map nf_sum_pairs == [6, 21, 56, 126, 246, 426]) && "
            "nf_sum_pairs 12 == h22_prim && "
            "nf_sum_pairs 18 == h31_prim && "
            "6 - 3 == 3 && 6 - 4 == 2) = true",
            self.lean_sha,
        )
        self.assertTrue(r40["lean_kernel_check_passed"], msg=str(r40))
        self.assertEqual(r40["axioms"], [])


if __name__ == "__main__":
    unittest.main()
