"""Real Lean 4 toolchain probe suite.

Demonstrates:
1. Probe 1 (Elementary Positive): step1 proves `n + 0 = n` using `propext`.
2. Probe 2 (False Statement): `n = n + 1` cannot be closed by `simp` (compilation failure).
3. Probe 3 (Sorry Rejection): `sorry` triggers linter warning and sorryAx rejection.
4. Probe 4 (Custom Axiom Rejection): unwhitelisted axiom triggers `DISALLOWED_AXIOMS`.

NOTE: These are demonstration probes verifying toolchain integrity and gate enforcement;
they are NOT proofs of Riemann Hypothesis or Hodge Conjecture claims.
"""

import hashlib
import os
import tempfile
import unittest
from pathlib import Path

from toolkit.governance.lean_step_runner import check_step as check_lean_step


class TestLeanProbes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lean_project_root = Path("examples/math_gov/LeanDemoProject").resolve()
        cls.lean_source_file = "ProofSteps.lean"
        cls.lean_full_path = cls.lean_project_root / cls.lean_source_file

    def test_probe_1_elementary_positive(self):
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
        self.assertEqual(res["returncode"], 0)

    def test_probe_2_false_statement_compilation_failure(self):
        with tempfile.NamedTemporaryFile(suffix=".lean", delete=False, dir=self.lean_project_root) as tf:
            temp_path = Path(tf.name)
            temp_path.write_text(
                "namespace MathGov\n\ntheorem false_thm (n : Nat) : n = n + 1 := by\n  simp\n\nend MathGov\n",
                encoding="utf-8",
            )

        src_sha = hashlib.sha256(temp_path.read_bytes()).hexdigest()
        try:
            res = check_lean_step(
                project_root=str(self.lean_project_root),
                relative_source=temp_path.name,
                theorem="MathGov.false_thm",
                expected_statement="forall (n : Nat), n = n + 1",
                expected_file_sha256=src_sha,
                timeout=120,
            )
            self.assertEqual(res["verdict"], "LEAN_COMPILATION_OR_WARNING")
            self.assertFalse(res["lean_kernel_check_passed"])
            self.assertEqual(res["returncode"], 1)
        finally:
            if temp_path.exists():
                temp_path.unlink()

    def test_probe_3_sorry_rejection(self):
        with tempfile.NamedTemporaryFile(suffix=".lean", delete=False, dir=self.lean_project_root) as tf:
            temp_path = Path(tf.name)
            temp_path.write_text(
                "namespace MathGov\n\ntheorem sorry_thm (n : Nat) : n = 0 := by\n  sorry\n\nend MathGov\n",
                encoding="utf-8",
            )

        src_sha = hashlib.sha256(temp_path.read_bytes()).hexdigest()
        try:
            res = check_lean_step(
                project_root=str(self.lean_project_root),
                relative_source=temp_path.name,
                theorem="MathGov.sorry_thm",
                expected_statement="forall (n : Nat), n = 0",
                expected_file_sha256=src_sha,
                timeout=120,
            )
            self.assertEqual(res["verdict"], "LEAN_COMPILATION_OR_WARNING")
            self.assertFalse(res["lean_kernel_check_passed"])
        finally:
            if temp_path.exists():
                temp_path.unlink()

    def test_probe_4_custom_disallowed_axiom_rejection(self):
        with tempfile.NamedTemporaryFile(suffix=".lean", delete=False, dir=self.lean_project_root) as tf:
            temp_path = Path(tf.name)
            temp_path.write_text(
                "namespace MathGov\naxiom CustomAxiom : False\ntheorem custom_thm (n : Nat) : n = 0 := False.elim CustomAxiom\nend MathGov\n",
                encoding="utf-8",
            )

        src_sha = hashlib.sha256(temp_path.read_bytes()).hexdigest()
        try:
            res = check_lean_step(
                project_root=str(self.lean_project_root),
                relative_source=temp_path.name,
                theorem="MathGov.custom_thm",
                expected_statement="forall (n : Nat), n = 0",
                expected_file_sha256=src_sha,
                timeout=120,
            )
            self.assertEqual(res["verdict"], "DISALLOWED_AXIOMS")
            self.assertFalse(res["lean_kernel_check_passed"])
            self.assertIn("MathGov.CustomAxiom", res["disallowed_axioms"])
        finally:
            if temp_path.exists():
                temp_path.unlink()


if __name__ == "__main__":
    unittest.main()
