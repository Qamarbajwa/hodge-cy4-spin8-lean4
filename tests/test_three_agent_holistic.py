"""Unit tests for the 3-Agent Holistic Investigation Engine."""

import unittest
from toolkit.three_agent_holistic_test import (
    ThreeAgentHolisticHarness,
    AgentPositiveExotic,
    AgentNegativeComplement,
    AgentAmbientHolistic,
)


class TestThreeAgentHolistic(unittest.TestCase):
    def setUp(self):
        self.harness1 = ThreeAgentHolisticHarness(d=1)
        self.harness3 = ThreeAgentHolisticHarness(d=3)

    def test_agent_1_positive_exotic(self):
        agent = AgentPositiveExotic(d=1)
        res = agent.analyze_exotic_patterns()
        self.assertEqual(res["status"], "ANALYSIS_COMPLETE")
        self.assertFalse(res["findings"]["non_reduced_schemes_evade_obstruction"])
        self.assertTrue(res["findings"]["hironaka_resolution_guarantees_smooth_model"])
        self.assertTrue(res["findings"]["all_singular_patterns_reduce_to_smooth_albanese"])
        self.assertTrue(res["findings"]["derived_category_objects_confined"])
        self.assertFalse(res["findings"]["calibrated_currents_are_polynomial_algebraic"])
        self.assertGreaterEqual(res["net_deformation_obstruction"], 12.0)

    def test_agent_2_negative_complement(self):
        agent = AgentNegativeComplement(d=1)
        res = agent.analyze_negative_space_and_residues()
        self.assertEqual(res["status"], "ANALYSIS_COMPLETE")
        self.assertTrue(res["findings"]["poincare_residue_sequence_valid"])
        self.assertEqual(res["findings"]["negative_space_dimension_H3"], 56)
        self.assertFalse(res["findings"]["negative_space_admits_weil_residue"])
        self.assertTrue(res["findings"]["mixed_hodge_weight_compatibility_failed"])
        self.assertAlmostEqual(res["findings"]["negative_space_boundary_tear_norm"], 12.0, places=10)

    def test_agent_3_and_harness_synthesis(self):
        for h in [self.harness1, self.harness3]:
            res = h.run_investigation()
            self.assertTrue(res["tripartite_consensus_reached"])
            self.assertIn("joint_audit_seal", res)
            self.assertEqual(len(res["joint_audit_seal"]), 64)

            amb = res["agent_3_ambient_holistic"]
            self.assertEqual(amb["status"], "CONSENSUS_REACHED")
            self.assertEqual(amb["positive_space_verdict"], "STRICTLY_OBSTRUCTED")
            self.assertEqual(amb["negative_space_verdict"], "STRICTLY_OBSTRUCTED")
            self.assertEqual(amb["exotic_patterns_verdict"], "REDUCED_TO_SMOOTH_BY_HIRONAKA")
            self.assertAlmostEqual(amb["coupled_obstruction_norm"], 12.0, places=5)


if __name__ == "__main__":
    unittest.main()
