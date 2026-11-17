"""Reviewer Audit Suite for Kuga-Satake & D_4 Triality Clifford Engine (Attacking Bridge B).

Verifies:
  1. Exact Clifford Algebra Grading C(V_8) = C^+(V_8) + C^-(V_8) (128 + 128 = 256)
     and Chevalley spinor decomposition End(S^+_8) (+) End(S^-_8) = 64 + 64 = 128.
  2. Exhaustive 32 / 512 zero-weight D_4 triality triples in V_8 x S^+_8 x S^-_8
     with (4, 4, 4)-regularity and Out(D_4) ~= S_3 triality symmetry.
  3. Self-dual / anti-self-dual branching wedge^4 S^+_8 = 35_+ (+) 35_- = 70
     matching Sym^2_0(V_8) = 36 - 1 = 35 and Cartan 3 + 3 = 6 zero-weight split.
  4. Adversarial Bridge B review: ABSOLUTE_HODGE_AND_MOTIVATED_VERIFIED = True,
     while naive promotion to ALGEBRAIC_CYCLE_PROVED / CLOSED_VERIFIED is rejected.
  5. Zero forbidden float constructs & 20/20 zero-axiom Lean 4.35.0 theorems.
"""

import unittest
from pathlib import Path

from toolkit.hodge_proof_closure_reviewer import HodgeProofClosureReviewer, LEAN_THEOREM_SPECS
from toolkit.integrity import scan_forbidden
from toolkit.kuga_satake_clifford_engine import KugaSatakeCliffordEngine


class TestKugaSatakeCliffordEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parent.parent
        cls.engine = KugaSatakeCliffordEngine()
        cls.audit = cls.engine.run_full_audit()
        cls.reviewer = HodgeProofClosureReviewer(repo_root=cls.root)

    def test_01_clifford_algebra_grading_and_chevalley_decomposition(self):
        """Verifies C^+(V_8) = 128, C^-(V_8) = 128, total = 256, and End(S^+_8)+End(S^-_8) = 64+64."""
        gr = self.audit["clifford_exterior_grading"]
        ch = self.audit["chevalley_spinor_decomposition"]

        self.assertTrue(gr["grading_verified"])
        self.assertEqual(gr["even_grades"], {0: 1, 2: 28, 4: 70, 6: 28, 8: 1})
        self.assertEqual(gr["odd_grades"], {1: 8, 3: 56, 5: 56, 7: 8})
        self.assertEqual(gr["dim_C_plus"], 128)
        self.assertEqual(gr["dim_C_minus"], 128)
        self.assertEqual(gr["total_clifford_dim"], 256)

        self.assertTrue(ch["chevalley_isomorphism_verified"])
        self.assertEqual(ch["dim_End_S_plus"], 64)
        self.assertEqual(ch["dim_End_S_minus"], 64)
        self.assertEqual(ch["dim_C_plus_chevalley"], 128)
        self.assertEqual(ch["dim_C_minus_chevalley"], 128)
        self.assertEqual(ch["dim_so8_bivectors_wedge2_V8"], 28)

    def test_02_d4_triality_32_zero_weight_incidence_triples(self):
        """Verifies 32/512 zero-weight triples, (4,4,4)-regularity, and Out(D_4) S_3 symmetry."""
        tr = self.audit["triality_32_incidence_triples"]

        self.assertEqual(tr["total_triples_evaluated"], 512)
        self.assertEqual(tr["zero_weight_triples_count"], 32)
        self.assertEqual(tr["degree_v8_per_weight"], [4])
        self.assertEqual(tr["degree_s_plus_per_weight"], [4])
        self.assertEqual(tr["degree_s_minus_per_weight"], [4])
        self.assertTrue(tr["is_4_4_4_biregular_hypergraph"])
        self.assertTrue(tr["out_d4_triality_cycle_preserves_32_triples"])

    def test_03_wedge4_branching_and_cartan_3_plus_3_split(self):
        """Verifies wedge^4 S^+_8 = 35_+ (+) 35_- = 70, Sym^2_0(V_8) = 35, and Cartan 3 + 3 = 6."""
        br = self.audit["wedge4_self_dual_branching"]

        self.assertTrue(br["branching_isomorphism_verified"])
        self.assertEqual(br["dim_wedge4_S_plus"], 70)
        self.assertEqual(br["dim_self_dual_35_plus"], 35)
        self.assertEqual(br["dim_anti_self_dual_35_minus"], 35)
        self.assertEqual(br["dim_sym2_V8"], 36)
        self.assertEqual(br["dim_sym2_0_V8"], 35)
        self.assertEqual(br["dim_sym2_0_S_minus"], 35)
        self.assertEqual(br["cartan_zero_weight_total"], 6)
        self.assertEqual(br["cartan_zero_weight_35_plus"], 3)
        self.assertEqual(br["cartan_zero_weight_35_minus"], 3)
        self.assertEqual(br["cartan_zero_weight_sym2_0_V8"], 3)
        self.assertEqual(len(br["cartan_zero_weight_pairs"]), 3)

    def test_04_adversarial_bridge_b_kuga_satake_boundary(self):
        """Verifies Absolute Hodge & Motivated = True while rejecting ALGEBRAIC_CYCLE_PROVED on Bridge B."""
        boundary = self.audit["kuga_satake_bridge_b_audit"]
        self.assertTrue(boundary["deligne_1982_absolute_hodge_verified"])
        self.assertTrue(boundary["andre_1996_motivated_cycle_verified"])
        self.assertTrue(boundary["ABSOLUTE_HODGE_AND_MOTIVATED_VERIFIED"])
        self.assertFalse(boundary["kuga_satake_algebraic_cycle_proved"])
        self.assertEqual(boundary["bridge_b_status"], "ADVERSARIALLY_BLOCKED_OPEN_BRIDGE")

        decision = self.reviewer.attempt_bridge_promotion(
            "S-BRIDGE-SPINOR-MOTIVE",
            "ALGEBRAIC_CYCLE_PROVED",
            (
                "Since C^+(V_8) = 128, 32 triality triples match V_8 x S^+_8 x S^-_8, and "
                "wedge^4 S^+_8 = 35_+ + 35_- lifts to Sym^2_0(V_8), Deligne (1982) and Andre (1996) "
                "yield an algebraic cycle in CH^*(X_K3 x A_spin)_Q for End_Q(A)=Q."
            ),
        )
        self.assertFalse(decision["accepted"])
        self.assertEqual(decision["verdict"], "REJECTED_BY_ADVERSARIAL_REVIEWER")
        self.assertEqual(decision["resulting_status"], "ADVERSARIALLY_BLOCKED_OPEN_BRIDGE")

        ev = decision["audit_evidence"]
        self.assertEqual(ev["clifford_even_dim"], 128)
        self.assertEqual(ev["triality_zero_triples_count"], 32)
        self.assertEqual(ev["cartan_zero_weight_branching_split"], [3, 3])
        self.assertTrue(ev["ABSOLUTE_HODGE_AND_MOTIVATED_VERIFIED"])
        self.assertFalse(ev["kuga_satake_algebraic_cycle_proved"])
        self.assertTrue(any("Kuga-Satake Algebraicity Conjecture" in r for r in decision["blocking_reasons"]))

    def test_05_twenty_zero_axiom_lean4_theorems_and_zero_floats(self):
        """Verifies zero floats in kuga_satake_clifford_engine.py and 20/20 zero-axiom Lean 4 proofs."""
        hits = scan_forbidden(str(self.root / "toolkit" / "kuga_satake_clifford_engine.py"))
        self.assertEqual(hits, [])

        lean_audit = self.reviewer.verify_lean_blueprint(fast=True)
        self.assertTrue(lean_audit["zero_cheating_clean"])
        self.assertTrue(lean_audit["all_axioms_empty"])
        self.assertGreaterEqual(lean_audit["theorems_verified_count"], 20)
        self.assertGreaterEqual(len(LEAN_THEOREM_SPECS), 20)
        self.assertEqual(lean_audit["axioms_by_theorem"]["clifford_even_dim_eq"], [])
        self.assertEqual(lean_audit["axioms_by_theorem"]["d4_triality_zero_triples_len"], [])


if __name__ == "__main__":
    unittest.main()
