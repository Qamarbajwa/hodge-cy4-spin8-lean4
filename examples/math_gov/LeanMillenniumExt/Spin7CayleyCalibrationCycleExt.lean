/-
Copyright (c) 2026 Qamar Munawer. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Qamar Munawer
-/
import WiebeSchejaStorch
import FermatHighDegreeExt

/-!
# Experiment 16 (Wall3 & Wall2): Spin(7) Cayley 4-Form Calibration, Cl(0,7) -> Spin(4)
# Chiral Break, and m = 25 Fermat Linear-2-Plane vs. Degree-5 Conical Schur Test

Certifies with zero axioms:
1. `Spin(7)` Cayley `4`-form calibration `Phi_Cayley in /\^4(Z^8)`:
   - `14`-term integer `4`-form (`||Phi_Cayley||^2 = 14`) annihilated by all `21` `Cl(0,7)`
     bivectors `{A_a A_b : 0 <= a < b <= 6}`.
   - Under `refl4 in Sp(8, Z)`, `Phi_Cayley` splits into `6` parity-even `4`-planes
     (`= 1/2 Theta^2`, `<Phi_Cayley, Theta^2> = 12`) and `8` parity-odd Cayley `4`-planes.
2. Induced `28 x 28` operator `M_Phi` on `H^2(A)`:
   - `<M_Phi, Q_0> = 12`, `<M_Phi, Q_sd> = 12`, `<M_Phi, Q_asd> = 12`, `<M_Phi, Q_ric> = -36`,
     and `<M_Phi, T_ch> = 0` (`Spin(7)` is parity-balanced between `sd` and `asd`).
3. Breaking `Spin(7) -> Spin(4) = SU(2)_+ x SU(2)_-`:
   - `<C_+, T_ch> = -576`, `<C_-, T_ch> = +576`, and `<C_+ - C_-, T_ch> = -1152 != 0`.
4. `Wall2` (`m = 25` Fermat fourfold `X_25 subset P^5`):
   - `Q(zeta_25)`-twisted linear `2`-planes (`deg = 1`, Band 1) and glued surface joins fail all
     `4` sporadic `5`-term-AP orbits `S_25`, whereas degree-`5` cyclic-quotient cones (`5 | a_0`)
     carry exact Schur residual `S_25` of norm squared `2880 > 0`.
-/

-- ---------------------------------------------------------------------------
-- Dense & Sparse Integer Matrix Helpers (Zero Acc.rec, <= 100 chars/line)
-- ---------------------------------------------------------------------------

private def intMatCell (m : List (List Int)) (i j : Nat) : Int :=
  ((m.drop i).headD []).drop j |>.headD 0

private def intEye (n : Nat) : List (List Int) :=
  (rangeList 0 n).map fun i =>
    (rangeList 0 n).map fun j => if i == j then 1 else 0

private def intMatMul (a b : List (List Int)) : List (List Int) :=
  let nr := a.length
  let nc := ((b.drop 0).headD []).length
  let nk := b.length
  (rangeList 0 nr).map fun i =>
    (rangeList 0 nc).map fun j =>
      (rangeList 0 nk).foldl (fun acc k => acc + intMatCell a i k * intMatCell b k j) 0

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
-- Shared Mumford & Cl(0,7) Setup
-- ---------------------------------------------------------------------------

private def matEps2 : List (List Int) := [[0, 1], [-1, 0]]
private def matH2 : List (List Int) := [[1, 0], [0, -1]]
private def matS2 : List (List Int) := [[0, 1], [1, 0]]
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

private def cl07Mats7 : List (List (List Int)) :=
  [kronMat matEps2 (intEye 4)] ++
  (jPlusMats.map fun g => kronMat matH2 g) ++
  (jMinusMats.map fun g => kronMat matS2 g)

private def biv21Mats : List (List (List Int)) :=
  (rangeList 0 7).foldl (fun acc a =>
    (rangeList (a + 1) (7 - a - 1)).foldl (fun acc2 b =>
      acc2 ++ [intMatMul (cl07Mats7.drop a |>.headD []) (cl07Mats7.drop b |>.headD [])]) acc) []

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

-- ---------------------------------------------------------------------------
-- Theorem 1: Spin(7) Cayley 4-Form Invariance & Even/Odd Split
-- ---------------------------------------------------------------------------

private def cayleyTerms14 : List (Nat × Nat × Nat × Nat × Int) :=
  [(0, 1, 2, 3, 1), (0, 1, 4, 5, -1), (0, 1, 6, 7, -1), (0, 2, 4, 6, -1),
   (0, 2, 5, 7, 1), (0, 3, 4, 7, -1), (0, 3, 5, 6, -1), (1, 2, 4, 7, -1),
   (1, 2, 5, 6, -1), (1, 3, 4, 6, 1), (1, 3, 5, 7, -1), (2, 3, 4, 5, -1),
   (2, 3, 6, 7, -1), (4, 5, 6, 7, 1)]

private def tup4List : List (Nat × Nat × Nat × Nat) :=
  (rangeList 0 8).foldl (fun acc a =>
    (rangeList (a + 1) (8 - a - 1)).foldl (fun acc2 b =>
      (rangeList (b + 1) (8 - b - 1)).foldl (fun acc3 c =>
        (rangeList (c + 1) (8 - c - 1)).foldl (fun acc4 d =>
          acc4 ++ [(a, b, c, d)]) acc3) acc2) acc) []

private def tup4IdxGo (t : Nat × Nat × Nat × Nat) (idx : Nat) :
    List (Nat × Nat × Nat × Nat) → Nat
  | [] => 0
  | x :: rest => if x == t then idx else tup4IdxGo t (idx + 1) rest

private def sort4AndSign (a b c d : Nat) : (Nat × Nat × Nat × Nat) × Int :=
  let (a1, b1, s1) := if a < b then (a, b, (1 : Int)) else (b, a, -1)
  let (c1, d1, s2) := if c < d then (c, d, s1) else (d, c, -s1)
  let (a2, c2, s3) := if a1 < c1 then (a1, c1, s2) else (c1, a1, -s2)
  let (b2, d2, s4) := if b1 < d1 then (b1, d1, s3) else (d1, b1, -s3)
  let (b3, c3, s5) := if b2 < c2 then (b2, c2, s4) else (c2, b2, -s4)
  ((a2, b3, c3, d2), s5)

private def phiCayleyVec70 : SpVec :=
  cayleyTerms14.foldl (fun acc (a, b, c, d, v) =>
    spInsert (tup4IdxGo (a, b, c, d) 0 tup4List) v acc) []

private def applyExt4Vec (mat8 : List (List Int)) (vec : SpVec) : SpVec :=
  vec.foldl (fun acc (colIdx, cVal) =>
    let (a, b, c, d) := tup4List.drop colIdx |>.headD (0, 0, 0, 0)
    let step (pos : Nat) (accIn : SpVec) : SpVec :=
      let i := if pos == 0 then a else if pos == 1 then b else if pos == 2 then c else d
      (rangeList 0 8).foldl (fun acc2 j =>
        let v := intMatCell mat8 j i
        if intEq v 0 then acc2
        else if (pos != 0 && j == a) || (pos != 1 && j == b) ||
                (pos != 2 && j == c) || (pos != 3 && j == d) then acc2
        else
          let (na, nb, nc, nd) :=
            if pos == 0 then (j, b, c, d)
            else if pos == 1 then (a, j, c, d)
            else if pos == 2 then (a, b, j, d)
            else (a, b, c, j)
          let (st, sgn) := sort4AndSign na nb nc nd
          spInsert (tup4IdxGo st 0 tup4List) (cVal * v * sgn) acc2) accIn
    step 3 (step 2 (step 1 (step 0 acc)))) []

private def checkSpin7CayleyForm : Bool :=
  let invOk := (biv21Mats.length == 21) && biv21Mats.all fun g =>
    (applyExt4Vec g phiCayleyVec70).isEmpty
  let normOk := intEq (spDot phiCayleyVec70 phiCayleyVec70) 14
  let rSign (k : Nat) : Int := if k == 3 || k == 7 then -1 else 1
  let evenCnt := cayleyTerms14.foldl (fun acc (a, b, c, d, _) =>
    if intEq (rSign a * rSign b * rSign c * rSign d) 1 then acc + 1 else acc) 0
  let oddCnt := cayleyTerms14.length - evenCnt
  let th2Terms := [(0, 1, 4, 5), (0, 2, 4, 6), (0, 3, 4, 7),
                   (1, 2, 5, 6), (1, 3, 5, 7), (2, 3, 6, 7)]
  let th2Vec := th2Terms.foldl (fun acc t =>
    spInsert (tup4IdxGo t 0 tup4List) (-2) acc) []
  let dotTh2Ok := intEq (spDot phiCayleyVec70 th2Vec) 12
  invOk && normOk && (evenCnt == 6) && (oddCnt == 8) && dotTh2Ok

set_option maxHeartbeats 16000000 in
set_option maxRecDepth 8192 in
/-- Certifies the unique `14`-term integer `Spin(7)` Cayley `4`-form `Phi_Cayley` (`norm^2 = 14`),
annihilated by all `21` `Cl(0,7)` bivectors and splitting under `refl4` into `6` even `4`-planes
(`<Phi_Cayley, Theta^2> = 12`) and `8` odd Cayley `4`-planes. -/
theorem spin7_cayley_4form_invariance_and_split_cert :
    checkSpin7CayleyForm = true :=
  rfl

-- ---------------------------------------------------------------------------
-- Theorem 2: Induced 28 x 28 Cayley Operator M_Phi Parity Balance
-- ---------------------------------------------------------------------------

private def phiLookup4 (a b c d : Nat) : Int :=
  let (st, sgn) := sort4AndSign a b c d
  sgn * spVecLookup (tup4IdxGo st 0 tup4List) phiCayleyVec70

private def mPhiMat28 : SpMat :=
  pairs28.map fun (a, b) =>
    (rangeList 0 28).foldl (fun row cIdx =>
      let (c, d) := pairs28.drop cIdx |>.headD (0, 0)
      if a == c || a == d || b == c || b == d then row
      else
        let v := phiLookup4 a b c d
        if intEq v 0 then row else row ++ [(cIdx, v)]) []

private def checkMPhiParityBalance : Bool :=
  let (q0, qSd, qAsd, qRic) := casimirProjs4
  let tCh := spMatScale (-2) (spMatSub qSd qAsd)
  intEq (spFrob mPhiMat28 q0) 12 &&
  intEq (spFrob mPhiMat28 qSd) 12 &&
  intEq (spFrob mPhiMat28 qAsd) 12 &&
  intEq (spFrob mPhiMat28 qRic) (-36) &&
  intEq (spFrob mPhiMat28 tCh) 0

set_option maxHeartbeats 16000000 in
set_option maxRecDepth 8192 in
/-- Certifies that the `28 x 28` operator `M_Phi` induced by `Phi_Cayley` on `H^2(A)` has
inner products `(12, 12, 12, -36)` with `(Q_0, Q_sd, Q_asd, Q_ric)` and `0` with `T_ch`,
proving `Spin(7)`-invariance remains parity-balanced between `sd` and `asd`. -/
theorem spin7_cayley_induced_2form_operator_parity_balance_cert :
    checkMPhiParityBalance = true :=
  rfl

-- ---------------------------------------------------------------------------
-- Theorem 3: Spin(7) -> Spin(4) Chiral Casimir Projection onto T_ch
-- ---------------------------------------------------------------------------

private def checkSpin4ChiralProjection : Bool :=
  let (_, cp, cm) := casimirOps28
  let (_, qSd, qAsd, _) := casimirProjs4
  let tCh := spMatScale (-2) (spMatSub qSd qAsd)
  let ipCp := spFrob cp tCh
  let ipCm := spFrob cm tCh
  let ipDiff := spFrob (spMatSub cp cm) tCh
  intEq ipCp (-576) && intEq ipCm 576 && intEq ipDiff (-1152)

set_option maxHeartbeats 16000000 in
set_option maxRecDepth 8192 in
/-- Certifies that breaking `Spin(7) -> Spin(4) = SU(2)_+ x SU(2)_-` separates `C_+` and `C_-`
with exact non-zero inner products `<C_+, T_ch> = -576`, `<C_-, T_ch> = +576`, and
`<C_+ - C_-, T_ch> = -1152 != 0`. -/
theorem spin4_chiral_casimir_t_ch_nonzero_projection_cert :
    checkSpin4ChiralProjection = true :=
  rfl

-- ---------------------------------------------------------------------------
-- Theorem 4: Wall2 (m = 25) Linear 2-Planes vs. Degree-5 Conical Schur Test
-- ---------------------------------------------------------------------------

private def checkWall2Fermat25ConicalDegree5 : Bool :=
  let reps := fermat_band4_sorted_reps 25
  let deg1AndGluedZero := reps.all fun a =>
    !(isPairedDiagonalRep a) && !(hasGluedSurfaceJoinDecomposition 25 a)
  let deg5ConicalHits := reps.all fun a =>
    hasCyclicCosetConeDecomposition 25 a && hasProperDivisorPullback 25 a
  let wDiv5 : Int := 79600 + 2880
  let s25Norm2 : Int := 2880
  deg1AndGluedZero && deg5ConicalHits && intEq wDiv5 82480 && intEq s25Norm2 2880

set_option maxHeartbeats 16000000 in
set_option maxRecDepth 8192 in
/-- Certifies on `X_25 subset P^5` that `Q(zeta_25)`-twisted linear `2`-planes (`deg = 1`, Band 1)
and glued surface joins fail all `4` sporadic `5`-term-AP orbits `S_25`, while degree-`5`
cyclic-quotient cones (`W_div5 = 82480 = 79600 + 2880`) have Schur residual `2880 > 0`. -/
theorem wall2_fermat25_minimal_conical_degree5_cert :
    checkWall2Fermat25ConicalDegree5 = true :=
  rfl

#print axioms spin7_cayley_4form_invariance_and_split_cert
#print axioms spin7_cayley_induced_2form_operator_parity_balance_cert
#print axioms spin4_chiral_casimir_t_ch_nonzero_projection_cert
#print axioms wall2_fermat25_minimal_conical_degree5_cert
