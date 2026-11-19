/-
Copyright (c) 2026 Qamar Munawer. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Qamar Munawer
-/
import MumfordCMSpecializationExt

/-!
# Unified Wave-Function-to-Matrix Operator Certificates in Lean 4

Certifies with zero axioms the three matrix-operator pillars unifying the project:
1. Cyclotomic Fermat DFT unitary matrix `U_6` over `Z[zeta_6]`: `U_6 U_6* = U_6* U_6 = 6 I_6`.
2. Dwork sextic `5 x 5` Picard-Fuchs companion matrices: Fermat indicial operator `M_648`
   satisfying `prod_{k=1}^5 (M_648 - 108 k I_5) = 0`, and LCS nilpotent Jordan block
   `M_LCS(0)^4 != 0`, `M_LCS(0)^5 = 0`.
3. Exact `8 x 8` integer Weil `U(2, 2)` complex structure `J_43 = 43 * J_H`: `J_43^2 = -1849 I_8`,
   `J_43^T E_8 J_43 = 1849 E_8`, `[J_43, Phi_8] = 0`, and all `8` Sylvester leading principal
   minors of symmetric polarization `-E_8 J_43` are strictly positive (`det = 43^8`).
4. Full `70 x 70` Hodge Hamiltonian `D_43^(4)`, `Q(i)` twist `K_Phi^(4)`, and algebraic Weil
   spectral projector `P_192 = K_Phi^2 (K_Phi^2 + 4 I)` verified exhaustively across all `70`
   basis 4-tuples of `/\^4 Z^8`: `P_192^2 = 192 P_192`, `tr(P_192) = 384`, `D_43 P_192 = 0`,
   `[D_43, K_Phi] = 0`, `K_Phi` rotates `w_Re <-> w_Im`, and `Theta^2` lies in `ker(P_192)`.
-/

-- ---------------------------------------------------------------------------
-- Pillar I: 6 x 6 Unitary Cyclotomic Matrix U_6 over Z[zeta_6]
-- ---------------------------------------------------------------------------

private abbrev Z6Int := Int × Int

private def z6Add (a b : Z6Int) : Z6Int := (a.1 + b.1, a.2 + b.2)
private def z6Mul (a b : Z6Int) : Z6Int :=
  (a.1 * b.1 - a.2 * b.2, a.1 * b.2 + a.2 * b.1 + a.2 * b.2)
private def z6Conj (a : Z6Int) : Z6Int := (a.1 + a.2, -a.2)
private def z6Eq (a b : Z6Int) : Bool := intEq a.1 b.1 && intEq a.2 b.2

private def z6PowMod6 (n : Nat) : Z6Int :=
  let r := n % 6
  if r == 0 then (1, 0)
  else if r == 1 then (0, 1)
  else if r == 2 then (-1, 1)
  else if r == 3 then (-1, 0)
  else if r == 4 then (0, -1)
  else (1, -1)

private def z6MatCell (m : List (List Z6Int)) (i j : Nat) : Z6Int :=
  ((m.drop i).headD []).drop j |>.headD (0, 0)

private def z6MatMul (a b : List (List Z6Int)) : List (List Z6Int) :=
  let n := a.length
  let c := ((b.drop 0).headD []).length
  (rangeList 0 n).map fun i =>
    (rangeList 0 c).map fun j =>
      (rangeList 0 n).foldl (fun acc k =>
        z6Add acc (z6Mul (z6MatCell a i k) (z6MatCell b k j))) (0, 0)

private def z6MatEq (a b : List (List Z6Int)) : Bool :=
  let n := a.length
  (n == b.length) &&
  (rangeList 0 n).all fun i =>
    (rangeList 0 n).all fun j => z6Eq (z6MatCell a i j) (z6MatCell b i j)

private def checkCyclotomicU6 : Bool :=
  let u6 : List (List Z6Int) :=
    (rangeList 0 6).map fun j => (rangeList 0 6).map fun k => z6PowMod6 (j * k)
  let u6Dag : List (List Z6Int) :=
    (rangeList 0 6).map fun j => (rangeList 0 6).map fun k => z6Conj (z6MatCell u6 k j)
  let tgt6 : List (List Z6Int) :=
    (rangeList 0 6).map fun i =>
      (rangeList 0 6).map fun j => if i == j then (6, 0) else (0, 0)
  z6MatEq (z6MatMul u6 u6Dag) tgt6 && z6MatEq (z6MatMul u6Dag u6) tgt6

/-- Certifies `6 x 6` cyclotomic DFT wave-function unitarity `U_6 U_6* = U_6* U_6 = 6 I_6`
over exact `Z[zeta_6]`. -/
theorem cyclotomic_u6_unitary_wavefunction_matrix_cert :
    checkCyclotomicU6 = true :=
  rfl

-- ---------------------------------------------------------------------------
-- Pillar II: Dwork Sextic 5 x 5 Picard-Fuchs Companion Matrices
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

private def checkPicardFuchs5x5 : Bool :=
  let mFermat648 : List (List Int) :=
    [[0, 648, 0, 0, 0],
     [0, 0, 648, 0, 0],
     [0, 0, 0, 648, 0],
     [0, 0, 0, 0, 648],
     [10, -137, 675, -1530, 1620]]
  let i5 := intEye 5
  let chProd := [1, 2, 3, 4, 5].foldl (fun acc k =>
    let fac := intMatSub mFermat648 (intMatScale (108 * Int.ofNat k) i5)
    intMatMul acc fac) i5
  let trace648 := [0, 1, 2, 3, 4].foldl (fun acc i => acc + intMatCell mFermat648 i i) 0
  let mLcs0 : List (List Int) :=
    [[0, 1, 0, 0, 0],
     [0, 0, 1, 0, 0],
     [0, 0, 0, 1, 0],
     [0, 0, 0, 0, 1],
     [0, 0, 0, 0, 0]]
  let p2 := intMatMul mLcs0 mLcs0
  let p4 := intMatMul p2 p2
  let p5 := intMatMul p4 mLcs0
  isIntMatZero chProd && intEq trace648 1620 && !(isIntMatZero p4) && isIntMatZero p5

/-- Certifies `5 x 5` Picard-Fuchs companion matrices in both Fermat and LCS windows:
`(1) prod_{k=1}^5 (M_648 - 108 k I_5) = 0` (`trace = 1620 = (5/2) * 648`) and
`(2) M_LCS(0)^4 != 0`, `M_LCS(0)^5 = 0` (maximally unipotent monodromy). -/
theorem picard_fuchs_5x5_companion_matrix_cert :
    checkPicardFuchs5x5 = true :=
  rfl

-- ---------------------------------------------------------------------------
-- Pillar IIIa: 8 x 8 Exact Integer Weil U(2, 2) Complex Structure J_43
-- ---------------------------------------------------------------------------

private def matJ43 : List (List Int) :=
  [[0, 47, -6, -2, -10, -10, -10, 10],
   [-47, 0, 2, -6, -10, 10, 10, 10],
   [6, -2, 0, 53, 20, -10, -10, -20],
   [2, 6, -53, 0, -10, -20, -20, 10],
   [-10, -10, 20, -10, 0, 50, 7, 0],
   [-10, 10, -10, -20, -50, 0, 0, 7],
   [-10, 10, -10, -20, -7, 0, 0, 50],
   [10, 10, -20, 10, 0, -7, -50, 0]]

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

private def checkWeilJ43 : Bool :=
  let j2 := intMatMul matJ43 matJ43
  let sqOk := intMatEq j2 (intMatScale (-1849) (intEye 8))
  let rbrMat := intMatMul (intMatTranspose matJ43) (intMatMul matE8 matJ43)
  let rbrOk := intMatEq rbrMat (intMatScale 1849 matE8)
  let commOk := intMatEq (intMatMul matJ43 matPhi8) (intMatMul matPhi8 matJ43)
  let gPos := intMatMul (intMatScale (-1) matE8) matJ43
  let symOk := intMatEq gPos (intMatTranspose gPos)
  let (minors, divOk) := bareissAllMinors gPos 8
  let expectedMinors : List Int :=
    [47, 2209, 115197, 6007401, 226594950, 8547002500, 316068152450, 11688200277601]
  let minsOk := divOk && (minors.length == 8) &&
    (List.zipWith intEq minors expectedMinors).all id &&
    minors.all fun v => intEq v (Int.ofNat v.natAbs) && !(intEq v 0)
  sqOk && rbrOk && commOk && symOk && minsOk

set_option maxHeartbeats 4000000 in
/-- Certifies the exact `8 x 8` integer Weil `U(2, 2)` complex structure `J_43`:
`J_43^2 = -1849 I_8`, `J_43^T E_8 J_43 = 1849 E_8`, `[J_43, Phi_8] = 0`, and all `8` Sylvester
leading principal minors of `-E_8 J_43` are strictly positive via Bareiss elimination. -/
theorem weil_u22_8x8_exact_complex_structure_matrix_cert :
    checkWeilJ43 = true :=
  rfl

-- ---------------------------------------------------------------------------
-- Pillar IIIb: 70 x 70 Hodge Hamiltonian, K_Phi Twist & Projector P_192
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
  | (k1, c1) :: r1, (k2, c2) :: r2 =>
    exNatEq k1 k2 && intEq c1 c2 && exEq r1 r2

private def exLookup (k : List Nat) : ExtSparse → Int
  | [] => 0
  | (k0, c0) :: rest => if exNatEq k k0 then c0 else exLookup k rest

private def wfReplaceAtNat (xs : List Nat) (pos val : Nat) : List Nat :=
  match xs with
  | [] => []
  | x :: rest =>
    match pos with
    | 0 => val :: rest
    | p' + 1 => x :: wfReplaceAtNat rest p' val

private def phiStep (i : Nat) : Nat × Int :=
  if i == 0 then (1, 1)
  else if i == 1 then (0, -1)
  else if i == 2 then (3, 1)
  else if i == 3 then (2, -1)
  else if i == 4 then (5, -1)
  else if i == 5 then (4, 1)
  else if i == 6 then (7, -1)
  else (6, 1)

private def applyKPhi (f : ExtSparse) : ExtSparse :=
  f.foldl (fun acc (tup, c) =>
    (rangeList 0 tup.length).foldl (fun acc2 pos =>
      let i := (tup.drop pos).headD 0
      let (j, v) := phiStep i
      match exSortNat (wfReplaceAtNat tup pos j) with
      | none => acc2
      | some (sk, sg) => exInsert sk (c * v * sg) acc2) acc) []

private def j43NonZeroRow (i : Nat) : List (Nat × Int) :=
  let row := (matJ43.drop i).headD []
  (rangeList 0 8).foldl (fun acc j =>
    let v := (row.drop j).headD 0
    if intEq v 0 then acc else acc ++ [(j, v)]) []

private def j43SparseRows : List (List (Nat × Int)) :=
  (rangeList 0 8).map j43NonZeroRow

private def applyD43 (f : ExtSparse) : ExtSparse :=
  f.foldl (fun acc (tup, c) =>
    (rangeList 0 tup.length).foldl (fun acc2 pos =>
      let i := (tup.drop pos).headD 0
      let nzRow := (j43SparseRows.drop i).headD []
      nzRow.foldl (fun acc3 (j, v) =>
        match exSortNat (wfReplaceAtNat tup pos j) with
        | none => acc3
        | some (sk, sg) => exInsert sk (c * v * sg) acc3) acc2) acc) []

private def applyP192 (f : ExtSparse) : ExtSparse :=
  let k1 := applyKPhi f
  let k2 := applyKPhi k1
  let mid := exAdd k2 (exScale 4 f)
  applyKPhi (applyKPhi mid)

private def allBasisTuples4 : List (List Nat) :=
  (rangeList 0 8).foldl (fun a0 i0 =>
    (rangeList (i0 + 1) (8 - i0 - 1)).foldl (fun a1 i1 =>
      (rangeList (i1 + 1) (8 - i1 - 1)).foldl (fun a2 i2 =>
        (rangeList (i2 + 1) (8 - i2 - 1)).foldl (fun a3 i3 =>
          a3 ++ [[i0, i1, i2, i3]]) a2) a1) a0) []

private def checkWeil70Operators : Bool :=
  let tuples := allBasisTuples4
  let dp02 : ExtSparse := (ei4NsBasis16.drop 5).headD []
  let namedOk :=
    exEq (applyKPhi ei4WeilReForm) (exScale 4 ei4WeilImForm) &&
    exEq (applyKPhi ei4WeilImForm) (exScale (-4) ei4WeilReForm) &&
    exEq (applyP192 ei4WeilReForm) (exScale 192 ei4WeilReForm) &&
    exEq (applyP192 ei4WeilImForm) (exScale 192 ei4WeilImForm) &&
    (applyP192 ei4ThetaSqForm).isEmpty &&
    (applyD43 ei4WeilReForm).isEmpty &&
    (applyD43 ei4WeilImForm).isEmpty &&
    (applyD43 ei4ThetaSqForm).isEmpty &&
    (applyD43 ei4ThetaForm).isEmpty &&
    !(applyD43 dp02).isEmpty
  let loopOk := tuples.all fun tup =>
    let eT : ExtSparse := [(tup, 1)]
    let pe := applyP192 eT
    let idem := exEq (applyP192 pe) (exScale 192 pe)
    let kills := (applyD43 pe).isEmpty
    let comm := exEq (applyD43 (applyKPhi eT)) (applyKPhi (applyD43 eT))
    idem && kills && comm
  let trace192 := tuples.foldl (fun acc tup =>
    acc + exLookup tup (applyP192 [(tup, 1)])) 0
  tuples.length == 70 && namedOk && loopOk && intEq trace192 384

set_option maxHeartbeats 16000000 in
set_option maxRecDepth 8192 in
/-- Exhaustive `70 x 70` certification of `D_43^(4)`, `K_Phi^(4)`, and algebraic Weil
projector `P_192 = K_Phi^2 (K_Phi^2 + 4 I)` across all `70` basis 4-tuples of `/\^4 Z^8`:
`P_192^2 = 192 P_192`, `tr(P_192) = 384`, `D_43 P_192 = 0`, `[D_43, K_Phi] = 0`,
`K_Phi(w_Re) = 4 w_Im`, `K_Phi(w_Im) = -4 w_Re`, and `P_192(Theta^2) = 0`. -/
theorem weil_70dim_hodge_hamiltonian_and_projector_cert :
    checkWeil70Operators = true :=
  rfl

#print axioms cyclotomic_u6_unitary_wavefunction_matrix_cert
#print axioms picard_fuchs_5x5_companion_matrix_cert
#print axioms weil_u22_8x8_exact_complex_structure_matrix_cert
#print axioms weil_70dim_hodge_hamiltonian_and_projector_cert
