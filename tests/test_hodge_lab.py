"""Unit tests for the Hodge Conjecture Experimental Laboratory.

Verifies:
1. Griffiths residue calculation of Hodge numbers on hypersurfaces.
2. Agreement between Hilbert-Poincare series of the Jacobian ideal and Hodge numbers.
3. Shioda's combinatorial classification of Hodge characters and linear cycle generation.
4. Consistency between independent algebraic and combinatorial engines.
"""

import unittest
from toolkit.hodge_diamond import (
    hypersurface_primitive_hodge_numbers,
    hypersurface_full_hodge_diamond,
    hodge_classes_dimension,
)
from toolkit.shioda_fermat import (
    ShiodaFermatAnalyzer,
    coprime_units,
    character_weight,
    is_decomposable,
)


class TestHodgeDiamondEngine(unittest.TestCase):
    def test_k3_surface(self):
        """K3 surface: n=2, d=4 in P^3.

        Expected: h^{2,0}=1, h^{1,1}=20, h^{0,2}=1, primitive h^{1,1}_prim=19.
        """
        prim = hypersurface_primitive_hodge_numbers(2, 4)
        diamond = hypersurface_full_hodge_diamond(2, 4)

        self.assertEqual(prim[(2, 0)], 1)
        self.assertEqual(prim[(1, 1)], 19)
        self.assertEqual(prim[(0, 2)], 1)

        self.assertEqual(diamond[(2, 0)], 1)
        self.assertEqual(diamond[(1, 1)], 20)
        self.assertEqual(diamond[(0, 2)], 1)
        self.assertEqual(hodge_classes_dimension(2, 4), 20)

    def test_cubic_surface(self):
        """Cubic surface: n=2, d=3 in P^3.

        Expected: h^{1,1}=7 (primitive = 6), h^{2,0}=0.
        """
        prim = hypersurface_primitive_hodge_numbers(2, 3)
        diamond = hypersurface_full_hodge_diamond(2, 3)

        self.assertEqual(prim[(2, 0)], 0)
        self.assertEqual(prim[(1, 1)], 6)
        self.assertEqual(diamond[(1, 1)], 7)

    def test_cubic_fourfold(self):
        """Cubic fourfold: n=4, d=3 in P^5.

        Expected: h^{2,2}_prim = 20, total h^{2,2} = 21, h^{3,1} = 1, h^{4,0} = 0.
        """
        prim = hypersurface_primitive_hodge_numbers(4, 3)
        diamond = hypersurface_full_hodge_diamond(4, 3)

        self.assertEqual(prim[(2, 2)], 20)
        self.assertEqual(diamond[(2, 2)], 21)
        self.assertEqual(diamond[(3, 1)], 1)
        self.assertEqual(diamond[(4, 0)], 0)

    def test_quintic_threefold(self):
        """Quintic threefold (Calabi-Yau 3-fold): n=3, d=5 in P^4.

        Expected: h^{1,1}=1, h^{2,1}=101, h^{3,0}=1.
        Euler characteristic chi = 2*(1 - 101) = -200.
        """
        prim = hypersurface_primitive_hodge_numbers(3, 5)
        diamond = hypersurface_full_hodge_diamond(3, 5)

        self.assertEqual(diamond[(1, 1)], 1)
        self.assertEqual(diamond[(3, 0)], 1)
        self.assertEqual(diamond[(2, 1)], 101)
        self.assertEqual(prim[(2, 1)], 101)


class TestShiodaFermatEngine(unittest.TestCase):
    def test_units(self):
        self.assertEqual(coprime_units(4), [1, 3])
        self.assertEqual(coprime_units(6), [1, 5])

    def test_decomposability(self):
        # Pairs (1, 3) and (2, 2) mod 4 sum to 4
        self.assertTrue(is_decomposable((1, 3, 2, 2), 4))
        # (1, 1, 1, 1) mod 4 cannot be paired to sum to 4
        self.assertFalse(is_decomposable((1, 1, 1, 1), 4))

    def test_shioda_cubic_surface(self):
        analyzer = ShiodaFermatAnalyzer(2, 3)
        s = analyzer.summary()
        self.assertEqual(s["hodge_characters_B"], 6)
        self.assertEqual(s["decomposable_D (linear cycles)"], 6)
        self.assertTrue(s["all_decomposable"])

    def test_shioda_k3_surface(self):
        analyzer = ShiodaFermatAnalyzer(2, 4)
        s = analyzer.summary()
        self.assertEqual(s["hodge_characters_B"], 19)
        self.assertEqual(s["decomposable_D (linear cycles)"], 19)
        self.assertTrue(s["all_decomposable"])

    def test_shioda_cubic_fourfold(self):
        analyzer = ShiodaFermatAnalyzer(4, 3)
        s = analyzer.summary()
        self.assertEqual(s["hodge_characters_B"], 20)
        self.assertEqual(s["decomposable_D (linear cycles)"], 20)
        self.assertTrue(s["all_decomposable"])

    def test_cross_engine_consistency(self):
        """Cross-check: Primitive Hodge dimension from Shioda combinatorial engine

        MUST match primitive Hodge dimension from Griffiths residue / Jacobian algebra.
        """
        for n, d in [(2, 3), (2, 4), (4, 3)]:
            with self.subTest(dim=n, deg=d):
                prim_geom = hypersurface_primitive_hodge_numbers(n, d)[(n // 2, n // 2)]
                analyzer = ShiodaFermatAnalyzer(n, d)
                s = analyzer.summary()
                prim_shioda = s["hodge_characters_B"]
                self.assertEqual(prim_geom, prim_shioda)


if __name__ == "__main__":
    unittest.main()
