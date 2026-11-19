/-
Copyright (c) 2026 Qamar Munawer. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Qamar Munawer
-/
import MumfordCMSpecializationExt

/-!
# Experiment 7: Indefinite SU(2,2) Lorentzian Boosts & SO(35,35) Weil Light-Cone Invariance

Certifies with zero axioms:
1. Symmetric coupled Pythagorean `SU(2, 2)` boost `G_9 = 9 * g` preserving both the split `(4, 4)`
   Lorentzian metric `eta_8 = -E_8 Phi_8 = diag(1,1,1,1,-1,-1,-1,-1)` and `E_8`:
   `G_9^T eta_8 G_9 = 81 eta_8`, `G_9^T E_8 G_9 = 81 E_8`, `[G_9, Phi_8] = 0`,
   `(G_9 - 27 I_8)(G_9 - 3 I_8) = 0`, exact null light-cone conjugate-half projectors
   `N_+ = G_9 - 3 I_8` and `N_- = 27 I_8 - G_9` (`N_+^T eta_8 N_+ = 0`, `N_-^T eta_8 N_- = 0`),
   and 50/50 light-cone diagonalization of radial boost `G_rad3`.
2. Boosted complex structure `J_27 = (1/3) G_9 E_8 (eta_8 G_9^T eta_8)` and polarization
   `G_pos = -E_8 J_27`: `J_27^2 = -729 I_8`, `J_27^T E_8 J_27 = 729 E_8`, `[J_27, Phi_8] = 0`,
   `(G_pos - 243 I_8)(G_pos - 3 I_8) = 0`, `8` strictly positive Bareiss leading principal
   minors (`det = 27^8`), plus exact cleared-denominator `2 x 2` Matrix Mobius spatial
   projection steps inside the period unit ball (`H_0 -> H_1 -> H_2 -> H_3`).
3. Exhaustive `70 x 70` certification of boosted Hodge Hamiltonian `D_27^(4)` (`D_27(w_Re) = 0`,
   `D_27(w_Im) = 0`, `D_27(Theta^2) = 0`, `D_27(Theta) = 0`, `D_27(D^+_{0,2}) != 0`,
   `D_27 P_192 = 0`, `[D_27, K_Phi] = 0`).
4. Exact `8 x 8` Bareiss determinant `det(G_9) = 9^8`, exact `70`-diagonal trace
   `sum_{|I|=4} det_4(G_9[I,I]) = 1724166` (`81 * 21286`), exact invariance of `w_Re`, `w_Im`,
   `Theta^2` under `/\^4 G_9`, and cup-product preservation on a sheared `SO(35,35)` pair.
-/

-- ---------------------------------------------------------------------------
-- Shared Exact Integer Matrix & 2 x 2 Gaussian Matrix Helpers
-- ---------------------------------------------------------------------------

private def intMatCell (m : List (List Int)) (i j : Nat) : Int :=
  ((m.drop i).headD []).drop j |>.headD 0

private def intMatMul (a b : List (List Int)) : List (List Int) :=
  let nr := a.length
  let nc := ((b.drop 0).headD []).length
  let nk := b.length
  (rangeList 0 nr).map fun i =>
    (rangeList 0 nc).map fun j =>
      (rangeList 0 nk).foldl (fun acc k => acc + intMatCell a i k * intMatCell b k j) 0

private def intEye (n : Nat) : List (List Int) :=
  (rangeList 0 n).map fun i =>
    (rangeList 0 n).map fun j => if i == j then 1 else 0

private def intDiag (ds : List Int) : List (List Int) :=
  let n := ds.length
  (rangeList 0 n).map fun i =>
    (rangeList 0 n).map fun j => if i == j then (ds.drop i).headD 0 else 0

private def intMatScale (c : Int) (m : List (List Int)) : List (List Int) :=
  m.map fun r => r.map fun x => c * x

private def intMatAdd (a b : List (List Int)) : List (List Int) :=
  List.zipWith (fun r1 r2 => List.zipWith (· + ·) r1 r2) a b

private def intMatSub (a b : List (List Int)) : List (List Int) :=
  List.zipWith (fun r1 r2 => List.zipWith (· - ·) r1 r2) a b

private def intMatTranspose (m : List (List Int)) : List (List Int) :=
  let nr := m.length
  let nc := ((m.drop 0).headD []).length
  (rangeList 0 nc).map fun j => (rangeList 0 nr).map fun i => intMatCell m i j

private def intMatEq (a b : List (List Int)) : Bool :=
  (a.length == b.length) &&
  (List.zipWith (fun r1 r2 => (r1.length == r2.length) &&
    (List.zipWith intEq r1 r2).all id) a b).all id

private def isIntMatZero (m : List (List Int)) : Bool :=
  m.all fun r => r.all fun x => intEq x 0

private def intMatTrace (m : List (List Int)) : Int :=
  (rangeList 0 m.length).foldl (fun acc i => acc + intMatCell m i i) 0

private def matE8 : List (List Int) :=
  (rangeList 0 8).map fun i =>
    (rangeList 0 8).map fun j =>
      if (i % 2 == 0) && (j == i + 1) then 1
      else if (j % 2 == 0) && (i == j + 1) then -1
      else 0

private def matPhi8 : List (List Int) :=
  (rangeList 0 8).map fun i =>
    (rangeList 0 8).map fun j =>
      if (i == 0 && j == 1) || (i == 2 && j == 3) || (i == 5 && j == 4) || (i == 7 && j == 6) then
        1
      else if (i == 1 && j == 0) || (i == 3 && j == 2) ||
              (i == 4 && j == 5) || (i == 6 && j == 7) then
        -1
      else 0

private def matEta8 : List (List Int) :=
  intMatMul (intMatScale (-1) matE8) matPhi8

private def uBlockCoord (r c : Nat) : Int × Int :=
  if r == 0 && c == 0 then (1, 2)
  else if r == 0 && c == 1 then (2, 0)
  else if r == 1 && c == 0 then (-2, 0)
  else (1, -2)

private def z2BlkCell (re im : Int) (dr dc : Nat) : Int :=
  if dr == 0 && dc == 0 then re
  else if dr == 0 && dc == 1 then im
  else if dr == 1 && dc == 0 then im
  else -re

private def matG9 : List (List Int) :=
  (rangeList 0 8).map fun i =>
    (rangeList 0 8).map fun j =>
      let bi := i / 2
      let bj := j / 2
      if bi == bj then if i == j then 15 else 0
      else if (bi < 2) && (2 <= bj) then
        let (re, im) := uBlockCoord bi (bj - 2)
        4 * z2BlkCell re im (i % 2) (j % 2)
      else if (2 <= bi) && (bj < 2) then
        let (re, im) := uBlockCoord bj (bi - 2)
        4 * z2BlkCell re im (j % 2) (i % 2)
      else 0

private def matGrad3 : List (List Int) :=
  (rangeList 0 8).map fun i =>
    (rangeList 0 8).map fun j =>
      let bi := i / 2
      let bj := j / 2
      if bi == bj then if i == j then 5 else 0
      else if (bi < 2) && (bj == bi + 2) then
        4 * z2BlkCell 1 0 (i % 2) (j % 2)
      else if (2 <= bi) && (bj + 2 == bi) then
        4 * z2BlkCell 1 0 (j % 2) (i % 2)
      else 0

private def matL8 : List (List Int) :=
  (rangeList 0 8).map fun i =>
    (rangeList 0 8).map fun j =>
      if i < 4 then
        if j == i then 1
        else if j == i + 4 then if i % 2 == 0 then 1 else -1
        else 0
      else
        if j + 4 == i then 1
        else if j == i then if (i - 4) % 2 == 0 then -1 else 1
        else 0

-- ---------------------------------------------------------------------------
-- Theorem 1: 8 x 8 Lorentzian Boost G_9, Null Light Cone & 50/50 Split
-- ---------------------------------------------------------------------------

private def checkBoostG9LightCone : Bool :=
  let etaOk := intMatEq matEta8 (intDiag [1, 1, 1, 1, -1, -1, -1, -1])
  let gSym := intMatEq matG9 (intMatTranspose matG9)
  let etaPres := intMatEq (intMatMul (intMatTranspose matG9) (intMatMul matEta8 matG9))
    (intMatScale 81 matEta8)
  let sympPres := intMatEq (intMatMul (intMatTranspose matG9) (intMatMul matE8 matG9))
    (intMatScale 81 matE8)
  let phiComm := intMatEq (intMatMul matG9 matPhi8) (intMatMul matPhi8 matG9)
  let gInv := intMatMul matEta8 (intMatMul (intMatTranspose matG9) matEta8)
  let invOk := intMatEq (intMatMul matG9 gInv) (intMatScale 81 (intEye 8))
  let i8 := intEye 8
  let nPlus := intMatSub matG9 (intMatScale 3 i8)
  let nMinus := intMatSub (intMatScale 27 i8) matG9
  let minPolyOk := isIntMatZero (intMatMul nMinus nPlus)
  let lcOk :=
    intMatEq (intMatMul nPlus nPlus) (intMatScale 24 nPlus) &&
    intEq (intMatTrace nPlus) 96 &&
    intMatEq (intMatMul nMinus nMinus) (intMatScale 24 nMinus) &&
    intEq (intMatTrace nMinus) 96 &&
    intMatEq (intMatAdd nPlus nMinus) (intMatScale 24 i8) &&
    isIntMatZero (intMatMul nPlus nMinus) &&
    isIntMatZero (intMatMul (intMatTranspose nPlus) (intMatMul matEta8 nPlus)) &&
    isIntMatZero (intMatMul (intMatTranspose nMinus) (intMatMul matEta8 nMinus))
  let l8T := intMatTranspose matL8
  let radOk :=
    intMatEq (intMatMul matL8 l8T) (intMatScale 2 i8) &&
    intMatEq (intMatMul matL8 (intMatMul matGrad3 l8T)) (intDiag [18, 18, 18, 18, 2, 2, 2, 2])
  etaOk && gSym && etaPres && sympPres && phiComm && invOk && minPolyOk && lcOk && radOk

set_option maxHeartbeats 4000000 in
/-- Certifies the exact `8 x 8` symmetric `SU(2, 2)` Lorentzian boost `G_9`, preserving both
split `(4, 4)` metric `eta_8` and `E_8` (`G_9^T eta_8 G_9 = 81 eta_8`), null light-cone
projectors `N_+^T eta_8 N_+ = 0` and `N_-^T eta_8 N_- = 0`, and 50/50 light-cone
diagonalization of radial boost `G_rad3`. -/
theorem lorentzian_su22_boost_g9_and_null_light_cone_cert :
    checkBoostG9LightCone = true :=
  rfl

-- ---------------------------------------------------------------------------
-- Theorem 2: Boosted Complex Structure J_27, Bareiss Minors & Mobius Ball
-- ---------------------------------------------------------------------------

private def bareissMinorsStep (m : List (List Int)) (prev : Int) (k n : Nat) :
    List (List Int) × Int × Bool :=
  let piv := intMatCell m k k
  let okRem : Bool :=
    if intEq prev 0 then false
    else
      ((rangeList (k + 1) (n - k - 1)).all fun i =>
        (rangeList (k + 1) (n - k - 1)).all fun j =>
          let num := intMatCell m i j * piv - intMatCell m i k * intMatCell m k j
          intEq (num % prev) 0)
  let nextM :=
    (rangeList 0 n).map fun i =>
      (rangeList 0 n).map fun j =>
        if Nat.ble i k || Nat.ble j k then intMatCell m i j
        else if intEq prev 0 then 0
        else (intMatCell m i j * piv - intMatCell m i k * intMatCell m k j) / prev
  (nextM, piv, okRem)

private def bareissAllMinors (m : List (List Int)) (n : Nat) : List Int × Bool :=
  let init : List (List Int) × Int × List Int × Bool := (m, 1, [], true)
  let final := (rangeList 0 n).foldl (fun (curM, prev, mins, ok) k =>
    if k + 1 == n then (curM, prev, mins ++ [intMatCell curM k k], ok)
    else
      let (nm, piv, stepOk) := bareissMinorsStep curM prev k n
      (nm, piv, mins ++ [piv], ok && stepOk)) init
  (final.2.2.1, final.2.2.2)

private abbrev GI := Int × Int
private def giAdd (a b : GI) : GI := (a.1 + b.1, a.2 + b.2)
private def giSub (a b : GI) : GI := (a.1 - b.1, a.2 - b.2)
private def giMul (a b : GI) : GI := (a.1 * b.1 - a.2 * b.2, a.1 * b.2 + a.2 * b.1)
private def giConj (a : GI) : GI := (a.1, -a.2)
private def giEq (a b : GI) : Bool := intEq a.1 b.1 && intEq a.2 b.2

private def giMatCell (m : List (List GI)) (i j : Nat) : GI :=
  ((m.drop i).headD []).drop j |>.headD (0, 0)

private def giMatMul (a b : List (List GI)) : List (List GI) :=
  let nr := a.length
  let nc := ((b.drop 0).headD []).length
  let nk := b.length
  (rangeList 0 nr).map fun i =>
    (rangeList 0 nc).map fun j =>
      (rangeList 0 nk).foldl (fun acc k =>
        giAdd acc (giMul (giMatCell a i k) (giMatCell b k j))) (0, 0)

private def giMatAdj (m : List (List GI)) : List (List GI) :=
  let nr := m.length
  let nc := ((m.drop 0).headD []).length
  (rangeList 0 nc).map fun i => (rangeList 0 nr).map fun j => giConj (giMatCell m j i)

private def giMatScale (s : Int) (m : List (List GI)) : List (List GI) :=
  m.map fun r => r.map fun (re, im) => (s * re, s * im)

private def giMatAdd (a b : List (List GI)) : List (List GI) :=
  List.zipWith (List.zipWith giAdd) a b

private def giMatSub (a b : List (List GI)) : List (List GI) :=
  List.zipWith (List.zipWith giSub) a b

private def giMatEq (a b : List (List GI)) : Bool :=
  (a.length == b.length) &&
  (List.zipWith (fun r1 r2 => (r1.length == r2.length) &&
    (List.zipWith giEq r1 r2).all id) a b).all id

private def matJ27 : List (List Int) :=
  let gInv := intMatMul matEta8 (intMatMul (intMatTranspose matG9) matEta8)
  let raw := intMatMul matG9 (intMatMul matE8 gInv)
  raw.map fun r => r.map fun x => x / 3

private def checkBoostedJ27AndMobius : Bool :=
  let gInv := intMatMul matEta8 (intMatMul (intMatTranspose matG9) matEta8)
  let rawJ := intMatMul matG9 (intMatMul matE8 gInv)
  let div3Ok := rawJ.all fun r => r.all fun x => intEq (x % 3) 0
  let i8 := intEye 8
  let j27 := matJ27
  let sqOk := intMatEq (intMatMul j27 j27) (intMatScale (-729) i8)
  let rbrOk := intMatEq (intMatMul (intMatTranspose j27) (intMatMul matE8 j27))
    (intMatScale 729 matE8)
  let commOk := intMatEq (intMatMul j27 matPhi8) (intMatMul matPhi8 j27)
  let gPos := intMatMul (intMatScale (-1) matE8) j27
  let symOk := intMatEq gPos (intMatTranspose gPos)
  let mpPosOk := isIntMatZero (intMatMul (intMatSub gPos (intMatScale 243 i8))
    (intMatSub gPos (intMatScale 3 i8)))
  let (minors, divBOk) := bareissAllMinors gPos 8
  let expectedMinors : List Int :=
    [123, 15129, 1860867, 228886641, 1356572043, 8040170889, 47652720147, 282429536481]
  let minsOk := divBOk && (minors.length == 8) &&
    (List.zipWith intEq minors expectedMinors).all id
  let u3 : List (List GI) := [[(1, 2), (2, 0)], [(-2, 0), (1, -2)]]
  let u3Adj := giMatAdj u3
  let giI2 : List (List GI) := [[(1, 0), (0, 0)], [(0, 0), (1, 0)]]
  let u3Unitary := giMatEq (giMatMul u3Adj u3) (giMatScale 9 giI2)
  let stepPairs : List (Int × Int × Int × Int × Int) :=
    [(0, 1, 4, 5, 1), (4, 5, 40, 41, 9), (40, 41, 364, 365, 81)]
  let mobiusOk := stepPairs.all fun (nk, dk, nNext, dNext, marginScale) =>
    let hk := giMatScale nk u3
    let hNext := giMatScale nNext u3
    let lhs := giMatScale (9 * dNext) (giMatAdd (giMatScale 5 hk) (giMatScale (4 * dk) u3))
    let rhs := giMatMul hNext
      (giMatAdd (giMatMul (giMatScale 4 u3Adj) hk) (giMatScale (45 * dk) giI2))
    let marginMat := giMatSub (giMatScale (9 * dk * dk) giI2) (giMatMul (giMatAdj hk) hk)
    giMatEq lhs rhs && giMatEq marginMat (giMatScale (9 * marginScale) giI2)
  div3Ok && sqOk && rbrOk && commOk && symOk && mpPosOk && minsOk && u3Unitary && mobiusOk

set_option maxHeartbeats 4000000 in
/-- Certifies boosted complex structure `J_27 = (1/3) G_9 E_8 (eta_8 G_9^T eta_8)`,
polarization `G_pos = -E_8 J_27` with spectrum `{3, 243}` and `8` positive Bareiss minors
(`det = 27^8`), and exact `2 x 2` Matrix Mobius steps inside the period unit ball. -/
theorem lorentzian_boosted_j27_polarization_and_mobius_ball_cert :
    checkBoostedJ27AndMobius = true :=
  rfl

-- ---------------------------------------------------------------------------
-- Exterior 70-Dim Operators for Theorems 3 and 4
-- ---------------------------------------------------------------------------

private abbrev ExtSparse := List (List Nat × Int)

private def exNatLt : List Nat → List Nat → Bool
  | [], [] => false
  | [], _ :: _ => true
  | _ :: _, [] => false
  | x :: xs, y :: ys => if x == y then exNatLt xs ys else Nat.blt x y

private def exNatEq : List Nat → List Nat → Bool
  | [], [] => true
  | [], _ :: _ => false
  | _ :: _, [] => false
  | x :: xs, y :: ys => (x == y) && exNatEq xs ys

private def exInsNat (x : Nat) : List Nat → Option (List Nat × Int)
  | [] => some ([x], 1)
  | y :: ys =>
    if x == y then none
    else if Nat.blt x y then some (x :: y :: ys, 1)
    else
      match exInsNat x ys with
      | none => none
      | some (zs, s) => some (y :: zs, -s)

private def exSortNat : List Nat → Option (List Nat × Int)
  | [] => some ([], 1)
  | x :: xs =>
    match exSortNat xs with
    | none => none
    | some (ys, s1) =>
      match exInsNat x ys with
      | none => none
      | some (zs, s2) => some (zs, s1 * s2)

private def exInsert (k : List Nat) (c : Int) : ExtSparse → ExtSparse
  | [] => if intEq c 0 then [] else [(k, c)]
  | (k0, c0) :: rest =>
    if exNatEq k k0 then
      let nc := c + c0
      if intEq nc 0 then rest else (k0, nc) :: rest
    else if exNatLt k k0 then
      if intEq c 0 then (k0, c0) :: rest else (k, c) :: (k0, c0) :: rest
    else
      (k0, c0) :: exInsert k c rest

private def exAdd (a b : ExtSparse) : ExtSparse :=
  b.foldl (fun acc (k, c) => exInsert k c acc) a

private def exScale (s : Int) (a : ExtSparse) : ExtSparse :=
  if intEq s 0 then [] else a.map fun (k, c) => (k, s * c)

private def exEq : ExtSparse → ExtSparse → Bool
  | [], [] => true
  | [], _ :: _ => false
  | _ :: _, [] => false
  | (k1, c1) :: r1, (k2, c2) :: r2 => exNatEq k1 k2 && intEq c1 c2 && exEq r1 r2

private def lwWedge (a b : ExtSparse) : ExtSparse :=
  a.foldl (fun acc (k1, c1) =>
    b.foldl (fun acc2 (k2, c2) =>
      match exSortNat (k1 ++ k2) with
      | none => acc2
      | some (k, s) => exInsert k (s * c1 * c2) acc2) acc) []

private def lwCupPair4 (a b : ExtSparse) : Int :=
  match lwWedge a b with
  | [] => 0
  | (k, c) :: rest =>
    match rest with
    | [] => if exNatEq k [0, 1, 2, 3, 4, 5, 6, 7] then c else 0
    | _ :: _ => 0

private def lwReplaceAtNat (xs : List Nat) (pos val : Nat) : List Nat :=
  match xs with
  | [] => []
  | x :: rest =>
    match pos with
    | 0 => val :: rest
    | k + 1 => x :: lwReplaceAtNat rest k val

private def phiStep8 (i : Nat) : Nat × Int :=
  if i == 0 then (1, -1)
  else if i == 1 then (0, 1)
  else if i == 2 then (3, -1)
  else if i == 3 then (2, 1)
  else if i == 4 then (5, 1)
  else if i == 5 then (4, -1)
  else if i == 6 then (7, 1)
  else (6, -1)

private def applyKPhi (f : ExtSparse) : ExtSparse :=
  f.foldl (fun acc (tup, c) =>
    (rangeList 0 tup.length).foldl (fun acc2 pos =>
      let i := (tup.drop pos).headD 0
      let (j, v) := phiStep8 i
      match exSortNat (lwReplaceAtNat tup pos j) with
      | none => acc2
      | some (sk, sg) => exInsert sk (c * v * sg) acc2) acc) []

private def applyP192 (f : ExtSparse) : ExtSparse :=
  let k2 := applyKPhi (applyKPhi f)
  let mid := exAdd k2 (exScale 4 f)
  applyKPhi (applyKPhi mid)

private def j27SparseRows : List (List (Nat × Int)) :=
  let j27 := matJ27
  (rangeList 0 8).map fun i =>
    let row := (j27.drop i).headD []
    (rangeList 0 8).foldl (fun acc j =>
      let v := (row.drop j).headD 0
      if intEq v 0 then acc else acc ++ [(j, v)]) []

private def applyD27 (f : ExtSparse) : ExtSparse :=
  f.foldl (fun acc (tup, c) =>
    (rangeList 0 tup.length).foldl (fun acc2 pos =>
      let i := (tup.drop pos).headD 0
      let nzRow := (j27SparseRows.drop i).headD []
      nzRow.foldl (fun acc3 (j, v) =>
        match exSortNat (lwReplaceAtNat tup pos j) with
        | none => acc3
        | some (sk, sg) => exInsert sk (c * v * sg) acc3) acc2) acc) []

private def allBasisTuples4 : List (List Nat) :=
  (rangeList 0 8).foldl (fun a0 i0 =>
    (rangeList (i0 + 1) (8 - i0 - 1)).foldl (fun a1 i1 =>
      (rangeList (i1 + 1) (8 - i1 - 1)).foldl (fun a2 i2 =>
        (rangeList (i2 + 1) (8 - i2 - 1)).foldl (fun a3 i3 =>
          a3 ++ [[i0, i1, i2, i3]]) a2) a1) a0) []

-- ---------------------------------------------------------------------------
-- Theorem 3: Boosted D_27 Hodge Invariance & Divisor Breaking (70 x 70)
-- ---------------------------------------------------------------------------

private def checkBoostedD27Operators : Bool :=
  let tuples := allBasisTuples4
  let dp02 : ExtSparse := (ei4NsBasis16.drop 5).headD []
  let namedOk :=
    (applyD27 ei4WeilReForm).isEmpty &&
    (applyD27 ei4WeilImForm).isEmpty &&
    (applyD27 ei4ThetaSqForm).isEmpty &&
    (applyD27 ei4ThetaForm).isEmpty &&
    !(applyD27 dp02).isEmpty
  let loopOk := tuples.all fun tup =>
    let eT : ExtSparse := [(tup, 1)]
    let kills := (applyD27 (applyP192 eT)).isEmpty
    let comm := exEq (applyD27 (applyKPhi eT)) (applyKPhi (applyD27 eT))
    kills && comm
  namedOk && loopOk

set_option maxHeartbeats 24000000 in
set_option maxRecDepth 8192 in
/-- Exhaustive `70 x 70` certification of boosted Hodge Hamiltonian `D_27`:
`D_27(w_Re) = D_27(w_Im) = D_27(Theta^2) = D_27(Theta) = 0`, `D_27(D^+_{0,2}) != 0`,
`D_27 P_192 = 0`, and `[D_27, K_Phi] = 0` across all `70` basis `4`-tuples of `/\^4 Z^8`. -/
theorem lorentzian_boosted_d27_hodge_invariance_and_divisor_break_cert :
    checkBoostedD27Operators = true :=
  rfl

-- ---------------------------------------------------------------------------
-- Theorem 4: SO(35,35) Exterior Boost /\^4 G_9, Trace & Weil Fixed Points
-- ---------------------------------------------------------------------------

private def det3Int (a00 a01 a02 a10 a11 a12 a20 a21 a22 : Int) : Int :=
  a00 * (a11 * a22 - a12 * a21) -
  a01 * (a10 * a22 - a12 * a20) +
  a02 * (a10 * a21 - a11 * a20)

private def subDet4 (m : List (List Int)) (rTup cTup : List Nat) : Int :=
  let r0 := (rTup.drop 0).headD 0
  let r1 := (rTup.drop 1).headD 0
  let r2 := (rTup.drop 2).headD 0
  let r3 := (rTup.drop 3).headD 0
  let c0 := (cTup.drop 0).headD 0
  let c1 := (cTup.drop 1).headD 0
  let c2 := (cTup.drop 2).headD 0
  let c3 := (cTup.drop 3).headD 0
  let e0 := intMatCell m r0 c0
  let e1 := intMatCell m r0 c1
  let e2 := intMatCell m r0 c2
  let e3 := intMatCell m r0 c3
  let d0 := if intEq e0 0 then 0 else e0 * det3Int
    (intMatCell m r1 c1) (intMatCell m r1 c2) (intMatCell m r1 c3)
    (intMatCell m r2 c1) (intMatCell m r2 c2) (intMatCell m r2 c3)
    (intMatCell m r3 c1) (intMatCell m r3 c2) (intMatCell m r3 c3)
  let d1 := if intEq e1 0 then 0 else e1 * det3Int
    (intMatCell m r1 c0) (intMatCell m r1 c2) (intMatCell m r1 c3)
    (intMatCell m r2 c0) (intMatCell m r2 c2) (intMatCell m r2 c3)
    (intMatCell m r3 c0) (intMatCell m r3 c2) (intMatCell m r3 c3)
  let d2 := if intEq e2 0 then 0 else e2 * det3Int
    (intMatCell m r1 c0) (intMatCell m r1 c1) (intMatCell m r1 c3)
    (intMatCell m r2 c0) (intMatCell m r2 c1) (intMatCell m r2 c3)
    (intMatCell m r3 c0) (intMatCell m r3 c1) (intMatCell m r3 c3)
  let d3 := if intEq e3 0 then 0 else e3 * det3Int
    (intMatCell m r1 c0) (intMatCell m r1 c1) (intMatCell m r1 c2)
    (intMatCell m r2 c0) (intMatCell m r2 c1) (intMatCell m r2 c2)
    (intMatCell m r3 c0) (intMatCell m r3 c1) (intMatCell m r3 c2)
  d0 - d1 + d2 - d3

private def applyWedge4Mat (tuples : List (List Nat)) (m : List (List Int))
    (f : ExtSparse) : ExtSparse :=
  tuples.foldl (fun acc rTup =>
    let val := f.foldl (fun s (cTup, coef) => s + coef * subDet4 m rTup cTup) 0
    if intEq val 0 then acc else acc ++ [(rTup, val)]) []

private def checkSo3535ExteriorBoost : Bool :=
  let (g9Mins, g9DivOk) := bareissAllMinors matG9 8
  let detG9Ok := g9DivOk && intEq ((g9Mins.drop 7).headD 0) 43046721
  let tuples := allBasisTuples4
  let diagSum := tuples.foldl (fun acc tup => acc + subDet4 matG9 tup tup) 0
  let diagOk := intEq diagSum 1724166
  let gRe := applyWedge4Mat tuples matG9 ei4WeilReForm
  let gIm := applyWedge4Mat tuples matG9 ei4WeilImForm
  let gTh := applyWedge4Mat tuples matG9 ei4ThetaSqForm
  let fixOk :=
    exEq gRe (exScale 6561 ei4WeilReForm) &&
    exEq gIm (exScale 6561 ei4WeilImForm) &&
    exEq gTh (exScale 6561 ei4ThetaSqForm)
  let uForm : ExtSparse := [([0, 1, 2, 4], 1)]
  let vForm : ExtSparse := [([3, 5, 6, 7], 1)]
  let gu := applyWedge4Mat tuples matG9 uForm
  let gv := applyWedge4Mat tuples matG9 vForm
  let shearOk :=
    !(exEq gu (exScale 6561 uForm)) &&
    intEq (lwCupPair4 uForm vForm) (-1) &&
    intEq (lwCupPair4 gu gv) (-43046721)
  detG9Ok && diagOk && fixOk && shearOk

set_option maxHeartbeats 16000000 in
set_option maxRecDepth 8192 in
/-- Certifies exact `SO(35, 35)` exterior lift `/\^4 G_9`: `det(G_9) = 9^8 = 43046721`,
`tr(/\^4 G_9) = 1724166` (`81 * 21286`), pointwise invariance of `w_Re`, `w_Im`, `Theta^2`
under `/\^4 G_9 = 6561 * I`, and cup-product preservation on a sheared non-invariant pair. -/
theorem lorentzian_so35_35_exterior_boost_weil_fixed_point_cert :
    checkSo3535ExteriorBoost = true :=
  rfl

#print axioms lorentzian_su22_boost_g9_and_null_light_cone_cert
#print axioms lorentzian_boosted_j27_polarization_and_mobius_ball_cert
#print axioms lorentzian_boosted_d27_hodge_invariance_and_divisor_break_cert
#print axioms lorentzian_so35_35_exterior_boost_weil_fixed_point_cert
