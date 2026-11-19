import Mathlib.Algebra.BigOperators.Finsupp.Basic

/-!
# Commutative Symmetry of Finitely Supported Contraction Sums

Proves `∑ m ∈ f.support, f m * g m = ∑ m ∈ g.support, g m * f m` over a `CommSemiring`.
-/

namespace Finsupp

variable {α R : Type*} [CommSemiring R]

/-- Symmetric contraction pairing identity between two finitely supported functions. -/
theorem sum_support_mul_comm (f g : α →₀ R) :
    ∑ m ∈ f.support, f m * g m = ∑ m ∈ g.support, g m * f m := by
  classical
  have hf : ∑ m ∈ f.support, f m * g m = ∑ m ∈ f.support ∪ g.support, f m * g m :=
    Finset.sum_subset Finset.subset_union_left fun m _ hm => by
      rw [Finsupp.notMem_support_iff.mp hm, zero_mul]
  have hg : ∑ m ∈ g.support, g m * f m = ∑ m ∈ f.support ∪ g.support, g m * f m :=
    Finset.sum_subset Finset.subset_union_right fun m _ hm => by
      rw [Finsupp.notMem_support_iff.mp hm, zero_mul]
  calc
    ∑ m ∈ f.support, f m * g m = ∑ m ∈ f.support ∪ g.support, f m * g m := hf
    _ = ∑ m ∈ f.support ∪ g.support, g m * f m :=
      Finset.sum_congr rfl fun m _ => mul_comm _ _
    _ = ∑ m ∈ g.support, g m * f m := hg.symm

end Finsupp
