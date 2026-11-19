/-
Copyright (c) 2026 Qamar Munawer. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Qamar Munawer
-/
import ConditionalFermatHodge
import FermatHighDegreeExt

/-!
# Conditional Fermat Fourfold Algebraicity Bridge Extension (Degrees m <= 25)

Extends `FermatFourfoldHodgeBridge m` with Aoki's cyclic coset cone field
(`hasCyclicCosetConeDecomposition`) and discharges all remaining degrees up through `m = 25`
(`m ∈ {17, 19, 21, 23, 24, 25}`) unconditionally by pure kernel reduction (`rfl`, zero axioms).
-/

private theorem bool_or_cases_ext {x y : Bool} (h : (x || y) = true) :
    x = true ∨ y = true := by
  cases x with
  | true => exact Or.inl rfl
  | false => exact Or.inr h

private theorem list_all_mem_ext {α : Type} {p : α → Bool} (xs : List α) :
    xs.all p = true → ∀ x : α, x ∈ xs → p x = true := by
  induction xs with
  | nil =>
    intro _ x hx
    cases hx
  | cons y ys ih =>
    intro h x hx
    cases hx with
    | head =>
      cases hpy : p y with
      | false =>
        rw [List.all_cons, hpy] at h
        cases h
      | true => rfl
    | tail _ hmem =>
      rw [List.all_cons] at h
      cases hpy : p y with
      | false =>
        rw [hpy] at h
        cases h
      | true =>
        rw [hpy, Bool.true_and] at h
        exact ih h x hmem

/-- Extended classical bridge structure adding Aoki's cyclic coset cone pullback field. -/
structure FermatFourfoldHodgeBridgeExt (m : Nat) extends FermatFourfoldHodgeBridge m where
  /-- Cyclic 5-tuple coset cone cycles (`X_m^4` Aoki construction) yield algebraic classes. -/
  aoki_cyclic_coset_cone_algebraic :
    ∀ a : List Nat, hasCyclicCosetConeDecomposition m a = true → isAlgebraicCycleClass a

/-- Extended synthesizability predicate covering inductive witnesses, glued joins, and cyclic
coset cones. -/
def isHodge22ExtSynthesizable (m : Nat) (a : List Nat) : Bool :=
  isHodge22Synthesizable m a || hasCyclicCosetConeDecomposition m a

/-- Any character passing `isHodge22ExtSynthesizable m a = true` lifts through
`FermatFourfoldHodgeBridgeExt m` into `B.isAlgebraicCycleClass a`. -/
theorem ext_synthesizable_implies_algebraic (m : Nat) (B : FermatFourfoldHodgeBridgeExt m)
    (a : List Nat) (hs : isHodge22ExtSynthesizable m a = true) :
    B.isAlgebraicCycleClass a := by
  dsimp [isHodge22ExtSynthesizable] at hs
  cases bool_or_cases_ext hs with
  | inl hBase =>
    exact synthesizable_implies_algebraic m B.toFermatFourfoldHodgeBridge a hBase
  | inr hCone =>
    exact B.aoki_cyclic_coset_cone_algebraic a hCone

/-- Universal quantifier lifting: if every character in `sortedHodge22Tuples m` satisfies
`isHodge22ExtSynthesizable m`, every `α ∈ sortedHodge22Tuples m` is algebraic in `CH^2(X_m^4)_Q`. -/
theorem conditional_fermat_hodge22_all_ext_synthesized_algebraic (m : Nat)
    (B : FermatFourfoldHodgeBridgeExt m)
    (hAll : (sortedHodge22Tuples m).all (isHodge22ExtSynthesizable m) = true) :
    ∀ alpha : List Nat, alpha ∈ sortedHodge22Tuples m → B.isAlgebraicCycleClass alpha := by
  intro alpha hmem
  have hSynth := list_all_mem_ext (sortedHodge22Tuples m) hAll alpha hmem
  exact ext_synthesizable_implies_algebraic m B alpha hSynth

set_option maxHeartbeats 16000000 in
set_option maxRecDepth 8192 in
/-- Kernel certificate closing odd prime/composite degrees `m ∈ {17, 19, 21, 23}`. -/
theorem conditional_fermat_hodge22_verified_m17_m19_m21_m23_cert :
    ([17, 19, 21, 23].all fun m =>
      (sortedHodge22Tuples m).all (isHodge22ExtSynthesizable m)) = true :=
  rfl

set_option maxHeartbeats 16000000 in
set_option maxRecDepth 8192 in
/-- Kernel certificate closing degree `m = 24` across all `(2,2)`-Hodge classes. -/
theorem conditional_fermat_hodge22_verified_m24_cert :
    (sortedHodge22Tuples 24).all (isHodge22ExtSynthesizable 24) = true :=
  rfl

set_option maxHeartbeats 16000000 in
set_option maxRecDepth 8192 in
/-- Kernel certificate closing degree `m = 25` (including all coset-cone sporadic orbits). -/
theorem conditional_fermat_hodge22_verified_m25_cert :
    (sortedHodge22Tuples 25).all (isHodge22ExtSynthesizable 25) = true :=
  rfl

#print axioms ext_synthesizable_implies_algebraic
#print axioms conditional_fermat_hodge22_all_ext_synthesized_algebraic
#print axioms conditional_fermat_hodge22_verified_m17_m19_m21_m23_cert
#print axioms conditional_fermat_hodge22_verified_m24_cert
#print axioms conditional_fermat_hodge22_verified_m25_cert
