import Mathlib.Data.ZMod.Basic

/-!
# Unit-Balanced Additive Complement Six-Tuples over `ZMod m`

Proves unit-twist cancellation for `[x, -x, y, -y, z, -z]` and uniform scaling in `ZMod m`.
-/

namespace ZMod

/-- Summing paired additive inverses `[x, -x, y, -y, z, -z]` twisted by `u` vanishes in `ZMod m`. -/
theorem sum_paired_complements_eq_zero {m : ℕ} (x y z : ZMod m) (u : (ZMod m)ˣ) :
    ([x, -x, y, -y, z, -z].map fun a => (u : ZMod m) * a).sum = 0 := by
  simp [mul_neg]

/-- Any `ZMod m` sum over a `Finset` vanishing under unit twists also vanishes after uniform scaling. -/
theorem sum_mul_smul_eq_zero {m : ℕ} {α : Type*} [DecidableEq α] (s : Finset α)
    (a : α → ZMod m) (t : ZMod m)
    (ha : ∀ u : (ZMod m)ˣ, ∑ i ∈ s, (u : ZMod m) * a i = 0) (u : (ZMod m)ˣ) :
    ∑ i ∈ s, (u : ZMod m) * (t * a i) = 0 := by
  have hmul : ∑ i ∈ s, t * ((u : ZMod m) * a i) = t * ∑ i ∈ s, (u : ZMod m) * a i := by
    clear ha
    induction s using Finset.induction with
    | empty => simp
    | @insert i s hi ih => simp [Finset.sum_insert hi, ih, mul_add]
  calc
    ∑ i ∈ s, (u : ZMod m) * (t * a i)
        = ∑ i ∈ s, t * ((u : ZMod m) * a i) :=
          Finset.sum_congr rfl fun i _ => mul_left_comm _ _ _
    _ = t * ∑ i ∈ s, (u : ZMod m) * a i := hmul
    _ = 0 := by rw [ha u, mul_zero]

end ZMod
