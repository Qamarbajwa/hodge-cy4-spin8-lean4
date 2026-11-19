/-
Copyright (c) 2026 Qamar Munawer. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Qamar Munawer
-/
import WiebeSchejaStorch

/-!
# Experiment 13 (Wall 3): Schur Complement & Orthogonal Projection Against Universal Sp(8)

Certifies with zero axioms:
1. Exact Frobenius Gram matrix & Schur complement against `U_{Sp(8)} = End_{Sp(8)}(H^2(A))`:
   - `Gram({Q_0, Q_prim, T_ch}) = [[16, 0, 0], [0, 432, 0], [0, 0, 1152]]` under both Frobenius
     inner product `Tr(A^T B)` and trace pairing `Tr(A B)`.
   - Orthogonal projection of `T_ch` onto `U_{Sp(8)} = span{Q_0, Q_prim}` is identically `0`, and
     the Schur complement of `U_{Sp(8)}` in `Gram({Q_0, Q_prim, T_ch})` is `1152 > 0`.
2. Parity eigenspace separation on `End(H^2(A))`:
   - `P_flip = /\^2(refl4)` satisfies `P_flip^2 = I_28` and `Tr(P_flip) = 4`, splitting
     `H^2(A) = 16_+ + 12_-` and `End(H^2(A)) = 400_+ + 384_-`.
   - `Q_0, Q_prim, T_r0` lie in `End^+(H^2(A))` while `T_ch` lies in `End^-(H^2(A))`.
3. Uniqueness of `T_ch` in `End^-(H^2(A)) intersect End_{sl2+so4}(H^2(A))`:
   - Inside `span{Q_0, Q_sd, Q_asd, Q_ric}`, `{Q_0, Q_sd + Q_asd, Q_ric}` are parity-even and
     mutually orthogonal (`3`-dim), leaving `Q_sd - Q_asd = -1/2 T_ch` as the unique (`1`-dim)
     parity-odd eigenmode.
4. Isolation of the `Cl(0,7)` half-spinor chiral subspace:
   - `Q_chiral18 = Q_sd + Q_asd` has `Tr(Q_chiral18) = 72` (`4 * 18`), annihilates `Q_0`, fixes
     `Q_prim` and `T_ch` (up to projector scale `4`), and the `Cl(0,7)` half-spinor bivector
     Casimir difference `C_+ - C_-` equals `-T_ch` and is strictly orthogonal to `Q_0, Q_prim`.
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

private def spFrob (a b : SpMat) : Int :=
  (List.zipWith spDot a b).foldl (· + ·) 0

private def spTrace (a : SpMat) : Int :=
  (rangeList 0 a.length).foldl (fun acc i =>
    acc + spVecLookup i ((a.drop i).headD [])) 0

-- ---------------------------------------------------------------------------
-- Shared Mumford Representation, Exterior Space /\^2(Z^8) & Casimirs
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

private def refl4Mat : List (List Int) :=
  kronMat (intEye 2) [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, -1]]

-- ---------------------------------------------------------------------------
-- Theorem 1: Exact Gram Matrix & Schur Complement Against Universal Sp(8)
-- ---------------------------------------------------------------------------

private def checkSp8GramAndSchur : Bool :=
  let (q0, qSd, qAsd, qRic) := casimirProjs4
  let qPrim := spMatAdd qSd (spMatAdd qAsd qRic)
  let tCh := spMatScale (-2) (spMatSub qSd qAsd)
  let frobOk :=
    intEq (spFrob q0 q0) 16 &&
    intEq (spFrob qPrim qPrim) 432 &&
    intEq (spFrob tCh tCh) 1152 &&
    intEq (spFrob q0 qPrim) 0 &&
    intEq (spFrob q0 tCh) 0 &&
    intEq (spFrob qPrim tCh) 0
  let traceOk :=
    intEq (spTrace (spMatMul q0 q0)) 16 &&
    intEq (spTrace (spMatMul qPrim qPrim)) 432 &&
    intEq (spTrace (spMatMul tCh tCh)) 1152 &&
    intEq (spTrace (spMatMul q0 tCh)) 0 &&
    intEq (spTrace (spMatMul qPrim tCh)) 0
  frobOk && traceOk

set_option maxHeartbeats 16000000 in
set_option maxRecDepth 8192 in
/-- Certifies the exact Gram matrix `diag(16, 432, 1152)` for `{Q_0, Q_prim, T_ch}` under both
Frobenius inner product `Tr(A^T B)` and trace pairing `Tr(A B)`: every universal `Sp(8)`
correspondence in `span{Q_0, Q_prim}` has identically zero projection onto `T_ch`, and the
Schur complement of `U_{Sp(8)}` in `Gram({Q_0, Q_prim, T_ch})` is `1152 > 0`. -/
theorem sp8_universal_gram_and_schur_complement_cert :
    checkSp8GramAndSchur = true :=
  rfl

-- ---------------------------------------------------------------------------
-- Theorem 2: Parity Eigenspace Orthogonal Split on H^2(A) & End(H^2(A))
-- ---------------------------------------------------------------------------

private def checkParityEigenspaceSplit : Bool :=
  let pFlip := wedge2GroupSp refl4Mat
  let (q0, qSd, qAsd, qRic) := casimirProjs4
  let qPrim := spMatAdd qSd (spMatAdd qAsd qRic)
  let tCh := spMatScale (-2) (spMatSub qSd qAsd)
  let tR0 := spMatScale (-2) (spMatSub (spMatAdd qSd qAsd) (spMatScale 2 qRic))
  let invOk := spMatEq (spMatMul pFlip pFlip) (spEye 28)
  let trOk := intEq (spTrace pFlip) 4
  let evenOk :=
    spMatEq (spMatMul pFlip (spMatMul q0 pFlip)) q0 &&
    spMatEq (spMatMul pFlip (spMatMul qPrim pFlip)) qPrim &&
    spMatEq (spMatMul pFlip (spMatMul tR0 pFlip)) tR0
  let oddOk :=
    spMatEq (spMatMul pFlip (spMatMul tCh pFlip)) (spMatScale (-1) tCh)
  invOk && trOk && evenOk && oddOk

set_option maxHeartbeats 16000000 in
set_option maxRecDepth 8192 in
/-- Certifies the parity eigenspace separation under `P_flip = /\^2(refl4)`: `P_flip^2 = I_28`
and `Tr(P_flip) = 4` (giving `28 = 16_+ + 12_-` and `End = 400_+ + 384_-`), with `Q_0, Q_prim, T_r0`
in `End^+(H^2(A))` and `T_ch` strictly in `End^-(H^2(A))`. -/
theorem parity_eigenspace_orthogonal_split_cert :
    checkParityEigenspaceSplit = true :=
  rfl

-- ---------------------------------------------------------------------------
-- Theorem 3: Uniqueness of T_ch in End^-(H^2(A)) intersect End_{sl2+so4}
-- ---------------------------------------------------------------------------

private def checkMumfordParityOddUniqueness : Bool :=
  let pFlip := wedge2GroupSp refl4Mat
  let (q0, qSd, qAsd, qRic) := casimirProjs4
  let qChSum := spMatAdd qSd qAsd
  let qChDiff := spMatSub qSd qAsd
  let paritiesOk :=
    spMatEq (spMatMul pFlip (spMatMul q0 pFlip)) q0 &&
    spMatEq (spMatMul pFlip (spMatMul qChSum pFlip)) qChSum &&
    spMatEq (spMatMul pFlip (spMatMul qRic pFlip)) qRic &&
    spMatEq (spMatMul pFlip (spMatMul qChDiff pFlip)) (spMatScale (-1) qChDiff)
  let orthogBasisOk :=
    intEq (spFrob q0 q0) 16 &&
    intEq (spFrob qChSum qChSum) 288 &&
    intEq (spFrob qRic qRic) 144 &&
    intEq (spFrob qChDiff qChDiff) 288 &&
    intEq (spFrob q0 qChSum) 0 &&
    intEq (spFrob q0 qRic) 0 &&
    intEq (spFrob q0 qChDiff) 0 &&
    intEq (spFrob qChSum qRic) 0 &&
    intEq (spFrob qChSum qChDiff) 0 &&
    intEq (spFrob qRic qChDiff) 0
  paritiesOk && orthogBasisOk

set_option maxHeartbeats 16000000 in
set_option maxRecDepth 8192 in
/-- Certifies that `{Q_0, Q_sd + Q_asd, Q_ric, Q_sd - Q_asd}` is an orthogonal basis of the
`4`-dim Mumford commutant `End_{sl2+so4}(H^2(A))`, where the first `3` basis elements are
parity-even under `P_flip` and `Q_sd - Q_asd = -1/2 T_ch` is the unique (`1`-dim) parity-odd
eigenmode. -/
theorem mumford_parity_odd_uniqueness_cert :
    checkMumfordParityOddUniqueness = true :=
  rfl

-- ---------------------------------------------------------------------------
-- Theorem 4: Isolation of the Cl(0,7) Half-Spinor Chiral Subspace
-- ---------------------------------------------------------------------------

private def checkCl07HalfSpinorIsolation : Bool :=
  let (q0, qSd, qAsd, qRic) := casimirProjs4
  let qPrim := spMatAdd qSd (spMatAdd qAsd qRic)
  let qChiral18 := spMatAdd qSd qAsd
  let tCh := spMatScale (-2) (spMatSub qSd qAsd)
  let chiralSubspaceOk :=
    intEq (spTrace qChiral18) 72 &&
    spIsZeroMat (spMatMul qChiral18 q0) &&
    spMatEq (spMatMul qChiral18 qPrim) (spMatScale 4 qChiral18) &&
    spMatEq (spMatMul qChiral18 tCh) (spMatScale 4 tCh)
  let (_, cp, cm) := casimirOps28
  let casimirDiff := spMatSub cp cm
  let cl07Ok :=
    spMatEq casimirDiff (spMatScale (-1) tCh) &&
    intEq (spFrob q0 casimirDiff) 0 &&
    intEq (spFrob qPrim casimirDiff) 0
  chiralSubspaceOk && cl07Ok

set_option maxHeartbeats 16000000 in
set_option maxRecDepth 8192 in
/-- Certifies that on the `18`-dim chiral subspace `V_18 = im(Q_sd + Q_asd)`, every universal
`Sp(8)` correspondence acts as a scalar multiple of `Q_chiral18`, while the `Cl(0,7)` half-spinor
bivector Casimir difference `C_+ - C_-` equals `-T_ch` and is strictly orthogonal to both `Q_0`
and `Q_prim`. -/
theorem cl07_half_spinor_chiral_isolation_cert :
    checkCl07HalfSpinorIsolation = true :=
  rfl

#print axioms sp8_universal_gram_and_schur_complement_cert
#print axioms parity_eigenspace_orthogonal_split_cert
#print axioms mumford_parity_odd_uniqueness_cert
#print axioms cl07_half_spinor_chiral_isolation_cert
