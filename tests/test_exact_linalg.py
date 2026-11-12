"""Unit tests for toolkit/exact_linalg.py (exact rational arithmetic over Q)."""

import unittest
from fractions import Fraction
import numpy as np
from toolkit.exact_linalg import (
    exact_rref,
    exact_matrix_rank,
    exact_vector_in_span,
    exact_kernel_basis,
    ExactColumnSpan,
)


class TestExactLinalg(unittest.TestCase):
    def test_exact_rank_and_rref_rationals(self):
        # Matrix with small ill-conditioned perturbation that would fail float SVD tolerances
        M = [
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, Fraction(1, 10**12)],
        ]
        # Over Q, rank is strictly 3
        self.assertEqual(exact_matrix_rank(M), 3)
        rref, pivots = exact_rref(M)
        self.assertEqual(pivots, [0, 1, 2])
        self.assertEqual(rref, [
            [Fraction(1), Fraction(0), Fraction(0)],
            [Fraction(0), Fraction(1), Fraction(0)],
            [Fraction(0), Fraction(0), Fraction(1)],
        ])

    def test_exact_rank_deficient_matrix(self):
        M = np.array([
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9],
        ])
        self.assertEqual(exact_matrix_rank(M), 2)
        ker = exact_kernel_basis(M)
        self.assertEqual(len(ker), 1)
        # Verify M * k == 0 exactly
        k = ker[0]
        for row in M:
            dot = sum(Fraction(int(row[j])) * k[j] for j in range(3))
            self.assertEqual(dot, 0)

    def test_exact_column_span_permutation_fillin(self):
        # Test sparse ordering where later columns have smaller pivot index than earlier columns
        cols = [
            [0, 0, 1, 1],
            [0, 1, 1, 0],
            [1, 1, 0, 0],
        ]
        # Note cols as rows vs columns: transpose so columns are [0,0,1,1], [0,1,1,0], [1,1,0,0]
        M = [
            [0, 0, 1],
            [0, 1, 1],
            [1, 1, 0],
            [1, 0, 0],
        ]
        span = ExactColumnSpan(M)
        self.assertEqual(span.rank, 3)
        # Any linear combination of M columns must be in span
        combo = [2 * 1, 3 * 1 + 2 * 1, 5 * 1 + 3 * 1, 5 * 1]  # 5*col0 + 3*col1 + 2*col2
        self.assertTrue(span.contains(combo))
        # Outside span vector (notice alternating sum x0 - x1 + x2 - x3 = 0 for all columns)
        # col0: 0-0+1-1 = 0; col1: 0-1+1-0 = 0; col2: 1-1+0-0 = 0
        self.assertFalse(span.contains([1, 0, 0, 0]))
        self.assertTrue(exact_vector_in_span(M, [0, 0, 0, 0]))


if __name__ == "__main__":
    unittest.main()
