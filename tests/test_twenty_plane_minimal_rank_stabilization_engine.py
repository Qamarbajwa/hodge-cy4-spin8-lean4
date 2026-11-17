"""Adversarial Tests for 20-Plane Minimal-Rank Recombination & Determinantal Macaulay Stabilization (Event 28)."""

from pathlib import Path
import unittest

from toolkit.governance.lean_step_runner import check_step, sha as sha_bytes
from toolkit.integrity import scan_forbidden
from toolkit.twenty_plane_minimal_rank_stabilization_engine import (
    TwentyPlaneMinimalRankStabilizationEngine,
)


class TestTwentyPlaneMinimalRankStabilizationEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parent.parent
        cls.engine = TwentyPlaneMinimalRankStabilizationEngine()
        cls.audit = cls.engine.run_full_audit()
        cls.lean_dir = cls.root / "examples" / "math_gov" / "LeanDemoProject"
        cls.lean_sha = sha_bytes((cls.lean_dir / "HodgeVerification.lean").read_bytes())

    def test_01_twenty_plane_incidence_and_high_support_annihilation(self) -> None:
        inc = self.audit["incidence"]
        self.assertEqual(inc["num_coordinate_planes"], 20)
        self.assertEqual(inc["per_plane_incidence_set"], [19])
        self.assertEqual(inc["total_incidences"], 380)
        self.assertEqual(inc["target_subspace_dim"], 245)
        self.assertEqual(inc["three_4_targets"], 200)
        self.assertEqual(inc["four_4_targets"], 45)
        self.assertEqual(inc["other_targets"], 0)
        self.assertEqual(inc["multiplicity_distribution"], {1: 200, 4: 45})
        self.assertEqual(inc["collision_excess"], 135)
        self.assertEqual(inc["support_distribution"], {2: 45, 3: 200, 4: 150, 5: 30, 6: 1})
        self.assertEqual(inc["low_support_total"], 245)
        self.assertEqual(inc["high_support_total"], 181)
        self.assertEqual(inc["high_support_counts"], {4: 150, 5: 30, 6: 1})
        self.assertEqual(inc["low_support_counts"], {2: 45, 3: 200})
        self.assertEqual(inc["low_support_hit_sets"], {2: [4], 3: [1]})
        self.assertEqual(inc["low_support_zero_hits"], 0)
        self.assertEqual(inc["high_support_zero_count"], 181)
        self.assertTrue(inc["high_support_all_zero_on_v20"])
        self.assertEqual(inc["monomial_v20_rank_histogram"], {0: 181, 1: 200, 4: 45})
        self.assertEqual(len(inc["partition_v20_census"]), 9)

    def test_02_quadruple_witness_and_collision_syzygies(self) -> None:
        quad = self.audit["quadruple_witness"]
        self.assertEqual(quad["quad_active_planes"], 9)
        self.assertEqual(quad["quad_individually_zero_planes"], 11)
        self.assertEqual(quad["quad_target_count"], 5)
        self.assertEqual(quad["quad_four_4_targets"], 5)
        self.assertEqual(quad["quad_three_4_targets"], 0)
        self.assertEqual(quad["quad_v20_rank"], 5)
        self.assertEqual(quad["quad_v20_kernel_dim"], 15)
        self.assertEqual(quad["quad_nontrivial_collision_syzygies"], 4)
        self.assertEqual(quad["quad_active_syzygy_basis_count"], 4)
        self.assertTrue(quad["all_kernel_vectors_annihilate_u_quad"])

    def test_03_fifteen_matching_band1_blocks_and_multiplicity(self) -> None:
        blk = self.audit["fifteen_matchings"]
        self.assertEqual(blk["num_matchings"], 15)
        self.assertEqual(blk["modes_per_block_set"], [125])
        self.assertEqual(blk["modes_per_block"], 125)
        self.assertEqual(blk["total_incidences"], 1875)
        self.assertEqual(blk["union_size"], 1001)
        self.assertEqual(blk["band1_reference_size"], 1001)
        self.assertTrue(blk["band1_exact_match"])
        self.assertEqual(blk["overlap_excess"], 874)
        self.assertEqual(blk["multiplicity_histogram"], {1: 360, 2: 540, 3: 60, 6: 40, 15: 1})
        self.assertEqual(blk["weighted_multiplicity_sum"], 1875)
        self.assertEqual(blk["central_monomial"], (2, 2, 2, 2, 2, 2))
        self.assertEqual(blk["central_monomial_multiplicity"], 15)
        self.assertEqual(blk["mult_15_monomials"], [(2, 2, 2, 2, 2, 2)])

    def test_04_determinantal_macaulay_stabilization_and_honesty_boundary(self) -> None:
        det = self.audit["determinantal_macaulay"]
        self.assertEqual(det["pi_static_r1"], 3)
        self.assertEqual(det["pi_static_ann1"], 3)
        self.assertEqual(det["pi_fixed_def_r1"], 6)
        self.assertTrue(det["pi_fixed_flat"])
        self.assertEqual(det["pi_moving_def_r1"], 6)
        self.assertTrue(det["pi_moving_flat"])
        self.assertEqual(det["recomb_static_r1"], 4)
        self.assertEqual(det["recomb_static_ann1"], 2)
        self.assertEqual(det["recomb_def_r1"], 8)
        self.assertTrue(det["recomb_flat"])
        self.assertEqual(det["generic_static_r1"], 6)
        self.assertEqual(det["generic_static_ann1"], 0)
        self.assertFalse(det["universal_non_fermat_determinantal_stabilization_proved"])
        self.assertFalse(self.audit["universal_non_fermat_determinantal_stabilization_proved"])
        self.assertEqual(det["global_hodge_conjecture_status"], "OPEN")

    def test_05_lean4_theorems_37_38_and_zero_float_scan(self) -> None:
        bp_bytes = (self.root / "lean_blueprint" / "HodgeVerification.lean").read_bytes()
        demo_bytes = (self.lean_dir / "HodgeVerification.lean").read_bytes()
        self.assertEqual(bp_bytes, demo_bytes)

        r37 = check_step(
            str(self.lean_dir),
            "HodgeVerification.lean",
            "twenty_plane_target_and_collision_counts_eq",
            "(twenty_plane_total_incidences == 380 && twenty_plane_target_dim == 245 && "
            "twenty_plane_three_4_targets * 1 + twenty_plane_four_4_targets * 4 == 380 && "
            "twenty_plane_collision_excess == 135 && "
            "twenty_plane_target_dim + high_support_moduli_dim == h31_prim && "
            "high_support_moduli_counts == [150, 30, 1] && high_support_moduli_dim == 181 && "
            "9 + 11 == saturation_three_count && 15 == saturation_three_count - 5 && "
            "15 - 11 == 4) = true",
            self.lean_sha,
        )
        self.assertTrue(r37["lean_kernel_check_passed"], msg=str(r37))
        self.assertEqual(r37["axioms"], [])

        r38 = check_step(
            str(self.lean_dir),
            "HodgeVerification.lean",
            "fifteen_matching_band1_block_incidence_eq",
            "(fifteen_perfect_matchings == 15 && modes_per_matching_block == 125 && "
            "band1_block_total_incidences == 1875 && "
            "band1_mult_mode_sum == fermat_band1_planes && "
            "band1_mult_incidence_sum == band1_block_total_incidences && "
            "band1_block_total_incidences - fermat_band1_planes == 874 && "
            "band1_multiplicity_pairs.map (fun p => p.2) == [360, 540, 60, 40, 1]) = true",
            self.lean_sha,
        )
        self.assertTrue(r38["lean_kernel_check_passed"], msg=str(r38))
        self.assertEqual(r38["axioms"], [])

        eng_path = self.root / "toolkit" / "twenty_plane_minimal_rank_stabilization_engine.py"
        self.assertEqual(scan_forbidden(str(eng_path)), [])
        self.assertEqual(scan_forbidden(__file__), [])


if __name__ == "__main__":
    unittest.main()
