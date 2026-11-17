"""Adversarial Tests for Universal Obstruction-Cancellation & Gorenstein Moduli Duality Engine (Event 26)."""

from pathlib import Path
import unittest

from toolkit.governance.lean_step_runner import check_step, sha as sha_bytes
from toolkit.integrity import scan_forbidden
from toolkit.universal_obstruction_cancellation_engine import (
    UniversalObstructionCancellationEngine,
)


class TestUniversalObstructionCancellationEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parent.parent
        cls.engine = UniversalObstructionCancellationEngine()
        cls.audit = cls.engine.run_full_audit()
        cls.lean_dir = cls.root / "examples" / "math_gov" / "LeanDemoProject"
        cls.lean_sha = sha_bytes((cls.lean_dir / "HodgeVerification.lean").read_bytes())

    def test_01_universal_rank_nullity_and_dense_deformation(self) -> None:
        rn = self.audit["universal_rank_nullity"]
        self.assertEqual(rn["dim_R6"], 426)
        self.assertEqual(rn["dim_R12"], 1751)
        self.assertEqual(rn["dim_R18"], 426)
        self.assertEqual(rn["dim_band1"], 1001)
        self.assertEqual(rn["dim_band2"], 630)
        self.assertEqual(rn["dim_band3"], 120)
        self.assertEqual(rn["dim_band4"], 0)
        self.assertEqual(rn["universal_total_kernel_lower_bound"], 1325)
        self.assertEqual(rn["universal_band1_kernel_lower_bound"], 575)
        self.assertEqual(rn["universal_band2_kernel_lower_bound"], 204)
        self.assertEqual(rn["dense_u_partitions_combined"], 9)
        self.assertEqual(rn["dense_full_rank"], 426)
        self.assertEqual(rn["dense_full_kernel_dim"], 1325)
        self.assertGreaterEqual(rn["dense_full_kernel_dim"], 1325)
        self.assertEqual(rn["dense_band1_rank"], 408)
        self.assertEqual(rn["dense_band1_kernel_dim"], 593)
        self.assertGreaterEqual(rn["dense_band1_kernel_dim"], 575)
        self.assertEqual(rn["dense_band2_rank"], 338)
        self.assertEqual(rn["dense_band2_kernel_dim"], 292)
        self.assertGreaterEqual(rn["dense_band2_kernel_dim"], 204)
        self.assertEqual(rn["dense_band3_rank"], 114)
        self.assertEqual(rn["dense_band3_kernel_dim"], 6)
        self.assertTrue(rn["universal_bounds_satisfied"])
        self.assertFalse(rn["all_order_castelnuovo_mumford_bound_proved"])

    def test_02_gorenstein_9_partition_moduli_census(self) -> None:
        mc = self.audit["gorenstein_moduli_census"]
        self.assertEqual(mc["total_moduli_monomials"], 426)
        self.assertEqual(mc["total_moduli_partitions"], 9)
        self.assertEqual(sum(p["multiplicity"] for p in mc["partitions"]), 426)
        self.assertEqual(mc["gorenstein_complement_duality_verified_count"], 9)
        self.assertTrue(mc["gorenstein_complement_duality_holds_all_9"])
        self.assertTrue(mc["matrix_rank_matches_capacity_all_9"])
        self.assertEqual(mc["global_min_rank"], 155)
        self.assertEqual(mc["global_min_rank_partition"], (4, 2, 0, 0, 0, 0))
        self.assertEqual(mc["global_max_kernel_dim"], 1596)
        self.assertEqual(mc["global_max_rank"], 336)
        self.assertEqual(mc["global_max_rank_partition"], (1, 1, 1, 1, 1, 1))
        self.assertEqual(mc["global_min_kernel_dim"], 1415)
        for rec in mc["partitions"]:
            self.assertEqual(rec["rank"], rec["gorenstein_dual_deg6_count"])
            self.assertEqual(rec["kernel_dim"], 1751 - rec["rank"])

    def test_03_turan_pigeonhole_k5_plane_coverage(self) -> None:
        tc = self.audit["turan_plane_coverage"]
        self.assertEqual(tc["coordinate_planes_count"], 20)
        self.assertEqual(tc["moduli_monomials_count"], 426)
        self.assertEqual(tc["support_2_monomials_count"], 45)
        self.assertEqual(tc["support_2_obstructed_planes"], 4)
        self.assertEqual(tc["support_2_surviving_planes"], 16)
        self.assertEqual(tc["support_3_monomials_count"], 200)
        self.assertEqual(tc["support_3_obstructed_planes"], 1)
        self.assertEqual(tc["support_3_surviving_planes"], 19)
        self.assertEqual(tc["support_ge4_monomials_count"], 181)
        self.assertEqual(tc["support_ge4_obstructed_planes"], 0)
        self.assertEqual(tc["support_ge4_surviving_planes"], 20)
        self.assertEqual(tc["max_obstructed_planes_per_monomial"], 4)
        self.assertEqual(tc["min_surviving_planes_per_monomial"], 16)
        self.assertEqual(tc["pigeonhole_min_K"], 5)
        self.assertEqual(tc["k5_subsets_tested"], 15504)
        self.assertEqual(tc["k5_total_incidences_tested"], 6604704)
        self.assertEqual(tc["k5_uncovered_incidences"], 0)
        self.assertEqual(tc["k4_failing_incidences_count"], 45)
        self.assertTrue(tc["pigeonhole_k5_coverage_verified"])

    def test_04_lean4_theorems_33_and_34_zero_axioms(self) -> None:
        r33 = check_step(
            str(self.lean_dir),
            "HodgeVerification.lean",
            "universal_band_obstruction_cancellation_bounds_eq",
            "(universal_total_ker_bound == 1325 && universal_band1_ker_bound == 575 && "
            "universal_band2_ker_bound == 204 && turan_max_obstructed_planes == 4 && "
            "turan_min_surviving_planes == 16 && turan_max_obstructed_planes + 1 == 5) = true",
            self.lean_sha,
        )
        self.assertTrue(r33["lean_kernel_check_passed"])
        self.assertEqual(r33["axioms"], [])

        r34 = check_step(
            str(self.lean_dir),
            "HodgeVerification.lean",
            "gorenstein_moduli_rank_extremes_eq",
            "(gorenstein_min_rank_deg12 == 155 && gorenstein_min_rank_deg6_dual == 155 && "
            "gorenstein_max_ker_dim == 1596 && gorenstein_max_rank_deg12 == 336 && "
            "gorenstein_max_rank_deg6_dual == 336 && gorenstein_min_ker_dim == 1415) = true",
            self.lean_sha,
        )
        self.assertTrue(r34["lean_kernel_check_passed"])
        self.assertEqual(r34["axioms"], [])

    def test_05_zero_float_and_honesty_guardrails(self) -> None:
        self.assertEqual(
            scan_forbidden(str(self.root / "toolkit" / "universal_obstruction_cancellation_engine.py")),
            [],
        )
        hb = self.audit["honesty_boundary"]
        self.assertEqual(self.audit["event_id"], 26)
        self.assertEqual(hb["GLOBAL_HODGE_CONJECTURE"], "OPEN")
        self.assertFalse(hb["release_authorized"])
        self.assertEqual(hb["theorem_progress"], "UNKNOWN")
        self.assertEqual(hb["bridge_a_status"], "ADVERSARIALLY_BLOCKED_OPEN_BRIDGE")
        self.assertEqual(hb["bridge_b_status"], "ADVERSARIALLY_BLOCKED_OPEN_BRIDGE")
        self.assertFalse(hb["all_order_castelnuovo_mumford_bound_proved"])


if __name__ == "__main__":
    unittest.main()
