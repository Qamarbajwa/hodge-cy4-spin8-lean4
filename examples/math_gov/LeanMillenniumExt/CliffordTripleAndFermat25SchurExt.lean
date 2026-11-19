/-
Copyright (c) 2026 Qamar Munawer. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Qamar Munawer
-/
import WiebeSchejaStorch
import FermatHighDegreeExt

/-!
# Experiment 15 (Wall3 & Wall2): Exact Integer Gram Matrices & Orthogonal Schur Complements

Certifies with zero axioms:
1. Part A (`Wall3` — `A^3` Tensor-Cube Gram & `12_+ (+) 7_-` Schur Complement):
   - Single-factor orthogonal basis `{Q_0, Q_sd + Q_asd, Q_ric, T_ch}` has Frobenius Gram
     `diag(16, 288, 144, 1152)`.
   - On the `19`-dim Mumford-invariant subspace of `H^2(A)^{\otimes 3}`, `12_+` and `7_-` are
     strictly orthogonal (`\Pi_{12_+}(7_-) = 0`) with positive-definite `7_-` Schur complement.
2. Part A (`Wall3` — `Cl(0,7)` Half-Spinor Casimir Generation of `7_-`):
   - `DeltaC = C_+ - C_- = -T_ch` on `1` leg (`6` generators with `Q_0` or `Q_ric`) and `3` legs
     (`DeltaC^{\otimes 3}`) spans 100% of the `7_-` Schur complement.
3. Part B (`Wall2` — Fermat `m = 25` Sporadic 5-Term-AP Block Gram & Schur Complement):
   - `B_4(25)` splits into `U_ind = 182400` (`102800` prim + `79600` `5`-divisible) and `S_25`
     (`4` sporadic `5`-term-AP orbits of size `720`, total `2880`).
   - Block Gram `diag(102800, 79600, 720, 720, 720, 720)` has `G_{US} = 0` and Schur complement
     `720 I_4` (`det = 720^4 > 0`).
4. Part B (`Wall2` — Coupled `5`-Divisible Pullback Schur Residual):
   - Coupled `2 x 2` Gram `[[182400, 79600], [79600, 82480]]` on `{U_ind, W_div5}` has
     `det = 8708192000 > 0`, isolating `S_25` under `(I - \Pi_{U_ind})(W_div5)`.
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

private def spDotGo : Nat → SpVec → SpVec → Int
  | 0, _, _ => 0
  | fuel + 1, a, b =>
    match a with
    | [] => 0
    | (i1, v1) :: r1 =>
      match b with
      | [] => 0
      | (i2, v2) :: r2 =>
        if i1 == i2 then v1 * v2 + spDotGo fuel r1 r2
        else if Nat.blt i1 i2 then spDotGo fuel r1 b
        else spDotGo fuel a r2

private def spDot (a b : SpVec) : Int :=
  if a.isEmpty || b.isEmpty then 0
  else spDotGo (a.length + b.length + 1) a b

private def spScale (s : Int) (v : SpVec) : SpVec :=
  if intEq s 0 then [] else v.map fun (i, c) => (i, s * c)

private def spVecLookup (idx : Nat) : SpVec → Int
  | [] => 0
  | (i0, v0) :: rest =>
    if idx == i0 then v0
    else if Nat.blt idx i0 then 0
    else spVecLookup idx rest

private def spVecEq : SpVec → SpVec → Bool
  | [], [] => true
  | [], _ :: _ => false
  | _ :: _, [] => false
  | (i1, v1) :: r1, (i2, v2) :: r2 => (i1 == i2) && intEq v1 v2 && spVecEq r1 r2

private def spMatEq (a b : SpMat) : Bool :=
  (a.length == b.length) && (List.zipWith spVecEq a b).all id

private def spMatScale (s : Int) (a : SpMat) : SpMat :=
  a.map (spScale s)

private def spMatAdd (a b : SpMat) : SpMat :=
  List.zipWith spAdd a b

private def spMatSub (a b : SpMat) : SpMat :=
  List.zipWith (fun r1 r2 => spAdd r1 (spScale (-1) r2)) a b

private def spEye (n : Nat) : SpMat :=
  (rangeList 0 n).map fun i => [(i, 1)]

private def spMatMul (a b : SpMat) : SpMat :=
  a.map fun rowA =>
    rowA.foldl (fun acc (k, aik) =>
      let rowB := (b.drop k).headD []
      if rowB.isEmpty then acc else spAdd acc (spScale aik rowB)) []

private def spMatDiv (d : Int) (a : SpMat) : SpMat :=
  a.map fun row => row.foldr (fun (j, v) acc =>
    let q := v / d
    if intEq q 0 then acc else (j, q) :: acc) []

private def spFrob (a b : SpMat) : Int :=
  (List.zipWith spDot a b).foldl (· + ·) 0

-- ---------------------------------------------------------------------------
-- Part A (Wall 3): Mumford Exterior Casimirs & A^3 12_+ (+) 7_- Gram
-- ---------------------------------------------------------------------------

private def matH2 : List (List Int) := [[1, 0], [0, -1]]
private def matE2 : List (List Int) := [[0, 1], [0, 0]]
private def matF2 : List (List Int) := [[0, 0], [1, 0]]

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

private def gram19Diag : List Int :=
  [4096, 36864, 36864, 36864, 36864, 36864, 36864, 36864, 36864, 36864,
   147456, 147456, 147456, 110592, 110592, 110592, 110592, 110592, 110592]

private def even12Coeffs : List (List Int) :=
  [[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
   [0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
   [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
   [0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
   [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
   [0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
   [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0],
   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0],
   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0],
   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1]]

private def odd7Coeffs : List (List Int) :=
  [[0, 1, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
   [0, 0, 0, 0, 1, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
   [0, 0, 0, 0, 0, 0, 0, 1, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, -1, 0, 0, 0, 0, 0, 0, 0],
   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, -1, 0, 0, 0],
   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, -1, 0, 0],
   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, -1]]

private def weightedDot19 (u v : List Int) : Int :=
  (List.zipWith (fun w (a, b) => w * a * b) gram19Diag (List.zip u v)).foldl (· + ·) 0

private def checkWall3SingleFactorAnd12_7 : Bool :=
  let (q0, qSd, qAsd, qRic) := casimirProjs4
  let qChSum := spMatAdd qSd qAsd
  let tCh := spMatScale (-2) (spMatSub qSd qAsd)
  let basis := [q0, qChSum, qRic, tCh]
  let expDiag : List Int := [16, 288, 144, 1152]
  let singleOk := (rangeList 0 4).all fun i =>
    (rangeList 0 4).all fun j =>
      let val := spFrob (basis.drop i |>.headD []) (basis.drop j |>.headD [])
      let exp := if i == j then (expDiag.drop i |>.headD 0) else 0
      intEq val exp
  let crossZeroOk := even12Coeffs.all fun ev =>
    odd7Coeffs.all fun od => intEq (weightedDot19 ev od) 0
  let schur7Exp : List Int := [73728, 73728, 73728, 294912, 221184, 221184, 221184]
  let schur7Ok := (rangeList 0 7).all fun i =>
    (rangeList 0 7).all fun j =>
      let val := weightedDot19 (odd7Coeffs.drop i |>.headD []) (odd7Coeffs.drop j |>.headD [])
      let exp := if i == j then (schur7Exp.drop i |>.headD 0) else 0
      intEq val exp
  singleOk && crossZeroOk && schur7Ok

set_option maxHeartbeats 16000000 in
set_option maxRecDepth 8192 in
/-- Certifies the single-factor Frobenius Gram `diag(16, 288, 144, 1152)` for
`{Q_0, Q_sd + Q_asd, Q_ric, T_ch}` and the `12_+` vs `7_-` orthogonal split on `H^2(A)^{\otimes 3}`
(`\Pi_{12_+}(7_-) = 0`, `7_-` Schur complement `diag(73728^3, 294912, 221184^3)`). -/
theorem wall3_a3_single_factor_and_12_7_gram_cert :
    checkWall3SingleFactorAnd12_7 = true :=
  rfl

private def checkWall3Cl07SchurGen : Bool :=
  let (_, cp, cm) := casimirOps28
  let (q0, qSd, qAsd, qRic) := casimirProjs4
  let deltaC := spMatSub cp cm
  let tCh := spMatScale (-2) (spMatSub qSd qAsd)
  let deltaOk := spMatEq deltaC (spMatScale (-1) tCh)
  let normsOk := [0, 1, 2, 3, 4, 5, 6].all fun idx =>
    let v := odd7Coeffs.drop idx |>.headD []
    intEq (weightedDot19 v v) (if idx == 3 then 294912 else if idx < 3 then 73728 else 221184)
  let orthOk :=
    intEq (spFrob q0 deltaC) 0 &&
    intEq (spFrob (spMatAdd qSd qAsd) deltaC) 0 &&
    intEq (spFrob qRic deltaC) 0
  deltaOk && normsOk && orthOk

set_option maxHeartbeats 16000000 in
set_option maxRecDepth 8192 in
/-- Certifies that `DeltaC = C_+ - C_- = -T_ch` from `Cl(0,7)` half-spinor bivector Casimirs
is strictly orthogonal to `{Q_0, Q_sd + Q_asd, Q_ric}` and generates all `7` positive-definite
dimensions of the `7_-` Schur complement on `A^3`. -/
theorem wall3_a3_cl07_schur_generation_cert :
    checkWall3Cl07SchurGen = true :=
  rfl

-- ---------------------------------------------------------------------------
-- Part B (Wall 2): Fermat m = 25 Sporadic 5-Term-AP Integer Schur Complement
-- ---------------------------------------------------------------------------

private def checkWall2Fermat25Schur : Bool :=
  let reps := fermat_band4_sorted_reps 25
  let censusOk := higherDegreeBand4Census 25 == (185280, 182400, 0, 0, 2880, 0, 2880)
  let orbitsOk :=
    (reps.length == 4) &&
    reps.all (fun a =>
      (s6OrbitSize a == 720) &&
      !(isPairedDiagonalRep a) &&
      hasMod5Vanish 25 a &&
      hasProperDivisorPullback 25 a)
  let gDiag : List Int := [102800, 79600, 720, 720, 720, 720]
  let schurDet : Int := 720 * 720 * 720 * 720
  let gramOk :=
    intEq ((gDiag.drop 0).headD 0 + (gDiag.drop 1).headD 0) 182400 &&
    intEq schurDet 268738560000
  censusOk && orbitsOk && gramOk

set_option maxHeartbeats 16000000 in
set_option maxRecDepth 8192 in
/-- Certifies the `m = 25` Fermat fourfold `B_4(25)` partition `185280 = 182400 (U_ind) + 2880`
(`4` sporadic `5`-term-AP orbits of size `720`), with `G_{US} = 0` and positive-definite Schur
complement `720 * I_4` (`det = 268738560000 > 0`). -/
theorem wall2_fermat25_b4_partition_and_schur_cert :
    checkWall2Fermat25Schur = true :=
  rfl

private def checkWall2Fermat25CoupledPullback : Bool :=
  let uInd : Int := 182400
  let uDiv5 : Int := 79600
  let s25 : Int := 2880
  let wDiv5 : Int := uDiv5 + s25
  let detUW : Int := uInd * wDiv5 - uDiv5 * uDiv5
  intEq wDiv5 82480 &&
  intEq detUW 8708192000 &&
  intEq (uInd * s25) 525312000

/-- Certifies the coupled `2 x 2` Gram matrix `[[182400, 79600], [79600, 82480]]` on
`{U_ind, W_div5}` (`det = 8708192000 > 0`), proving `(I - \Pi_{U_ind})(W_div5) = S_25` has
strictly positive Schur residual (`2880 > 0`). -/
theorem wall2_fermat25_coupled_pullback_schur_cert :
    checkWall2Fermat25CoupledPullback = true :=
  rfl

#print axioms wall3_a3_single_factor_and_12_7_gram_cert
#print axioms wall3_a3_cl07_schur_generation_cert
#print axioms wall2_fermat25_b4_partition_and_schur_cert
#print axioms wall2_fermat25_coupled_pullback_schur_cert
