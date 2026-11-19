/-
Copyright (c) 2026 Qamar Munawer. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Qamar Munawer
-/
import WiebeSchejaStorch
import MumfordCMSpecializationExt

/-!
# Experiment 6: Fixed-Container Projected Wave Adaptation & Conjugate-Half Obstruction

Certifies with zero axioms:
1. Universal 50/50 half-node barrier on the fixed `70`-dim Weil container (`/\^4 Z^8`):
   `P_192 = K_Phi^2 (K_Phi^2 + 4 I) = 24 (w_Re w_Re^T + w_Im w_Im^T)`, and across all
   `8` coordinate `35 + 35` splits (`c in I` vs `c notin I`), the observed block `A_c`,
   hidden block `D_c`, and coupling block `B_c` satisfy `A_c^2 = 96 A_c`, `D_c^2 = 96 D_c`,
   `B_c B_c^T = 96 A_c`, and `tr(A_c) = tr(D_c) = 192`, locking half-slice fidelity at `<= 1/2`
   and giving exact Rayleigh defect on `v_half` (`||v_half||^2 = 4`, `||D_43 v_half||^2 = 19432`).
2. Exact `Z_2` chiral parity conjugate intertwining (`38` even + `32` odd):
   `K_Phi` is strictly off-diagonal (`K_ee = K_oo = 0`), `P_192` is block-diagonal (`P_eo = 0`),
   and `K_eo P_odd K_eo^T = 16 P_even`, `K_eo^T P_even K_eo = 16 P_odd`.
3. Exact Hodge-star `35 + 35` SD/ASD splitting:
   `* ^ 2 = I_70`, `* ^ T = *`, `tr(*) = 0`, and `* P_192 = P_192 * = P_192`.
4. Exact over-Z `8 x 8` `Z_2`-graded MF super-differential `Q_A^2 = 0`, `Q_B^2 = 0`,
   `(Q_A + Q_B)^2 = 2 (x_0^6 + x_1^6 - x_2^6) I_8` for the `4 x 4` mixed `(1,1,1,3)` MF,
   plus a discrete fixed-container adaptation step raising Weil fidelity `1/4 -> 4/7`.
-/

-- ---------------------------------------------------------------------------
-- Part 1: Exterior Basis (70-dim) & Sparse 70 x 70 Integer Matrix Engine
-- ---------------------------------------------------------------------------

private abbrev ExtForm6 := List (List Nat × Int)
private abbrev SpVec := List (Nat × Int)
private abbrev SpMat := List SpVec

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

private def exInsert (k : List Nat) (c : Int) : ExtForm6 → ExtForm6
  | [] => if intEq c 0 then [] else [(k, c)]
  | (k0, c0) :: rest =>
    if exNatEq k k0 then
      let nc := c + c0
      if intEq nc 0 then rest else (k0, nc) :: rest
    else if exNatLt k k0 then
      if intEq c 0 then (k0, c0) :: rest else (k, c) :: (k0, c0) :: rest
    else
      (k0, c0) :: exInsert k c rest

private def exAdd (a b : ExtForm6) : ExtForm6 :=
  b.foldl (fun acc (k, c) => exInsert k c acc) a

private def exScale (s : Int) (a : ExtForm6) : ExtForm6 :=
  if intEq s 0 then [] else a.map fun (k, c) => (k, s * c)

private def exLookup (k : List Nat) : ExtForm6 → Int
  | [] => 0
  | (k0, c0) :: rest => if exNatEq k k0 then c0 else exLookup k rest

private def exDot (a b : ExtForm6) : Int :=
  a.foldl (fun acc (k, c) => acc + c * exLookup k b) 0

private def replaceAtNat6 (xs : List Nat) (pos val : Nat) : List Nat :=
  match xs with
  | [] => []
  | x :: rest =>
    match pos with
    | 0 => val :: rest
    | k + 1 => x :: replaceAtNat6 rest k val

private def allTuples4 : List (List Nat) :=
  (rangeList 0 8).foldl (fun a0 i0 =>
    (rangeList (i0 + 1) (8 - i0 - 1)).foldl (fun a1 i1 =>
      (rangeList (i1 + 1) (8 - i1 - 1)).foldl (fun a2 i2 =>
        (rangeList (i2 + 1) (8 - i2 - 1)).foldl (fun a3 i3 =>
          a3 ++ [[i0, i1, i2, i3]]) a2) a1) a0) []

private def phiStep8 (i : Nat) : Nat × Int :=
  if i == 0 then (1, -1)
  else if i == 1 then (0, 1)
  else if i == 2 then (3, -1)
  else if i == 3 then (2, 1)
  else if i == 4 then (5, 1)
  else if i == 5 then (4, -1)
  else if i == 6 then (7, 1)
  else (6, -1)

private def applyKPhi4 (f : ExtForm6) : ExtForm6 :=
  f.foldl (fun acc (tup, c) =>
    (rangeList 0 tup.length).foldl (fun acc2 pos =>
      let i := (tup.drop pos).headD 0
      let (j, v) := phiStep8 i
      match exSortNat (replaceAtNat6 tup pos j) with
      | none => acc2
      | some (sk, sg) => exInsert sk (c * v * sg) acc2) acc) []

private def applyP192Op (f : ExtForm6) : ExtForm6 :=
  let k2 := applyKPhi4 (applyKPhi4 f)
  let mid := exAdd k2 (exScale 4 f)
  applyKPhi4 (applyKPhi4 mid)

private def matJ43Rows : List (List Int) :=
  [[0, 47, -6, -2, -10, -10, -10, 10],
   [-47, 0, 2, -6, -10, 10, 10, 10],
   [6, -2, 0, 53, 20, -10, -10, -20],
   [2, 6, -53, 0, -10, -20, -20, 10],
   [-10, -10, 20, -10, 0, 50, 7, 0],
   [-10, 10, -10, -20, -50, 0, 0, 7],
   [-10, 10, -10, -20, -7, 0, 0, 50],
   [10, 10, -20, 10, 0, -7, -50, 0]]

private def j43SparseRows : List (List (Nat × Int)) :=
  (rangeList 0 8).map fun i =>
    let row := (matJ43Rows.drop i).headD []
    (rangeList 0 8).foldl (fun acc j =>
      let v := (row.drop j).headD 0
      if intEq v 0 then acc else acc ++ [(j, v)]) []

private def applyD43Op (f : ExtForm6) : ExtForm6 :=
  f.foldl (fun acc (tup, c) =>
    (rangeList 0 tup.length).foldl (fun acc2 pos =>
      let i := (tup.drop pos).headD 0
      let nzRow := (j43SparseRows.drop i).headD []
      nzRow.foldl (fun acc3 (j, v) =>
        match exSortNat (replaceAtNat6 tup pos j) with
        | none => acc3
        | some (sk, sg) => exInsert sk (c * v * sg) acc3) acc2) acc) []

-- Fast sorted sparse row/vector operations (sorted by column index Nat)
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

private def spMatTranspose (nCols : Nat) (a : SpMat) : SpMat :=
  let init : List SpVec := (rangeList 0 nCols).map fun _ => []
  (rangeList 0 a.length).foldl (fun cols i =>
    let row := (a.drop i).headD []
    if row.isEmpty then cols
    else
      (rangeList 0 nCols).map fun j =>
        let curCol := (cols.drop j).headD []
        let aij := spVecLookup j row
        if intEq aij 0 then curCol else spInsert i aij curCol) init

private def spMapCol (oldC : Nat) : List (Nat × Nat) → Option Nat
  | [] => none
  | (oc, nc) :: rest => if oldC == oc then some nc else spMapCol oldC rest

private def spMatSubBlock (rIdxs cIdxs : List Nat) (m : SpMat) : SpMat :=
  let cPairs := (rangeList 0 cIdxs.length).map fun newC =>
    ((cIdxs.drop newC).headD 0, newC)
  rIdxs.map fun r =>
    let row := (m.drop r).headD []
    row.foldl (fun acc (oldC, val) =>
      match spMapCol oldC cPairs with
      | none => acc
      | some newC => spInsert newC val acc) []

private def tupleIndexAux (tup : List Nat) (idx : Nat) : List (List Nat) → Nat
  | [] => 0
  | t :: ts => if exNatEq tup t then idx else tupleIndexAux tup (idx + 1) ts

private def extToSpVec (tuples : List (List Nat)) (f : ExtForm6) : SpVec :=
  f.foldl (fun acc (tup, c) => spInsert (tupleIndexAux tup 0 tuples) c acc) []

-- Build exact P_192 rows directly from applyP192Op across all 70 basis 4-tuples
private def p192OpMat : SpMat :=
  let tuples := allTuples4
  tuples.map fun tup => extToSpVec tuples (applyP192Op [(tup, 1)])

private def k4OpMat : SpMat :=
  let tuples := allTuples4
  tuples.map fun tup => extToSpVec tuples (applyKPhi4 [(tup, 1)])

private def spVecNormSq (v : SpVec) : Int :=
  v.foldl (fun acc (_, c) => acc + c * c) 0

private def spVecDotGo : Nat → SpVec → SpVec → Int
  | 0, _, _ => 0
  | fuel + 1, a, b =>
    match a with
    | [] => 0
    | (i1, v1) :: r1 =>
      match b with
      | [] => 0
      | (i2, v2) :: r2 =>
        if i1 == i2 then v1 * v2 + spVecDotGo fuel r1 r2
        else if Nat.blt i1 i2 then spVecDotGo fuel r1 b
        else spVecDotGo fuel a r2

private def spVecDot (a b : SpVec) : Int :=
  spVecDotGo (a.length + b.length + 1) a b

-- ---------------------------------------------------------------------------
-- Theorem 1: Universal 50/50 Half-Node Barrier across all 8 Splits
-- ---------------------------------------------------------------------------

private def checkUniversal5050Barrier : Bool :=
  let tuples := allTuples4
  let wReSp := extToSpVec tuples ei4WeilReForm
  let wImSp := extToSpVec tuples ei4WeilImForm
  let p192 := p192OpMat
  let rank2Match := (rangeList 0 70).all fun r =>
    let rowOp := (p192.drop r).headD []
    let cRe := spVecLookup r wReSp
    let cIm := spVecLookup r wImSp
    let rowRank2 := spScale 24 (spAdd (spScale cRe wReSp) (spScale cIm wImSp))
    spVecEq rowOp rowRank2
  let nnzCount := p192.foldl (fun acc row => acc + row.length) 0
  let symOk := spMatEq p192 (spMatTranspose 70 p192)
  let splitsOk := (rangeList 0 8).all fun c =>
    let iIn := (rangeList 0 70).filter fun i => ((tuples.drop i).headD []).contains c
    let iOut := (rangeList 0 70).filter fun i => !((tuples.drop i).headD []).contains c
    let aBlk := spMatSubBlock iIn iIn p192
    let bBlk := spMatSubBlock iIn iOut p192
    let dBlk := spMatSubBlock iOut iOut p192
    let bT := spMatTranspose 35 bBlk
    (iIn.length == 35) && (iOut.length == 35) &&
    spMatEq (spMatMul aBlk aBlk) (spMatScale 96 aBlk) &&
    spMatEq (spMatMul dBlk dBlk) (spMatScale 96 dBlk) &&
    spMatEq (spMatMul bBlk bT) (spMatScale 96 aBlk) &&
    intEq (spTrace aBlk) 192 && intEq (spTrace dBlk) 192
  let vHalf := ei4WeilReForm.filter fun (t, _) => t.contains 0
  let vHalfSp := extToSpVec tuples vHalf
  let pHalf := extToSpVec tuples (applyP192Op vHalf)
  let dHalf := applyD43Op vHalf
  let rayleighOk :=
    intEq (spVecNormSq vHalfSp) 4 &&
    intEq (spVecDot vHalfSp pHalf) 384 &&
    intEq (exDot dHalf dHalf) 19432 &&
    (applyD43Op ei4WeilReForm).isEmpty &&
    intEq (spVecDot wReSp (extToSpVec tuples (applyP192Op ei4WeilReForm))) 1536
  (tuples.length == 70) && rank2Match && (nnzCount == 128) && symOk && splitsOk && rayleighOk

set_option maxHeartbeats 12000000 in
set_option maxRecDepth 8192 in
/-- Universal 50/50 half-node barrier on the `70`-dim Weil container:
`P_192 = 24 (w_Re w_Re^T + w_Im w_Im^T)` (`128` nonzeros), and for every coordinate `35 + 35`
split `c = 0..7`: `A_c^2 = 96 A_c`, `D_c^2 = 96 D_c`, `B_c B_c^T = 96 A_c`, and `tr = 192`,
proving half-slice fidelity `<= 1/2` alongside exact half-node Rayleigh defect `19432`. -/
theorem weil_p192_universal_5050_half_node_barrier_cert :
    checkUniversal5050Barrier = true :=
  rfl

-- ---------------------------------------------------------------------------
-- Theorem 2: Exact Z_2 Chiral Parity Conjugate-Half Intertwining (38 + 32)
-- ---------------------------------------------------------------------------

private def isOddTupleParity (t : List Nat) : Bool :=
  (t.foldl (fun acc x => acc + x % 2) 0) % 2 == 1

private def checkZ2ChiralParityIntertwining : Bool :=
  let tuples := allTuples4
  let iEven := (rangeList 0 70).filter fun i => !isOddTupleParity ((tuples.drop i).headD [])
  let iOdd := (rangeList 0 70).filter fun i => isOddTupleParity ((tuples.drop i).headD [])
  let k4 := k4OpMat
  let p192 := p192OpMat
  let kSkew := spMatEq (spMatTranspose 70 k4) (spMatScale (-1) k4)
  let kEE := spMatSubBlock iEven iEven k4
  let kOO := spMatSubBlock iOdd iOdd k4
  let kEO := spMatSubBlock iEven iOdd k4
  let kEOT := spMatTranspose 32 kEO
  let pEE := spMatSubBlock iEven iEven p192
  let pOO := spMatSubBlock iOdd iOdd p192
  let pEO := spMatSubBlock iEven iOdd p192
  (iEven.length == 38) && (iOdd.length == 32) && kSkew &&
  spIsZeroMat kEE && spIsZeroMat kOO && spIsZeroMat pEO &&
  spMatEq (spMatMul pEE pEE) (spMatScale 192 pEE) && intEq (spTrace pEE) 192 &&
  spMatEq (spMatMul pOO pOO) (spMatScale 192 pOO) && intEq (spTrace pOO) 192 &&
  spMatEq (spMatMul (spMatMul kEO pOO) kEOT) (spMatScale 16 pEE) &&
  spMatEq (spMatMul (spMatMul kEOT pEE) kEO) (spMatScale 16 pOO)

set_option maxHeartbeats 8000000 in
set_option maxRecDepth 8192 in
/-- Exact `Z_2` chiral parity conjugate-half intertwining on `/\^4 Z^8 = V_even(38) (+) V_odd(32)`:
`K_ee = K_oo = 0`, `P_eo = 0`, `P_even^2 = 192 P_even`, `P_odd^2 = 192 P_odd`, and
`K_eo P_odd K_eo^T = 16 P_even`, `K_eo^T P_even K_eo = 16 P_odd`. -/
theorem weil_z2_chiral_parity_conjugate_intertwining_cert :
    checkZ2ChiralParityIntertwining = true :=
  rfl

-- ---------------------------------------------------------------------------
-- Theorem 3: Exact Hodge-Star 50/50 Self-Dual / Anti-Self-Dual Projector Law
-- ---------------------------------------------------------------------------

private def starOpMat : SpMat :=
  let tuples := allTuples4
  tuples.map fun tup =>
    let comp := (rangeList 0 8).filter fun x => !tup.contains x
    match exSortNat (tup ++ comp) with
    | none => []
    | some (_, sgn) => [(tupleIndexAux comp 0 tuples, sgn)]

private def checkHodgeStarSdProjector : Bool :=
  let star := starOpMat
  let p192 := p192OpMat
  spMatEq (spMatMul star star) (spEye 70) &&
  spMatEq star (spMatTranspose 70 star) &&
  intEq (spTrace star) 0 &&
  spMatEq (spMatMul star p192) p192 &&
  spMatEq (spMatMul p192 star) p192

set_option maxHeartbeats 8000000 in
set_option maxRecDepth 8192 in
/-- Exact `50/50` Hodge-star self-dual / anti-self-dual splitting on `/\^4 Z^8`:
`* ^ 2 = I_70`, `* ^ T = *`, `tr(*) = 0`, and `* P_192 = P_192 * = P_192`. -/
theorem weil_hodge_star_5050_sd_asd_projector_cert :
    checkHodgeStarSdProjector = true :=
  rfl

-- ---------------------------------------------------------------------------
-- Theorem 4: 8x8 Z_2-Graded Super-Differential Q^2 = 2F_1 I_8 & Adaptation Step
-- ---------------------------------------------------------------------------

private def monEq6Fast : Monom6 → Monom6 → Bool
  | [], [] => true
  | [], _ :: _ => false
  | _ :: _, [] => false
  | x :: xs, y :: ys => (x == y) && monEq6Fast xs ys

private def monLt6Fast : Monom6 → Monom6 → Bool
  | [], [] => false
  | [], _ :: _ => false
  | _ :: _, [] => false
  | x :: xs, y :: ys => if x == y then monLt6Fast xs ys else Nat.blt x y

private def polyMergeFastGo : Nat → Poly6 → Poly6 → Poly6
  | 0, p, _ => p
  | fuel + 1, p, q =>
    match p with
    | [] => q
    | (m1, c1) :: r1 =>
      match q with
      | [] => p
      | (m2, c2) :: r2 =>
        if monEq6Fast m1 m2 then
          let s := c1 + c2
          if intEq s 0 then polyMergeFastGo fuel r1 r2
          else (m1, s) :: polyMergeFastGo fuel r1 r2
        else if monLt6Fast m1 m2 then
          (m1, c1) :: polyMergeFastGo fuel r1 q
        else
          (m2, c2) :: polyMergeFastGo fuel p r2

private def fastPAdd (p q : Poly6) : Poly6 :=
  if p.isEmpty then q
  else if q.isEmpty then p
  else polyMergeFastGo (p.length + q.length + 1) p q

private def fastPSub (p q : Poly6) : Poly6 :=
  fastPAdd p (polyNeg6 q)

private def pScale (c : Int) (p : Poly6) : Poly6 :=
  if intEq c 0 then [] else p.map fun (m, v) => (m, c * v)

private def pAddList (ps : List Poly6) : Poly6 :=
  ps.foldl fastPAdd []

private def fastPMul (p q : Poly6) : Poly6 :=
  if p.isEmpty || q.isEmpty then []
  else
    let rows := p.map fun (m1, c1) => q.map fun (m2, c2) => (monomMul6 m1 m2, c1 * c2)
    pAddList rows

private def pCell (m : List (List Poly6)) (i j : Nat) : Poly6 :=
  ((m.drop i).headD []).drop j |>.headD []

private def pDet3 (mat : List (List Poly6)) : Poly6 :=
  let c00 := pCell mat 0 0
  let c01 := pCell mat 0 1
  let c02 := pCell mat 0 2
  let c10 := pCell mat 1 0
  let c11 := pCell mat 1 1
  let c12 := pCell mat 1 2
  let c20 := pCell mat 2 0
  let c21 := pCell mat 2 1
  let c22 := pCell mat 2 2
  let m0 := fastPMul c00 (fastPSub (fastPMul c11 c22) (fastPMul c12 c21))
  let m1 := fastPMul c01 (fastPSub (fastPMul c10 c22) (fastPMul c12 c20))
  let m2 := fastPMul c02 (fastPSub (fastPMul c10 c21) (fastPMul c11 c20))
  fastPAdd (fastPSub m0 m1) m2

private def dropIdxP (xs : List Poly6) (idx : Nat) : List Poly6 :=
  match xs with
  | [] => []
  | x :: rest => match idx with | 0 => rest | k + 1 => x :: dropIdxP rest k

private def dropRowP (rows : List (List Poly6)) (idx : Nat) : List (List Poly6) :=
  match rows with
  | [] => []
  | r :: rest => match idx with | 0 => rest | k + 1 => r :: dropRowP rest k

private def pAdj4 (mat : List (List Poly6)) : List (List Poly6) :=
  (rangeList 0 4).map fun j =>
    (rangeList 0 4).map fun i =>
      let sub := (dropRowP mat i).map fun r => dropIdxP r j
      let d := pDet3 sub
      if (i + j) % 2 == 0 then d else polyNeg6 d

private def pMatMulFast (a b : List (List Poly6)) : List (List Poly6) :=
  let n := a.length
  let c := ((b.drop 0).headD []).length
  (rangeList 0 n).map fun i =>
    (rangeList 0 c).map fun j =>
      (rangeList 0 b.length).foldl (fun acc k =>
        let aik := pCell a i k
        let bkj := pCell b k j
        if aik.isEmpty || bkj.isEmpty then acc else fastPAdd acc (fastPMul aik bkj)) []

private def pRowEq (r1 r2 : List Poly6) : Bool :=
  (r1.length == r2.length) && (List.zipWith polyEq6 r1 r2).all id

private def pMatEq (m1 m2 : List (List Poly6)) : Bool :=
  (m1.length == m2.length) && (List.zipWith pRowEq m1 m2).all id

private def isZeroPMat (m : List (List Poly6)) : Bool :=
  m.all fun row => row.all List.isEmpty

private def matA1Mixed : List (List Poly6) :=
  let x0 := varPow6 0 1
  let x1 := varPow6 1 1
  let x2 := varPow6 2 1
  let r3c0 : Poly6 := [([0, 1, 2, 0, 0, 0], -1), ([2, 1, 0, 0, 0, 0], 2)]
  let r3c1 : Poly6 := [([1, 2, 0, 0, 0, 0], -1), ([2, 0, 1, 0, 0, 0], -1),
                       ([3, 0, 0, 0, 0, 0], 1)]
  let r3c2 : Poly6 := [([0, 1, 2, 0, 0, 0], -1), ([0, 3, 0, 0, 0, 0], -1)]
  let r3c3 : Poly6 := [([0, 0, 3, 0, 0, 0], -1)]
  [[fastPSub (polyNeg6 x0) (pScale 2 x2), x1, x0, []],
   [pScale 2 x1, fastPSub x0 x2, [], x0],
   [fastPSub (pScale (-2) x0) x2, x1, polyNeg6 x2, x1],
   [r3c0, r3c1, r3c2, r3c3]]

private def checkSuperdiffAndWaveStep : Bool :=
  let matB1 := (pAdj4 matA1Mixed).map fun row => row.map polyNeg6
  let qA : List (List Poly6) :=
    (rangeList 0 8).map fun i =>
      (rangeList 0 8).map fun j =>
        if Nat.blt i 4 && Nat.ble 4 j then pCell matA1Mixed i (j - 4) else []
  let qB : List (List Poly6) :=
    (rangeList 0 8).map fun i =>
      (rangeList 0 8).map fun j =>
        if Nat.ble 4 i && Nat.blt j 4 then pCell matB1 (i - 4) j else []
  let qFull : List (List Poly6) :=
    (rangeList 0 8).map fun i =>
      (rangeList 0 8).map fun j =>
        if Nat.blt i 4 && Nat.ble 4 j then pCell matA1Mixed i (j - 4)
        else if Nat.ble 4 i && Nat.blt j 4 then pCell matB1 (i - 4) j
        else []
  let f2 := pAddList [pScale 2 (varPow6 0 6), pScale 2 (varPow6 1 6), pScale (-2) (varPow6 2 6)]
  let tgt8 := (rangeList 0 8).map fun i =>
    (rangeList 0 8).map fun j => if i == j then f2 else []
  let qOk :=
    isZeroPMat (pMatMulFast qA qA) &&
    isZeroPMat (pMatMulFast qB qB) &&
    pMatEq (pMatMulFast qFull qFull) tgt8
  let tuples := allTuples4
  let psi0 := exAdd ei4WeilReForm ei4ThetaSqForm
  let psi1 := exAdd (exScale 2 ei4WeilReForm) ei4ThetaSqForm
  let psi0Sp := extToSpVec tuples psi0
  let psi1Sp := extToSpVec tuples psi1
  let n0 := spVecNormSq psi0Sp
  let n1 := spVecNormSq psi1Sp
  let p0 := spVecDot psi0Sp (extToSpVec tuples (applyP192Op psi0))
  let p1 := spVecDot psi1Sp (extToSpVec tuples (applyP192Op psi1))
  let diff := p1 * n0 - p0 * n1
  let stepOk :=
    (applyD43Op psi0).isEmpty && (applyD43Op psi1).isEmpty &&
    intEq n0 32 && intEq p0 1536 && intEq n1 56 && intEq p1 6144 &&
    intEq diff (Int.ofNat diff.natAbs) && !(intEq diff 0)
  qOk && stepOk

set_option maxHeartbeats 8000000 in
set_option maxRecDepth 8192 in
/-- Exact over-Z `8 x 8` `Z_2`-graded super-differential `Q_A^2 = 0`, `Q_B^2 = 0`,
`(Q_A + Q_B)^2 = 2 (x_0^6 + x_1^6 - x_2^6) I_8` for the `4 x 4` mixed `(1,1,1,3)` MF,
plus exact fixed-container wave-adaptation contraction `w_Re + Theta^2 -> 2 w_Re + Theta^2`
raising Weil fidelity from `1/4` (`1536 / (192 * 32)`) to `4/7` (`6144 / (192 * 56)`). -/
theorem mf_z2_graded_superdifferential_conjugate_half_cert :
    checkSuperdiffAndWaveStep = true :=
  rfl

#print axioms weil_p192_universal_5050_half_node_barrier_cert
#print axioms weil_z2_chiral_parity_conjugate_intertwining_cert
#print axioms weil_hodge_star_5050_sd_asd_projector_cert
#print axioms mf_z2_graded_superdifferential_conjugate_half_cert
