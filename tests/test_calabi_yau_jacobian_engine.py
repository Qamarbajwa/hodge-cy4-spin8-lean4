r"""Unit tests for Calabi-Yau Fourfold Jacobian Engine.

Verifies exact Koszul dimensions, Griffiths residue primitive Hodge diamond (1, 426, 1751, 426, 1),
Gorenstein Macaulay duality, monomial basis generation, exact Noether-Lefschetz ranks
(including rank 19 for the linear 2-plane cycle), and Markman inapplicability.
"""

import unittest
from toolkit.calabi_yau_jacobian_engine import CalabiYauJacobianEngine


class TestCalabiYauJacobianEngine(unittest.TestCase):
    def setUp(self):
        self.engine = CalabiYauJacobianEngine()

    def test_koszul_dimensions(self):
        self.assertEqual(self.engine.koszul_dimension(0), 1)
        self.assertEqual(self.engine.koszul_dimension(6), 426)
        self.assertEqual(self.engine.koszul_dimension(12), 1751)
        self.assertEqual(self.engine.koszul_dimension(18), 426)
        self.assertEqual(self.engine.koszul_dimension(24), 1)

        total_sum = sum(self.engine.koszul_dimension(m) for m in range(25))
        self.assertEqual(total_sum, 15625)
        self.assertEqual(total_sum, 5 ** 6)

    def test_hilbert_poincare_series(self):
        hp = self.engine.hilbert_poincare_series()
        self.assertEqual(len(hp), 25)
        for m in range(25):
            self.assertEqual(hp[m], self.engine.koszul_dimension(m))
            # Gorenstein symmetry
            self.assertEqual(hp[m], hp[24 - m])

    def test_primitive_hodge_diamond(self):
        diamond = self.engine.primitive_hodge_diamond()
        prim = diamond["primitive_hodge_numbers"]
        self.assertEqual(prim["h^{4,0}_prim"], 1)
        self.assertEqual(prim["h^{3,1}_prim"], 426)
        self.assertEqual(prim["h^{2,2}_prim"], 1751)
        self.assertEqual(prim["h^{1,3}_prim"], 426)
        self.assertEqual(prim["h^{0,4}_prim"], 1)

        self.assertEqual(diamond["total_middle_hodge_number_h22"], 1752)
        self.assertEqual(diamond["total_middle_betti_number_b4"], 2606)
        self.assertEqual(diamond["milnor_number"], 15625)

    def test_monomial_bases(self):
        m6 = self.engine.generate_monomial_basis(6)
        m12 = self.engine.generate_monomial_basis(12)
        m18 = self.engine.generate_monomial_basis(18)

        self.assertEqual(len(m6), 426)
        self.assertEqual(len(m12), 1751)
        self.assertEqual(len(m18), 426)

        # Confirm all components are in [0, 4]
        for a in m6:
            self.assertEqual(len(a), 6)
            self.assertEqual(sum(a), 6)
            self.assertTrue(all(0 <= x <= 4 for x in a))

        for a in m12:
            self.assertEqual(len(a), 6)
            self.assertEqual(sum(a), 12)
            self.assertTrue(all(0 <= x <= 4 for x in a))

    def test_gorenstein_macaulay_duality(self):
        res = self.engine.gorenstein_macaulay_duality()
        self.assertTrue(res["is_non_degenerate"])
        self.assertEqual(res["dimension"], 426)
        self.assertEqual(res["dual_pairs_count"], 426)

    def test_noether_lefschetz_ranks(self):
        nl = self.engine.analyze_noether_lefschetz_loci()
        self.assertEqual(nl["matrix_shape"], (426, 426))
        # The 2-plane cycle has rank EXACTLY 19
        self.assertEqual(nl["plane_cycle_rank"], 19)
        self.assertEqual(nl["plane_cycle_codimension"], 19)
        self.assertEqual(nl["plane_cycle_tangent_dim"], 407)

        # Center monomial rank
        self.assertEqual(nl["center_monomial_rank"], 141)

        # Multi-plane rank
        self.assertEqual(nl["four_planes_rank"], 64)

        # Dense combination has high rank
        self.assertGreaterEqual(nl["dense_50_monomials_rank"], 400)

    def test_markman_escape_audit(self):
        esc = self.engine.markman_escape_audit()
        self.assertFalse(esc["markman_secant_engine_applicable"])
        self.assertEqual(esc["middle_primitive_dimension"], 1751)
        self.assertEqual(esc["albanese_variety"], "Alb(X_4) = 0 (since b_1(X_4) = 0)")

    def test_koszul_syzygy_exact_division(self):
        m6 = self.engine.generate_monomial_basis(6)
        lam_pi = {(4, 4, 4, 0, 0, 0): 1}
        # Pick 5 kernel elements
        u_samples = [m for m in m6 if m[0] >= 1 or m[1] >= 1 or m[2] >= 1][:5]
        for u in u_samples:
            A = self.engine.compute_koszul_syzygy(u, lam_pi)
            self.assertEqual(len(A), 6)
            # Reconstruct sum A_i * x_i^5
            recon = {}
            for i in range(6):
                for mono, c in A[i].items():
                    full = list(mono)
                    full[i] += 5
                    t_full = tuple(full)
                    recon[t_full] = recon.get(t_full, 0) + c
            expected = {tuple(u[k] + (4 if k < 3 else 0) for k in range(6)): 1}
            self.assertEqual(recon, expected)

    def test_voisin_pairing_2plane_canonical_integrability(self):
        res = self.engine.evaluate_geometric_cycle_integrability()
        self.assertEqual(res["first_order_rank"], 19)
        self.assertEqual(res["canonical_subspace_dim"], 56)
        self.assertEqual(res["canonical_obstructed_pairs"], 0)
        self.assertTrue(res["canonical_is_100_percent_integrable"])
        self.assertGreaterEqual(res["kernel_self_pairing_zero_count"], 350)

    def test_voisin_pairing_artificial_class_obstruction(self):
        res = self.engine.evaluate_artificial_class_obstruction()
        self.assertEqual(res["first_order_rank"], 68)
        self.assertEqual(res["base_rank"], 68)
        self.assertEqual(res["augmented_rank"], 69)
        self.assertTrue(res["obstruction_leaked_to_cokernel"])
        self.assertFalse(res["is_unobstructed"])


if __name__ == "__main__":
    unittest.main()
