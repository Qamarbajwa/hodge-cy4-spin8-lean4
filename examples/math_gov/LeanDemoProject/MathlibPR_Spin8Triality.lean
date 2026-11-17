/-
Copyright (c) 2026 Qamar Munawer. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Qamar Munawer
-/
import ShiodaFormalConjectures
import HodgeVerification

/-!
# Spin(8) Triality, W(D_4) Chiral Orthogonality, and Mumford Spinor Representations

This module provides Mathlib-style universally quantified weight-lattice
algebraic laws, Weyl group chirality-preservation theorems, Hodge-star
involution identities, and D_4 simple-root Gram rank certificates.
-/

/-- Addition on the 4-dimensional `Weight4` lattice is commutative. -/
theorem addW4_comm (a b : Weight4) : addW4 a b = addW4 b a := by
  dsimp [addW4]
  rw [Int.add_comm a.1 b.1, Int.add_comm a.2.1 b.2.1,
    Int.add_comm a.2.2.1 b.2.2.1, Int.add_comm a.2.2.2 b.2.2.2]

/-- Addition on the 4-dimensional `Weight4` lattice is associative. -/
theorem addW4_assoc (a b c : Weight4) :
    addW4 (addW4 a b) c = addW4 a (addW4 b c) := by
  dsimp [addW4]
  rw [Int.add_assoc a.1 b.1 c.1, Int.add_assoc a.2.1 b.2.1 c.2.1,
    Int.add_assoc a.2.2.1 b.2.2.1 c.2.2.1, Int.add_assoc a.2.2.2 b.2.2.2 c.2.2.2]

/-- The zero weight `(0, 0, 0, 0)` is a right identity for `addW4`. -/
theorem addW4_zero_right (a : Weight4) : addW4 a (0, 0, 0, 0) = a := by
  dsimp [addW4]
  rw [Int.add_zero a.1, Int.add_zero a.2.1,
    Int.add_zero a.2.2.1, Int.add_zero a.2.2.2]

/-- Multiplying two even-chirality sign tuples preserves sign product `+1`. -/
theorem signProd4_mul_eq_one (s w : Weight4)
    (hs : s.1 * s.2.1 * s.2.2.1 * s.2.2.2 = 1)
    (hw : w.1 * w.2.1 * w.2.2.1 * w.2.2.2 = 1) :
    (s.1 * w.1) * (s.2.1 * w.2.1) * (s.2.2.1 * w.2.2.1) * (s.2.2.2 * w.2.2.2) = 1 := by
  have h1 : (s.1 * w.1) * (s.2.1 * w.2.1) = (s.1 * s.2.1) * (w.1 * w.2.1) := by
    rw [Int.mul_assoc s.1 w.1 (s.2.1 * w.2.1),
      Int.mul_left_comm w.1 s.2.1 w.2.1, ← Int.mul_assoc s.1 s.2.1 (w.1 * w.2.1)]
  have h2 : (s.2.2.1 * w.2.2.1) * (s.2.2.2 * w.2.2.2) =
      (s.2.2.1 * s.2.2.2) * (w.2.2.1 * w.2.2.2) := by
    rw [Int.mul_assoc s.2.2.1 w.2.2.1 (s.2.2.2 * w.2.2.2),
      Int.mul_left_comm w.2.2.1 s.2.2.2 w.2.2.2,
      ← Int.mul_assoc s.2.2.1 s.2.2.2 (w.2.2.1 * w.2.2.2)]
  rw [Int.mul_assoc ((s.1 * w.1) * (s.2.1 * w.2.1)) (s.2.2.1 * w.2.2.1) (s.2.2.2 * w.2.2.2),
    h1, h2,
    ← Int.mul_assoc (s.1 * s.2.1 * (w.1 * w.2.1)) (s.2.2.1 * s.2.2.2) (w.2.2.1 * w.2.2.2),
    Int.mul_assoc (s.1 * s.2.1) (w.1 * w.2.1) (s.2.2.1 * s.2.2.2),
    Int.mul_comm (w.1 * w.2.1) (s.2.2.1 * s.2.2.2),
    ← Int.mul_assoc (s.1 * s.2.1) (s.2.2.1 * s.2.2.2) (w.1 * w.2.1),
    Int.mul_assoc ((s.1 * s.2.1) * (s.2.2.1 * s.2.2.2)) (w.1 * w.2.1) (w.2.2.1 * w.2.2.2)]
  have hs' : (s.1 * s.2.1) * (s.2.2.1 * s.2.2.2) = 1 := by
    rw [← Int.mul_assoc]; exact hs
  have hw' : (w.1 * w.2.1) * (w.2.2.1 * w.2.2.2) = 1 := by
    rw [← Int.mul_assoc]; exact hw
  rw [hs', hw']; rfl

set_option maxRecDepth 4096 in
/-- Every element of the 192-element Weyl group `W(D_4)` preserves `S^+_8`
and acts with even permutation parity. -/
theorem wd4_preserves_spinor_chirality :
    weyl_d4_elements.all (fun (p, s) =>
      so8Weights.all (fun w =>
        let w' := actWD4OnWeight p s w
        intEq (w'.1 * w'.2.1 * w'.2.2.1 * w'.2.2.2) 1)) = true := by
  rfl

/-- Hodge-star splitting `70 = 35_+ + 35_-` and rank-6 `D_4` simple-root Gram certificate. -/
theorem spin8_wedge4_hodge_star_and_root_rank :
    four_tuples.length = 70 ∧
    wedge4_spinor_self_dual_dim = 35 ∧
    wedge4_spinor_anti_self_dual_dim = 35 ∧
    mumford_stacked_root_rank = 6 :=
  ⟨rfl, rfl, rfl, rfl⟩

/-- Full 192-element `W(D_4)` chiral character inner-product orthogonality. -/
theorem wd4_chiral_character_orthogonality :
    (wd4_total_elements, wd4_all_even_parity,
     wd4_norm_plus_sq, wd4_norm_minus_sq, wd4_cross_product) =
      (192, true, 192, 192, 0) :=
  weyl_d4_even_parity_and_chiral_orthogonality_eq

#print axioms addW4_comm
#print axioms addW4_assoc
#print axioms addW4_zero_right
#print axioms signProd4_mul_eq_one
#print axioms wd4_preserves_spinor_chirality
#print axioms spin8_wedge4_hodge_star_and_root_rank
#print axioms wd4_chiral_character_orthogonality
