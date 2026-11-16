"""Adversarial Unit & Integration Tests for Erdős–Fourier Incidence & Residual Shadow Engine.

Validates:
1. Exact Combinatorial IVHS Rank Identity Check across R^{12}(F) (matching 426x426 matrix rank).
2. Exact Fourier Pairing Dimension Audit (1,001 2-Plane pairable + 750 Residual = 1,751).
3. Shioda Inductive 3-Plus-3 Split Audit (1,001 Planes + 630 Inductive + 120 Indecomposable = 1,751).
4. Erdős K_{2,2} Spinor Graph Audit (exactly 6 out of 70 tuples in \\bigwedge^4 S^+_8, 0 false positives).
5. Wirtinger Unit-Metric Calibration and Signed Unit-Balance Law.
"""

import unittest
from fractions import Fraction
from toolkit.erdos_fourier_incidence_engine import (
    WirtingerUnitCalibrator,
    SpinorErdosFourierEngine,
    JacobianSaturationCensus,
    FourierShadowDetector,
    ErdosFourierIncidenceEngine,
)
from toolkit.calabi_yau_jacobian_engine import CalabiYauJacobianEngine
from toolkit.exact_linalg import exact_matrix_rank


class TestErdosFourierIncidenceEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = ErdosFourierIncidenceEngine()
        cls.cy_engine = CalabiYauJacobianEngine()
        cls.m6 = cls.cy_engine.generate_monomial_basis(6)
        cls.m18 = cls.cy_engine.generate_monomial_basis(18)

    # --------------------------------------------------------------------------
    # CHECK 1: EXACT COMBINATORIAL IVHS RANK IDENTITY
    # --------------------------------------------------------------------------
    def test_01_combinatorial_ivhs_rank_vs_exact_matrix_rank(self):
        """Verifies combinatorial rank formula |{b in R^6 : b <= 4 - a}| == exact matrix rank of M_{x^a}."""
        census = self.engine.census
        census_data = census.partition_census()
        self.assertEqual(census_data["total_partitions"], 18)
        self.assertEqual(census_data["total_monomials"], 1751)

        # Check global minimum on 2-plane monomial (4, 4, 4, 0, 0, 0)
        plane_mono = (4, 4, 4, 0, 0, 0)
        c_rk_plane = census.combinatorial_ivhs_rank(plane_mono)
        self.assertEqual(c_rk_plane, 19)
        mat_plane = self.cy_engine.build_ivhs_multiplication_matrix({plane_mono: 1}, self.m6, self.m18)
        m_rk_plane = exact_matrix_rank(mat_plane)
        self.assertEqual(m_rk_plane, 19)
        self.assertEqual(426 - m_rk_plane, 407)

        # Check global maximum on center monomial (2, 2, 2, 2, 2, 2)
        center_mono = (2, 2, 2, 2, 2, 2)
        c_rk_center = census.combinatorial_ivhs_rank(center_mono)
        self.assertEqual(c_rk_center, 141)
        mat_center = self.cy_engine.build_ivhs_multiplication_matrix({center_mono: 1}, self.m6, self.m18)
        m_rk_center = exact_matrix_rank(mat_center)
        self.assertEqual(m_rk_center, 141)
        self.assertEqual(426 - m_rk_center, 285)

        # Audit representative for all 18 partitions
        for record in census_data["partitions"]:
            part = record["partition"]
            expected_rk = record["ivhs_rank"]
            comb_rk = census.combinatorial_ivhs_rank(part)
            self.assertEqual(comb_rk, expected_rk)

            # Test actual matrix rank over Q
            mat = self.cy_engine.build_ivhs_multiplication_matrix({part: 1}, self.m6, self.m18)
            mat_rk = exact_matrix_rank(mat)
            self.assertEqual(mat_rk, expected_rk, f"Matrix rank mismatch on partition {part}")

    # --------------------------------------------------------------------------
    # CHECK 2: EXACT FOURIER PAIRING DIMENSION AUDIT
    # --------------------------------------------------------------------------
    def test_02_exact_fourier_pairing_dimension_audit(self):
        """Verifies exhaustive 15-matching test partitioning R^{12} into 2-Plane Fourier Space and Residual."""
        detector = self.engine.detector
        self.assertEqual(len(detector.matchings_15), 15)

        decomp = detector.full_three_band_decomposition()
        dim_planes = decomp["dim_fourier_planes_2_2_2"]
        dim_residual = decomp["dim_residual_shadow_space"]

        self.assertEqual(dim_planes, 1001)
        self.assertEqual(dim_residual, 750)
        self.assertEqual(dim_planes + dim_residual, 1751)
        self.assertTrue(decomp["exact_sum_check"])

    # --------------------------------------------------------------------------
    # CHECK 3: SHIODA INDUCTIVE 3-PLUS-3 SPLIT AUDIT
    # --------------------------------------------------------------------------
    def test_03_shioda_inductive_3_plus_3_split_audit(self):
        """Audits the decomposition 1751 = 1001 (Planes) + 630 (Inductive) + 120 (Indecomposable)."""
        detector = self.engine.detector
        self.assertEqual(len(detector.triplets_10), 10)

        # Test Shioda Galois Norm Criterion on all 1751 modes
        galois_res = detector.verify_shioda_galois_criterion()
        self.assertTrue(galois_res["all_modes_are_rational_hodge"])
        self.assertEqual(galois_res["modes_satisfying_galois_norm_18"], 1751)

        decomp = detector.full_three_band_decomposition()
        dim_planes = decomp["dim_fourier_planes_2_2_2"]
        dim_inductive = decomp["dim_inductive_cones_3_3"]
        dim_indecomp = decomp["dim_indecomposable"]

        self.assertEqual(dim_planes, 1001)
        self.assertEqual(dim_inductive, 630)
        self.assertEqual(dim_indecomp, 120)
        self.assertEqual(dim_planes + dim_inductive + dim_indecomp, 1751)

        # Check exact partitions in Indecomposable band (should be exactly (4,2,2,2,1,1) [60] and (3,3,2,2,2,0) [60])
        indecomp_parts = {item["partition"]: item["multiplicity"] for item in decomp["band_partitions"]["INDECOMPOSABLE"]}
        self.assertEqual(indecomp_parts, {(4, 2, 2, 2, 1, 1): 60, (3, 3, 2, 2, 2, 0): 60})

    # --------------------------------------------------------------------------
    # CHECK 4: ERDŐS K_{2,2} SPINOR GRAPH AUDIT
    # --------------------------------------------------------------------------
    def test_04_erdos_k22_spinor_graph_audit(self):
        """Confirms 6/70 tuples in \\bigwedge^4 S^+_8 have K_{2,2} profile and 0/64 remaining have it."""
        spinor = self.engine.spinor_engine
        census = spinor.erdos_distance_graph_census()
        self.assertEqual(census["num_vertices"], 8)
        self.assertEqual(census["total_edges"], 28)
        self.assertEqual(census["root_unit_edges_D2"], 24)
        self.assertEqual(census["antipodal_diameter_edges_D4"], 4)

        audit = spinor.audit_wedge4_tuples()
        self.assertEqual(audit["total_wedge4_tuples"], 70)
        self.assertEqual(audit["zero_weight_tuples_count"], 6)
        self.assertEqual(audit["k22_induced_subgraph_tuples_count"], 6)
        self.assertEqual(audit["odd_fourier_vanishing_tuples_count"], 6)
        self.assertTrue(audit["is_exact_k22_equivalence"])

        # Walsh-Hadamard Transform of S+_8 indicator function
        wht = spinor.walsh_hadamard_transform_indicator()
        self.assertEqual(wht[()], 8)
        self.assertEqual(wht[(0, 1, 2, 3)], 8)
        # All other 14 characters must be identically zero
        for k, v in wht.items():
            if k not in ((), (0, 1, 2, 3)):
                self.assertEqual(v, 0)

    # --------------------------------------------------------------------------
    # CHECK 5: WIRTINGER CALIBRATION & SIGNED UNIT-BALANCE
    # --------------------------------------------------------------------------
    def test_05_wirtinger_calibration_and_signed_unit_balance(self):
        """Verifies Wirtinger unit-volume calibration and Signed Unit-Balance Law."""
        calib = self.engine.calibrator
        self.assertEqual(calib.unit_ambient_volume, Fraction(1, 1))

        # Surface of degree 12 has calibrated unit volume 6
        res = calib.calibrate_surface_degree(12)
        self.assertEqual(res["calibrated_unit_volume"], Fraction(6, 1))
        self.assertTrue(res["is_effective_positive"])

        # Signed Unit-Balance Law: w = [Z_+] - [Z_-] has <w, Theta^2> = 0 iff Vol(Z_+) == Vol(Z_-)
        bal_true = calib.verify_signed_unit_balance(24, 24)
        self.assertTrue(bal_true["is_unit_balanced"])
        self.assertEqual(bal_true["net_volume_difference"], 0)

        bal_false = calib.verify_signed_unit_balance(24, 18)
        self.assertFalse(bal_false["is_unit_balanced"])
        self.assertNotEqual(bal_false["net_volume_difference"], 0)

    # --------------------------------------------------------------------------
    # CHECK 6: 2+4 SHIODA-LEFSCHETZ COMPLETE CLOSURE AUDIT (0/1751 UNEXPLAINED)
    # --------------------------------------------------------------------------
    def test_06_shioda_lefschetz_2_plus_4_complete_closure_audit(self):
        """Audits the 4-band split 1001 + 630 + 120 + 0 = 1751 on Fermat X^4_6 via Lefschetz (1,1)."""
        detector = self.engine.detector
        self.assertEqual(len(detector.pairs_15), 15)

        decomp = detector.full_four_band_decomposition()
        self.assertEqual(decomp["dim_fourier_planes_2_2_2"], 1001)
        self.assertEqual(decomp["dim_inductive_cones_3_3"], 630)
        self.assertEqual(decomp["dim_inductive_2_plus_4_lefschetz"], 120)
        self.assertEqual(decomp["truly_indecomposable_count"], 0)
        self.assertTrue(decomp["exact_four_band_closure"])
        self.assertEqual(
            decomp["dim_fourier_planes_2_2_2"]
            + decomp["dim_inductive_cones_3_3"]
            + decomp["dim_inductive_2_plus_4_lefschetz"]
            + decomp["truly_indecomposable_count"],
            1751,
        )

        # Verify Band-3 partitions explicitly map into INDUCTIVE_2_PLUS_4_LEFSCHETZ and TRULY_INDECOMPOSABLE is empty
        self.assertEqual(decomp["band_partitions"]["TRULY_INDECOMPOSABLE"], [])
        band3_parts = {
            item["partition"]: item["multiplicity"]
            for item in decomp["band_partitions"]["INDUCTIVE_2_PLUS_4_LEFSCHETZ"]
        }
        self.assertEqual(band3_parts, {(4, 2, 2, 2, 1, 1): 60, (3, 3, 2, 2, 2, 0): 60})

        # Verify surface origin R^8(F_{P^3}) ~ H^{1,1}_{prim}(X^2_6)
        surf = detector.verify_band3_surface_lefschetz_origin()
        self.assertEqual(surf["band3_count"], 120)
        self.assertEqual(surf["witness_pair"], (2, 2))
        self.assertEqual(surf["surface_jacobian_degree"], 8)
        self.assertEqual(surf["dim_H11_prim_X2_6"], 85)
        self.assertTrue(surf["all_in_H11_prim_X2_6"])
        self.assertTrue(surf["lefschetz_1_1_algebraic"])
        self.assertEqual(surf["fermat_unexplained_modes"], 0)


if __name__ == "__main__":
    unittest.main()
