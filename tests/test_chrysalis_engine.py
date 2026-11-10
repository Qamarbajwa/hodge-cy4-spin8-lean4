"""Unit tests for the complete Google Cloud Project Chrysalis Engine."""

import unittest
from toolkit.chrysalis_engine import ChrysalisAutonomousLab, RuntimeToolSynthesizer


class TestChrysalisEngine(unittest.TestCase):
    def test_runtime_tool_synthesis_and_execution(self):
        synthesizer = RuntimeToolSynthesizer("test_author")
        code = """
def test_calc(a, b):
    return a * b + 42
"""
        ok, seal, msg = synthesizer.synthesize_tool("calc_tool", code)
        self.assertTrue(ok)
        self.assertIsNotNone(seal)

        exec_ok, res, exec_msg = synthesizer.execute_tool(code, seal, "test_calc", 3, 4)
        self.assertTrue(exec_ok)
        self.assertEqual(res, 54)

    def test_runtime_tool_tampering_blocked(self):
        synthesizer = RuntimeToolSynthesizer("test_author")
        code = "def f(): return 1"
        ok, seal, _ = synthesizer.synthesize_tool("t", code)
        self.assertTrue(ok)

        # Tamper with code
        tampered = "def f(): return 2"
        exec_ok, _, err = synthesizer.execute_tool(tampered, seal, "f")
        self.assertFalse(exec_ok)
        self.assertIn("BINARY_AUTHORIZATION_FAILED", err)

    def test_chrysalis_cycle_k3_surface(self):
        lab = ChrysalisAutonomousLab()
        result = lab.run_hodge_moduli_cycle(
            dimension_n=2,
            degree_d=4,
            family_name="K3 Surface Family",
            target_codim=1,
        )
        self.assertEqual(result["status"], "CHRYALIS_CYCLE_SUCCESSFUL")
        self.assertTrue(result["boundary_cycles_algebraic"])
        self.assertEqual(len(lab.receipts), 5)

    def test_chrysalis_cycle_cubic_fourfold(self):
        lab = ChrysalisAutonomousLab()
        result = lab.run_hodge_moduli_cycle(
            dimension_n=4,
            degree_d=3,
            family_name="Cubic Fourfold Family",
            target_codim=2,
        )
        self.assertEqual(result["status"], "CHRYALIS_CYCLE_SUCCESSFUL")
        self.assertTrue(result["boundary_cycles_algebraic"])
        self.assertEqual(len(lab.receipts), 5)

    def test_chrysalis_normal_function_audit(self):
        lab = ChrysalisAutonomousLab(dual_custody_token="LEAD_RESEARCHER_DUAL_CUSTODY_APPROVAL_TOKEN_2026")
        result = lab.run_normal_function_audit(field_d=1)
        self.assertEqual(result["status"], "CHRYSALIS_NORMAL_FUNCTION_AUDIT_SUCCESSFUL")
        self.assertEqual(result["ivhs_rank"], 4)
        self.assertEqual(result["dim_chow_image"], 1)
        self.assertEqual(result["primitive_weil_cycles"], 0)
        self.assertIn("signed_invariant_sha256", result)
        self.assertEqual(len(lab.receipts), 5)


if __name__ == "__main__":
    unittest.main()
