/-
Copyright (c) 2026 Qamar Munawer. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Qamar Munawer
-/
import WiebeSchejaStorch
import MumfordCMSpecializationExt

/-!
# Experiment 8: Strict-Matrix Discrete Curvature, Weyl (n - 3) Threshold & Non-Fermat MF Pencil

Certifies with zero axioms:
1. Rational whitening vs. unimodular lattice rigidity & many-to-one invariant collapse:
   - Exact symmetric rational whitening matrix `P_W = W_int / 90` (`W_int = 273 I_8 - G_pos`)
     satisfying `W_int^T G_pos W_int = 218700 I_8` (`27 * 90^2 I_8`).
   - Strict unimodular obstruction over `Z^8`: `det(G_pos) = 27^8 != 1`, `det(W_int) = 90^8`,
     and `W_int / 90` fails integrality (`!(all entries divisible by 90)`).
   - Many-to-one spectral collapse: isospectral partner `(J_iso, G_iso)` shares identical
     `tr = 984`, `tr(G^2) = 236232`, `det = 27^8`, and `(G - 243 I)(G - 3 I) = 0`, yet `J_iso`
     preserves factor-torus divisors and `81 e_{0,4} + e_{1,5}` while `J_27` breaks them.
2. Exact `(n - 3)` Weyl threshold & strict 3D vs. 4D matrix curvature decomposition:
   - Universal integer identity `n^2 (n^2 - 1) - 6 n (n + 1) = n (n + 1) (n + 2) (n - 3)`.
   - In 3D (`Lambda^2 Z^3`), the `6 x 6` Ricci linear map has `det = -2 != 0` (`N_Weyl(3) = 0`).
   - In 4D (`Lambda^2 Z^4`), exact `6 x 6` orthogonal splitting `R = R_scal + R_Ric0 + W^+ + W^-`
     (`1 + 9 + 5 + 5 = 20`) obeying first Bianchi, `*_4 W^+ = W^+`, `*_4 W^- = -W^-`,
     zero Ricci on `W^\pm`, and pairwise Frobenius orthogonality.
3. Normal-coordinate 2nd-order curvature obstruction at `g(0) = I_8` on `SU(2, 2)`:
   - Explicit symmetric tangents `X_1, X_2 in p` satisfy `K = [X_1, X_2] != 0` in `k`,
     `R(X_1, X_2) X_1 = -[K, X_1] != 0`, `R(X_1, X_2) X_2 != 0`, and negative sectional curvature
     `tr(X_1^T R(X_1, X_2) X_2) = tr(K^2) = -48 < 0`.
4. Strict `8 x 8` octonionic Hurwitz-Radon matrix factorization pencil over `Z[x_0..x_5, t]`:
   - Verified `64` Clifford identities `Omega_j Omega_k^T + Omega_k Omega_j^T = 2 delta_{jk} I_8`.
   - Exact 1-parameter coupled non-Fermat CY4 pencil `(A_0 + t A_1)(B_0 + t B_1) = (F_0 + t F_1 +
     t^2 F_2) I_8` identically at `t^0, t^1, t^2` with `F_1 != 0 mod Jac(F_0)`.
-/

-- ---------------------------------------------------------------------------
-- Shared Exact Integer Matrix & Bareiss Determinant Helpers
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

private def intMatTrace (m : List (List Int)) : Int :=
  (rangeList 0 m.length).foldl (fun acc i => acc + intMatCell m i i) 0

private def intMatFrobDot (a b : List (List Int)) : Int :=
  intMatTrace (intMatMul a (intMatTranspose b))

private def bareissStep (m : List (List Int)) (prev : Int) (k n : Nat) :
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

private def bareissDet (m : List (List Int)) (n : Nat) : Int × Bool :=
  let init : List (List Int) × Int × Bool := (m, 1, true)
  let res := (rangeList 0 n).foldl (fun (curM, prev, ok) k =>
    if k + 1 == n then (curM, intMatCell curM k k, ok)
    else
      let (nm, piv, stepOk) := bareissStep curM prev k n
      (nm, piv, ok && stepOk)) init
  (res.2.1, res.2.2)

-- ---------------------------------------------------------------------------
-- Part 1: SU(2,2) Boost G_9, Rational Whitening P_W & Isospectral Rigidity
-- ---------------------------------------------------------------------------

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

private def matJ27 : List (List Int) :=
  let gInv := intMatMul matEta8 (intMatMul (intMatTranspose matG9) matEta8)
  let raw := intMatMul matG9 (intMatMul matE8 gInv)
  raw.map fun r => r.map fun x => x / 3

private def matJIso : List (List Int) :=
  (rangeList 0 8).map fun i =>
    (rangeList 0 8).map fun j =>
      if (i % 2 == 0) && (j == i + 1) then 3
      else if (j % 2 == 0) && (i == j + 1) then -243
      else 0

private def pairs28 : List (Nat × Nat) :=
  (rangeList 0 8).foldl (fun acc a =>
    (rangeList (a + 1) (8 - a - 1)).foldl (fun acc2 b => acc2 ++ [(a, b)]) acc) []

private def applyD2Form (jMat : List (List Int)) (form2 : List ((Nat × Nat) × Int)) :
    List ((Nat × Nat) × Int) :=
  pairs28.foldl (fun acc (r, s) =>
    let val := form2.foldl (fun tot ((a, b), coef) =>
      let t1 :=
        if b == s then intMatCell jMat a r
        else if b == r then -(intMatCell jMat a s)
        else 0
      let t2 :=
        if a == r then intMatCell jMat b s
        else if a == s then -(intMatCell jMat b r)
        else 0
      tot + coef * (t1 + t2)) 0
    if intEq val 0 then acc else acc ++ [((r, s), val)]) []

private def checkUnimodularWhitening : Bool :=
  let i8 := intEye 8
  let gPos := intMatMul (intMatScale (-1) matE8) matJ27
  let wInt := intMatSub (intMatScale 273 i8) gPos
  let wSym := intMatEq wInt (intMatTranspose wInt)
  let whitenEq := intMatEq (intMatMul (intMatTranspose wInt) (intMatMul gPos wInt))
    (intMatScale 218700 i8)
  let (detGPos, ok1) := bareissDet gPos 8
  let (detWInt, ok2) := bareissDet wInt 8
  let notIntP := !(wInt.all fun r => r.all fun x => intEq (x % 90) 0)
  let gIso := intMatMul (intMatScale (-1) matE8) matJIso
  let isoSq := intMatEq (intMatMul matJIso matJIso) (intMatScale (-729) i8)
  let isoRbr := intMatEq (intMatMul (intMatTranspose matJIso) (intMatMul matE8 matJIso))
    (intMatScale 729 matE8)
  let isoMinPoly := isIntMatZero (intMatMul (intMatSub gIso (intMatScale 243 i8))
    (intMatSub gIso (intMatScale 3 i8)))
  let (detGIso, ok3) := bareissDet gIso 8
  let sameInvs :=
    intEq (intMatTrace gPos) 984 && intEq (intMatTrace gIso) 984 &&
    intEq (intMatTrace (intMatMul gPos gPos)) (intMatTrace (intMatMul gIso gIso)) &&
    intEq detGPos 282429536481 && intEq detGIso 282429536481 &&
    intEq detWInt 4304672100000000
  let f01 : List ((Nat × Nat) × Int) := [((0, 1), 1)]
  let fScale : List ((Nat × Nat) × Int) := [((0, 4), 81), ((1, 5), 1)]
  let isoPres := (applyD2Form matJIso f01).isEmpty && (applyD2Form matJIso fScale).isEmpty
  let j27Breaks := !((applyD2Form matJ27 f01).isEmpty) &&
    !((applyD2Form matJ27 fScale).isEmpty)
  wSym && whitenEq && ok1 && ok2 && ok3 && notIntP && isoSq && isoRbr &&
  isoMinPoly && sameInvs && isoPres && j27Breaks

set_option maxHeartbeats 8000000 in
/-- Certifies rational whitening `W_int^T G_pos W_int = 27 * 90^2 I_8` (`W_int = 273 I_8 - G_pos`),
unimodular impossibility over `Z^8` (`det(G_pos) = 27^8`, `W_int / 90 notin M_8(Z)`), and
many-to-one invariant collapse against isospectral `(J_iso, G_iso)`. -/
theorem strict_matrix_unimodular_whitening_obstruction_cert :
    checkUnimodularWhitening = true :=
  rfl

-- ---------------------------------------------------------------------------
-- Part 2: Universal (n - 3) Weyl Threshold & 3D vs. 4D Matrix Curvature Split
-- ---------------------------------------------------------------------------

private def pairs4 : List (Nat × Nat) :=
  [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]

private def pairIdxGo (lo hi idx : Nat) : List (Nat × Nat) → Nat
  | [] => 0
  | (x, y) :: rest => if x == lo && y == hi then idx else pairIdxGo lo hi (idx + 1) rest

private def pairIdx (ps : List (Nat × Nat)) (a b : Nat) : Int × Nat :=
  let (sgn, lo, hi) := if a < b then ((1 : Int), a, b) else ((-1 : Int), b, a)
  (sgn, pairIdxGo lo hi 0 ps)

private def curvEval4 (r6 : List (List Int)) (a b c d : Nat) : Int :=
  if a == b || c == d then 0
  else
    let (s1, i) := pairIdx pairs4 a b
    let (s2, j) := pairIdx pairs4 c d
    s1 * s2 * intMatCell r6 i j

private def bianchi4 (r6 : List (List Int)) : Int :=
  curvEval4 r6 0 1 2 3 + curvEval4 r6 0 2 3 1 + curvEval4 r6 0 3 1 2

private def ricci4 (r6 : List (List Int)) : List (List Int) :=
  (rangeList 0 4).map fun a =>
    (rangeList 0 4).map fun b =>
      (rangeList 0 4).foldl (fun acc c => acc + curvEval4 r6 c a c b) 0

private def pairs3 : List (Nat × Nat) := [(0, 1), (0, 2), (1, 2)]

private def ricci3Map : List (List Int) :=
  let basis :=
    (rangeList 0 3).foldl (fun acc i =>
      (rangeList i (3 - i)).foldl (fun acc2 j =>
        let m := (rangeList 0 3).map fun r =>
          (rangeList 0 3).map fun c =>
            if (r == i && c == j) || (r == j && c == i) then 1 else 0
        acc2 ++ [m]) acc) []
  let cols := basis.map fun m =>
    let ric := (rangeList 0 3).map fun a =>
      (rangeList 0 3).map fun b =>
        (rangeList 0 3).foldl (fun acc c =>
          if c == a || c == b then acc
          else
            let (s1, i) := pairIdx pairs3 c a
            let (s2, j) := pairIdx pairs3 c b
            acc + s1 * s2 * intMatCell m i j) 0
    (rangeList 0 3).foldl (fun acc r =>
      (rangeList r (3 - r)).foldl (fun acc2 c => acc2 ++ [intMatCell ric r c]) acc) []
  intMatTranspose cols

private def star4Mat : List (List Int) :=
  [[0, 0, 0, 0, 0, 1],
   [0, 0, 0, 0, -1, 0],
   [0, 0, 0, 1, 0, 0],
   [0, 0, 1, 0, 0, 0],
   [0, -1, 0, 0, 0, 0],
   [1, 0, 0, 0, 0, 0]]

private def rScal4Mat : List (List Int) :=
  intMatScale 6 (intEye 6)

private def rRic0Mat : List (List Int) :=
  [[2, 0, 0, 0, 0, 0],
   [0, 2, 0, 1, 0, 0],
   [0, 0, 2, 0, 1, 0],
   [0, 1, 0, -2, 0, 0],
   [0, 0, 1, 0, -2, 0],
   [0, 0, 0, 0, 0, -2]]

private def wPlus4Mat : List (List Int) :=
  [[2, 1, 0, 0, -1, 2],
   [1, -1, 0, 0, 1, 1],
   [0, 0, -1, -1, 0, 0],
   [0, 0, -1, -1, 0, 0],
   [-1, 1, 0, 0, -1, -1],
   [2, 1, 0, 0, -1, 2]]

private def wMinus4Mat : List (List Int) :=
  [[1, 0, 2, -2, 0, -1],
   [0, -2, 0, 0, -2, 0],
   [2, 0, 1, -1, 0, -2],
   [-2, 0, -1, 1, 0, 2],
   [0, -2, 0, 0, -2, 0],
   [-1, 0, -2, 2, 0, 1]]

private def ricci3Adj : List (List Int) :=
  [[-1, 0, 0, -1, 0, 1],
   [0, 0, 0, 0, -2, 0],
   [0, 0, 2, 0, 0, 0],
   [-1, 0, 0, 1, 0, -1],
   [0, -2, 0, 0, 0, 0],
   [1, 0, 0, -1, 0, -1]]

private def checkWeylThresholdAndDecomp : Bool :=
  let countsOk :=
    (List.zipWith intEq
      (([3, 4, 5, 6] : List Int).map (fun n => n * (n + 1) * (n + 2) * (n - 3) / 12))
      [0, 10, 35, 84]).all id
  let neg2I6 := intMatScale (-2) (intEye 6)
  let dim3Rigidity :=
    intMatEq (intMatMul ricci3Map ricci3Adj) neg2I6 &&
    intMatEq (intMatMul ricci3Adj ricci3Map) neg2I6
  let starSq := intMatEq (intMatMul star4Mat star4Mat) (intEye 6)
  let rFull := intMatAdd (intMatAdd rScal4Mat rRic0Mat) (intMatAdd wPlus4Mat wMinus4Mat)
  let bianchiAll :=
    intEq (bianchi4 rScal4Mat) 0 && intEq (bianchi4 rRic0Mat) 0 &&
    intEq (bianchi4 wPlus4Mat) 0 && intEq (bianchi4 wMinus4Mat) 0 &&
    intEq (bianchi4 rFull) 0
  let ricZeroWeyl := isIntMatZero (ricci4 wPlus4Mat) && isIntMatZero (ricci4 wMinus4Mat)
  let ricTraceSplit :=
    intEq (intMatTrace (ricci4 rRic0Mat)) 0 && !(isIntMatZero (ricci4 rRic0Mat)) &&
    intMatEq (ricci4 rFull) (intMatAdd (ricci4 rScal4Mat) (ricci4 rRic0Mat))
  let sdAsdOk :=
    intMatEq (intMatMul star4Mat wPlus4Mat) wPlus4Mat &&
    intMatEq (intMatMul wPlus4Mat star4Mat) wPlus4Mat &&
    intMatEq (intMatMul star4Mat wMinus4Mat) (intMatScale (-1) wMinus4Mat) &&
    intMatEq (intMatMul wMinus4Mat star4Mat) (intMatScale (-1) wMinus4Mat)
  let orthOk :=
    intEq (intMatFrobDot rScal4Mat rRic0Mat) 0 &&
    intEq (intMatFrobDot rScal4Mat wPlus4Mat) 0 &&
    intEq (intMatFrobDot rScal4Mat wMinus4Mat) 0 &&
    intEq (intMatFrobDot rRic0Mat wPlus4Mat) 0 &&
    intEq (intMatFrobDot rRic0Mat wMinus4Mat) 0 &&
    intEq (intMatFrobDot wPlus4Mat wMinus4Mat) 0
  countsOk && dim3Rigidity && starSq && bianchiAll && ricZeroWeyl &&
  ricTraceSplit && sdAsdOk && orthOk

private theorem nAddAssoc (a b c : Nat) : (a + b) + c = a + (b + c) := by
  induction c with
  | zero => rfl
  | succ c ih => exact congrArg Nat.succ ih

private theorem nZeroMul (a : Nat) : 0 * a = 0 := by
  induction a with
  | zero => rfl
  | succ a ih => exact ih

private theorem nSuccMul (a b : Nat) : (a + 1) * b = a * b + b := by
  induction b with
  | zero => rfl
  | succ b ih =>
    change (a + 1) * b + (a + 1) = a * b + a + (b + 1)
    rw [ih, nAddAssoc, nAddAssoc]
    exact congrArg (fun x => a * b + x) (by
      rw [← nAddAssoc, ← nAddAssoc, Nat.add_comm a b])

private theorem nAddMul (a b c : Nat) : (a + b) * c = a * c + b * c := by
  induction c with
  | zero => rfl
  | succ c ih =>
    change (a + b) * c + (a + b) = (a * c + a) + (b * c + b)
    rw [ih, nAddAssoc, ← nAddAssoc (b * c) a b, Nat.add_comm (b * c) a,
      nAddAssoc a (b * c) b, ← nAddAssoc]

private theorem nMulComm (a b : Nat) : a * b = b * a := by
  induction b with
  | zero => exact (nZeroMul a).symm
  | succ b ih =>
    change a * b + a = (b + 1) * a
    rw [nSuccMul, ih]

private theorem nMulAssoc (a b c : Nat) : (a * b) * c = a * (b * c) := by
  induction c with
  | zero => rfl
  | succ c ih =>
    change (a * b) * c + a * b = a * (b * c + b)
    rw [ih, Nat.mul_add]

set_option maxHeartbeats 8000000 in
/-- Certifies the universal `(n - 3)` Weyl threshold identity for all integers `n = k + 3 >= 3`
(no subtraction gap: `N_Riemann = N_Ricci + N_Weyl`) together with strict `3D` Ricci bijection
(`det = -2`, `N_Weyl(3) = 0`) and exact `4D` orthogonal decomposition
`R = R_scal + R_Ric0 + W^+ + W^-` (`1 + 9 + 5 + 5 = 20`) on `Lambda^2 Z^4`. -/
theorem strict_matrix_weyl_threshold_and_decomp_cert (k : Nat) :
    ((k + 3) * (k + 3) * ((k + 3) * (k + 3) - 1) =
      6 * (k + 3) * (k + 4) + (k + 3) * (k + 4) * (k + 5) * k) ∧
    checkWeylThresholdAndDecomp = true := by
  have hSqSub : (k + 3) * (k + 3) - 1 = (k + 2) * (k + 4) := by
    have hL : (k + 3) * (k + 3) = (k * k + 6 * k + 8) + 1 := by
      have c3 : k * 3 + 3 * k = 6 * k := by
        rw [nMulComm 3 k, ← Nat.mul_add]
        exact nMulComm k 6
      calc
        (k + 3) * (k + 3) = (k * k + k * 3) + (3 * k + 9) := by
          rw [nAddMul, Nat.mul_add, Nat.mul_add]
        _ = (k * k + (k * 3 + 3 * k)) + 9 := by
          rw [← nAddAssoc, nAddAssoc (k * k) (k * 3) (3 * k)]
        _ = (k * k + 6 * k + 8) + 1 := by rw [c3]
    have hR : (k + 2) * (k + 4) = k * k + 6 * k + 8 := by
      have c24 : k * 4 + 2 * k = 6 * k := by
        rw [nMulComm 2 k, ← Nat.mul_add]
        exact nMulComm k 6
      calc
        (k + 2) * (k + 4) = (k * k + k * 4) + (2 * k + 8) := by
          rw [nAddMul, Nat.mul_add, Nat.mul_add]
        _ = (k * k + (k * 4 + 2 * k)) + 8 := by
          rw [← nAddAssoc, nAddAssoc (k * k) (k * 4) (2 * k)]
        _ = k * k + 6 * k + 8 := by rw [c24]
    rw [hL, hR]
    rfl
  have hMid : (k + 3) * (k + 2) = 6 + (k + 5) * k := by
    have c32 : k * 2 + 3 * k = 5 * k := by
      rw [nMulComm 3 k, ← Nat.mul_add]
      exact nMulComm k 5
    have lhs : (k + 3) * (k + 2) = k * k + 5 * k + 6 := by
      calc
        (k + 3) * (k + 2) = (k * k + k * 2) + (3 * k + 6) := by
          rw [nAddMul, Nat.mul_add, Nat.mul_add]
        _ = (k * k + (k * 2 + 3 * k)) + 6 := by
          rw [← nAddAssoc, nAddAssoc (k * k) (k * 2) (3 * k)]
        _ = k * k + 5 * k + 6 := by rw [c32]
    have rhs : 6 + (k + 5) * k = k * k + 5 * k + 6 := by
      rw [nAddMul, Nat.add_comm 6 (k * k + 5 * k)]
    rw [lhs, rhs]
  have hId : (k + 3) * (k + 3) * ((k + 3) * (k + 3) - 1) =
      6 * (k + 3) * (k + 4) + (k + 3) * (k + 4) * (k + 5) * k := by
    rw [hSqSub]
    have rearr1 : (k + 3) * (k + 3) * ((k + 2) * (k + 4)) =
        (k + 3) * (k + 4) * ((k + 3) * (k + 2)) := by
      rw [nMulAssoc (k + 3) (k + 3) ((k + 2) * (k + 4)),
        nMulAssoc (k + 3) (k + 4) ((k + 3) * (k + 2)),
        nMulComm (k + 2) (k + 4)]
      exact congrArg ((k + 3) * ·) (by
        rw [← nMulAssoc (k + 3) (k + 4) (k + 2), nMulComm (k + 3) (k + 4),
          nMulAssoc (k + 4) (k + 3) (k + 2)])
    have rearr2 : 6 * (k + 3) * (k + 4) + (k + 3) * (k + 4) * (k + 5) * k =
        (k + 3) * (k + 4) * (6 + (k + 5) * k) := by
      rw [nMulAssoc 6 (k + 3) (k + 4), nMulComm 6 ((k + 3) * (k + 4)),
        nMulAssoc ((k + 3) * (k + 4)) (k + 5) k, ← Nat.mul_add]
    rw [rearr1, rearr2, hMid]
  exact ⟨hId, rfl⟩

-- ---------------------------------------------------------------------------
-- Part 3: Normal-Coordinate 2nd-Order Curvature at g(0) = I_8 on SU(2, 2)
-- ---------------------------------------------------------------------------

private def matX1 : List (List Int) :=
  [[0, 0, 0, 0, 1, 0, 0, 0],
   [0, 0, 0, 0, 0, -1, 0, 0],
   [0, 0, 0, 0, 0, 0, 1, 0],
   [0, 0, 0, 0, 0, 0, 0, -1],
   [1, 0, 0, 0, 0, 0, 0, 0],
   [0, -1, 0, 0, 0, 0, 0, 0],
   [0, 0, 1, 0, 0, 0, 0, 0],
   [0, 0, 0, -1, 0, 0, 0, 0]]

private def matX2 : List (List Int) :=
  [[0, 0, 0, 0, 0, 1, 1, 0],
   [0, 0, 0, 0, 1, 0, 0, -1],
   [0, 0, 0, 0, -1, 0, 0, 0],
   [0, 0, 0, 0, 0, 1, 0, 0],
   [0, 1, -1, 0, 0, 0, 0, 0],
   [1, 0, 0, 1, 0, 0, 0, 0],
   [1, 0, 0, 0, 0, 0, 0, 0],
   [0, -1, 0, 0, 0, 0, 0, 0]]

private def checkSu22NormalCoordCurvature : Bool :=
  let tangOk := [matX1, matX2].all fun x =>
    isIntMatZero (intMatAdd (intMatMul matEta8 x) (intMatMul (intMatTranspose x) matEta8)) &&
    intMatEq (intMatMul x matPhi8) (intMatMul matPhi8 x) &&
    intMatEq x (intMatTranspose x)
  let matK := intMatSub (intMatMul matX1 matX2) (intMatMul matX2 matX1)
  let kOk :=
    !(isIntMatZero matK) &&
    intMatEq matK (intMatScale (-1) (intMatTranspose matK)) &&
    isIntMatZero (intMatAdd (intMatMul matEta8 matK) (intMatMul (intMatTranspose matK) matEta8)) &&
    intMatEq (intMatMul matK matPhi8) (intMatMul matPhi8 matK)
  let r121 := intMatSub (intMatMul matX1 matK) (intMatMul matK matX1)
  let r122 := intMatSub (intMatMul matX2 matK) (intMatMul matK matX2)
  let rNz := !(isIntMatZero r121) && !(isIntMatZero r122)
  let secNum := intMatFrobDot matX1 r122
  let kSqTr := intMatTrace (intMatMul matK matK)
  tangOk && kOk && rNz && intEq secNum (-48) && intEq kSqTr (-48)

set_option maxHeartbeats 4000000 in
/-- Certifies non-vanishing normal-coordinate Riemann curvature `R(X_1, X_2) X_1 = -[K, X_1] != 0`
at `g(0) = I_8` on `SU(2, 2)`, compact holonomy `K = [X_1, X_2] != 0`, and negative sectional
curvature `tr(X_1^T R(X_1, X_2) X_2) = tr(K^2) = -48`. -/
theorem strict_matrix_normal_coord_curvature_cert :
    checkSu22NormalCoordCurvature = true :=
  rfl

-- ---------------------------------------------------------------------------
-- Part 4: 8 x 8 Octonionic Hurwitz-Radon Non-Fermat MF Pencil over Z[x, t]
-- ---------------------------------------------------------------------------

private def monEq6 (l1 l2 : Monom6) : Bool :=
  match l1 with
  | [] => match l2 with | [] => true | _ :: _ => false
  | x :: xs => match l2 with | [] => false | y :: ys => (x == y) && monEq6 xs ys

private def monLt6 (l1 l2 : Monom6) : Bool :=
  match l1 with
  | [] => false
  | x :: xs =>
    match l2 with
    | [] => false
    | y :: ys => if x == y then monLt6 xs ys else Nat.blt x y

private def pMergeGo : Nat → Poly6 → Poly6 → Poly6
  | 0, p, _ => p
  | fuel + 1, p, q =>
    match p with
    | [] => q
    | (m1, c1) :: r1 =>
      match q with
      | [] => p
      | (m2, c2) :: r2 =>
        if monEq6 m1 m2 then
          let s := c1 + c2
          if intEq s 0 then pMergeGo fuel r1 r2
          else (m1, s) :: pMergeGo fuel r1 r2
        else if monLt6 m1 m2 then
          (m1, c1) :: pMergeGo fuel r1 q
        else
          (m2, c2) :: pMergeGo fuel p r2

private def fastPAdd (p q : Poly6) : Poly6 :=
  if p.isEmpty then q
  else if q.isEmpty then p
  else pMergeGo (p.length + q.length + 1) p q

private def pScale (c : Int) (p : Poly6) : Poly6 :=
  if intEq c 0 then [] else p.map fun (m, v) => (m, c * v)

private def pScaleTerm (m1 : Monom6) (c1 : Int) (q : Poly6) : Poly6 :=
  if intEq c1 0 then [] else q.map fun (m2, c2) => (monomMul6 m1 m2, c1 * c2)

private def pMergePairwise : List Poly6 → List Poly6
  | [] => []
  | p :: rest =>
    match rest with
    | [] => [p]
    | q :: tail => fastPAdd p q :: pMergePairwise tail

private def pMergeAllGo : Nat → List Poly6 → Poly6
  | 0, ps => match ps with | [] => [] | p :: _ => p
  | fuel + 1, ps =>
    match ps with
    | [] => []
    | p :: rest =>
      match rest with
      | [] => p
      | _ :: _ => pMergeAllGo fuel (pMergePairwise ps)

private def fastPMul (p q : Poly6) : Poly6 :=
  if p.isEmpty || q.isEmpty then []
  else
    let (small, big) := if Nat.ble p.length q.length then (p, q) else (q, p)
    let rows := small.map fun (m1, c1) => pScaleTerm m1 c1 big
    pMergeAllGo (rows.length + 1) rows

private def pAddList (ps : List Poly6) : Poly6 :=
  pMergeAllGo (ps.length + 1) ps

private def pRow (m : List (List Poly6)) (i : Nat) : List Poly6 :=
  (m.drop i).headD []

private def pAt (row : List Poly6) (j : Nat) : Poly6 :=
  (row.drop j).headD []

private def pMatMulFast (a b : List (List Poly6)) : List (List Poly6) :=
  let cols := (pRow b 0).length
  let bCols := (rangeList 0 cols).map fun j => b.map fun r => pAt r j
  a.map fun row =>
    bCols.map fun col =>
      pAddList (List.zipWith fastPMul row col)

private def pMatAdd (a b : List (List Poly6)) : List (List Poly6) :=
  List.zipWith (List.zipWith fastPAdd) a b

private def pDiag8 (p : Poly6) : List (List Poly6) :=
  (rangeList 0 8).map fun i => (rangeList 0 8).map fun j => if i == j then p else []

private def pMatEq (m1 m2 : List (List Poly6)) : Bool :=
  (m1.length == m2.length) &&
  (List.zipWith (fun r1 r2 => (r1.length == r2.length) &&
    (List.zipWith polyEq6 r1 r2).all id) m1 m2).all id

private def kron3 (a b c : List (List Int)) : List (List Int) :=
  let bc := (rangeList 0 4).map fun i =>
    (rangeList 0 4).map fun j => intMatCell b (i / 2) (j / 2) * intMatCell c (i % 2) (j % 2)
  (rangeList 0 8).map fun i =>
    (rangeList 0 8).map fun j => intMatCell a (i / 4) (j / 4) * intMatCell bc (i % 4) (j % 4)

private def octBasis8 : List (List (List Int)) :=
  let i2 : List (List Int) := [[1, 0], [0, 1]]
  let j2 : List (List Int) := [[0, -1], [1, 0]]
  let z2 : List (List Int) := [[1, 0], [0, -1]]
  let x2 : List (List Int) := [[0, 1], [1, 0]]
  [kron3 i2 i2 i2, kron3 j2 i2 i2, kron3 z2 j2 i2, kron3 x2 j2 z2,
   kron3 x2 j2 x2, kron3 z2 z2 j2, kron3 z2 x2 j2, kron3 x2 i2 j2]

private def pMatFromScale (p : Poly6) (m : List (List Int)) : List (List Poly6) :=
  m.map fun row => row.map fun c => pScale c p

private def monVarPow6 (k e : Nat) : Monom6 :=
  (rangeList 0 6).map fun i => if i == k then e else 0

private def cubicCoupledMon6 (k : Nat) : Monom6 :=
  let a := (k + 1) % 6
  let b := (k + 2) % 6
  let c := (k + 3) % 6
  (rangeList 0 6).map fun i => if i == a || i == b || i == c then 1 else 0

private def checkOctonionicNonFermatMFPencil : Bool :=
  let oms := octBasis8
  let i8 := intEye 8
  let twoI8 := intMatScale 2 i8
  let cliffordOk := (rangeList 0 8).all fun j =>
    (rangeList 0 8).all fun k =>
      let mj := (oms.drop j).headD []
      let mk := (oms.drop k).headD []
      let sumM := intMatAdd (intMatMul mj (intMatTranspose mk))
        (intMatMul mk (intMatTranspose mj))
      if j == k then intMatEq sumM twoI8 else isIntMatZero sumM
  let zeroMat := pDiag8 []
  let buildSum (useT : Bool) (trans : Bool) : List (List Poly6) :=
    (rangeList 0 6).foldl (fun acc k =>
      let mk0 := (oms.drop k).headD []
      let mk := if trans then intMatTranspose mk0 else mk0
      let pk : Poly6 := if useT then [(cubicCoupledMon6 k, 1)] else [(monVarPow6 k 3, 1)]
      pMatAdd acc (pMatFromScale pk mk)) zeroMat
  let a0 := buildSum false false
  let b0 := buildSum false true
  let a1 := buildSum true false
  let b1 := buildSum true true
  let f0 := pAddList ((rangeList 0 6).map fun k => [(monVarPow6 k 6, 1)])
  let f1 := pAddList ((rangeList 0 6).map fun k =>
    [(monomMul6 (monVarPow6 k 3) (cubicCoupledMon6 k), 2)])
  let f2 := pAddList ((rangeList 0 6).map fun k =>
    [(monomMul6 (cubicCoupledMon6 k) (cubicCoupledMon6 k), 1)])
  let mf0Ok := pMatEq (pMatMulFast a0 b0) (pDiag8 f0) && pMatEq (pMatMulFast b0 a0) (pDiag8 f0)
  let mf1L := pMatAdd (pMatMulFast a0 b1) (pMatMulFast a1 b0)
  let mf1R := pMatAdd (pMatMulFast b0 a1) (pMatMulFast b1 a0)
  let mf1Ok := pMatEq mf1L (pDiag8 f1) && pMatEq mf1R (pDiag8 f1)
  let mf2Ok := pMatEq (pMatMulFast a1 b1) (pDiag8 f2) && pMatEq (pMatMulFast b1 a1) (pDiag8 f2)
  let jacNonzero := (f1.length == 6) && f1.all fun (m, _) => m.all fun e => Nat.blt e 5
  cliffordOk && mf0Ok && mf1Ok && mf2Ok && jacNonzero

set_option maxHeartbeats 8000000 in
/-- Certifies the `64` Clifford identities for the `8` octonion units `Omega_0..Omega_7` and the
exact `8 x 8` non-Fermat CY4 matrix factorization pencil `(A_0 + t A_1)(B_0 + t B_1) =
(F_0 + t F_1 + t^2 F_2) I_8` over `Z[x_0..x_5, t]` with `F_1` nonzero in `R(F_0)_6`. -/
theorem strict_matrix_non_fermat_mf_ray_cert :
    checkOctonionicNonFermatMFPencil = true :=
  rfl

-- ---------------------------------------------------------------------------
-- Part 5: Observable-Half Conjugate Reconstruction Lift Across 8 Splits (70-Dim)
-- ---------------------------------------------------------------------------

private abbrev ExtForm6 := List (List Nat × Int)

private def smNatEq : List Nat → List Nat → Bool
  | [], [] => true
  | [], _ :: _ => false
  | _ :: _, [] => false
  | x :: xs, y :: ys => (x == y) && smNatEq xs ys

private def smNatLt : List Nat → List Nat → Bool
  | [], [] => false
  | [], _ :: _ => true
  | _ :: _, [] => false
  | x :: xs, y :: ys => if x == y then smNatLt xs ys else Nat.blt x y

private def smInsNat (x : Nat) : List Nat → Option (List Nat × Int)
  | [] => some ([x], 1)
  | y :: ys =>
    if x == y then none
    else if Nat.blt x y then some (x :: y :: ys, 1)
    else
      match smInsNat x ys with
      | none => none
      | some (zs, s) => some (y :: zs, -s)

private def smSortNat : List Nat → Option (List Nat × Int)
  | [] => some ([], 1)
  | x :: xs =>
    match smSortNat xs with
    | none => none
    | some (ys, s1) =>
      match smInsNat x ys with
      | none => none
      | some (zs, s2) => some (zs, s1 * s2)

private def smExInsert (k : List Nat) (c : Int) : ExtForm6 → ExtForm6
  | [] => if intEq c 0 then [] else [(k, c)]
  | (k0, c0) :: rest =>
    if smNatEq k k0 then
      let nc := c + c0
      if intEq nc 0 then rest else (k0, nc) :: rest
    else if smNatLt k k0 then
      if intEq c 0 then (k0, c0) :: rest else (k, c) :: (k0, c0) :: rest
    else
      (k0, c0) :: smExInsert k c rest

private def smExAdd (a b : ExtForm6) : ExtForm6 :=
  b.foldl (fun acc (k, c) => smExInsert k c acc) a

private def smExScale (s : Int) (a : ExtForm6) : ExtForm6 :=
  if intEq s 0 then [] else a.map fun (k, c) => (k, s * c)

private def smExLookup (k : List Nat) : ExtForm6 → Int
  | [] => 0
  | (k0, c0) :: rest => if smNatEq k k0 then c0 else smExLookup k rest

private def smExDot (a b : ExtForm6) : Int :=
  a.foldl (fun acc (k, c) => acc + c * smExLookup k b) 0

private def smExEq (a b : ExtForm6) : Bool :=
  (a.length == b.length) &&
  (List.zipWith (fun (k1, v1) (k2, v2) => smNatEq k1 k2 && intEq v1 v2) a b).all id

private def smReplaceAt (xs : List Nat) (pos val : Nat) : List Nat :=
  match xs with
  | [] => []
  | x :: rest =>
    match pos with
    | 0 => val :: rest
    | k + 1 => x :: smReplaceAt rest k val

private def allTuples4 : List (List Nat) :=
  (rangeList 0 8).foldl (fun a0 i0 =>
    (rangeList (i0 + 1) (8 - i0 - 1)).foldl (fun a1 i1 =>
      (rangeList (i1 + 1) (8 - i1 - 1)).foldl (fun a2 i2 =>
        (rangeList (i2 + 1) (8 - i2 - 1)).foldl (fun a3 i3 =>
          a3 ++ [[i0, i1, i2, i3]]) a2) a1) a0) []

private def smPhiStep (i : Nat) : Nat × Int :=
  if i == 0 then (1, -1)
  else if i == 1 then (0, 1)
  else if i == 2 then (3, -1)
  else if i == 3 then (2, 1)
  else if i == 4 then (5, 1)
  else if i == 5 then (4, -1)
  else if i == 6 then (7, 1)
  else (6, -1)

private def smApplyKPhi (f : ExtForm6) : ExtForm6 :=
  f.foldl (fun acc (tup, c) =>
    (rangeList 0 tup.length).foldl (fun acc2 pos =>
      let i := (tup.drop pos).headD 0
      let (j, v) := smPhiStep i
      match smSortNat (smReplaceAt tup pos j) with
      | none => acc2
      | some (sk, sg) => smExInsert sk (c * v * sg) acc2) acc) []

private def smApplyP192 (f : ExtForm6) : ExtForm6 :=
  let k2 := smApplyKPhi (smApplyKPhi f)
  let mid := smExAdd k2 (smExScale 4 f)
  smApplyKPhi (smApplyKPhi mid)

private def j43MatRows : List (List Int) :=
  [[0, 47, -6, -2, -10, -10, -10, 10],
   [-47, 0, 2, -6, -10, 10, 10, 10],
   [6, -2, 0, 53, 20, -10, -10, -20],
   [2, 6, -53, 0, -10, -20, -20, 10],
   [-10, -10, 20, -10, 0, 50, 7, 0],
   [-10, 10, -10, -20, -50, 0, 0, 7],
   [-10, 10, -10, -20, -7, 0, 0, 50],
   [10, 10, -20, 10, 0, -7, -50, 0]]

private def j43NzRows : List (List (Nat × Int)) :=
  (rangeList 0 8).map fun i =>
    let row := (j43MatRows.drop i).headD []
    (rangeList 0 8).foldl (fun acc j =>
      let v := (row.drop j).headD 0
      if intEq v 0 then acc else acc ++ [(j, v)]) []

private def smApplyD43 (f : ExtForm6) : ExtForm6 :=
  f.foldl (fun acc (tup, c) =>
    (rangeList 0 tup.length).foldl (fun acc2 pos =>
      let i := (tup.drop pos).headD 0
      let nzRow := (j43NzRows.drop i).headD []
      nzRow.foldl (fun acc3 (j, v) =>
        match smSortNat (smReplaceAt tup pos j) with
        | none => acc3
        | some (sk, sg) => smExInsert sk (c * v * sg) acc3) acc2) acc) []

private def checkObsHalfLift : Bool :=
  let tuples := allTuples4
  let wRe := ei4WeilReForm
  let wIm := ei4WeilImForm
  let coreOk :=
    (tuples.length == 70) &&
    (smApplyD43 wRe).isEmpty && (smApplyD43 wIm).isEmpty &&
    smExEq (smApplyP192 wRe) (smExScale 192 wRe) &&
    smExEq (smApplyP192 wIm) (smExScale 192 wIm)
  let basisSpanOk := tuples.all fun tup =>
    let eT : ExtForm6 := [(tup, 1)]
    let pe := smApplyP192 eT
    let cRe := smExLookup tup wRe
    let cIm := smExLookup tup wIm
    let expPe := smExScale 24 (smExAdd (smExScale cRe wRe) (smExScale cIm wIm))
    smExEq pe expPe
  let lift8Ok := (rangeList 0 8).all fun c =>
    let obsRe := wRe.filter fun (t, _) => t.contains c
    let hidRe := wRe.filter fun (t, _) => !(t.contains c)
    let obsIm := wIm.filter fun (t, _) => t.contains c
    let hidIm := wIm.filter fun (t, _) => !(t.contains c)
    let liftRe := smApplyP192 obsRe
    let liftIm := smApplyP192 obsIm
    let halfEnergy :=
      intEq (smExDot obsRe obsRe) 4 && intEq (smExDot hidRe hidRe) 4 &&
      intEq (smExDot obsIm obsIm) 4 && intEq (smExDot hidIm hidIm) 4
    let truncBreaks := !(smApplyD43 obsRe).isEmpty && !(smApplyD43 obsIm).isEmpty
    let liftRecovers :=
      smExEq liftRe (smExScale 96 wRe) &&
      smExEq liftIm (smExScale 96 wIm) &&
      (smApplyD43 liftRe).isEmpty && (smApplyD43 liftIm).isEmpty
    halfEnergy && truncBreaks && liftRecovers
  coreOk && basisSpanOk && lift8Ok

set_option maxHeartbeats 12000000 in
set_option maxRecDepth 8192 in
/-- Certifies the conjugate-half reconstruction lift across all `8` coordinate `35 + 35` splits
`c = 0..7`: although single-half truncation `obs_Re` breaks Hodge invariance (`D_43 != 0`) and
carries exact `50%` norm (`4` of `8`), `P_192(obs_Re) = 96 w_Re`, `P_192(obs_Im) = 96 w_Im`,
and every column of `L_c = P_192[:, I_in]` is in `ker D_43^(4)` with `P_192 L_c = 192 L_c`. -/
theorem strict_matrix_observable_half_reconstruction_lift_cert :
    checkObsHalfLift = true :=
  rfl

-- ---------------------------------------------------------------------------
-- Part 6: Unique 4D (n - 4) Exact 50/50 Ricci-Weyl Split Identity
-- ---------------------------------------------------------------------------

private theorem nMulOne (a : Nat) : a * 1 = a := by
  induction a with
  | zero => rfl
  | succ a ih => exact congrArg Nat.succ ih

private theorem nMulPosZero {a b : Nat} (ha : 0 < a) (hb : 0 < b) : 0 < a * b := by
  cases a with
  | zero => exact False.elim (Nat.not_lt_zero 0 ha)
  | succ a' =>
    cases b with
    | zero => exact False.elim (Nat.not_lt_zero 0 hb)
    | succ b' =>
      change 0 < (a' + 1) * b' + (a' + 1)
      exact Nat.zero_lt_succ ((a' + 1) * b' + a')

set_option maxHeartbeats 4000000 in
/-- Certifies the exact `(n - 4)` threshold forcing `n = 4` to be the unique dimension `n >= 3`
where `N_Weyl(n) = N_Ricci(n) = (1/2) N_Riemann(n)`: proves universally
`12 * N_Weyl(k+4) = 12 * N_Ricci(k+4) + (k+4)*(k+5)*(k+7)*k` with strictly positive excess
for every `n = m + 5 >= 5`, equality `10 = 10` at `n = 4`, and `0 < 6` at `n = 3`. -/
theorem strict_matrix_4d_unique_5050_curvature_split_cert (k m : Nat) :
    ((k + 4) * (k + 5) * (k + 6) * (k + 1) =
      6 * (k + 4) * (k + 5) + (k + 4) * (k + 5) * (k + 7) * k) ∧
    (0 < (m + 5) * (m + 6) * (m + 8) * (m + 1)) ∧
    ((3 * 4 * 5 * 0 / 12 < 3 * 4 / 2) &&
     (4 * 5 * 6 * 1 / 12 == 4 * 5 / 2) &&
     (4 * 5 * 6 * 1 / 12 + 4 * 5 / 2 == 4 * 4 * (4 * 4 - 1) / 12)) = true := by
  have c61 : k * 1 + 6 * k = 7 * k := by
    have h2 : 6 * k = k * 6 := nMulComm 6 k
    have h3 : k * (1 + 6) = 7 * k := nMulComm k 7
    rw [h2, ← Nat.mul_add, h3]
  have hQuad : (k + 6) * (k + 1) = 6 + (k + 7) * k := by
    have lhs : (k + 6) * (k + 1) = k * k + 7 * k + 6 := by
      calc
        (k + 6) * (k + 1) = (k * k + k * 1) + (6 * k + 6) := by
          rw [nAddMul, Nat.mul_add, Nat.mul_add]
        _ = (k * k + (k * 1 + 6 * k)) + 6 := by
          rw [← nAddAssoc, nAddAssoc (k * k) (k * 1) (6 * k)]
        _ = k * k + 7 * k + 6 := by rw [c61]
    have rhs : 6 + (k + 7) * k = k * k + 7 * k + 6 := by
      rw [nAddMul, Nat.add_comm 6 (k * k + 7 * k)]
    rw [lhs, rhs]
  have hMain : (k + 4) * (k + 5) * (k + 6) * (k + 1) =
      6 * (k + 4) * (k + 5) + (k + 4) * (k + 5) * (k + 7) * k := by
    have rL : (k + 4) * (k + 5) * (k + 6) * (k + 1) =
        (k + 4) * (k + 5) * ((k + 6) * (k + 1)) :=
      nMulAssoc ((k + 4) * (k + 5)) (k + 6) (k + 1)
    have rR : 6 * (k + 4) * (k + 5) + (k + 4) * (k + 5) * (k + 7) * k =
        (k + 4) * (k + 5) * (6 + (k + 7) * k) := by
      rw [nMulAssoc 6 (k + 4) (k + 5), nMulComm 6 ((k + 4) * (k + 5)),
        nMulAssoc ((k + 4) * (k + 5)) (k + 7) k, ← Nat.mul_add]
    rw [rL, rR, hQuad]
  have hPos : 0 < (m + 5) * (m + 6) * (m + 8) * (m + 1) :=
    nMulPosZero
      (nMulPosZero
        (nMulPosZero (Nat.zero_lt_succ (m + 4)) (Nat.zero_lt_succ (m + 5)))
        (Nat.zero_lt_succ (m + 7)))
      (Nat.zero_lt_succ m)
  exact ⟨hMain, hPos, rfl⟩

#print axioms strict_matrix_unimodular_whitening_obstruction_cert
#print axioms strict_matrix_weyl_threshold_and_decomp_cert
#print axioms strict_matrix_normal_coord_curvature_cert
#print axioms strict_matrix_non_fermat_mf_ray_cert
#print axioms strict_matrix_observable_half_reconstruction_lift_cert
#print axioms strict_matrix_4d_unique_5050_curvature_split_cert
