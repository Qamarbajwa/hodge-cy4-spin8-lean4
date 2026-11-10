r"""Unit tests for Terence Tao Lean 4 Blueprint & Verifier.

Verifies:
1. Formal Lean 4 compilation (return code 0).
2. Zero cheating policy (0 sorry, 0 admit, 0 axiom).
3. Exact theorem counts across all 4 blueprint nodes.
4. Python moving-plane variation absorbing all 407 tangent vectors (100.0%).
5. Python Cartan zero-weight space vs full so(8) root operator annihilation (ker = 0).
"""

import unittest
from toolkit.lean_blueprint_verifier import LeanBlueprintVerifier
from toolkit.calabi_yau_jacobian_engine import CalabiYauJacobianEngine
from toolkit.mumford_spinor_engine import MumfordSpinorEngine


class TestLeanBlueprint(unittest.TestCase):
    def setUp(self):
        self.verifier = LeanBlueprintVerifier()
        self.cy_engine = CalabiYauJacobianEngine()
        self.mumford_engine = MumfordSpinorEngine()

    def test_lean_blueprint_zero_cheating(self):
        scan = self.verifier.scan_for_forbidden_keywords()
        self.assertTrue(scan["is_clean"], f"Found forbidden keywords: {scan['violations']}")
        self.assertEqual(scan["violations_count"], 0)

    def test_lean_blueprint_compilation(self):
        comp = self.verifier.compile_lean_file()
        self.assertEqual(comp["returncode"], 0, f"Lean compilation failed: {comp['stderr']}")
        self.assertTrue(comp["is_success"])

    def test_lean_blueprint_proved_theorems(self):
        audit = self.verifier.full_audit()
        self.assertTrue(audit["all_passed"])
        self.assertEqual(audit["blueprint_status"], "ALL_PROOFS_STRICTLY_CLOSED_WITHOUT_SORRY")

        theorems = audit["proved_theorems"]
        self.assertGreaterEqual(len(theorems), 13)

        # Check key node theorems
        self.assertIn("exact_chain_im_sub_ker", theorems)
        self.assertIn("weil_w1_orthogonal_to_theta2", theorems)
        self.assertIn("weil_w2_orthogonal_to_theta2", theorems)
        self.assertIn("four_tuples_len", theorems)
        self.assertIn("zero_tuples_len", theorems)
        self.assertIn("h40_prim_eq", theorems)
        self.assertIn("h31_prim_eq", theorems)
        self.assertIn("h22_prim_eq", theorems)
        self.assertIn("h22_total_eq", theorems)
        self.assertIn("b4_total_eq", theorems)
        self.assertIn("milnor_number_eq", theorems)
        self.assertIn("r6_dim_eq", theorems)
        self.assertIn("plane_kernel_dim_eq", theorems)

    def test_python_moving_plane_integrability(self):
        res = self.cy_engine.evaluate_moving_plane_full_integrability()
        self.assertEqual(res["plane_total_kernel_vectors"], 407)
        self.assertEqual(res["plane_obstructed_vectors"], 0)
        self.assertEqual(res["plane_unobstructed_vectors"], 407)
        self.assertEqual(res["plane_integrability_percentage"], 100.0)
        self.assertEqual(res["chain_base_subspace_rank"], 304)
        self.assertEqual(res["chain_augmented_rank"], 305)
        self.assertTrue(res["chain_is_still_obstructed"])

    def test_python_cartan_weight_zero_vs_root_annihilation(self):
        res = self.mumford_engine.cartan_weight_zero_vs_root_annihilation()
        self.assertEqual(res["cartan_zero_weight_dim"], 6)
        self.assertEqual(res["stacked_root_operator_rank"], 6)
        self.assertEqual(res["root_annihilation_kernel_dim"], 0)
        self.assertEqual(res["full_so8_invariants_dim"], 0)
        self.assertFalse(res["is_cartan_zero_weight_annihilated_by_roots"])


if __name__ == "__main__":
    unittest.main()
