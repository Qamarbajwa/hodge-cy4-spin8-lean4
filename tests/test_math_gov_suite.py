r"""Comprehensive positive and adversarial test suite for MATH-GOV v0.6 Governance OS.

Tests:
1. Event Ledger: durable exact-byte prompt/result capture and tampering detection.
2. Math Step Engine: structural schema checks, acyclic dependency graphs, edge verification.
3. Negative Engine Tests: cycle detection, missing required edges, unapproved formal targets.
4. Truthful Progress Reporting (C13): 5/10 tasks executed does NOT equal 50% theorem proved.
5. Real Lean Verification (G6, C05): Lake execution, theorem check, and axiom report.
6. Adversarial Lean Tests (C06, C08): rejection of 'sorry', compilation failure on false theorems.
7. Candidate Install Audit: verification of authority files and fail-closed release policy.
8. Manifest Byte-Integrity: verification of candidate distribution with POSIX path normalization.
"""

import copy
import hashlib
import json
import os
import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path

from toolkit.governance.event_ledger import append as append_event, verify as verify_event_ledger, init as init_event_ledger
from toolkit.governance.math_step_engine import audit as audit_step_case, digest, canonical, index_graph
from toolkit.governance.step_verifier import check_formal_step
from toolkit.governance.lean_step_runner import check_step as check_lean_step
from toolkit.governance.gemini_install_audit import audit as audit_install
from toolkit.governance.verify_manifest import verify as verify_manifest_dir


class TestMathGovSuite(unittest.TestCase):
    def setUp(self):
        self.lean_project_root = Path("examples/math_gov/LeanDemoProject").resolve()
        self.lean_source_file = "ProofSteps.lean"
        self.lean_full_path = self.lean_project_root / self.lean_source_file

    # -------------------------------------------------------------------------
    # 1. Event Ledger & Tampering Detection
    # -------------------------------------------------------------------------
    def test_event_ledger_integrity_and_tampering(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
            db_path = tf.name

        conn = None
        try:
            conn = sqlite3.connect(db_path)
            init_event_ledger(conn)

            prompt1 = b"Compute the intersection matrix of primitive cycles."
            result1 = b"Result: Matrix is symmetric with zero diagonal."
            res1 = append_event(conn, "PROMPT", "Worker1", "HODGE-STEP-01", prompt1, result1)
            self.assertEqual(res1["seq"], 1)

            prompt2 = b"Verify orthogonality to Theta^2."
            result2 = b"Orthogonality verified: <w, Theta^2> = 0."
            res2 = append_event(conn, "VERIFICATION", "Worker2", "HODGE-STEP-02", prompt2, result2)
            self.assertEqual(res2["seq"], 2)

            # Positive check: verify untouched chain
            check = verify_event_ledger(conn)
            self.assertEqual(check["verdict"], "LOCAL_CHAIN_VALID_UNAUTHENTICATED")
            self.assertEqual(check["count"], 2)

            # Adversarial check: tamper with event actor/subject in raw database
            conn.execute("UPDATE events SET event = replace(event, 'HODGE-STEP-01', 'TAMPERED-STEP') WHERE seq = 1")
            conn.commit()

            tampered_check = verify_event_ledger(conn)
            self.assertIn(tampered_check["verdict"], ("TAMPER_DETECTED", "TAMPER_OR_INVALID_EVENT"))
        finally:
            if conn is not None:
                conn.close()
            if os.path.exists(db_path):
                os.remove(db_path)

    # -------------------------------------------------------------------------
    # 2. Math Step Engine: Structural & Dependency Tests
    # -------------------------------------------------------------------------
    def test_math_step_engine_positive_case(self):
        case_path = Path("examples/math_gov/demo_case.json")
        self.assertTrue(case_path.exists())
        case = json.loads(case_path.read_text(encoding="utf-8"))

        orig_digest = case["original"]["digest"]
        target_digest = case["formal_target"]["digest"]
        contract_digest = digest(canonical({'required_inventory': case['required_inventory'], 'required_edges': case['required_edges']}))

        res = audit_step_case(case, orig_digest, target_digest, contract_digest)
        self.assertEqual(res["verdict"], "STRUCTURAL_PREFLIGHT_PASS_ONLY")
        self.assertFalse(res["release_authorized"])

    def test_math_step_engine_cyclic_graph_rejection(self):
        case = json.loads(Path("examples/math_gov/demo_case.json").read_text(encoding="utf-8"))
        # Add a cycle: S2 -> S1 (while S1 -> S2 already exists)
        case["edges"].append({"source": "S2", "target": "S1", "kind": "AND"})
        case["required_edges"].append({"source": "S2", "target": "S1", "kind": "AND", "group": None})

        orig_digest = case["original"]["digest"]
        target_digest = case["formal_target"]["digest"]
        contract_digest = digest(canonical({'required_inventory': case['required_inventory'], 'required_edges': case['required_edges']}))

        res = audit_step_case(case, orig_digest, target_digest, contract_digest)
        self.assertEqual(res["verdict"], "BLOCKED")
        self.assertTrue(any("cycle" in err for err in res["errors"]))

    def test_math_step_engine_unapproved_target_rejection(self):
        case = json.loads(Path("examples/math_gov/demo_case.json").read_text(encoding="utf-8"))
        case["formal_target"]["approved"] = False

        orig_digest = case["original"]["digest"]
        target_digest = case["formal_target"]["digest"]
        contract_digest = digest(canonical({'required_inventory': case['required_inventory'], 'required_edges': case['required_edges']}))

        res = audit_step_case(case, orig_digest, target_digest, contract_digest)
        self.assertEqual(res["verdict"], "BLOCKED")
        self.assertTrue(any("not recorded as approved" in err for err in res["errors"]))

    # -------------------------------------------------------------------------
    # 3. Truthful Progress Reporting (Control C13)
    # -------------------------------------------------------------------------
    def test_truthful_progress_reporting_five_of_ten(self):
        status = json.loads(Path("examples/math_gov/five_of_ten_status.json").read_text(encoding="utf-8"))

        # Verify that 5 of 10 tasks executed is recorded honestly
        self.assertEqual(status["tasks_total"], 10)
        self.assertEqual(status["tasks_execution_finished"], 5)
        self.assertEqual(status["theorem_progress_percent"], "UNKNOWN")
        self.assertFalse(status["proof_verified"])
        # Proof must never claim 50%
        self.assertNotIn("50%", str(status))

    # -------------------------------------------------------------------------
    # 4. Real Lean Step Runner & Axiom Checking
    # -------------------------------------------------------------------------
    def test_real_lean_step_verification_positive(self):
        src_bytes = self.lean_full_path.read_bytes()
        src_sha = hashlib.sha256(src_bytes).hexdigest()

        res = check_lean_step(
            project_root=str(self.lean_project_root),
            relative_source=self.lean_source_file,
            theorem="MathGov.step1",
            expected_statement="forall (n : Nat), n + 0 = n",
            expected_file_sha256=src_sha,
            timeout=120,
        )

        self.assertEqual(res["verdict"], "LOCAL_LEAN_STEP_CHECK_PASS_PENDING_INDEPENDENT_RECHECK")
        self.assertTrue(res["lean_kernel_check_passed"])
        self.assertFalse(res["proof_complete"])
        self.assertFalse(res["release_authorized"])
        self.assertEqual(res["axioms"], ["propext"])

    def test_adversarial_lean_sorry_rejection(self):
        with tempfile.TemporaryDirectory() as td:
            # Clone Lean project into isolated temporary directory
            td_path = Path(td)
            shutil.copytree(self.lean_project_root, td_path / "project")
            proj = td_path / "project"

            # Inject a theorem using sorry
            bad_lean = proj / "ProofSteps.lean"
            bad_lean.write_text(
                "namespace MathGov\n\ntheorem false_thm (n : Nat) : n = 0 := by\n  sorry\n\nend MathGov\n",
                encoding="utf-8",
            )
            src_sha = hashlib.sha256(bad_lean.read_bytes()).hexdigest()

            res = check_lean_step(
                project_root=str(proj),
                relative_source="ProofSteps.lean",
                theorem="MathGov.false_thm",
                expected_statement="forall (n : Nat), n = 0",
                expected_file_sha256=src_sha,
                timeout=120,
            )

            # Lean emits a warning when 'sorry' is used; fail-closed policy treats warnings as failure
            self.assertFalse(res["lean_kernel_check_passed"])
            self.assertEqual(res["verdict"], "LEAN_COMPILATION_OR_WARNING")

    def test_adversarial_lean_invalid_proof_rejection(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            shutil.copytree(self.lean_project_root, td_path / "project")
            proj = td_path / "project"

            # Inject false theorem that simp cannot close
            bad_lean = proj / "ProofSteps.lean"
            bad_lean.write_text(
                "namespace MathGov\n\ntheorem false_thm (n : Nat) : n = n + 1 := by\n  simp\n\nend MathGov\n",
                encoding="utf-8",
            )
            src_sha = hashlib.sha256(bad_lean.read_bytes()).hexdigest()

            res = check_lean_step(
                project_root=str(proj),
                relative_source="ProofSteps.lean",
                theorem="MathGov.false_thm",
                expected_statement="forall (n : Nat), n = n + 1",
                expected_file_sha256=src_sha,
                timeout=120,
            )

            self.assertFalse(res["lean_kernel_check_passed"])
            self.assertEqual(res["verdict"], "LEAN_COMPILATION_OR_WARNING")

    # -------------------------------------------------------------------------
    # 5. Gemini Candidate Installation Audit
    # -------------------------------------------------------------------------
    def test_gemini_candidate_install_audit(self):
        audit_res = audit_install(Path("."), mode="unknown")
        # Authorities must be observed
        self.assertEqual(audit_res["checks"]["authority_count_observed"], 3)
        self.assertIn("governance/GOVERNANCE.md", audit_res["files"])
        self.assertIn("governance/PROJECT_DIRECTION.md", audit_res["files"])
        self.assertIn("governance/PROJECT_STATE.yaml", audit_res["files"])
        # Release authorization must be False without independent external cutover
        self.assertFalse(audit_res["release_authorized"])

    # -------------------------------------------------------------------------
    # 6. Manifest Byte Integrity Verification
    # -------------------------------------------------------------------------
    def test_candidate_manifest_byte_integrity(self):
        candidate_dir = Path("math_gov_candidate_source/MATH_GOV_v0_6_PROJECT_GOVERNANCE_ADOPTION_CANDIDATE")
        if candidate_dir.exists():
            res = verify_manifest_dir(candidate_dir)
            self.assertEqual(res["verdict"], "BYTE_INTEGRITY_PASS_UNAUTHENTICATED")
            self.assertEqual(len(res["missing"]), 0)
            self.assertEqual(len(res["extra"]), 0)
            self.assertEqual(len(res["changed"]), 0)


if __name__ == "__main__":
    unittest.main()
