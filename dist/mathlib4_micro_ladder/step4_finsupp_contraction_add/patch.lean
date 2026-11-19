import Mathlib.Algebra.BigOperators.Finsupp.Basic

/-!
# Bilinear Contraction Pairing on Finitely Supported Maps (Additivity)

Defines `Finsupp.contractionPairing` and proves zero and additive laws in the left argument.
-/

namespace Finsupp

variable {α R : Type*} [CommSemiring R]

/-- Contraction pairing between a finitely supported map `f` and evaluation map `g`. -/
noncomputable def contractionPairing (f : α →₀ R) (g : α → R) : R :=
  f.sum fun _m c => c * g _m

@[simp]
theorem contractionPairing_zero_left (g : α → R) :
    contractionPairing (0 : α →₀ R) g = 0 := by
  simp [contractionPairing]

theorem contractionPairing_add_left (f₁ f₂ : α →₀ R) (g : α → R) :
    contractionPairing (f₁ + f₂) g = contractionPairing f₁ g + contractionPairing f₂ g := by
  classical
  simp only [contractionPairing]
  exact Finsupp.sum_add_index' (fun _ => zero_mul _) (fun _ _ _ => add_mul _ _ _)

end Finsupp
