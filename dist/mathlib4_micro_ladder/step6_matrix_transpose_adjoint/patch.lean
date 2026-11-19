import Mathlib.LinearAlgebra.Matrix.DotProduct

/-!
# Dot-Product Adjointness for Matrix Transpose

Packages `(A *ᵥ x) ⬝ᵥ y = x ⬝ᵥ (Aᵀ *ᵥ y)` and its symmetric Gram quadratic form identity.
-/

namespace Matrix

variable {m n R : Type*} [Fintype m] [Fintype n] [CommRing R]

/-- Adjointness of `Matrix.mulVec` and `Matrix.transpose` with respect to `dotProduct`. -/
theorem mulVec_dotProduct_eq_dotProduct_transpose_mulVec
    (A : Matrix m n R) (x : n → R) (y : m → R) :
    (A *ᵥ x) ⬝ᵥ y = x ⬝ᵥ (Aᵀ *ᵥ y) := by
  simp [Matrix.dotProduct_mulVec, Matrix.vecMul_transpose]

/-- Quadratic form identity `((Aᵀ * A) *ᵥ x) ⬝ᵥ x = (A *ᵥ x) ⬝ᵥ (A *ᵥ x)`. -/
theorem transpose_mul_self_quadratic (A : Matrix m n R) (x : n → R) :
    ((Aᵀ * A) *ᵥ x) ⬝ᵥ x = (A *ᵥ x) ⬝ᵥ (A *ᵥ x) := by
  rw [← Matrix.mulVec_mulVec, mulVec_dotProduct_eq_dotProduct_transpose_mulVec, transpose_transpose]

end Matrix
