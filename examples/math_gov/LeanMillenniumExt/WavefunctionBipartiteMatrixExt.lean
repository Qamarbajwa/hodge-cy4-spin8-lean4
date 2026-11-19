/-
Copyright (c) 2026 Qamar Munawer. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Qamar Munawer
-/
import WiebeSchejaStorch

/-!
# Experiment 10 (Wall 3): Bipartite Wave-Function Correspondence Matrix Algebra on A x A

Reinterprets the `784`-component (`28 x 28`) bipartite Hodge `(2,2)` wave function on Mumford's
`End_Q(A) = Q` product `A x A` as a closed strict-matrix correspondence algebra on `/\^2 Z^8`:
1. Exact cup-product Lefschetz pairing `B_2` and Hodge-Riemann sign flip:
   - `E_2 = /\^2(E_real)` is symmetric, involutive (`E_2^2 = I_28`), and commutes with
     `Q_0, Q_sd, Q_asd, Q_ric`.
   - `B_2(u, v) = <u ^ v ^ Theta^2, vol_8>` satisfies `B_2^T = B_2` and `B_2 E_2 = 2 Q_0 - 2 I_28`
     (`+6` on `Theta` vs. `-2` on all `27` primitive `2`-forms), with separable divisor lift
     `C_th = thVec * thVec^T = 4 E_2 Q_0`.
2. Bose-Mesner correspondence algebra & `2D -> 1D` chiral single-generator reduction:
   - Closed `2`-dim divisor algebra `A_div = span{T_th, T_dd}` and `3`-dim parity-even algebra
     `A_even = span{T_th, T_dd, T_r0}`.
   - Single-generator chiral closure `8 T_r0 = 32 T_dd + 4 T_th - 3 T_ch^2`, reducing the
     `2`-dim non-divisor obstruction to the single parity-odd generator `T_ch`.
3. `Z_2`-graded superoperator split (`16_+ + 12_-`), reduced density parity blindness
   (`E_+ (T_ch T_ch^T) E_- = 0`), `576` equipartition on `Q_sd`/`Q_asd`, and observable-half
   reconstruction lift `K_obs + K_obs^T = 4 T_ch`.
4. Spectral trace moments, semigroup oscillation `T_ch^3 = 64 T_ch`, and commutativity with both
   `D^(2)(J_Mum3)` and `/\^2(G_Mum9)`.
-/

-- ---------------------------------------------------------------------------
-- Dense & Sparse Integer Matrix Helpers (Zero Acc.rec, <= 100 chars/line)
-- ---------------------------------------------------------------------------

private def intMatCell (m : List (List Int)) (i j : Nat) : Int :=
  ((m.drop i).headD []).drop j |>.headD 0

private def intEye (n : Nat) : List (List Int) :=
  (rangeList 0 n).map fun i =>
    (rangeList 0 n).map fun j => if i == j then 1 else 0

private def kronMat (a b : List (List Int)) : List (List Int) :=
  let ra := a.length
  let ca := ((a.drop 0).headD []).length
  let rb := b.length
  let cb := ((b.drop 0).headD []).length
  (rangeList 0 (ra * rb)).map fun i =>
    (rangeList 0 (ca * cb)).map fun j =>
      intMatCell a (i / rb) (j / cb) * intMatCell b (i % rb) (j % cb)

private abbrev SpVec := List (Nat × Int)
private abbrev SpMat := List SpVec

private def spInsert (idx : Nat) (v : Int) : SpVec → SpVec
  | [] => if intEq v 0 then [] else [(idx, v)]
  | (i0, v0) :: rest =>
    if idx == i0 then
      let nv := v + v0
      if intEq nv 0 then rest else (i0, nv) :: rest
    else if Nat.blt idx i0 then
      if intEq v 0 then (i0, v0) :: rest else (idx, v) :: (i0, v0) :: rest
    else
      (i0, v0) :: spInsert idx v rest

private def spAddGo : Nat → SpVec → SpVec → SpVec
  | 0, a, _ => a
  | fuel + 1, a, b =>
    match a with
    | [] => b
    | (i1, v1) :: r1 =>
      match b with
      | [] => a
      | (i2, v2) :: r2 =>
        if i1 == i2 then
          let s := v1 + v2
          let tail := spAddGo fuel r1 r2
          if intEq s 0 then tail else (i1, s) :: tail
        else if Nat.blt i1 i2 then
          (i1, v1) :: spAddGo fuel r1 b
        else
          (i2, v2) :: spAddGo fuel a r2

private def spAdd (a b : SpVec) : SpVec :=
  if a.isEmpty then b
  else if b.isEmpty then a
  else spAddGo (a.length + b.length + 1) a b

private def spScale (s : Int) (v : SpVec) : SpVec :=
  if intEq s 0 then [] else v.map fun (i, c) => (i, s * c)

private def spVecEq : SpVec → SpVec → Bool
  | [], [] => true
  | [], _ :: _ => false
  | _ :: _, [] => false
  | (i1, v1) :: r1, (i2, v2) :: r2 => (i1 == i2) && intEq v1 v2 && spVecEq r1 r2

private def spVecLookup (idx : Nat) : SpVec → Int
  | [] => 0
  | (i0, v0) :: rest =>
    if idx == i0 then v0
    else if Nat.blt idx i0 then 0
    else spVecLookup idx rest

private def spMatEq (a b : SpMat) : Bool :=
  (a.length == b.length) && (List.zipWith spVecEq a b).all id

private def spMatScale (s : Int) (a : SpMat) : SpMat :=
  a.map (spScale s)

private def spMatAdd (a b : SpMat) : SpMat :=
  List.zipWith spAdd a b

private def spMatSub (a b : SpMat) : SpMat :=
  List.zipWith (fun r1 r2 => spAdd r1 (spScale (-1) r2)) a b

private def spIsZeroMat (a : SpMat) : Bool :=
  a.all List.isEmpty

private def spEye (n : Nat) : SpMat :=
  (rangeList 0 n).map fun i => [(i, 1)]

private def spTrace (a : SpMat) : Int :=
  (rangeList 0 a.length).foldl (fun acc i => acc + spVecLookup i ((a.drop i).headD [])) 0

private def spMatMul (a b : SpMat) : SpMat :=
  a.map fun rowA =>
    rowA.foldl (fun acc (k, aik) =>
      let rowB := (b.drop k).headD []
      if rowB.isEmpty then acc else spAdd acc (spScale aik rowB)) []

private def spMatDiv (d : Int) (a : SpMat) : SpMat :=
  a.map fun row => row.foldr (fun (j, v) acc =>
    let q := v / d
    if intEq q 0 then acc else (j, q) :: acc) []

private def spMatTranspose (n : Nat) (m : SpMat) : SpMat :=
  (rangeList 0 n).map fun j =>
    (rangeList 0 m.length).foldl (fun row i =>
      let v := spVecLookup j ((m.drop i).headD [])
      if intEq v 0 then row else row ++ [(i, v)]) []

private def spMatFrob2 (m : SpMat) : Int :=
  m.foldl (fun acc row => acc + row.foldl (fun s (_, v) => s + v * v) 0) 0

-- ---------------------------------------------------------------------------
-- Mumford Representation, Exterior Space /\^2(Z^8), E_2, B_2, and Casimirs
-- ---------------------------------------------------------------------------

private def matEps2 : List (List Int) := [[0, 1], [-1, 0]]
private def matH2 : List (List Int) := [[1, 0], [0, -1]]
private def matE2 : List (List Int) := [[0, 1], [0, 0]]
private def matF2 : List (List Int) := [[0, 0], [1, 0]]

private def matEReal : List (List Int) :=
  kronMat matEps2 (intEye 4)

private def jPlusMats : List (List (List Int)) :=
  [[[0, -1, 0, 0], [1, 0, 0, 0], [0, 0, 0, -1], [0, 0, 1, 0]],
   [[0, 0, -1, 0], [0, 0, 0, 1], [1, 0, 0, 0], [0, -1, 0, 0]],
   [[0, 0, 0, -1], [0, 0, -1, 0], [0, 1, 0, 0], [1, 0, 0, 0]]]

private def jMinusMats : List (List (List Int)) :=
  [[[0, -1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 1], [0, 0, -1, 0]],
   [[0, 0, -1, 0], [0, 0, 0, -1], [1, 0, 0, 0], [0, 1, 0, 0]],
   [[0, 0, 0, -1], [0, 0, 1, 0], [0, -1, 0, 0], [1, 0, 0, 0]]]

private def gensSl2 : List (List (List Int)) :=
  [matH2, matE2, matF2].map fun x => kronMat x (intEye 4)

private def gensSu2P : List (List (List Int)) :=
  jPlusMats.map fun a => kronMat (intEye 2) a

private def gensSu2M : List (List (List Int)) :=
  jMinusMats.map fun b => kronMat (intEye 2) b

private def pairs28 : List (Nat × Nat) :=
  (rangeList 0 8).foldl (fun acc a =>
    (rangeList (a + 1) (8 - a - 1)).foldl (fun acc2 b => acc2 ++ [(a, b)]) acc) []

private def pairIdx28Go (a b idx : Nat) : List (Nat × Nat) → Nat
  | [] => 0
  | (x, y) :: rest => if x == a && y == b then idx else pairIdx28Go a b (idx + 1) rest

private def pairIdx28 (a b : Nat) : Nat :=
  pairIdx28Go a b 0 pairs28

private def ext2Sp (mat8 : List (List Int)) : SpMat :=
  let cols := pairs28.map fun tup =>
    let (a, b) := tup
    let addCol (acc : SpVec) (pos : Nat) : SpVec :=
      let i := if pos == 0 then a else b
      let other := if pos == 0 then b else a
      (rangeList 0 8).foldl (fun acc2 j =>
        let v := intMatCell mat8 j i
        if intEq v 0 || j == other then acc2
        else
          let (lo, hi, sgn) := if j < other then (j, other, 1) else (other, j, -1)
          let sPos := if pos == 0 then sgn else -sgn
          spInsert (pairIdx28 lo hi) (v * sPos) acc2) acc
    addCol (addCol [] 0) 1
  (rangeList 0 28).map fun r =>
    (rangeList 0 28).foldl (fun row c =>
      let val := spVecLookup r ((cols.drop c).headD [])
      if intEq val 0 then row else row ++ [(c, val)]) []

private def wedge2GroupSp (g8 : List (List Int)) : SpMat :=
  pairs28.map fun (p, q) =>
    (rangeList 0 28).foldl (fun row c =>
      let (a, b) := (pairs28.drop c).headD (0, 0)
      let v := intMatCell g8 p a * intMatCell g8 q b - intMatCell g8 p b * intMatCell g8 q a
      if intEq v 0 then row else row ++ [(c, v)]) []

private def matE2_28 : SpMat :=
  wedge2GroupSp matEReal

private def casimirOps28 : SpMat × SpMat × SpMat :=
  let ms := gensSl2.map ext2Sp
  let mH := ms.headD []
  let mE := (ms.drop 1).headD []
  let mF := (ms.drop 2).headD []
  let cSl2 := spMatAdd (spMatMul mH mH) (spMatScale 2 (spMatAdd (spMatMul mE mF) (spMatMul mF mE)))
  let sumSq (gs : List (List (List Int))) : SpMat :=
    gs.foldl (fun acc g =>
      let dg := ext2Sp g
      spMatAdd acc (spMatScale (-1) (spMatMul dg dg))) (List.replicate 28 [])
  (cSl2, sumSq gensSu2P, sumSq gensSu2M)

private def casimirProjs4 : SpMat × SpMat × SpMat × SpMat :=
  let (cSl2, cp, cm) := casimirOps28
  let eig8 := spMatScale 8 (spEye 28)
  let oSl2 := spMatSub eig8 cSl2
  let oP := spMatSub eig8 cp
  let oM := spMatSub eig8 cm
  let q0 := spMatDiv 128 (spMatMul oSl2 (spMatMul oP oM))
  let qSd := spMatDiv 128 (spMatMul cSl2 (spMatMul cp oM))
  let qAsd := spMatDiv 128 (spMatMul cSl2 (spMatMul oP cm))
  let qRic := spMatDiv 128 (spMatMul oSl2 (spMatMul cp cm))
  (q0, qSd, qAsd, qRic)

private def thetaPairsList : List ((Nat × Nat) × Int) :=
  (rangeList 0 8).foldl (fun acc i =>
    (rangeList (i + 1) (8 - i - 1)).foldl (fun acc2 j =>
      let v := intMatCell matEReal i j
      if intEq v 0 then acc2 else acc2 ++ [((i, j), v)]) acc) []

private def theta2QuadTerms : List ((Nat × Nat × Nat × Nat) × Int) :=
  thetaPairsList.foldl (fun acc ((a, b), c1) =>
    thetaPairsList.foldl (fun acc2 ((p, q), c2) =>
      if a == p || a == q || b == p || b == q then acc2
      else acc2 ++ [((a, b, p, q), c1 * c2)]) acc) []

private def invSign8 (l : List Nat) : Int :=
  let rec goInv : List Nat → Nat
    | [] => 0
    | x :: xs =>
      let c := xs.foldl (fun acc y => if Nat.blt y x then acc + 1 else acc) 0
      c + goInv xs
  if goInv l % 2 == 0 then 1 else -1

private def matB2_28 : SpMat :=
  let t2 := theta2QuadTerms
  pairs28.map fun (a, b) =>
    (rangeList 0 28).foldl (fun row c =>
      let (p, q) := (pairs28.drop c).headD (0, 0)
      if a == p || a == q || b == p || b == q then row
      else
        let val := t2.foldl (fun acc ((x0, x1, x2, x3), coeff) =>
          if a == x0 || a == x1 || a == x2 || a == x3 ||
             b == x0 || b == x1 || b == x2 || b == x3 ||
             p == x0 || p == x1 || p == x2 || p == x3 ||
             q == x0 || q == x1 || q == x2 || q == x3 then acc
          else acc + coeff * invSign8 [a, b, p, q, x0, x1, x2, x3]) 0
        if intEq val 0 then row else row ++ [(c, val)]) []

private def thVec28 : SpVec :=
  (rangeList 0 8).foldl (fun acc i =>
    (rangeList (i + 1) (8 - i - 1)).foldl (fun acc2 j =>
      let v := intMatCell matEReal i j - intMatCell matEReal j i
      if intEq v 0 then acc2 else spInsert (pairIdx28 i j) v acc2) acc) []

private def spOuter28 (u v : SpVec) : SpMat :=
  (rangeList 0 28).map fun r =>
    let ur := spVecLookup r u
    if intEq ur 0 then [] else spScale ur v

-- ---------------------------------------------------------------------------
-- Theorem 1: Cup-Product Lefschetz Pairing & Hodge-Riemann Sign Flip
-- ---------------------------------------------------------------------------

private def checkLefschetzHodgeRiemann : Bool :=
  let e2 := matE2_28
  let b2 := matB2_28
  let i28 := spEye 28
  let (q0, qSd, qAsd, qRic) := casimirProjs4
  let qs := [q0, qSd, qAsd, qRic]
  let e2Sym := spMatEq e2 (spMatTranspose 28 e2)
  let e2Inv := spMatEq (spMatMul e2 e2) i28
  let qOk := qs.all fun q =>
    spMatEq q (spMatTranspose 28 q) && spMatEq (spMatMul e2 q) (spMatMul q e2)
  let b2Sym := spMatEq b2 (spMatTranspose 28 b2)
  let mBe := spMatMul b2 e2
  let mBeExact := spMatEq mBe (spMatSub (spMatScale 2 q0) (spMatScale 2 i28))
  let hrSplit :=
    spMatEq (spMatMul mBe q0) (spMatScale 6 q0) &&
    spMatEq (spMatMul mBe qSd) (spMatScale (-2) qSd) &&
    spMatEq (spMatMul mBe qAsd) (spMatScale (-2) qAsd) &&
    spMatEq (spMatMul mBe qRic) (spMatScale (-2) qRic)
  let cTh := spOuter28 thVec28 thVec28
  let cThMatch := spMatEq cTh (spMatScale 4 (spMatMul e2 q0))
  e2Sym && e2Inv && qOk && b2Sym && mBeExact && hrSplit && cThMatch

set_option maxHeartbeats 16000000 in
set_option maxRecDepth 8192 in
/-- Certifies the exact `28 x 28` cup-product Lefschetz pairing `B_2` and Hodge-Riemann sign flip:
`E_2^T = E_2`, `E_2^2 = I_28`, `B_2^T = B_2`, `B_2 E_2 = 2 Q_0 - 2 I_28` (`+6` on `Theta` vs. `-2`
on all `27` primitive `2`-forms), and separable divisor lift `C_th = 4 E_2 Q_0`. -/
theorem wf_bipartite_lefschetz_hodge_riemann_pairing_cert :
    checkLefschetzHodgeRiemann = true :=
  rfl

-- ---------------------------------------------------------------------------
-- Theorem 2: Bose-Mesner Correspondence Algebra & 2D -> 1D Chiral Reduction
-- ---------------------------------------------------------------------------

private def checkCorrespondenceChiralReduction : Bool :=
  let e2 := matE2_28
  let b2 := matB2_28
  let i28 := spEye 28
  let (q0, qSd, qAsd, qRic) := casimirProjs4
  let cTh := spOuter28 thVec28 thVec28
  let cDd := spMatScale (-2) e2
  let tTh := spMatMul b2 cTh
  let tDd := spMatMul b2 cDd
  let mCh := spMatSub qSd qAsd
  let mR0 := spMatSub (spMatAdd qSd qAsd) (spMatScale 2 qRic)
  let tCh := spMatMul b2 (spMatMul e2 mCh)
  let tR0 := spMatMul b2 (spMatMul e2 mR0)
  let exactDefs :=
    spMatEq tTh (spMatScale 24 q0) &&
    spMatEq tDd (spMatSub (spMatScale 4 i28) (spMatScale 4 q0)) &&
    spMatEq tCh (spMatScale (-2) mCh) &&
    spMatEq tR0 (spMatScale (-2) mR0)
  let aDivClosed :=
    spMatEq (spMatMul tTh tTh) (spMatScale 96 tTh) &&
    spMatEq (spMatMul tTh tDd) (spMatScale (-12) tTh) &&
    spMatEq (spMatMul tDd tDd) (spMatAdd (spMatScale 4 tDd) (spMatScale 2 tTh))
  let aEvenClosed :=
    spIsZeroMat (spMatMul tR0 tTh) &&
    spMatEq (spMatMul tR0 tDd) (spMatScale 4 tR0) &&
    spMatEq (spMatMul tR0 tR0)
      (spMatAdd (spMatAdd (spMatScale 32 tDd) (spMatScale 4 tTh)) (spMatScale 8 tR0))
  let tChSq := spMatMul tCh tCh
  let chiralClosure :=
    spMatEq (spMatScale 8 tR0)
      (spMatSub (spMatAdd (spMatScale 32 tDd) (spMatScale 4 tTh)) (spMatScale 3 tChSq)) &&
    spIsZeroMat (spMatMul tCh tTh) &&
    spMatEq (spMatMul tCh tDd) (spMatScale 4 tCh) &&
    spMatEq (spMatMul tCh tR0) (spMatScale (-8) tCh)
  let minPolys :=
    spIsZeroMat (spMatMul tCh (spMatSub tChSq (spMatScale 64 i28))) &&
    spIsZeroMat (spMatMul tR0 (spMatMul (spMatAdd tR0 (spMatScale 8 i28))
      (spMatSub tR0 (spMatScale 16 i28))))
  exactDefs && aDivClosed && aEvenClosed && chiralClosure && minPolys

set_option maxHeartbeats 16000000 in
set_option maxRecDepth 8192 in
/-- Certifies the closed `28 x 28` Bose-Mesner correspondence algebra (`A_div` `2`-dim, `A_even`
`3`-dim) and exact `2D -> 1D` chiral reduction `8 T_r0 = 32 T_dd + 4 T_th - 3 T_ch^2`, reducing the
non-divisor `A x A` obstruction to the single generator `T_ch`. -/
theorem wf_bipartite_correspondence_chiral_reduction_cert :
    checkCorrespondenceChiralReduction = true :=
  rfl

-- ---------------------------------------------------------------------------
-- Theorem 3: Z_2 Superoperator (16_+ + 12_-), Density Blindness & Half-Lift
-- ---------------------------------------------------------------------------

private def refl4 : List (List Int) :=
  kronMat (intEye 2) [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, -1]]

private def checkZ2SuperoperatorAndBlindness : Bool :=
  let (q0, qSd, qAsd, qRic) := casimirProjs4
  let i28 := spEye 28
  let tTh := spMatScale 24 q0
  let tDd := spMatSub (spMatScale 4 i28) (spMatScale 4 q0)
  let tCh := spMatScale (-2) (spMatSub qSd qAsd)
  let tR0 := spMatScale (-2) (spMatSub (spMatAdd qSd qAsd) (spMatScale 2 qRic))
  let pFlip := wedge2GroupSp refl4
  let ep := spMatAdd i28 pFlip
  let em := spMatSub i28 pFlip
  let flipOk :=
    spMatEq (spMatMul pFlip pFlip) i28 &&
    intEq (spTrace pFlip) 4 &&
    spMatEq (spMatMul ep ep) (spMatScale 2 ep) &&
    spMatEq (spMatMul em em) (spMatScale 2 em) &&
    spIsZeroMat (spMatMul ep em)
  let evenBlockDiag := [tTh, tDd, tR0].all fun m =>
    spIsZeroMat (spMatMul ep (spMatMul m em)) &&
    spIsZeroMat (spMatMul em (spMatMul m ep))
  let chEquip := [qSd, qAsd].all fun q =>
    intEq (spMatFrob2 (spMatMul ep (spMatMul q ep))) 576 &&
    intEq (spMatFrob2 (spMatMul em (spMatMul q em))) 576 &&
    intEq (spMatFrob2 (spMatMul ep (spMatMul q em))) 576 &&
    intEq (spMatFrob2 (spMatMul em (spMatMul q ep))) 576
  let chOffDiag :=
    spIsZeroMat (spMatMul ep (spMatMul tCh ep)) &&
    spIsZeroMat (spMatMul em (spMatMul tCh em)) &&
    intEq (spMatFrob2 (spMatMul ep (spMatMul tCh em))) 9216 &&
    intEq (spMatFrob2 (spMatMul em (spMatMul tCh ep))) 9216
  let rhoCh := spMatMul tCh (spMatTranspose 28 tCh)
  let rhoBlind :=
    spMatEq rhoCh (spMatMul tCh tCh) &&
    spMatEq rhoCh (spMatScale 16 (spMatAdd qSd qAsd)) &&
    spMatEq (spMatMul pFlip (spMatMul rhoCh pFlip)) rhoCh &&
    spIsZeroMat (spMatMul ep (spMatMul rhoCh em))
  let kObs := spMatMul ep (spMatMul tCh em)
  let halfLift := spMatEq (spMatAdd kObs (spMatTranspose 28 kObs)) (spMatScale 4 tCh)
  flipOk && evenBlockDiag && chEquip && chOffDiag && rhoBlind && halfLift

set_option maxHeartbeats 16000000 in
set_option maxRecDepth 8192 in
/-- Certifies the `Z_2`-graded superoperator split `16_+ (+) 12_-`: parity-even `T_th, T_dd, T_r0`
are block-diagonal, `Q_sd`/`Q_asd` split `25/25/25/25` (`576` Frobenius squared), `T_ch` is `100%`
off-diagonal (`9216`), `rho_ch = T_ch T_ch^T` is parity-blind, and `K_obs + K_obs^T = 4 T_ch`. -/
theorem wf_bipartite_z2_superoperator_and_density_blindness_cert :
    checkZ2SuperoperatorAndBlindness = true :=
  rfl

-- ---------------------------------------------------------------------------
-- Theorem 4: Trace Moments, Semigroup Oscillation & Moduli Commutativity
-- ---------------------------------------------------------------------------

private def jMum3Mat : List (List Int) :=
  kronMat [[4, 5], [-5, -4]] (intEye 4)

private def gMum9Mat : List (List Int) :=
  kronMat [[5, 4], [4, 5]]
    [[1, -2, -2, 0], [2, 1, 0, -2], [2, 0, 1, 2], [0, 2, -2, 1]]

private def checkTracesSemigroupAndModuli : Bool :=
  let (q0, qSd, qAsd, qRic) := casimirProjs4
  let i28 := spEye 28
  let tTh := spMatScale 24 q0
  let tDd := spMatSub (spMatScale 4 i28) (spMatScale 4 q0)
  let tCh := spMatScale (-2) (spMatSub qSd qAsd)
  let tR0 := spMatScale (-2) (spMatSub (spMatAdd qSd qAsd) (spMatScale 2 qRic))
  let q02 := spMatMul q0 q0
  let dd2 := spMatMul tDd tDd
  let dd3 := spMatMul dd2 tDd
  let ch2 := spMatMul tCh tCh
  let ch3 := spMatMul ch2 tCh
  let ch4 := spMatMul ch3 tCh
  let r02 := spMatMul tR0 tR0
  let r03 := spMatMul r02 tR0
  let r04 := spMatMul r03 tR0
  let trOk :=
    intEq (spTrace q0) 4 && intEq (spTrace q02) 16 &&
    intEq (spTrace tDd) 96 && intEq (spTrace dd2) 576 && intEq (spTrace dd3) 0 &&
    intEq (spTrace tCh) 0 && intEq (spTrace ch2) 1152 &&
    intEq (spTrace ch3) 0 && intEq (spTrace ch4) 73728 &&
    intEq (spTrace tR0) 0 && intEq (spTrace r02) 3456 &&
    intEq (spTrace r03) 27648 && intEq (spTrace r04) 663552
  let semiOk :=
    spMatEq ch3 (spMatScale 64 tCh) &&
    spMatEq ch4 (spMatScale 64 ch2)
  let d2J3 := ext2Sp jMum3Mat
  let w2G9 := wedge2GroupSp gMum9Mat
  let modOk := [tTh, tDd, tCh, tR0].all fun op =>
    spMatEq (spMatMul d2J3 op) (spMatMul op d2J3) &&
    spMatEq (spMatMul w2G9 op) (spMatMul op w2G9)
  trOk && semiOk && modOk

set_option maxHeartbeats 16000000 in
set_option maxRecDepth 8192 in
/-- Certifies exact spectral trace moments (`T_dd`, `T_ch`, `T_r0`, `Q_0`), transfer semigroup
oscillation (`T_ch^3 = 64 T_ch`, `T_ch^4 = 64 T_ch^2`), and full moduli commutativity of both
`D^(2)(J_Mum3)` and `/\^2(G_Mum9)` with `{T_th, T_dd, T_ch, T_r0}`. -/
theorem wf_bipartite_transfer_semigroup_and_schmidt_spectrum_cert :
    checkTracesSemigroupAndModuli = true :=
  rfl

#print axioms wf_bipartite_lefschetz_hodge_riemann_pairing_cert
#print axioms wf_bipartite_correspondence_chiral_reduction_cert
#print axioms wf_bipartite_z2_superoperator_and_density_blindness_cert
#print axioms wf_bipartite_transfer_semigroup_and_schmidt_spectrum_cert
