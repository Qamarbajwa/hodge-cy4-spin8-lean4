"""Adversarial Tests for Global Cycle Recombination & Weyl-Coset Weil Spanning Engine (Event 25)."""

from fractions import Fraction
from pathlib import Path
import unittest

from toolkit.global_recombination_and_coset_engine import (
    GlobalRecombinationAndCosetEngine,
)
from toolkit.governance.lean_step_runner import check_step, sha as sha_bytes
from toolkit.higher_order_gauss_manin_sieve import poly_mod_jacobian, poly_mul
from toolkit.integrity import scan_forbidden


class TestGlobalRecombinationAndCosetEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parent.parent
        cls.engine = GlobalRecombinationAndCosetEngine()
        cls.audit = cls.engine.run_full_audit()
        cls.lean_dir = cls.root / "examples" / "math_gov" / "LeanDemoProject"
        cls.lean_sha = sha_bytes((cls.lean_dir / "HodgeVerification.lean").read_bytes())

    def test_01_zero_floats_and_honesty_boundary(self) -> None:
        self.assertEqual(
            scan_forbidden(str(self.root / "toolkit" / "global_recombination_and_coset_engine.py")),
            [],
        )
        self.assertEqual(self.audit["event_id"], 25)
        self.assertEqual(self.audit["bridge_a_status"], "ADVERSARIALLY_BLOCKED_OPEN_BRIDGE")
        self.assertEqual(self.audit["bridge_b_status"], "ADVERSARIALLY_BLOCKED_OPEN_BRIDGE")
        self.assertEqual(self.audit["global_hodge_conjecture_status"], "OPEN")
        self.assertFalse(self.audit["release_authorized"])
        self.assertEqual(self.audit["theorem_progress"], "UNKNOWN")

    def test_02_bridge_a_recombination_and_all_order_jet_survival(self) -> None:
        m1 = self.audit["recombination_audit"]
        self.assertEqual(m1["lambda1_rank"], 19)
        self.assertEqual(m1["lambda2_rank"], 19)
        self.assertEqual(m1["lambda1_ker_dim"], 407)
        self.assertEqual(m1["lambda2_ker_dim"], 407)
        self.assertEqual(m1["stacked_rank_1_and_2"], 35)
        self.assertEqual(m1["shared_kernel_dim"], 391)
        self.assertEqual(m1["recombined_rank"], 32)
        self.assertEqual(m1["recombined_kernel_dim"], 394)
        self.assertEqual(m1["recombination_kernel_gain"], 3)
        self.assertTrue(m1["all_3_directions_pass_orders_1_2_3"])
        self.assertEqual(m1["macaulay_rank_vector"], (4, 9, 16, 24, 30, 32))
        self.assertEqual(m1["macaulay_ann_dims"], (2, 12, 40, 102, 216, 394))
        self.assertTrue(m1["ann_R1_is_x0_x1"])
        self.assertTrue(m1["x2_x3_in_ann_R2"])
        self.assertEqual(m1["subadditive_quadric_degree"], 2)
        self.assertFalse(m1["convergence_over_non_fermat_islands_proved"])

        # Explicit check that u_A, u_B, u_C fail both individual planes yet cancel on sum
        lam1 = {(4, 4, 4, 0, 0, 0): Fraction(1, 1)}
        lam2 = {(4, 4, 0, 4, 0, 0): Fraction(1, 1)}
        for u_poly in (
            {(0, 0, 0, 4, 2, 0): Fraction(1, 1), (0, 0, 4, 0, 2, 0): Fraction(-1, 1)},
            {(0, 0, 0, 4, 1, 1): Fraction(1, 1), (0, 0, 4, 0, 1, 1): Fraction(-1, 1)},
            {(0, 0, 0, 4, 0, 2): Fraction(1, 1), (0, 0, 4, 0, 0, 2): Fraction(-1, 1)},
        ):
            self.assertTrue(poly_mod_jacobian(poly_mul(u_poly, lam1), 5))
            self.assertTrue(poly_mod_jacobian(poly_mul(u_poly, lam2), 5))

    def test_03_bridge_a_18_partition_apolar_dictionary(self) -> None:
        m2 = self.audit["band_apolarity_dictionary"]
        self.assertEqual(m2["total_partitions"], 18)
        self.assertEqual(m2["total_modes"], 1751)
        self.assertEqual(m2["partitions_with_raw_ann_R1_or_R2"], 17)
        self.assertEqual(m2["central_222222_atom_fallback_ann_R1"], 3)
        self.assertEqual(m2["max_generator_degree_d_gen"], 4)
        self.assertTrue(m2["all_18_partitions_bounded_d_gen_le_4"])
        self.assertFalse(m2["general_non_fermat_degree_bound_known"])

    def test_04_bridge_b_weyl_coset_6_of_6_spanning(self) -> None:
        m3 = self.audit["weyl_coset_weil_spanning"]
        self.assertEqual(m3["coord_pure_weil_count"], 8)
        self.assertEqual(m3["hadamard_pure_weil_count"], 8)
        self.assertEqual(m3["total_pure_weil_count"], 16)
        self.assertEqual(m3["wd4_order"], 192)
        self.assertEqual(m3["dim_so8"], 28)
        self.assertEqual(m3["dim_su22_plus_u1"], 16)
        self.assertEqual(m3["dim_coset_p"], 12)
        self.assertEqual(m3["single_axis_singlet_dim"], 1)
        self.assertEqual(m3["wd4_self_dual_singlet_orbit_rank"], 3)
        self.assertEqual(m3["conjugate_dual_pair_weil_spanning_rank"], 6)
        self.assertEqual(m3["coset_transport_single_axis_rank"], 5)
        self.assertEqual(m3["coset_transport_multi_axis_rank"], 6)
        self.assertTrue(m3["full_6_of_6_k22_spanned"])
        self.assertFalse(m3["chow_flatness_over_end_Q_proved"])

    def test_05_lean4_theorems_31_and_32_zero_axioms(self) -> None:
        r31 = check_step(
            str(self.lean_dir),
            "HodgeVerification.lean",
            "recombination_kernel_dim_gain_eq",
            "(deg6_triples_le4.length == 19 && shared_deg6_triples.length == 3 && "
            "cancel_deg2_pairs.length == 3 && shared_ker_dim == 391 && recomb_rank == 32 && "
            "recomb_ker_dim == 394 && recomb_ker_dim - shared_ker_dim == 3) = true",
            self.lean_sha,
        )
        self.assertTrue(r31["lean_kernel_check_passed"])
        self.assertEqual(r31["axioms"], [])

        r32 = check_step(
            str(self.lean_dir),
            "HodgeVerification.lean",
            "weyl_d4_conjugate_weil_axes_eq",
            "(coord_pure_weil_tuples.length == 8 && hadamard_pure_weil_tuples.length == 8 && "
            "coord_pure_weil_tuples.length + hadamard_pure_weil_tuples.length == 16 && "
            "binom 8 2 == 28 && binom 6 2 + 1 == 16 && shimura_coset_dim == 12 && "
            "k22_pair0_count == 2 && k22_pair1_count == 2 && k22_pair2_count == 2 && "
            "k22_pair0_count + k22_pair1_count + k22_pair2_count == zero_weight_tuples.length) = true",
            self.lean_sha,
        )
        self.assertTrue(r32["lean_kernel_check_passed"])
        self.assertEqual(r32["axioms"], [])


if __name__ == "__main__":
    unittest.main()
