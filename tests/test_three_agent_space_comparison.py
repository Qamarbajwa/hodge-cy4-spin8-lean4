"""Unit tests for Three-Agent Space Comparison Engine."""

import unittest
import numpy as np
from toolkit.three_agent_space_comparison import (
    ExactAbelianFourfoldCohomology,
    ExactLocalizationSequence,
    ClassesAuditor,
)


class TestThreeAgentSpaceComparison(unittest.TestCase):
    def setUp(self):
        self.geom = ExactAbelianFourfoldCohomology()
        self.loc = ExactLocalizationSequence(num_components=4, dim_ambient_H4=70)

    def test_betti_numbers(self):
        b = self.geom.betti_numbers()
        self.assertEqual(b[0], 1)
        self.assertEqual(b[1], 8)
        self.assertEqual(b[2], 28)
        self.assertEqual(b[3], 56)
        self.assertEqual(b[4], 70)
        self.assertEqual(b[5], 56)
        self.assertEqual(b[6], 28)
        self.assertEqual(b[7], 8)
        self.assertEqual(b[8], 1)
        self.assertEqual(sum(b.values()), 256)  # 2^8 = 256

    def test_hodge_numbers_H4(self):
        h = self.geom.hodge_numbers_H4()
        self.assertEqual(h["h^4,0"], 1)
        self.assertEqual(h["h^3,1"], 16)
        self.assertEqual(h["h^2,2"], 36)
        self.assertEqual(h["h^1,3"], 16)
        self.assertEqual(h["h^0,4"], 1)
        self.assertEqual(sum(h.values()), 70)

    def test_su22_decomposition(self):
        rep = self.geom.su22_h4_decomposition()
        self.assertEqual(rep["dim_polarization_span"], 1)
        self.assertEqual(rep["dim_primitive_weil_W0"], 2)
        self.assertEqual(rep["dim_h22_transcendental"], 33)
        self.assertEqual(rep["total_h4_dimension"], 70)
        self.assertEqual(
            rep["dim_polarization_span"] + rep["dim_primitive_weil_W0"] + rep["dim_h22_transcendental"],
            36,  # h^{2,2}
        )

    def test_localization_exactness(self):
        # 1. Exactness at H^0(S): im(Res) == ker(i_*) and i_* o Res == 0
        res_h0 = self.loc.verify_exactness_at_H0()
        self.assertTrue(res_h0["i_star_circ_Res_is_zero"])
        self.assertTrue(res_h0["im_Res_equals_ker_i_star"])
        self.assertEqual(res_h0["rank_Res"], res_h0["nullity_i_star"])

        # 2. Exactness at H^4(A): im(i_*) == ker(j^*) and j^* o i_* == 0
        res_h4 = self.loc.verify_exactness_at_H4()
        self.assertTrue(res_h4["j_star_circ_i_star_is_zero"])
        self.assertTrue(res_h4["im_i_star_equals_ker_j_star"])
        self.assertEqual(res_h4["rank_i_star"], res_h4["nullity_j_star"])

    def test_class_support_negative_space_vanishing(self):
        # Create an algebraic class inside im(i_*)
        # Basis vector e_0 is in im(i_*)
        supported_vec = np.zeros(70, dtype=int)
        supported_vec[0] = 1
        self.assertTrue(self.loc.test_class_support(supported_vec))

        # Create a class outside im(i_*), e.g. e_10
        unsupported_vec = np.zeros(70, dtype=int)
        unsupported_vec[10] = 1
        self.assertFalse(self.loc.test_class_support(unsupported_vec))

    def test_classes_auditor(self):
        for audit_fn in [
            ClassesAuditor.audit_class_1_singular,
            ClassesAuditor.audit_class_2_non_reduced,
            ClassesAuditor.audit_class_3_derived,
            ClassesAuditor.audit_class_4_ominimal,
            ClassesAuditor.audit_class_5_calibrated_currents,
        ]:
            res = audit_fn()
            self.assertFalse(res["produces_new_cohomology_shadow"])
            self.assertEqual(res["status"], "CONFINED_TO_CHOW_RING")


if __name__ == "__main__":
    unittest.main()
