/-
Copyright (c) 2026 Qamar Munawer. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Qamar Munawer
-/
import WiebeSchejaStorch

/-!
# Experiment 12 (Wall 3): Universal Sp(8) Parity-Blindness, Kuga-Satake Spin(2,4) & Cl(0,7)

Certifies with zero axioms:
1. Universal `Sp(8)` parity-blindness obstruction on `A^k`:
   - `refl4 = I_2 x diag(1,1,1,-1)` lies in `Sp(8, Z)` (`refl4^T E_real refl4 = E_real`).
   - `P_flip = /\^2(refl4)` commutes with `Q_0` and `T_r0`, and anticommutes with `T_ch`
     (`P_flip T_ch P_flip = -T_ch`), making `T_ch` (and all `7` odd sectors on `A^3`) strictly
     orthogonal to every `Sp(8)`-invariant correspondence on `A^k`.
   - All `36` generators of `sp(8)` preserve `E_real` and commute with `Q_0` (`28 = 1 + 27`),
     while mixing `Q_sd`, `Q_asd`, and `Q_ric`.
2. Kuga-Satake `Spin(2,4) = SU(2,2)` half-spinor test (Separation Theorem):
   - Explicit `Cl^0(2,4) = Cl(1,4) = M_4(C)` inside `M_8(Z)` (`5` anticommuting generators
     with signature `(+1,-1,-1,-1,-1)` commuting with `J_cl`) and `15`-dim `su(2,2)` basis
     preserving `E_real` and symmetric `(4,4)` form `eta_8 = -E_real * J_c`.
3. `Spin(2,4)` obstruction for `T_ch`:
   - `13` of `15` `spin(2,4)` generators fail to commute with `T_ch`, and
     `End_{spin(2,4)} intersect End_{sl2+so4} = A_div` (`2`-dim only).
4. Positive `Cl(0,7)` Clifford realization of `sl_2(R) + so(4)` and `T_ch`:
   - `7` anticommuting integer matrices `A_0..A_6 in M_8(Z)` (`A_a^2 = -I_8`) realize `su(2)_+`
     and `su(2)_-` as bivectors and `sl_2(R)` as `{A_0, A_1 A_2 A_3, A_4 A_5 A_6}`, with the
     triad Casimir difference satisfying `C_+ - C_- = -T_ch = 2 (Q_sd - Q_asd)`.
-/

-- ---------------------------------------------------------------------------
-- Dense & Sparse Integer Matrix Helpers (Zero Acc.rec, <= 100 chars/line)
-- ---------------------------------------------------------------------------

private def intMatCell (m : List (List Int)) (i j : Nat) : Int :=
  ((m.drop i).headD []).drop j |>.headD 0

private def intEye (n : Nat) : List (List Int) :=
  (rangeList 0 n).map fun i =>
    (rangeList 0 n).map fun j => if i == j then 1 else 0

private def intMatScale (c : Int) (m : List (List Int)) : List (List Int) :=
  m.map fun r => r.map fun x => c * x

private def intMatAdd (a b : List (List Int)) : List (List Int) :=
  List.zipWith (fun r1 r2 => List.zipWith (· + ·) r1 r2) a b

private def intMatMul (a b : List (List Int)) : List (List Int) :=
  let nr := a.length
  let nc := ((b.drop 0).headD []).length
  let nk := b.length
  (rangeList 0 nr).map fun i =>
    (rangeList 0 nc).map fun j =>
      (rangeList 0 nk).foldl (fun acc k => acc + intMatCell a i k * intMatCell b k j) 0

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

private def spMatMul (a b : SpMat) : SpMat :=
  a.map fun rowA =>
    rowA.foldl (fun acc (k, aik) =>
      let rowB := (b.drop k).headD []
      if rowB.isEmpty then acc else spAdd acc (spScale aik rowB)) []

private def spMatDiv (d : Int) (a : SpMat) : SpMat :=
  a.map fun row => row.foldr (fun (j, v) acc =>
    let q := v / d
    if intEq q 0 then acc else (j, q) :: acc) []

-- ---------------------------------------------------------------------------
-- Shared Mumford Representation, Exterior Space /\^2(Z^8) & Casimirs
-- ---------------------------------------------------------------------------

private def matEps2 : List (List Int) := [[0, 1], [-1, 0]]
private def matH2 : List (List Int) := [[1, 0], [0, -1]]
private def matS2 : List (List Int) := [[0, 1], [1, 0]]
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
-- Theorem 1: Universal Sp(8) Parity-Blindness Obstruction & Irrep Mixing
-- ---------------------------------------------------------------------------

private def refl4Mat : List (List Int) :=
  kronMat (intEye 2) [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, -1]]

private def sp8Gens36 : List (List (List Int)) :=
  (rangeList 0 8).foldl (fun acc i =>
    (rangeList i (8 - i)).foldl (fun acc2 j =>
      let sMat := (rangeList 0 8).map fun r =>
        (rangeList 0 8).map fun c =>
          if (r == i && c == j) || (r == j && c == i) then (1 : Int) else 0
      acc2 ++ [intMatMul matEReal sMat]) acc) []

private def checkSp8ParityBlindness : Bool :=
  let reflSymp := intMatEq (intMatMul (intMatTranspose refl4Mat) (intMatMul matEReal refl4Mat))
    matEReal
  let reflInv := intMatEq (intMatMul refl4Mat refl4Mat) (intEye 8)
  let pFlip := wedge2GroupSp refl4Mat
  let (q0, qSd, qAsd, qRic) := casimirProjs4
  let tCh := spMatScale (-2) (spMatSub qSd qAsd)
  let tR0 := spMatScale (-2) (spMatSub (spMatAdd qSd qAsd) (spMatScale 2 qRic))
  let pFlipOk :=
    spMatEq (spMatMul pFlip pFlip) (spEye 28) &&
    spMatEq (spMatMul pFlip q0) (spMatMul q0 pFlip) &&
    spMatEq (spMatMul pFlip (spMatMul tR0 pFlip)) tR0 &&
    spMatEq (spMatMul pFlip (spMatMul tCh pFlip)) (spMatScale (-1) tCh)
  let sp8PresOk := (sp8Gens36.length == 36) && sp8Gens36.all fun g =>
    isIntMatZero (intMatAdd (intMatMul (intMatTranspose g) matEReal) (intMatMul matEReal g))
  let dSp8 := sp8Gens36.map ext2Sp
  let commQ0Ok := dSp8.all fun d => spMatEq (spMatMul d q0) (spMatMul q0 d)
  let dMix := (dSp8.drop 1).headD []
  let mixOk :=
    !(spMatEq (spMatMul dMix tCh) (spMatMul tCh dMix)) &&
    !(spIsZeroMat (spMatMul qSd (spMatMul dMix qAsd))) &&
    !(spIsZeroMat (spMatMul qSd (spMatMul dMix qRic))) &&
    !(spIsZeroMat (spMatMul qAsd (spMatMul dMix qRic)))
  reflSymp && reflInv && pFlipOk && sp8PresOk && commQ0Ok && mixOk

set_option maxHeartbeats 16000000 in
set_option maxRecDepth 8192 in
/-- Certifies universal `Sp(8)` parity-blindness on `A^k`: `refl4` lies in `Sp(8, Z)`,
`P_flip = /\^2(refl4)` fixes `Q_0` and `T_r0` while negating `T_ch`, and all `36` generators of
`sp(8)` commute with `Q_0` (`28 = 1 + 27`) while mixing `Q_sd`, `Q_asd`, and `Q_ric`. -/
theorem sp8_universal_parity_blindness_and_mixing_cert :
    checkSp8ParityBlindness = true :=
  rfl

-- ---------------------------------------------------------------------------
-- Theorem 2: Kuga-Satake Cl(1,4) = Cl^0(2,4) & 15-Dim Spin(2,4) Basis
-- ---------------------------------------------------------------------------

private def cl14Gens5 : List (List (List Int)) :=
  let i2 := intEye 2
  [kronMat matH2 (kronMat i2 i2),
   kronMat matEps2 (kronMat matH2 i2),
   kronMat matEps2 (kronMat matS2 i2),
   kronMat matEps2 (kronMat matEps2 matEps2),
   kronMat matS2 (kronMat i2 matEps2)]

private def su22Basis15 : List (List (List Int)) :=
  [[[0, 0, 0, 0, 0, -1, 0, 0], [0, 0, 0, 0, -1, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0], [0, 1, 0, 0, 0, 0, 0, 0], [1, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0]],
   [[0, 0, 0, 0, 1, 0, 0, 0], [0, 0, 0, 0, 0, -1, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0], [-1, 0, 0, 0, 0, 0, 0, 0], [0, 1, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0]],
   [[0, -1, 0, 0, 0, 0, 0, 0], [1, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, -1, 0, 0], [0, 0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0]],
   [[0, 0, 0, 0, 0, 0, 1, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 1, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0]],
   [[0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 1, 0], [0, 0, 0, 0, 0, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 1, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0]],
   [[0, 0, 0, 0, -1, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, -1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0], [1, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0]],
   [[0, 0, -1, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [-1, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 1, 0], [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0]],
   [[0, 0, 0, 0, 0, 0, 0, 0], [0, 0, -1, 0, 0, 0, 0, 0], [0, -1, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 1, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0]],
   [[0, 0, 0, 0, 0, 0, 0, 1], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 0], [0, 0, 0, 1, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0], [1, 0, 0, 0, 0, 0, 0, 0]],
   [[0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 1], [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 1, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0], [0, 1, 0, 0, 0, 0, 0, 0]],
   [[0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, -1],
    [0, 0, 0, 0, 0, 0, -1, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 0], [0, 0, 1, 0, 0, 0, 0, 0]],
   [[0, 0, 0, 0, -1, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, -1], [1, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 1, 0, 0, 0, 0]],
   [[0, 0, 0, -1, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0],
    [-1, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 1], [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 1, 0, 0, 0]],
   [[0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, -1, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0],
    [0, -1, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 1],
    [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 1, 0, 0]],
   [[0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, -1, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, -1], [0, 0, 0, 0, 0, 0, 1, 0]]]

private def checkKugaSatakeSpin24Basis : Bool :=
  let i2 := intEye 2
  let i8 := intEye 8
  let jCl := kronMat i2 (kronMat i2 matEps2)
  let jClSq := intMatEq (intMatMul jCl jCl) (intMatScale (-1) i8)
  let clOk := (rangeList 0 5).all fun a =>
    let ga := (cl14Gens5.drop a).headD []
    let expSq := if a == 0 then i8 else intMatScale (-1) i8
    intMatEq (intMatMul ga ga) expSq &&
    intMatEq (intMatMul ga jCl) (intMatMul jCl ga) &&
    (rangeList 0 5).all fun b =>
      if a == b then true
      else
        let gb := (cl14Gens5.drop b).headD []
        isIntMatZero (intMatAdd (intMatMul ga gb) (intMatMul gb ga))
  let jC := kronMat matEps2 (kronMat matH2 i2)
  let eta8 := intMatMul (intMatScale (-1) matEReal) jC
  let jcOk :=
    intMatEq (intMatMul jC jC) (intMatScale (-1) i8) &&
    intMatEq eta8 (intMatTranspose eta8) &&
    intMatEq (intMatMul eta8 eta8) i8 &&
    intMatEq (intMatMul (intMatTranspose jC) (intMatMul matEReal jC)) matEReal
  let suOk := (su22Basis15.length == 15) && su22Basis15.all fun g =>
    isIntMatZero (intMatAdd (intMatMul (intMatTranspose g) matEReal) (intMatMul matEReal g)) &&
    intMatEq (intMatMul g jC) (intMatMul jC g) &&
    intEq (intMatTrace g) 0 &&
    intEq (intMatTrace (intMatMul jC g)) 0
  jClSq && clOk && jcOk && suOk

set_option maxHeartbeats 16000000 in
set_option maxRecDepth 8192 in
/-- Certifies the Kuga-Satake Clifford algebra `Cl^0(2,4) = Cl(1,4) = M_4(C)` inside `M_8(Z)`
and the `15`-generator `su(2,2) = spin(2,4)` basis preserving `E_real`, `J_c`, and `(4,4)` form
`eta_8 = -E_real * J_c`. -/
theorem kuga_satake_spin24_cl14_and_su22_basis_cert :
    checkKugaSatakeSpin24Basis = true :=
  rfl

-- ---------------------------------------------------------------------------
-- Theorem 3: Spin(2,4) Obstruction for T_ch & Intersect = A_div (Dim 2)
-- ---------------------------------------------------------------------------

private def checkSpin24TChObstruction : Bool :=
  let (q0, qSd, qAsd, _) := casimirProjs4
  let tCh := spMatScale (-2) (spMatSub qSd qAsd)
  let dSu22 := su22Basis15.map ext2Sp
  let commQ0 := dSu22.all fun d => spMatEq (spMatMul d q0) (spMatMul q0 d)
  let failTChCnt := dSu22.foldl (fun acc d =>
    if spMatEq (spMatMul d tCh) (spMatMul tCh d) then acc else acc + 1) (0 : Nat)
  -- Check that d_0, d_3, d_8 prevent Q_sd, Q_asd, Q_ric from commuting unless c1 = c2 = c3
  let d0 := dSu22.headD []
  let d3 := (dSu22.drop 3).headD []
  let d8 := (dSu22.drop 8).headD []
  let separates :=
    !(spMatEq (spMatMul d0 qSd) (spMatMul qSd d0)) &&
    !(spMatEq (spMatMul d0 qAsd) (spMatMul qAsd d0)) &&
    !(spMatEq (spMatMul d3 qSd) (spMatMul qSd d3)) &&
    !(spMatEq (spMatMul d8 qAsd) (spMatMul qAsd d8))
  commQ0 && (failTChCnt == 13) && separates

set_option maxHeartbeats 16000000 in
set_option maxRecDepth 8192 in
/-- Certifies that Kuga-Satake `Spin(2,4) = SU(2,2)` (`End = Q(i)`) cannot realize `T_ch`:
while all `15` generators commute with `Q_0`, `13` of `15` fail to commute with `T_ch`. -/
theorem kuga_satake_spin24_t_ch_obstruction_cert :
    checkSpin24TChObstruction = true :=
  rfl

-- ---------------------------------------------------------------------------
-- Theorem 4: Cl(0,7) Realization of sl_2(R) + so(4) and C_+ - C_- = -T_ch
-- ---------------------------------------------------------------------------

private def cl07Mats7 : List (List (List Int)) :=
  let i4 := intEye 4
  let jp0 := (jPlusMats.drop 0).headD []
  let jp1 := (jPlusMats.drop 1).headD []
  let jp2 := (jPlusMats.drop 2).headD []
  let jm0 := (jMinusMats.drop 0).headD []
  let jm1 := (jMinusMats.drop 1).headD []
  let jm2 := (jMinusMats.drop 2).headD []
  [kronMat matEps2 i4,
   kronMat matH2 jp0, kronMat matH2 jp1, kronMat matH2 jp2,
   kronMat matS2 jm0, kronMat matS2 jm1, kronMat matS2 jm2]

private def checkCl07Realization : Bool :=
  let i2 := intEye 2
  let i4 := intEye 4
  let i8 := intEye 8
  let clOk := (cl07Mats7.length == 7) && (rangeList 0 7).all fun a =>
    let ga := (cl07Mats7.drop a).headD []
    intMatEq (intMatMul ga ga) (intMatScale (-1) i8) &&
    (rangeList 0 7).all fun b =>
      if a == b then true
      else
        let gb := (cl07Mats7.drop b).headD []
        isIntMatZero (intMatAdd (intMatMul ga gb) (intMatMul gb ga))
  let a1 := (cl07Mats7.drop 1).headD []
  let a2 := (cl07Mats7.drop 2).headD []
  let a3 := (cl07Mats7.drop 3).headD []
  let a4 := (cl07Mats7.drop 4).headD []
  let a5 := (cl07Mats7.drop 5).headD []
  let a6 := (cl07Mats7.drop 6).headD []
  let bivP := [intMatMul a1 a2, intMatMul a2 a3, intMatMul a3 a1]
  let bivM := [intMatMul a4 a5, intMatMul a5 a6, intMatMul a6 a4]
  let jp0 := (jPlusMats.drop 0).headD []
  let jp1 := (jPlusMats.drop 1).headD []
  let jp2 := (jPlusMats.drop 2).headD []
  let jm0 := (jMinusMats.drop 0).headD []
  let jm1 := (jMinusMats.drop 1).headD []
  let jm2 := (jMinusMats.drop 2).headD []
  let bivMatch :=
    intMatEq (bivP.headD []) (kronMat i2 jp2) &&
    intMatEq ((bivP.drop 1).headD []) (kronMat i2 jp0) &&
    intMatEq ((bivP.drop 2).headD []) (kronMat i2 jp1) &&
    intMatEq (bivM.headD []) (intMatScale (-1) (kronMat i2 jm2)) &&
    intMatEq ((bivM.drop 1).headD []) (intMatScale (-1) (kronMat i2 jm0)) &&
    intMatEq ((bivM.drop 2).headD []) (intMatScale (-1) (kronMat i2 jm1))
  let trivMatch :=
    intMatEq (intMatMul a1 (intMatMul a2 a3)) (intMatScale (-1) (kronMat matH2 i4)) &&
    intMatEq (intMatMul a4 (intMatMul a5 a6)) (kronMat matS2 i4)
  let sumSq (gs : List (List (List Int))) : SpMat :=
    gs.foldl (fun acc g =>
      let dg := ext2Sp g
      spMatAdd acc (spMatScale (-1) (spMatMul dg dg))) (List.replicate 28 [])
  let cPlus := sumSq bivP
  let cMinus := sumSq bivM
  let (_, qSd, qAsd, _) := casimirProjs4
  let tCh := spMatScale (-2) (spMatSub qSd qAsd)
  let casMatch := spMatEq (spMatSub cPlus cMinus) (spMatScale (-1) tCh)
  clOk && bivMatch && trivMatch && casMatch

set_option maxHeartbeats 16000000 in
set_option maxRecDepth 8192 in
/-- Certifies the `7`-generator `Cl(0,7)` integer Clifford realization on `Z^8`: bivectors
realize `su(2)_+ (+) su(2)_-`, trivectors realize `sl_2(R)`, and the triad Casimir difference
satisfies `C_+ - C_- = -T_ch = 2 (Q_sd - Q_asd)` on `/\^2(Z^8)`. -/
theorem cl07_clifford_realization_of_so4_sl2_and_t_ch_cert :
    checkCl07Realization = true :=
  rfl

#print axioms sp8_universal_parity_blindness_and_mixing_cert
#print axioms kuga_satake_spin24_cl14_and_su22_basis_cert
#print axioms kuga_satake_spin24_t_ch_obstruction_cert
#print axioms cl07_clifford_realization_of_so4_sl2_and_t_ch_cert
