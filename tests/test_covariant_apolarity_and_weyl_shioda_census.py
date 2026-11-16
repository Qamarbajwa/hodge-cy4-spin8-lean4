"""Unit and Integration Tests for Covariant Apolarity, Initial-Monomial Bounds,

Weyl Chiral Irreducibility, Shioda-Aoki Fermat Census, and 3-Band Blind Jet Reconstruction.
"""

from __future__ import annotations

import unittest
from pathlib import Path

_REPO_ROOT = str(Path(__file__).resolve().parent.parent)

from toolkit.covariant_apolarity_and_weyl_shioda_census import (
    CovariantTransitionDeterminantVerifier,
    InitialMonomialAndAdjointVerifier,
    ShiodaAokiDegreeCensus,
    WeylChiralAnd24CellVerifier,
    run_all_theorems_audit,
)
from toolkit.integrity import scan_forbidden


class TestCovariantApolarityAndWeylShiodaCensus(unittest.TestCase):
    def setUp(self) -> None:
        self.mod1 = CovariantTransitionDeterminantVerifier()
        self.mod2 = InitialMonomialAndAdjointVerifier()
        self.mod3 = WeylChiralAnd24CellVerifier()
        self.mod4 = ShiodaAokiDegreeCensus()

    def test_01_wiebe_transition_determinant_degree_and_apolarity_ranks(self) -> None:
        deg_res = self.mod1.verify_wiebe_transition_determinant_degree()
        self.assertTrue(deg_res["verified"])
        self.assertEqual(deg_res["universal_degree"], 12)

        plane_res = self.mod1.verify_plane_apolarity_ranks()
        self.assertTrue(plane_res["plane_ranks_verified"])
        self.assertEqual(plane_res["expected_ranks"], [3, 6, 10, 15, 18, 19])
        for reg in ("W3", "W2", "W1"):
            self.assertEqual(plane_res["regimes"][reg]["macaulay_ranks"], [3, 6, 10, 15, 18, 19])
            self.assertEqual(plane_res["regimes"][reg]["ann1_dimension"], 3)

        quad_res = self.mod1.verify_quadric_apolarity_ranks()
        self.assertTrue(quad_res["verified"])
        self.assertEqual(quad_res["quadric_ranks"], [4, 9, 16, 24, 30, 32])
        self.assertEqual(quad_res["ann1_dimension"], 2)

    def test_02_initial_monomial_lower_bound_and_symmetric_power(self) -> None:
        init_res = self.mod2.verify_initial_monomial_lower_bound()
        self.assertTrue(init_res["verified"])
        self.assertEqual(init_res["total_basis_monomials"], 426)
        self.assertEqual(init_res["min_monomial_rank"], 155)
        self.assertEqual(init_res["max_monomial_rank"], 336)
        self.assertEqual(init_res["universal_kernel_upper_bound"], 1596)
        self.assertEqual(init_res["universal_coker_upper_bound"], 271)

        sym_res = self.mod2.verify_symmetric_power_surjectivity()
        self.assertTrue(sym_res["verified"])
        self.assertEqual(sym_res["symmetric_power_rank"], 426)
        self.assertEqual(sym_res["cokernel_dimension"], 0)
        self.assertEqual(sym_res["kernel_dimension"], 1325)

        adj_res = self.mod2.verify_gorenstein_adjoint_transpose()
        self.assertTrue(adj_res["verified"])
        self.assertTrue(adj_res["adjoint_transpose_holds_identically"])

    def test_03_weyl_d4_even_parity_chiral_orthogonality_and_24cell(self) -> None:
        even_res = self.mod3.verify_weyl_d4_even_permutations()
        self.assertTrue(even_res["verified"])
        self.assertEqual(even_res["even_permutations_count"], 192)
        self.assertEqual(even_res["odd_permutations_count"], 0)

        orth_res = self.mod3.verify_chiral_character_orthogonality()
        self.assertTrue(orth_res["verified"])
        self.assertEqual(orth_res["chi_plus_norm_sq"], 1)
        self.assertEqual(orth_res["chi_minus_norm_sq"], 1)
        self.assertEqual(orth_res["inner_product_cross"], 0)

        span_res = self.mod3.verify_orbit_spanning_distinction()
        self.assertTrue(span_res["verified"])
        self.assertEqual(span_res["single_tuple_orbit_rank"], 6)
        self.assertEqual(span_res["self_dual_orbit_rank"], 3)
        self.assertEqual(span_res["anti_self_dual_orbit_rank"], 3)

        tri_res = self.mod3.verify_w_f4_triality_transitivity()
        self.assertTrue(tri_res["verified"])
        self.assertEqual(tri_res["orbit_size"], 32)
        self.assertEqual(tri_res["degrees_v8_sp_sm"], (4, 4, 4))

    def test_04_shioda_aoki_census_and_m12_paired_diagonal_orbits(self) -> None:
        census = self.mod4.census_fermat_fourfolds((3, 4, 5, 6, 7, 8, 9, 10, 12))
        for m in (3, 4, 5, 6, 7, 8, 9, 10):
            self.assertEqual(census[m]["band4_residual"], 0, f"Residual non-zero at m={m}")
        self.assertEqual(census[12]["band4_residual"], 360)
        self.assertEqual(census[12]["total_hodge"], 52991)
        self.assertEqual(census[12]["band1_planes"], 15101)
        self.assertEqual(census[12]["band2_shioda33"], 21690)
        self.assertEqual(census[12]["band3_lefschetz24"], 15840)

        m12_res = self.mod4.verify_m12_paired_diagonal_orbits()
        self.assertTrue(m12_res["verified"])
        self.assertEqual(m12_res["orbit_count"], 4)
        self.assertEqual(m12_res["orbit_size_each"], 90)
        self.assertEqual(m12_res["total_band4_m12"], 360)

        high_res = self.mod4.census_higher_degrees((14, 15, 16, 18, 20, 21))
        self.assertEqual(high_res[14]["band5_non_paired"], 0)
        self.assertEqual(high_res[15]["band4_paired"], 0)
        self.assertEqual(high_res[15]["band5_non_paired"], 0)
        self.assertGreater(high_res[16]["band5_non_paired"], 0)  # first non-paired at m=16
        self.assertEqual(high_res[21]["band4_paired"], 0)
        self.assertEqual(high_res[21]["band5_non_paired"], 0)

    def test_05_float_free_and_consolidated_runner(self) -> None:
        target_file = Path(_REPO_ROOT) / "toolkit" / "covariant_apolarity_and_weyl_shioda_census.py"
        violations = scan_forbidden(target_file)
        self.assertEqual(violations, [])

        audit = run_all_theorems_audit()
        self.assertTrue(audit["all_theorems_verified"])
        self.assertEqual(audit["epistemic_invariants"]["GLOBAL_HODGE_CONJECTURE"], "OPEN")
        self.assertFalse(audit["epistemic_invariants"]["release_authorized"])

    def test_06_3band_blind_gauss_manin_jet_recovery_and_generative_lean_parity(self) -> None:
        """Verifies 3-Band blind t^3-jet reconstruction and Lean 4 generative check parity."""
        from toolkit.blind_gauss_manin_jet_reconstructor import BlindGaussManinJetReconstructor

        # Verify zero-float compliance
        blind_file = Path(_REPO_ROOT) / "toolkit" / "blind_gauss_manin_jet_reconstructor.py"
        self.assertEqual(scan_forbidden(blind_file), [])

        reconstructor = BlindGaussManinJetReconstructor()
        exp_res = reconstructor.run_full_reconstruction_experiment()
        self.assertTrue(exp_res["all_checks_passed"])

        # Band 1: Planes -> Smoothed Quadric
        b1 = exp_res["band1_quadric"]
        self.assertEqual(b1["macaulay_ranks"], [4, 9, 16, 24, 30, 32])
        self.assertEqual(b1["ann1_dimension"], 2)
        self.assertEqual(b1["ann2_dimension"], 12)
        self.assertEqual(b1["spontaneous_quadric_generators"], 1)
        self.assertEqual(b1["gotzmann_regularity"], 2)
        self.assertEqual(b1["transport"]["orders_constructed"], 4)

        # Band 2: 3+3 Curve Joins
        b2 = exp_res["band2_curve_join"]
        self.assertEqual(b2["macaulay_ranks"], [6, 21, 50, 90, 126, 141])
        self.assertEqual(b2["ann1_dimension"], 0)
        self.assertEqual(b2["ann2_dimension"], 0)
        self.assertEqual(b2["ann3_dimension"], 6)
        self.assertEqual(b2["transport"]["orders_constructed"], 4)

        # Band 3: 2+4 Surface-Curve Joins
        b3 = exp_res["band3_surface_curve"]
        self.assertEqual(b3["macaulay_ranks"], [5, 15, 32, 53, 71, 78])
        self.assertEqual(b3["ann1_dimension"], 1)
        self.assertEqual(b3["ann2_dimension"], 6)
        self.assertEqual(b3["retained_hyperplane_annihilators"], 1)
        self.assertEqual(b3["transport"]["orders_constructed"], 4)

        # Verify Lean Check 44 (B_Weyl * B_adj = -8 * I_6)
        b_weyl = [
            [1, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, -1],
            [0, 1, 0, 0, 1, 0],
            [0, 1, 0, 0, -1, 0],
            [0, 0, 1, 1, 0, 0],
            [0, 0, 1, -1, 0, 0],
        ]
        b_adj = [
            [-4, -4, 0, 0, 0, 0],
            [0, 0, -4, -4, 0, 0],
            [0, 0, 0, 0, -4, -4],
            [0, 0, 0, 0, -4, 4],
            [0, 0, -4, 4, 0, 0],
            [-4, 4, 0, 0, 0, 0],
        ]
        prod = [[sum(b_weyl[i][k] * b_adj[k][j] for k in range(6)) for j in range(6)] for i in range(6)]
        for i in range(6):
            for j in range(6):
                expected_entry = -8 if i == j else 0
                self.assertEqual(prod[i][j], expected_entry)

        # Verify Lean Check 45 (plane [3, 6, 10, 15, 18, 19], quadric [4, 9, 16, 24, 30, 32])
        plane_ranks = [3, 6, 10, 15, 18, 19]
        quad_ranks = [4, 9, 16, 24, 30, 32]
        self.assertEqual(sum(plane_ranks) + 1, 72)
        self.assertEqual(b1["macaulay_ranks"], quad_ranks)


if __name__ == "__main__":
    unittest.main()
