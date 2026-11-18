import Mathlib.Algebra.BigOperators.Group.List.Basic
import Mathlib.Algebra.Group.Basic

/-!
# Commutativity of List `zipWith` Inner Products

Proves `(List.zipWith (· * ·) xs ys).sum = (List.zipWith (· * ·) ys xs).sum`.
-/

namespace List

variable {R : Type*} [AddCommMonoid R] [CommMagma R]

/-- Swapping the two input lists leaves the `zipWith` multiplication sum unchanged. -/
theorem sum_zipWith_mul_comm (xs ys : List R) :
    (List.zipWith (· * ·) xs ys).sum = (List.zipWith (· * ·) ys xs).sum := by
  induction xs generalizing ys with
  | nil => cases ys <;> simp
  | cons x xs ih =>
    cases ys with
    | nil => simp
    | cons y ys =>
      simp only [List.zipWith_cons_cons, List.sum_cons]
      rw [mul_comm x y, ih ys]

end List
