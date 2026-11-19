import Mathlib.Algebra.BigOperators.Group.Finset.Basic

/-!
# Double-Bipartition Balance and Upper Bound for Filtered Sums

Packages the `ℕ` upper bound and three-part incidence conservation identity over `Finset`.
-/

namespace Finset

variable {α : Type*}

/-- Any filtered `ℕ`-sum is at most the total weighted sum over the ambient finite set. -/
theorem sum_filter_le_sum (s : Finset α) (p : α → Prop) [DecidablePred p] (f : α → ℕ) :
    ∑ x ∈ s with p x, f x ≤ ∑ x ∈ s, f x := by
  have h := Finset.sum_filter_add_sum_filter_not s p f
  omega

/-- Weighted double-bipartition conservation across predicates `p` and `q`. -/
theorem sum_double_filter_balance (s : Finset α) (p q : α → Prop)
    [DecidablePred p] [DecidablePred q] (f : α → ℕ) :
    (∑ x ∈ s with p x ∧ q x, f x) + (∑ x ∈ s with p x ∧ ¬ q x, f x) +
      (∑ x ∈ s with ¬ p x, f x) = ∑ x ∈ s, f x := by
  have hp := Finset.sum_filter_add_sum_filter_not s p f
  have hq := Finset.sum_filter_add_sum_filter_not (s.filter p) q f
  simp only [Finset.filter_filter] at hq
  rw [← hp, ← hq]

end Finset
