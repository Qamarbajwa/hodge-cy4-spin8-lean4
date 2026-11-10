"""Unit tests for Markman Secant Sheaf and Schoen Degeneration Engine."""

import unittest
from toolkit.markman_secant_engine import MarkmanSecantWeilEngine


class TestMarkmanSecantEngine(unittest.TestCase):
    def setUp(self):
        self.engine = MarkmanSecantWeilEngine()

    def test_moonen_zarhin_reduction(self):
        table = self.engine.moonen_zarhin_reduction_table()
        self.assertIn("dim_1_elliptic_curves", table)
        self.assertIn("dim_2_abelian_surfaces", table)
        self.assertIn("dim_3_abelian_threefolds", table)
        self.assertIn("dim_4_abelian_fourfolds", table)

        fourfolds = table["dim_4_abelian_fourfolds"]
        self.assertIn("reduction_theorem", fourfolds)
        self.assertEqual(fourfolds["hodge_conjecture_status"], "RESOLVED_AFFIRMATIVELY_BY_MARKMAN_2025")

    def test_secant_sheaf_properties(self):
        sec = self.engine.secant_sheaf_invariants(rank_r=4)
        self.assertEqual(sec["ambient_variety"], "Abelian threefold Y (dim = 3)")
        self.assertEqual(sec["rank"], 4)
        self.assertEqual(sec["todd_genus_abelian_variety"], 1)
        self.assertEqual(sec["chern_character_degrees"], [0, 1, 2, 3])

    def test_schoen_degeneration_codimensions(self):
        schoen = self.engine.schoen_degeneration_specialization()
        self.assertEqual(schoen["sixfold_weil_class_codimension"], 3)
        self.assertEqual(schoen["fourfold_weil_class_codimension"], 2)
        self.assertEqual(schoen["consequence_for_hodge_conjecture"], "HODGE_CONJECTURE_TRUE_FOR_ALL_ABELIAN_FOURFOLDS")

    def test_resolution_of_internal_bottleneck(self):
        res = self.engine.resolution_of_internal_bottleneck()
        self.assertEqual(res["status"], "PARADOX_RESOLVED_MATHEMATICALLY")
        self.assertIn("NOT a complete intersection", res["external_resolution_mechanism"])


if __name__ == "__main__":
    unittest.main()
