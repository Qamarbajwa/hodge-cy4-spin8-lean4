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
        self.assertEqual(ver["count"], 12)

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
        self.assertEqual(res3["axioms"], ["propext", "Classical.choice", "Quot.sound"])

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


if __name__ == "__main__":
    unittest.main()
