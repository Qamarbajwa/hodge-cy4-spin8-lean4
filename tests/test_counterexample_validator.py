"""Unit tests for Counterexample Validator and Clay Compliance Auditor."""

import unittest
from toolkit.counterexample_validator import CounterexampleValidator


class TestCounterexampleValidator(unittest.TestCase):
    def setUp(self):
        self.validator1 = CounterexampleValidator(d=1)
        self.validator3 = CounterexampleValidator(d=3)

    def test_full_chain_audit(self):
        for val in [self.validator1, self.validator3]:
            audit = val.run_full_chain_audit()

            # Verify all 5 structural pillars
            self.assertEqual(audit["pillar_1_divisor_orthogonality"]["status"], "CONFIRMED")
            self.assertEqual(audit["pillar_2_deformation_obstruction"]["status"], "CONFIRMED")
            self.assertEqual(audit["pillar_3_kummer_contraction"]["status"], "CONFIRMED")
            self.assertEqual(audit["pillar_4_albanese_clash"]["status"], "CONFIRMED")
            self.assertEqual(audit["pillar_5_normal_function_and_singular_sieve"]["status"], "CONFIRMED")

            # Verify all pillars certified flag
            self.assertTrue(audit["all_five_pillars_certified"])

            # Verify Clay Compliance
            clay = audit["clay_compliance"]
            self.assertTrue(clay["is_smooth_manifold"])
            self.assertTrue(clay["is_projective_variety"])
            self.assertTrue(clay["base_field_is_complex_C"])
            self.assertTrue(clay["coefficients_are_rational_Q"])
            self.assertTrue(clay["target_is_hodge_class"])
            self.assertEqual(clay["codimension"], 2)
            self.assertEqual(clay["dimension"], 4)
            self.assertTrue(clay["fully_compliant_with_clay_statement"])

            # Verify cryptographic audit seal
            self.assertIn("audit_sha256_seal", audit)
            self.assertEqual(len(audit["audit_sha256_seal"]), 64)


if __name__ == "__main__":
    unittest.main()
