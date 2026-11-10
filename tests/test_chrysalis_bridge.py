"""Tests for Google Cloud Project Chrysalis Bridge integration."""

import unittest
from toolkit.chrysalis_bridge import (
    ModelArmor,
    BinaryAuthorization,
    PolicyAsCodeValidator,
    ChrysalisRuntimeHost,
)


class TestProjectChrysalisBridge(unittest.TestCase):
    def setUp(self):
        self.host = ChrysalisRuntimeHost()

    def test_model_armor_clean(self):
        ok, msg = ModelArmor.screen_text("Studying Hodge cycles on Fermat varieties with rational coefficients.")
        self.assertTrue(ok)
        self.assertEqual(msg, "PASSED")

    def test_model_armor_flagged(self):
        ok, msg = ModelArmor.screen_text("The Hodge conjecture is trivially proved by linear algebra.")
        self.assertFalse(ok)
        self.assertIn("ModelArmor Flag", msg)

    def test_binary_authorization_signature(self):
        code = "def compute_picard(): return 20"
        seal = BinaryAuthorization.sign_code(code, author_id="agent_worker_01")
        self.assertTrue(BinaryAuthorization.verify_code(code, seal))
        # Tampered code fails verification
        tampered = "def compute_picard(): return 21"
        self.assertFalse(BinaryAuthorization.verify_code(tampered, seal))

    def test_policy_as_code_rejections(self):
        # 1. Reject integral coefficients (Atiyah-Hirzebruch trap)
        proposal_integral = {
            "coefficients": "Z",
            "space": {"is_projective": True},
            "codimension": 2,
        }
        allowed, denials = PolicyAsCodeValidator.evaluate(proposal_integral)
        self.assertFalse(allowed)
        self.assertTrue(any("Gate 1" in d for d in denials))

        # 2. Reject non-projective Kähler (Voisin trap)
        proposal_kahler = {
            "coefficients": "Q",
            "space": {"is_projective": False},
            "codimension": 2,
        }
        allowed, denials = PolicyAsCodeValidator.evaluate(proposal_kahler)
        self.assertFalse(allowed)
        self.assertTrue(any("Gate 2" in d for d in denials))

        # 3. Reject vector-bundle only span for codim >= 2
        proposal_vb = {
            "coefficients": "Q",
            "space": {"is_projective": True},
            "codimension": 2,
            "construction": {"relies_only_on_vector_bundles": True},
        }
        allowed, denials = PolicyAsCodeValidator.evaluate(proposal_vb)
        self.assertFalse(allowed)
        self.assertTrue(any("Gate 3" in d for d in denials))

        # 4. Reject unapproved self-promotion to PROVED
        proposal_unapproved = {
            "coefficients": "Q",
            "space": {"is_projective": True},
            "codimension": 2,
            "promoted_status": "PROVED",
            "dual_custody_approved": False,
        }
        allowed, denials = PolicyAsCodeValidator.evaluate(proposal_unapproved)
        self.assertFalse(allowed)
        self.assertTrue(any("Chrysalis Gate 4" in d for d in denials))

    def test_valid_proposal_passes_all_gates(self):
        valid_proposal = {
            "description": "Constructing algebraic 2-cycles on Fermat cubic fourfold using linear planes.",
            "coefficients": "Q",
            "space": {"is_projective": True},
            "codimension": 2,
            "construction": {"relies_only_on_vector_bundles": False},
            "unjustified_assumptions": [],
            "promoted_status": "STAGE_ADVANCED",
            "dual_custody_approved": False,
        }
        res = self.host.audit_claim_proposal(valid_proposal)
        self.assertEqual(res["status"], "ACCEPTED_FOR_STAGE")


if __name__ == "__main__":
    unittest.main()
