/-
Copyright (c) 2026 Qamar Munawer. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Qamar Munawer
-/
module

public import Mathlib.LinearAlgebra.Matrix.Adjugate
public import Mathlib.RingTheory.Ideal.Span

/-!
# Koszul Complex and Wiebe–Scheja–Storch Determinant Colon Bridge

This file establishes the universal commutative-algebra bridge connecting change-of-generator
matrices (`C *ᵥ g = a`) and adjugate determinants (`C.det ∈ (a) : (g)`), together with the
low-degree Koszul boundary vanishing identity `d_1 ∘ d_2 = 0`.

## Main results

* `RingTheory.adjugate_mulVec_eq_det_smul`: `C.adjugate *ᵥ a = C.det • g` whenever `C *ᵥ g = a`.
* `RingTheory.det_mul_mem_span_of_mulVec_eq`: `C.det * g i ∈ Ideal.span (Set.range a)`.
* `RingTheory.det_mul_mem_span_of_mem_span`: universal Wiebe–Scheja–Storch colon inclusion,
  `x ∈ Ideal.span (Set.range g) → C.det * x ∈ Ideal.span (Set.range a)`.
* `RingTheory.koszulD1_comp_koszulD2`: exact Koszul identity `d_1(d_2(M)) = 0` over any
  commutative ring.
-/

@[expose] public section

namespace RingTheory

open Matrix

section WiebeBridge

variable {R : Type*} [CommRing R] {ι : Type*} [Fintype ι] [DecidableEq ι]

/-- If a matrix `C` transforms generators `g` into `a` via `C *ᵥ g = a`, then multiplying `a`
on the left by `C.adjugate` yields `C.det • g`. -/
theorem adjugate_mulVec_eq_det_smul (C : Matrix ι ι R) (a g : ι → R)
    (h : C *ᵥ g = a) :
    C.adjugate *ᵥ a = C.det • g := by
  rw [← h, Matrix.mulVec_mulVec, Matrix.adjugate_mul, Matrix.smul_mulVec, Matrix.one_mulVec]

/-- Each transformed generator product `C.det * g i` lies in `Ideal.span (Set.range a)`
whenever `C *ᵥ g = a`. -/
theorem det_mul_mem_span_of_mulVec_eq (C : Matrix ι ι R) (a g : ι → R)
    (h : C *ᵥ g = a) (i : ι) :
    C.det * g i ∈ Ideal.span (Set.range a) := by
  have hrow := congr_fun (adjugate_mulVec_eq_det_smul C a g h) i
  have hsum : (C.adjugate *ᵥ a) i ∈ Ideal.span (Set.range a) := by
    change ∑ j : ι, C.adjugate i j * a j ∈ Ideal.span (Set.range a)
    exact Submodule.sum_mem _ fun j _ =>
      Ideal.mul_mem_left _ (C.adjugate i j) (Ideal.subset_span ⟨j, rfl⟩)
  rwa [hrow, Pi.smul_apply, smul_eq_mul] at hsum

/-- **Universal Wiebe–Scheja–Storch colon inclusion**: if `C *ᵥ g = a`, then `C.det` multiplies
every element `x ∈ Ideal.span (Set.range g)` into `Ideal.span (Set.range a)`. -/
theorem det_mul_mem_span_of_mem_span (C : Matrix ι ι R) (a g : ι → R)
    (h : C *ᵥ g = a) {x : R} (hx : x ∈ Ideal.span (Set.range g)) :
    C.det * x ∈ Ideal.span (Set.range a) := by
  change x ∈ Submodule.span R (Set.range g) at hx
  induction hx using Submodule.span_induction with
  | mem y hy =>
    obtain ⟨i, rfl⟩ := hy
    exact det_mul_mem_span_of_mulVec_eq C a g h i
  | zero =>
    rw [mul_zero]
    exact Ideal.zero_mem _
  | add u v _ _ hu hv =>
    rw [mul_add]
    exact Ideal.add_mem _ hu hv
  | smul r u _ hu =>
    rw [smul_eq_mul, mul_left_comm]
    exact Ideal.mul_mem_left _ r hu

end WiebeBridge

section KoszulBoundary

variable {R : Type*} [CommRing R] {ι : Type*} [Fintype ι]

/-- Degree-1 Koszul differential `d_1(v) = ∑ i, a i * v i`. -/
def koszulD1 (a v : ι → R) : R :=
  ∑ i : ι, a i * v i

/-- Degree-2 Koszul differential `d_2(M)_i = ∑ j, a j * (M i j - M j i)` from the canonical
skew-symmetrization of a matrix `M`. -/
def koszulD2 (a : ι → R) (M : Matrix ι ι R) : ι → R :=
  fun i => ∑ j : ι, a j * (M i j - M j i)

/-- **Koszul complex identity `d_1 ∘ d_2 = 0`** over any commutative ring `R`. -/
theorem koszulD1_comp_koszulD2 (a : ι → R) (M : Matrix ι ι R) :
    koszulD1 a (koszulD2 a M) = 0 := by
  unfold koszulD1 koszulD2
  have hsplit :
      (∑ i : ι, a i * ∑ j : ι, a j * (M i j - M j i)) =
        (∑ i : ι, ∑ j : ι, a i * a j * M i j) -
          (∑ i : ι, ∑ j : ι, a i * a j * M j i) := by
    rw [← Finset.sum_sub_distrib]
    refine Finset.sum_congr rfl fun i _ => ?_
    rw [Finset.mul_sum, ← Finset.sum_sub_distrib]
    refine Finset.sum_congr rfl fun j _ => ?_
    rw [mul_sub, mul_sub, mul_assoc, mul_assoc]
  rw [hsplit]
  conv_rhs =>
    rw [← sub_self (∑ i : ι, ∑ j : ι, a i * a j * M i j)]
  congr 1
  rw [Finset.sum_comm]
  refine Finset.sum_congr rfl fun j _ => Finset.sum_congr rfl fun i _ => ?_
  rw [mul_comm (a i) (a j)]

/-- For a skew-symmetric matrix `Mᵀ = -M`, `2 * d_1(M a) = 0` over any commutative ring. -/
theorem two_mul_koszulD1_skew (a : ι → R) (M : Matrix ι ι R) (hM : Mᵀ = -M) :
    2 * koszulD1 a (fun i => ∑ j : ι, a j * M i j) = 0 := by
  have hMij : ∀ i j, M j i = -M i j := fun i j => by
    have h := congr_fun (congr_fun hM i) j
    simpa [Matrix.transpose_apply, Matrix.neg_apply] using h
  have hd : koszulD2 a M = fun i => 2 * ∑ j : ι, a j * M i j := by
    ext i
    unfold koszulD2
    rw [Finset.mul_sum]
    refine Finset.sum_congr rfl fun j _ => ?_
    rw [hMij i j, sub_neg_eq_add, ← two_mul, mul_left_comm]
  have hcomp := koszulD1_comp_koszulD2 a M
  rw [hd] at hcomp
  rw [← hcomp]
  simp only [koszulD1, Finset.mul_sum]
  refine Finset.sum_congr rfl fun i _ => ?_
  exact Finset.sum_congr rfl fun j _ => mul_left_comm 2 (a i) (a j * M i j)

end KoszulBoundary

end RingTheory
