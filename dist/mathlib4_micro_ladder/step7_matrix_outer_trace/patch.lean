import Mathlib.LinearAlgebra.Matrix.Trace
import Mathlib.LinearAlgebra.Matrix.DotProduct

/-!
# Trace Identities for Outer Products and Gram Matrices

Relates `Matrix.trace (Matrix.vecMulVec u v)` and `Matrix.trace (Aᵀ * A)` to sums and dots.
-/

namespace Matrix

variable {m n R : Type*} [Fintype m] [Fintype n] [CommRing R]

/-- The trace of an outer-product rank-1 matrix `vecMulVec u v` equals `u ⬝ᵥ v`. -/
theorem trace_vecMulVec_eq_dotProduct (u v : n → R) :
    Matrix.trace (Matrix.vecMulVec u v) = u ⬝ᵥ v := by
  simp [Matrix.trace, Matrix.diag, Matrix.vecMulVec, dotProduct]

/-- Frobenius squared-entry trace formula `trace (Aᵀ * A) = ∑ i, ∑ j, A i j * A i j`. -/
theorem trace_transpose_mul_self_eq_sum_sq (A : Matrix m n R) :
    Matrix.trace (Aᵀ * A) = ∑ i : m, ∑ j : n, A i j * A i j := by
  simp only [Matrix.trace, Matrix.diag, Matrix.mul_apply, Matrix.transpose_apply]
  rw [Finset.sum_comm]

end Matrix
