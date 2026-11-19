/-
Copyright (c) 2026 Qamar Munawer. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Qamar Munawer
-/
module

public import Mathlib.RingTheory.Ideal.Quotient.Operations
public import Mathlib.RingTheory.Ideal.Span
public import Mathlib.RingTheory.JacobianRing.KoszulWiebeBridge

/-!
# Artinian Gorenstein Apolarity Bilinear Pairing

This file defines the apolarity bilinear pairing induced by a `k`-linear functional
`ℓ : (R ⧸ I) →ₗ[k] k` on a quotient `k`-algebra `R ⧸ I`, constructs its annihilating kernel
ideal `apolarityKernel I ℓ`, characterizes Gorenstein/Frobenius nondegeneracy, and connects
Wiebe–Scheja–Storch colon multipliers (`C *ᵥ g = a`) directly to pairing vanishing.

## Main definitions and results

* `RingTheory.apolarityPairing`: `k`-bilinear map `(x, y) ↦ ℓ (x * y)` on `R ⧸ I`.
* `RingTheory.apolarityKernel`: ideal `{x | ∀ y, apolarityPairing I ℓ x y = 0}` in `R ⧸ I`.
* `RingTheory.apolarityKernel_eq_bot_iff`: characterizes nondegeneracy of the pairing.
* `RingTheory.apolarityPairing_det_mul_eq_zero_of_mulVec_eq`: any `C *ᵥ g = a` induces
  pairing annihilation of `C.det * x` against arbitrary `y` modulo `Ideal.span (Set.range a)`.
-/

@[expose] public section

namespace RingTheory

open Matrix

section Apolarity

variable {k R : Type*} [CommRing k] [CommRing R] [Algebra k R]

/-- The symmetric `k`-bilinear apolarity pairing `(x, y) ↦ ℓ (x * y)` on `R ⧸ I`. -/
def apolarityPairing (I : Ideal R) (ℓ : (R ⧸ I) →ₗ[k] k) :
    (R ⧸ I) →ₗ[k] (R ⧸ I) →ₗ[k] k :=
  LinearMap.mk₂ k (fun x y => ℓ (x * y))
    (fun x₁ x₂ y => by rw [add_mul, map_add])
    (fun c x y => by rw [smul_mul_assoc, map_smul])
    (fun x y₁ y₂ => by rw [mul_add, map_add])
    (fun c x y => by rw [mul_smul_comm, map_smul])

@[simp]
theorem apolarityPairing_apply (I : Ideal R) (ℓ : (R ⧸ I) →ₗ[k] k) (x y : R ⧸ I) :
    apolarityPairing I ℓ x y = ℓ (x * y) := rfl

theorem apolarityPairing_comm (I : Ideal R) (ℓ : (R ⧸ I) →ₗ[k] k) (x y : R ⧸ I) :
    apolarityPairing I ℓ x y = apolarityPairing I ℓ y x := by
  simp only [apolarityPairing_apply, mul_comm]

theorem apolarityPairing_assoc (I : Ideal R) (ℓ : (R ⧸ I) →ₗ[k] k) (x y z : R ⧸ I) :
    apolarityPairing I ℓ (x * y) z = apolarityPairing I ℓ x (y * z) := by
  simp only [apolarityPairing_apply, mul_assoc]

theorem apolarityPairing_mk_eq_zero_of_mem (I : Ideal R) (ℓ : (R ⧸ I) →ₗ[k] k)
    {r : R} (hr : r ∈ I) (y : R ⧸ I) :
    apolarityPairing I ℓ (Ideal.Quotient.mk I r) y = 0 := by
  have hr0 : Ideal.Quotient.mk I r = 0 := Ideal.Quotient.eq_zero_iff_mem.mpr hr
  simp [hr0]

/-- The annihilating kernel ideal `{x ∈ R ⧸ I | ∀ y, ℓ (x * y) = 0}` of the apolarity pairing. -/
def apolarityKernel (I : Ideal R) (ℓ : (R ⧸ I) →ₗ[k] k) : Ideal (R ⧸ I) where
  carrier := {x | ∀ y, apolarityPairing I ℓ x y = 0}
  zero_mem' y := by simp
  add_mem' hx hy y := by simp [map_add, hx y, hy y]
  smul_mem' r x hx y := by
    rw [smul_eq_mul, mul_comm r x, apolarityPairing_assoc]
    exact hx (r * y)

theorem mem_apolarityKernel_iff (I : Ideal R) (ℓ : (R ⧸ I) →ₗ[k] k) (x : R ⧸ I) :
    x ∈ apolarityKernel I ℓ ↔ ∀ y : R ⧸ I, apolarityPairing I ℓ x y = 0 :=
  Iff.rfl

/-- Nondegeneracy of the apolarity pairing holds iff `apolarityKernel I ℓ = ⊥`. -/
theorem apolarityKernel_eq_bot_iff (I : Ideal R) (ℓ : (R ⧸ I) →ₗ[k] k) :
    apolarityKernel I ℓ = ⊥ ↔ ∀ x : R ⧸ I, (∀ y : R ⧸ I, apolarityPairing I ℓ x y = 0) → x = 0 := by
  rw [Submodule.eq_bot_iff]
  rfl

/-- Compatibility between Wiebe–Scheja–Storch colon multipliers (`C *ᵥ g = a`) and apolarity
annihilation modulo `Ideal.span (Set.range a)`. -/
theorem apolarityPairing_det_mul_eq_zero_of_mulVec_eq
    {ι : Type*} [Fintype ι] [DecidableEq ι]
    (C : Matrix ι ι R) (a g : ι → R) (h : C *ᵥ g = a)
    (ℓ : (R ⧸ Ideal.span (Set.range a)) →ₗ[k] k)
    {x : R} (hx : x ∈ Ideal.span (Set.range g))
    (y : R ⧸ Ideal.span (Set.range a)) :
    apolarityPairing (Ideal.span (Set.range a)) ℓ
      (Ideal.Quotient.mk (Ideal.span (Set.range a)) (C.det * x)) y = 0 :=
  apolarityPairing_mk_eq_zero_of_mem _ ℓ (det_mul_mem_span_of_mem_span C a g h hx) y

end Apolarity

end RingTheory
