"""Tests for Float-Free Multi-Prime CRT Solver & Finite Lean 4 Checks."""

import unittest
from fractions import Fraction
from pathlib import Path

from toolkit.governance.lean_step_runner import check_step, sha as sha_bytes
from toolkit.integrity import scan_forbidden
from toolkit.modular_crt_linear_solver import (
    MODULAR_PRIMES_61BIT,
    MODULAR_PRIMES_62BIT,
    ModularCRTLinearSolver,
    certify_rank_and_nullspace_crt,
    clear_row_denominators,
    crt_combine,
    crt_reconstruct_integers,
    fast_modular_sparse_rank,
    is_prime_deterministic_64,
    rational_reconstruct,
    rref_and_nullspace_mod_p,
    run_non_fermat_1751x426_crt_certification,
)
from toolkit.non_fermat_determinantal_stabilization_engine import FiniteNonFermatMacaulayEngine


class TestModularCrtAndBridgeInterface(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parent.parent
        cls.lean_dir = cls.root / "examples" / "math_gov" / "LeanDemoProject"
        cls.lean_sha = sha_bytes((cls.lean_dir / "HodgeVerification.lean").read_bytes())

    def test_01_primes_and_zero_float_clean(self) -> None:
        self.assertEqual(len(MODULAR_PRIMES_62BIT), 3)
        for p in MODULAR_PRIMES_62BIT:
            self.assertTrue(is_prime_deterministic_64(p))
            self.assertLess(p, 1 << 62)
            self.assertGreater(p, 1 << 61)
        self.assertEqual(
            scan_forbidden(str(self.root / "toolkit" / "modular_crt_linear_solver.py")),
            [],
        )
        self.assertEqual(scan_forbidden(__file__), [])

    def test_02_bad_prime_drop_theorem_and_crt_reconstruction(self) -> None:
        rows = [
            {0: Fraction(7, 5), 1: Fraction(0, 1), 2: Fraction(21, 5)},
            {0: Fraction(0, 1), 1: Fraction(11 * 13, 3), 2: Fraction(0, 1)},
        ]
        int_rows, _ = clear_row_denominators(rows)
        # p = 11 or p = 13 drops rank from 2 to 1; CRT over 62-bit primes certifies exact rk = 2 and kernel
        self.assertEqual(rref_and_nullspace_mod_p(int_rows, 3, 11)["rank"], 1)
        self.assertEqual(rref_and_nullspace_mod_p(int_rows, 3, 13)["rank"], 1)

        cert = certify_rank_and_nullspace_crt(rows, 3, MODULAR_PRIMES_62BIT, return_nullspace=True)
        self.assertEqual(cert["certified_q_rank"], 2)
        self.assertEqual(cert["nullity"], 1)
        self.assertTrue(cert["exact_q_residual_verified"])
        self.assertEqual(cert["nullspace_q"][0], {2: Fraction(1, 1), 0: Fraction(-3, 1)})

        # Check CRT + Wang round-trip
        target = Fraction(-15625, 37)
        p1, p2, p3 = MODULAR_PRIMES_62BIT
        pairs = [((target.numerator * pow(target.denominator, -1, p)) % p, p) for p in (p1, p2, p3)]
        comb, mod = crt_combine(pairs)
        self.assertEqual(rational_reconstruct(comb, mod), target)

    def test_03_non_fermat_1751x426_crt_under_2s_and_speedup(self) -> None:
        rep = run_non_fermat_1751x426_crt_certification(
            include_fraction_submatrix_cross_check=True
        )
        self.assertEqual(rep["matrix_shape"], [1751, 426])
        self.assertEqual(rep["certified_q_rank"], 426)
        self.assertEqual(rep["modular_ranks_across_3_primes"], [426, 426, 426])
        self.assertTrue(rep["exact_q_residual_verified"])
        self.assertTrue(rep["under_2_seconds"], msg=f"elapsed_ns={rep['solve_elapsed_ns']}")
        self.assertTrue(rep["bad_prime_drop_theorem_verified"])
        self.assertTrue(rep["rank_deficient_425_crt_kernel_verified"])

        sl = rep["slice_fraction_cross_check"]
        self.assertTrue(sl["ranks_match_exact"])
        self.assertGreater(sl["observed_slice_speedup"], 100)

    def test_04_lean4_node13_finite_checks_zero_axioms(self) -> None:
        bp_bytes = (self.root / "lean_blueprint" / "HodgeVerification.lean").read_bytes()
        demo_bytes = (self.lean_dir / "HodgeVerification.lean").read_bytes()
        self.assertEqual(bp_bytes, demo_bytes)

        checks = [
            (
                "noether_macaulay_gorenstein_symmetry_eq",
                "(cy4_socle_degree == 24 && "
                "cy4_middle_degree == 12 && "
                "cy4_hilbert_series.length == 25 && "
                "cy4_hilbert_series == cy4_hilbert_series.reverse && "
                "nf_sum_pairs 0 == 1 && "
                "nf_sum_pairs 12 == h22_prim && "
                "nf_sum_pairs 24 == 1) = true",
            ),
            (
                "weyl_d4_spinor_weight_decomposition_eq",
                "(four_tuples.length == 70 && "
                "wedge4_spinor_self_dual_dim + wedge4_spinor_anti_self_dual_dim == four_tuples.length && "
                "zero_weight_tuples.length == 6 && "
                "mumford_stacked_root_rank == zero_weight_tuples.length && "
                "weyl_d4_group_order == 192 && "
                "triality_zero_triples.length == 32) = true",
            ),
        ]
        for thm, stmt in checks:
            res = check_step(
                str(self.lean_dir),
                "HodgeVerification.lean",
                thm,
                stmt,
                self.lean_sha,
            )
            self.assertTrue(res["lean_kernel_check_passed"], msg=f"{thm}: {res}")
            self.assertEqual(res["axioms"], [], msg=f"{thm}: {res}")

    def test_05_signed_crt_u_dense_finite_nf_and_hilbert_symmetry(self) -> None:
        # Verify 61-bit primes and composite exclusion
        self.assertFalse(is_prime_deterministic_64(2305843009213693903))
        for p in MODULAR_PRIMES_61BIT:
            self.assertTrue(is_prime_deterministic_64(p))
            self.assertLessEqual(p, (1 << 61) - 1)

        # Signed CRT integer reconstruction over positive and negative integers
        for x in (0, 1, -1, 1751, -15625, 10**18, -(10**18), 98765432109876543210):
            residues = [x % p for p in MODULAR_PRIMES_61BIT]
            self.assertEqual(crt_reconstruct_integers(residues, MODULAR_PRIMES_61BIT), x)

        solver = ModularCRTLinearSolver()
        dense_res = solver.verify_dense_moduli_1751x426()
        self.assertEqual(dense_res["matrix_shape"], [426, 1751])
        self.assertEqual(dense_res["certified_rank"], 426)
        self.assertEqual(dense_res["kernel_dim"], 1325)
        self.assertTrue(dense_res["all_primes_agree"])
        self.assertTrue(dense_res["under_1500ms"])

        nf_res = solver.verify_finite_non_fermat_macaulay_agreement()
        self.assertEqual(nf_res["plane_nf"]["modular_ranks"], [3, 6, 10, 15, 18, 19])
        self.assertTrue(nf_res["plane_nf"]["exact_match"])
        self.assertEqual(nf_res["quad_nf"]["modular_ranks"], [4, 9, 16, 24, 30, 32])
        self.assertTrue(nf_res["quad_nf"]["exact_match"])

        # Direct fast_modular_sparse_rank API check
        cols = [{0: 1, 1: 2}, {0: 3, 1: 6}, {1: 5, 2: 7}]
        mod_rk = fast_modular_sparse_rank(cols, 3, MODULAR_PRIMES_61BIT)
        self.assertEqual(mod_rk["certified_rank"], 2)

        eng = FiniteNonFermatMacaulayEngine()
        hr = [len(eng._pair_basis_dim_split(d)) for d in range(25)]
        self.assertEqual(hr, list(reversed(hr)))
        self.assertEqual(hr[12], 1751)


if __name__ == "__main__":
    unittest.main()
