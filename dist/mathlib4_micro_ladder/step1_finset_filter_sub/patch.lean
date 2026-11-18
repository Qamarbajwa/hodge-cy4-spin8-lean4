import Mathlib.Algebra.BigOperators.Group.Finset.Basic

/-!
# Complement Subtraction Lemmas for Weighted Finite Sums

Adds two `ℕ` subtraction identities derived from `Finset.sum_filter_add_sum_filter_not`.
-/

namespace Finset

variable {α : Type*}

/-- Express a filtered `ℕ`-sum as total sum minus the complement filtered sum. -/
theorem sum_filter_eq_sub_sum_filter_not (s : Finset α) (p : α → Prop) [DecidablePred p]
    (f : α → ℕ) :
    ∑ x ∈ s with p x, f x = (∑ x ∈ s, f x) - ∑ x ∈ s with ¬ p x, f x := by
  have h := Finset.sum_filter_add_sum_filter_not s p f
  omega

/-- Subtracting a filtered `ℕ`-sum from the total leaves the complementary filtered sum. -/
theorem sum_sub_sum_filter_eq_sum_filter_not (s : Finset α) (p : α → Prop) [DecidablePred p]
    (f : α → ℕ) :
    (∑ x ∈ s, f x) - ∑ x ∈ s with p x, f x = ∑ x ∈ s with ¬ p x, f x := by
  have h := Finset.sum_filter_add_sum_filter_not s p f
  omega

end Finset
