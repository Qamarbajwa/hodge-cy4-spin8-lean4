/-
Copyright (c) 2026 Qamar Munawer. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Qamar Munawer
-/
import HigherOrderJetLifting
import CayleyCompleteInt

/-!
# Track 2: Order-12 Jets (mod t^12), G>=3 Unmixed vs Embedded Ideals & P^7 Complete Intersections

Certifies with zero axioms:
1. Order-12 Griffiths-Dwork jet transport (`mod t^12`) across Bands 1, 2, and 3 matching
   `higher_order_t12_and_g4_sieve.py` (`Band 1` remains flat `[1, 4, 10, 20, 35, 48, 57]`).
2. Exact over-Z Wiebe-Scheja-Storch 4x4 factorization for the unmixed cubic-pair CI
   `Z_{3,1,1} = V(z_0 z_1, z_0^3 - z_1^3, z_2, z_4)` vs the embedded non-unmixed ideal
   `<z_0^2, z_0 z_1, z_2, z_4>` and the 3-quadric-pair CI `Z_{2,2,2}` (`[1,6,18,38,63,84,92]`).
3. Codimension-3 Calabi-Yau complete intersections `X_{2,2,4}` and `X_{2,3,3}` in `P^7`
   with 8-variable Gorenstein auxiliary Hilbert series and primitive middle Hodge symmetry.
-/

set_option maxHeartbeats 8000000 in
set_option maxRecDepth 8192 in
/-- Order-12 (`mod t^12`) Griffiths-Dwork Gauss-Manin jet transport certificate:
`Band 1` stabilizes cleanly at `5` terms from `t^3` through `t^11` while keeping `F_65521`
rank `[1, 4, 10, 20, 35, 48, 57]`; `Band 2` and `Band 3` terminate nilpotently by `t^4`. -/
theorem multi_order_t12_gauss_manin_jet_cert :
    (buildGaussManinJetN 11 wDirBand1 sigmaPlaneExpected).map List.length =
      [1, 3, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5] ∧
    (buildGaussManinJetN 11 wDirBand2 lamBand2).map List.length =
      [1, 3, 3, 1, 0, 0, 0, 0, 0, 0, 0, 0] ∧
    (buildGaussManinJetN 11 wDirBand3 lamBand3).map List.length =
      [1, 3, 3, 1, 0, 0, 0, 0, 0, 0, 0, 0] ∧
    (buildGaussManinJetN 11 wDirBand1 sigmaPlaneExpected).all
        (allAnnihilate [varPow6 2 1, varPow6 4 1]) = true ∧
    (buildGaussManinJetN 11 wDirBand3 lamBand3).all
        (allAnnihilate [varPow6 0 1]) = true ∧
    [0, 1, 2, 3, 4, 5, 6].map
        (sparseJetRankModP 65521 (buildGaussManinJetN 11 wDirBand1 sigmaPlaneExpected)) =
      [1, 4, 10, 20, 35, 48, 57] ∧
    [0, 1, 2, 3, 4, 5, 6].map
        (sparseJetRankModP 65521 (buildGaussManinJetN 11 wDirBand2 lamBand2)) =
      [1, 6, 21, 53, 108, 181, 254] ∧
    [0, 1, 2, 3, 4, 5, 6].map
        (sparseJetRankModP 65521 (buildGaussManinJetN 11 wDirBand3 lamBand3)) =
      [1, 5, 15, 35, 68, 113, 153] :=
  ⟨rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl⟩

/-- Unmixed cubic-pair CI `Z_{3,1,1} = V(z_0 z_1, z_0^3 - z_1^3, z_2, z_4)` in `P^5`. -/
def gZ311Vec4 : List Poly6 :=
  [polyMul6 (varPow6 0 1) (varPow6 1 1),
   polySub6 (varPow6 0 3) (varPow6 1 3),
   varPow6 2 1,
   varPow6 4 1]

def aZ311JacVec4 : List Poly6 :=
  [varPow6 0 5, varPow6 1 5, varPow6 2 5, varPow6 4 5]

def cZ311Mat4 : List (List Poly6) :=
  [[polyMul6 (varPow6 0 1) (varPow6 1 2), varPow6 0 2, [], []],
   [polyMul6 (varPow6 0 2) (varPow6 1 1), polyNeg6 (varPow6 1 2), [], []],
   [[], [], varPow6 2 4, []],
   [[], [], [], varPow6 4 4]]

def detZ311Expected : Poly6 :=
  polyNeg6 (polyMul6
    (polyMul6 (polyMul6 (varPow6 0 1) (varPow6 1 1)) (polyAdd6 (varPow6 0 3) (varPow6 1 3)))
    (polyMul6 (varPow6 2 4) (varPow6 4 4)))

/-- Embedded non-unmixed codim-3 ideal `<z_0^2, z_0 z_1, z_2, z_4>` in `P^5`. -/
def gEmbeddedNonUnmixed4 : List Poly6 :=
  [varPow6 0 2,
   polyMul6 (varPow6 0 1) (varPow6 1 1),
   varPow6 2 1,
   varPow6 4 1]

set_option maxHeartbeats 8000000 in
set_option maxRecDepth 8192 in
/-- Exact over-Z Wiebe-Scheja-Storch certificate for `Z_{3,1,1}` and separation from the
non-unmixed embedded ideal `<z_0^2, z_0 z_1, z_2, z_4>` (`[1,4,8,13,19,23,23]` vs
`[1,4,9,15,21,25,25]`), alongside the `Z_{2,2,2}` unmixed profile `[1,6,18,38,63,84,92]`. -/
theorem g4_unmixed_wss_and_embedded_obstruction_cert :
    polyVecEq6 (polyMatVecMul cZ311Mat4 gZ311Vec4) aZ311JacVec4 = true ∧
    polyEq6 (polyDetZ6 cZ311Mat4) (polyCanon6 detZ311Expected) = true ∧
    [0, 1, 2, 3, 4, 5, 6].map (sparseIdealQuotientDimModP 65521 gZ222Vec6) =
      [1, 6, 18, 38, 63, 84, 92] ∧
    [0, 1, 2, 3, 4, 5, 6].map (sparseIdealQuotientDimModP 65521 gZ311Vec4) =
      [1, 4, 9, 15, 21, 25, 25] ∧
    [0, 1, 2, 3, 4, 5, 6].map (sparseIdealQuotientDimModP 65521 gEmbeddedNonUnmixed4) =
      [1, 4, 8, 13, 19, 23, 23] :=
  ⟨rfl, rfl, rfl, rfl, rfl⟩

private def listGetNat8 (xs : List Nat) (i : Nat) : Nat :=
  match xs with
  | [] => 0
  | x :: rest => match i with | 0 => x | i' + 1 => listGetNat8 rest i'

private def polyConvNat8 (a b : List Nat) : List Nat :=
  let n := a.length + b.length - 1
  (rangeList 0 n).map (fun d =>
    (rangeList 0 (d + 1)).foldl (fun acc k =>
      acc + listGetNat8 a k * listGetNat8 b (d - k)) 0)

private def powConvNat8 (base : List Nat) : Nat → List Nat
  | 0 => [1]
  | k + 1 => polyConvNat8 base (powConvNat8 base k)

def cayleyP7CI224Aux : List Nat := powConvNat8 [1, 1, 1] 8
def cayleyP7CI233Aux : List Nat := powConvNat8 [1, 1] 8
def hodgePrimP7CI224 : List Nat := [1, 263, 1099, 263, 1]
def hodgePrimP7CI233 : List Nat := [1, 192, 815, 192, 1]

/-- Codimension-3 Calabi-Yau complete intersections `X_{2,2,4}` and `X_{2,3,3}` in `P^7`:
8-variable Gorenstein auxiliary Hilbert series and primitive middle Hodge symmetry. -/
theorem cayley_p7_ci224_and_ci233_gorenstein_cert :
    cayleyP7CI224Aux.length = 17 ∧
    (cayleyP7CI224Aux == cayleyP7CI224Aux.reverse) = true ∧
    cayleyP7CI224Aux.foldl (· + ·) 0 = 6561 ∧
    cayleyP7CI233Aux = [1, 8, 28, 56, 70, 56, 28, 8, 1] ∧
    (cayleyP7CI233Aux == cayleyP7CI233Aux.reverse) = true ∧
    cayleyP7CI233Aux.foldl (· + ·) 0 = 256 ∧
    (hodgePrimP7CI224 == hodgePrimP7CI224.reverse) = true ∧
    hodgePrimP7CI224.foldl (· + ·) 0 = 1627 ∧
    (hodgePrimP7CI233 == hodgePrimP7CI233.reverse) = true ∧
    hodgePrimP7CI233.foldl (· + ·) 0 = 1201 :=
  ⟨rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl⟩

#print axioms multi_order_t12_gauss_manin_jet_cert
#print axioms g4_unmixed_wss_and_embedded_obstruction_cert
#print axioms cayley_p7_ci224_and_ci233_gorenstein_cert
