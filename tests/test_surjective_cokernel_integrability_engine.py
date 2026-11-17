"""Adversarial Tests for Surjective Cokernel Annihilation & Rank-Independent All-Order Integrability (Event 27)."""

from pathlib import Path
import unittest

from toolkit.governance.lean_step_runner import check_step, sha as sha_bytes
from toolkit.integrity import scan_forbidden
from toolkit.surjective_cokernel_integrability_engine import (
    SurjectiveCokernelIntegrabilityEngine,
)


class TestSurjectiveCokernelIntegrabilityEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parent.parent
        cls.engine = SurjectiveCokernelIntegrabilityEngine()
        cls.audit = cls.engine.run_full_audit()
        cls.lean_dir = cls.root / "examples" / "math_gov" / "LeanDemoProject"
        cls.lean_sha = sha_bytes((cls.lean_dir / "HodgeVerification.lean").read_bytes())

    def test_01_surjective_cokernel_and_recursive_power_series_lifts(self) -> None:
        sc = self.audit["surjective_cokernel"]
        self.assertEqual(sc["dense_u_rank"], 426)
        self.assertEqual(sc["dim_R18"], 426)
        self.assertEqual(sc["dense_u_cokernel_dim"], 0)
        self.assertTrue(sc["dense_u_surjective"])
        self.assertEqual(sc["dense_u_kernel_dim"], 1325)
        self.assertEqual(sc["all_order_unobstructed_kernel_dim"], 1325)
        self.assertEqual(
            sc["monomial_kernel_vectors_count"] + sc["multi_term_kernel_vectors_count"],
            1325,
        )
        self.assertEqual(sc["recursive_sample_vectors_tested"], 6)
        self.assertTrue(sc["recursive_orders_1_2_3_all_exact"])
        for rec in sc["sample_lift_records"]:
            self.assertTrue(rec["orders_1_2_3_exact"])

    def test_02_rank_independent_second_order_cancellation(self) -> None:
        ri = self.audit["rank_independent_second_order"]
        self.assertTrue(ri["rank_nullity_index_exact_for_all_426"])
        self.assertEqual(ri["universal_cancellation_lower_bound"], 1325)
        self.assertEqual(ri["partitions_count"], 9)
        self.assertEqual(
            ri["partition_ranks"],
            [155, 165, 207, 248, 264, 279, 297, 316, 336],
        )
        self.assertEqual(
            ri["partition_coker_dims"],
            [271, 261, 219, 178, 162, 147, 129, 110, 90],
        )
        self.assertEqual(
            ri["partition_psi2_ranks"],
            [52, 93, 0, 31, 55, 30, 48, 71, 90],
        )
        self.assertEqual(
            ri["partition_ker_psi2_dims"],
            [1544, 1493, 1544, 1472, 1432, 1442, 1406, 1364, 1325],
        )
        for rec in ri["partition_records"]:
            self.assertGreaterEqual(rec["ker_psi2_dim"], 1325)
        self.assertEqual(ri["all_426_monomials_checked"], 426)
        self.assertEqual(ri["all_426_monomials_ge_1325_count"], 426)
        self.assertEqual(ri["min_ker_psi2_dim"], 1325)
        self.assertEqual(ri["max_ker_psi2_dim"], 1544)

    def test_03_formal_series_to_hilbert_honesty_boundary(self) -> None:
        hn = self.audit["formal_to_hilbert_honesty"]
        self.assertTrue(hn["zariski_open_surjective_locus_exists"])
        self.assertEqual(hn["formal_power_series_integrable_dim"], 1325)
        self.assertEqual(hn["rank_independent_order2_lower_bound"], 1325)
        self.assertTrue(hn["cdk_1995_hodge_locus_algebraic_in_moduli"])
        self.assertFalse(hn["global_non_fermat_hilbert_stabilization_proved"])
        self.assertFalse(hn["effective_hilbert_degree_bound_known"])
        self.assertEqual(hn["global_hodge_conjecture"], "OPEN")
        self.assertFalse(hn["release_authorized"])

    def test_04_lean4_check_35_nine_partition_zero_axioms(self) -> None:
        r35 = check_step(
            str(self.lean_dir),
            "HodgeVerification.lean",
            "nine_partition_cokernel_dims_eq",
            "(nine_partition_moduli_ranks.map (fun r => 426 - r) == nine_partition_cokernels && "
            "nine_gorenstein_exact_ranks.map (fun r => 426 - r) == nine_gorenstein_exact_cokernels) = true",
            self.lean_sha,
        )
        self.assertTrue(r35["lean_kernel_check_passed"], msg=str(r35))
        self.assertEqual(r35["axioms"], [])

    def test_05_zero_float_guardrail(self) -> None:
        hits = scan_forbidden(
            str(self.root / "toolkit" / "surjective_cokernel_integrability_engine.py")
        )
        self.assertEqual(hits, [])


if __name__ == "__main__":
    unittest.main()
