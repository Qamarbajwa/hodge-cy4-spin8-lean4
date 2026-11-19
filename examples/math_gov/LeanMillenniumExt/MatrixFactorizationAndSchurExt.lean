/-
Copyright (c) 2026 Qamar Munawer. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Qamar Munawer
-/
import WiebeSchejaStorch
import MumfordCMSpecializationExt

/-!
# Matrix Factorization Scaling and 50/50 Block Schur / Diagonal Coverage Audit

Certifies with zero axioms:
1. Exact Koszul matrix factorizations `A B = B A = F I_r` over `Z[x_0..x_5]` for `r = 4`
   sextic Band-1, symmetric quadric-triple, quadric 4-variable, and cubic-product 4-variable
   identities, together with `r = 8` deformed sextic and `r = 4` Newton-Aoki `m = 5` MFs.
2. Exact 50/50 block Schur-complement bias on `Spin(8)` Gram matrices (`G_D4`, `G_A13`, `G_A2`):
   unbiased diagonal `G_D4`, hidden-block singularity `det D = 0` on contiguous `G_A13`/`G_A2`,
   and interleaved fake invertibility (`det A = 2` -> `det S = 0`) exposed by `B D^{-1} C`.
3. Exact integer dual annihilators proving non-coverage across pure-diagonal (`rho = 4`) and
   50%-coupled (`diag + D^+`, `diag + D^-`) slices of `NS(E_i^4)` vs minimal `rho = 8` closure.
-/

-- ---------------------------------------------------------------------------
-- Part 1: Sparse Z[x_0..x_5] Matrix Factorization Engine
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

private def isCanonGo (prev : Monom6) : Poly6 → Bool
  | [] => true
  | (m, c) :: rest =>
    (m.length == 6) && !(intEq c 0) && monLt6 prev m && isCanonGo m rest

private def isCanon6 : Poly6 → Bool
  | [] => true
  | (m, c) :: rest => (m.length == 6) && !(intEq c 0) && isCanonGo m rest

private def polyMergeGo : Nat → Poly6 → Poly6 → Poly6
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
          if intEq s 0 then polyMergeGo fuel r1 r2
          else (m1, s) :: polyMergeGo fuel r1 r2
        else if monLt6 m1 m2 then
          (m1, c1) :: polyMergeGo fuel r1 q
        else
          (m2, c2) :: polyMergeGo fuel p r2

private def fastPolyAdd6 (p q : Poly6) : Poly6 :=
  if p.isEmpty then q
  else if q.isEmpty then p
  else polyMergeGo (p.length + q.length + 1) p q

private def fastPolySub6 (p q : Poly6) : Poly6 :=
  fastPolyAdd6 p (polyNeg6 q)

private def polyScale6 (c : Int) (p : Poly6) : Poly6 :=
  if intEq c 0 then [] else p.map fun (m, v) => (m, c * v)

private def polyScaleTerm6 (m1 : Monom6) (c1 : Int) (q : Poly6) : Poly6 :=
  if intEq c1 0 then [] else q.map fun (m2, c2) => (monomMul6 m1 m2, c1 * c2)

private def polyMergePairwise : List Poly6 → List Poly6
  | [] => []
  | p :: rest =>
    match rest with
    | [] => [p]
    | q :: tail => fastPolyAdd6 p q :: polyMergePairwise tail

private def polyMergeAllGo : Nat → List Poly6 → Poly6
  | 0, ps =>
    match ps with
    | [] => []
    | p :: _ => p
  | fuel + 1, ps =>
    match ps with
    | [] => []
    | p :: rest =>
      match rest with
      | [] => p
      | _ :: _ => polyMergeAllGo fuel (polyMergePairwise ps)

private def fastPolyMul6 (p q : Poly6) : Poly6 :=
  if p.isEmpty || q.isEmpty then []
  else
    let (small, big) := if Nat.ble p.length q.length then (p, q) else (q, p)
    let rows := small.map fun (m1, c1) => polyScaleTerm6 m1 c1 big
    polyMergeAllGo (rows.length + 1) rows

private def pAddList (ps : List Poly6) : Poly6 :=
  polyMergeAllGo (ps.length + 1) ps

private def polyMatNeg (m : List (List Poly6)) : List (List Poly6) :=
  m.map (fun row => row.map polyNeg6)

private def getPolyRow (m : List (List Poly6)) (i : Nat) : List Poly6 :=
  (m.drop i).headD []

private def getPolyAt (row : List Poly6) (j : Nat) : Poly6 :=
  (row.drop j).headD []

private def diagBlock (n : Nat) (p : Poly6) : List (List Poly6) :=
  (rangeList 0 n).map fun i =>
    (rangeList 0 n).map fun j => if i == j then p else []

private def polyMatHStack (left right : List (List Poly6)) : List (List Poly6) :=
  List.zipWith (· ++ ·) left right

private def koszulStep (ab : List (List Poly6) × List (List Poly6)) (uv : Poly6 × Poly6) :
    List (List Poly6) × List (List Poly6) :=
  let (a, b) := ab
  let (u, v) := uv
  let n := a.length
  let uBlk := diagBlock n u
  let vBlk := diagBlock n v
  let a' := polyMatHStack a uBlk ++ polyMatHStack vBlk (polyMatNeg b)
  let b' := polyMatHStack b uBlk ++ polyMatHStack vBlk (polyMatNeg a)
  (a', b')

private def koszulMF : List (Poly6 × Poly6) → List (List Poly6) × List (List Poly6)
  | [] => ([], [])
  | (u0, v0) :: rest => rest.foldl koszulStep ([[u0]], [[v0]])

private def polyMatMul (a b : List (List Poly6)) : List (List Poly6) :=
  let cols := (getPolyRow b 0).length
  let bCols := (rangeList 0 cols).map fun j => b.map fun r => getPolyAt r j
  a.map fun row =>
    bCols.map fun col =>
      (List.zipWith fastPolyMul6 row col).foldl fastPolyAdd6 []

private def polyRowEq6 (v1 v2 : List Poly6) : Bool :=
  match v1 with
  | [] => match v2 with | [] => true | _ :: _ => false
  | p :: ps =>
    match v2 with
    | [] => false
    | q :: qs => polyEq6 p q && polyRowEq6 ps qs

private def polyMatEq (m1 m2 : List (List Poly6)) : Bool :=
  match m1 with
  | [] => match m2 with | [] => true | _ :: _ => false
  | r1 :: rs1 =>
    match m2 with
    | [] => false
    | r2 :: rs2 => polyRowEq6 r1 r2 && polyMatEq rs1 rs2

private def verifyKoszulMF (pairs : List (Poly6 × Poly6)) (f : Poly6) : Bool :=
  let canonOk := pairs.all (fun (u, v) => isCanon6 u && isCanon6 v) && isCanon6 f
  let (a, b) := koszulMF pairs
  let t := diagBlock a.length f
  canonOk && polyMatEq (polyMatMul a b) t && polyMatEq (polyMatMul b a) t

private def pPairUV (i j : Nat) : Poly6 × Poly6 :=
  let u := fastPolySub6 (varPow6 i 1) (varPow6 j 1)
  let v := pAddList ((rangeList 0 6).map fun a =>
    fastPolyMul6 (varPow6 i (5 - a)) (varPow6 j a))
  (u, v)

private def fSexticB1 : Poly6 :=
  pAddList
    [varPow6 0 6, polyNeg6 (varPow6 1 6), varPow6 2 6,
     polyNeg6 (varPow6 3 6), varPow6 4 6, polyNeg6 (varPow6 5 6)]

private def fSexticTri : Poly6 :=
  pAddList
    [varPow6 0 6, varPow6 1 6, varPow6 2 6,
     polyNeg6 (varPow6 3 6), polyNeg6 (varPow6 4 6), polyNeg6 (varPow6 5 6)]

private def fSexticB3 : Poly6 :=
  pAddList
    [varPow6 0 6, polyNeg6 (varPow6 1 6), varPow6 2 6,
     varPow6 3 6, polyNeg6 (varPow6 4 6), polyNeg6 (varPow6 5 6)]

private def pairsSexticB1 : List (Poly6 × Poly6) :=
  [pPairUV 0 1, pPairUV 2 3, pPairUV 4 5]

private def pairsSexticQuadTri : List (Poly6 × Poly6) :=
  let x02 := varPow6 0 2
  let x12 := varPow6 1 2
  let x22 := varPow6 2 2
  let x32 := varPow6 3 2
  let x42 := varPow6 4 2
  let x52 := varPow6 5 2
  let s012 := pAddList [x02, x12, x22]
  let q012 := fastPolySub6
    (pAddList [varPow6 0 4, varPow6 1 4, varPow6 2 4])
    (pAddList [fastPolyMul6 x02 x12, fastPolyMul6 x12 x22, fastPolyMul6 x22 x02])
  let s345 := pAddList [x32, x42, x52]
  let q345 := fastPolySub6
    (pAddList [varPow6 3 4, varPow6 4 4, varPow6 5 4])
    (pAddList [fastPolyMul6 x32 x42, fastPolyMul6 x42 x52, fastPolyMul6 x52 x32])
  let p012 := fastPolyMul6 (fastPolyMul6 (varPow6 0 1) (varPow6 1 1)) (varPow6 2 1)
  let p345 := fastPolyMul6 (fastPolyMul6 (varPow6 3 1) (varPow6 4 1)) (varPow6 5 1)
  [(s012, q012), (polyNeg6 s345, q345),
   (polyScale6 3 (fastPolySub6 p012 p345), fastPolyAdd6 p012 p345)]

private def pairsSexticQuadB3 : List (Poly6 × Poly6) :=
  let s23 := fastPolyAdd6 (varPow6 2 2) (varPow6 3 2)
  let s45 := fastPolyAdd6 (varPow6 4 2) (varPow6 5 2)
  let m23 := fastPolyMul6 (varPow6 2 2) (varPow6 3 2)
  let m45 := fastPolyMul6 (varPow6 4 2) (varPow6 5 2)
  let u2 := fastPolySub6 s23 s45
  let v2 := fastPolySub6
    (pAddList [fastPolyMul6 s23 s23, fastPolyMul6 s23 s45, fastPolyMul6 s45 s45])
    (polyScale6 3 m23)
  [pPairUV 0 1, (u2, v2), (polyScale6 (-3) s45, fastPolySub6 m23 m45)]

private def pairsSexticCubicB3 : List (Poly6 × Poly6) :=
  let x23 := fastPolyMul6 (varPow6 2 1) (varPow6 3 1)
  let x45 := fastPolyMul6 (varPow6 4 1) (varPow6 5 1)
  let sum23 := fastPolyAdd6 (varPow6 2 3) (varPow6 3 3)
  let sum45 := fastPolyAdd6 (varPow6 4 3) (varPow6 5 3)
  let u2 := fastPolySub6 sum23 sum45
  let v2 := fastPolyAdd6 sum23 sum45
  let u3 := polyScale6 2 (fastPolySub6 x45 x23)
  let v3 := pAddList [fastPolyMul6 x23 x23, fastPolyMul6 x23 x45, fastPolyMul6 x45 x45]
  [pPairUV 0 1, (u2, v2), (u3, v3)]

set_option maxHeartbeats 8000000 in
set_option maxRecDepth 8192 in
/-- Exact `4 x 4` over-Z Koszul matrix factorizations `A B = B A = F I_4` for sextic
Band-1 pairwise, symmetric quadric-triple, quadric 4-variable, and cubic 4-variable MFs. -/
theorem koszul_mf_sextic_band1_quadric_cubic_z_cert :
    verifyKoszulMF pairsSexticB1 fSexticB1 = true ∧
    verifyKoszulMF pairsSexticQuadTri fSexticTri = true ∧
    verifyKoszulMF pairsSexticQuadB3 fSexticB3 = true ∧
    verifyKoszulMF pairsSexticCubicB3 fSexticB3 = true :=
  ⟨rfl, rfl, rfl, rfl⟩

private def pairsDeformed8 : List (Poly6 × Poly6) :=
  let u4 := fastPolyMul6 (fastPolyMul6 (varPow6 0 1) (varPow6 2 1)) (varPow6 4 1)
  let v4 := fastPolyMul6 (fastPolyMul6 (varPow6 1 1) (varPow6 3 1)) (varPow6 5 1)
  pairsSexticB1 ++ [(u4, v4)]

private def fSexticDeformed : Poly6 :=
  fastPolyAdd6 fSexticB1 [([1, 1, 1, 1, 1, 1], 1)]

private def pairsAokiM5 : List (Poly6 × Poly6) :=
  let xs := (rangeList 0 5).map (fun i => varPow6 i 1)
  let e1 := pAddList xs
  let e2 := pAddList ((rangeList 0 5).foldl (fun acc i =>
    (rangeList 0 5).foldl (fun a2 j =>
      if Nat.blt i j then a2 ++ [fastPolyMul6 (varPow6 i 1) (varPow6 j 1)] else a2) acc) [])
  let e3 := pAddList ((rangeList 0 5).foldl (fun acc i =>
    (rangeList 0 5).foldl (fun a2 j =>
      if Nat.blt i j then
        (rangeList 0 5).foldl (fun a3 k =>
          if Nat.blt j k then
            a3 ++ [fastPolyMul6 (fastPolyMul6 (varPow6 i 1) (varPow6 j 1)) (varPow6 k 1)]
          else a3) a2
      else a2) acc) [])
  let e4 := pAddList
    [fastPolyMul6 (fastPolyMul6 (varPow6 1 1) (varPow6 2 1))
                  (fastPolyMul6 (varPow6 3 1) (varPow6 4 1)),
     fastPolyMul6 (fastPolyMul6 (varPow6 0 1) (varPow6 2 1))
                  (fastPolyMul6 (varPow6 3 1) (varPow6 4 1)),
     fastPolyMul6 (fastPolyMul6 (varPow6 0 1) (varPow6 1 1))
                  (fastPolyMul6 (varPow6 3 1) (varPow6 4 1)),
     fastPolyMul6 (fastPolyMul6 (varPow6 0 1) (varPow6 1 1))
                  (fastPolyMul6 (varPow6 2 1) (varPow6 4 1)),
     fastPolyMul6 (fastPolyMul6 (varPow6 0 1) (varPow6 1 1))
                  (fastPolyMul6 (varPow6 2 1) (varPow6 3 1))]
  let e1Sq := fastPolyMul6 e1 e1
  let q4 := pAddList
    [fastPolyMul6 e1Sq e1Sq, polyScale6 (-5) (fastPolyMul6 e1Sq e2),
     polyScale6 5 (fastPolyMul6 e1 e3), polyScale6 5 (fastPolyMul6 e2 e2), polyScale6 (-5) e4]
  [(e1, q4), (polyScale6 (-5) e2, e3), (varPow6 5 1, varPow6 5 4)]

private def fAokiM5 : Poly6 :=
  fastPolySub6 (pAddList ((rangeList 0 6).map fun i => varPow6 i 5)) [([1, 1, 1, 1, 1, 0], 5)]

set_option maxHeartbeats 12000000 in
set_option maxRecDepth 8192 in
/-- Exact `8 x 8` deformed sextic (`F_b1 + x_0..x_5`) and `4 x 4` Newton-Aoki `m = 5`
(`F_aoki(5)`) over-Z Koszul matrix factorization identities. -/
theorem koszul_mf_r8_deformed_and_m5_aoki_cert :
    (koszulMF pairsDeformed8).1.length = 8 ∧
    verifyKoszulMF pairsDeformed8 fSexticDeformed = true ∧
    (koszulMF pairsAokiM5).1.length = 4 ∧
    verifyKoszulMF pairsAokiM5 fAokiM5 = true :=
  ⟨rfl, rfl, rfl, rfl⟩

-- ---------------------------------------------------------------------------
-- Part 2: 50/50 Block Schur-Complement Bias on Spin(8) Gram Matrices
-- ---------------------------------------------------------------------------

private def getIntMatAt (m : List (List Int)) (r c : Nat) : Int :=
  ((m.drop r).headD []).drop c |>.headD 0

private def subMat3 (m : List (List Int)) (rs cs : List Nat) : List (List Int) :=
  rs.map fun r => cs.map fun c => getIntMatAt m r c

private def intMatMul3 (a b : List (List Int)) : List (List Int) :=
  [0, 1, 2].map fun i =>
    [0, 1, 2].map fun j =>
      getIntMatAt a i 0 * getIntMatAt b 0 j +
      getIntMatAt a i 1 * getIntMatAt b 1 j +
      getIntMatAt a i 2 * getIntMatAt b 2 j

private def intMatSub3 (a b : List (List Int)) : List (List Int) :=
  [0, 1, 2].map fun i =>
    [0, 1, 2].map fun j => getIntMatAt a i j - getIntMatAt b i j

private def intMatScale3 (k : Int) (m : List (List Int)) : List (List Int) :=
  [0, 1, 2].map fun i => [0, 1, 2].map fun j => k * getIntMatAt m i j

private def intMatEq3 (a b : List (List Int)) : Bool :=
  [0, 1, 2].all fun i => [0, 1, 2].all fun j => intEq (getIntMatAt a i j) (getIntMatAt b i j)

private def intDet3 (m : List (List Int)) : Int :=
  let a00 := getIntMatAt m 0 0
  let a01 := getIntMatAt m 0 1
  let a02 := getIntMatAt m 0 2
  let a10 := getIntMatAt m 1 0
  let a11 := getIntMatAt m 1 1
  let a12 := getIntMatAt m 1 2
  let a20 := getIntMatAt m 2 0
  let a21 := getIntMatAt m 2 1
  let a22 := getIntMatAt m 2 2
  a00 * (a11 * a22 - a12 * a21) -
  a01 * (a10 * a22 - a12 * a20) +
  a02 * (a10 * a21 - a11 * a20)

private def intAdj3 (m : List (List Int)) : List (List Int) :=
  let a00 := getIntMatAt m 0 0
  let a01 := getIntMatAt m 0 1
  let a02 := getIntMatAt m 0 2
  let a10 := getIntMatAt m 1 0
  let a11 := getIntMatAt m 1 1
  let a12 := getIntMatAt m 1 2
  let a20 := getIntMatAt m 2 0
  let a21 := getIntMatAt m 2 1
  let a22 := getIntMatAt m 2 2
  [[a11 * a22 - a12 * a21, -(a01 * a22 - a02 * a21), a01 * a12 - a02 * a11],
   [-(a10 * a22 - a12 * a20), a00 * a22 - a02 * a20, -(a00 * a12 - a02 * a10)],
   [a10 * a21 - a11 * a20, -(a00 * a21 - a01 * a20), a00 * a11 - a01 * a10]]

private def gSpinAlpha1 : Weight := addW4 (basisVec4 0 2) (basisVec4 1 (-2))
private def gSpinAlpha2 : Weight := addW4 (basisVec4 1 2) (basisVec4 2 (-2))
private def gSpinAlpha3 : Weight := addW4 (basisVec4 2 2) (basisVec4 3 (-2))
private def gSpinAlpha4 : Weight := addW4 (basisVec4 2 2) (basisVec4 3 2)

private def checkSpin8Schur5050 : Bool :=
  let gD4 := rootSubsystemGram6 d4AllRoots
  let gA13 := rootSubsystemGram6 [gSpinAlpha1, gSpinAlpha3, gSpinAlpha4]
  let gA2 := rootSubsystemGram6 [gSpinAlpha1, gSpinAlpha2]
  let obsC := [0, 1, 2]
  let hidC := [3, 4, 5]
  let obsI := [0, 2, 4]
  let hidI := [1, 3, 5]
  let d4Ok := [obsC, obsI].all fun obs =>
    let hid := if (obs.drop 1).headD 0 == 1 then hidC else hidI
    let a := subMat3 gD4 obs obs
    let b := subMat3 gD4 obs hid
    let c := subMat3 gD4 hid obs
    let d := subMat3 gD4 hid hid
    let detD := intDet3 d
    let scaledS := intMatSub3 (intMatScale3 detD a) (intMatMul3 b (intMatMul3 (intAdj3 d) c))
    intEq (intDet3 a) 4096 && intEq detD 4096 &&
    intMatEq3 b [[0, 0, 0], [0, 0, 0], [0, 0, 0]] &&
    intMatEq3 scaledS (intMatScale3 detD a)
  let aA2I := subMat3 gA2 obsI obsI
  let bA2I := subMat3 gA2 obsI hidI
  let cA2I := subMat3 gA2 hidI obsI
  let dA2I := subMat3 gA2 hidI hidI
  let detDA2I := intDet3 dA2I
  let biasScaledA2I := intMatMul3 bA2I (intMatMul3 (intAdj3 dA2I) cA2I)
  let schurScaledA2I := intMatSub3 (intMatScale3 detDA2I aA2I) biasScaledA2I
  let a2InterleavedOk :=
    intEq (intDet3 aA2I) 2 && intEq detDA2I 2 &&
    intMatEq3 biasScaledA2I [[1, -1, 0], [-1, 1, 0], [0, 0, 4]] &&
    intMatEq3 schurScaledA2I [[1, 1, 0], [1, 1, 0], [0, 0, 0]] &&
    intEq (intDet3 schurScaledA2I) 0
  let singOk :=
    intEq (intDet3 (subMat3 gA13 hidC hidC)) 0 &&
    intEq (intDet3 (subMat3 gA2 hidC hidC)) 0
  d4Ok && a2InterleavedOk && singOk

set_option maxHeartbeats 4000000 in
set_option maxRecDepth 8192 in
/-- 50/50 block Schur-complement bias audit on `Spin(8)`:
full `D_4` is block-unbiased (`B = 0`, `det A = det D = 4096`), `A_1^3` and contiguous `A_2`
suffer hidden-block singularity (`det D = 0`), while interleaved `A_2` (`{0,2,4}|{1,3,5}`)
exhibits false observed invertibility (`det A = 2`) corrected to `det S = 0` via `B D^{-1} C`. -/
theorem spin8_schur_5050_block_bias_cert :
    checkSpin8Schur5050 = true :=
  rfl

-- ---------------------------------------------------------------------------
-- Part 3: 6-Stage Diagonal & 50/50 Off-Diagonal Ladder on E_i^4
-- ---------------------------------------------------------------------------

private abbrev ExtSparse := List (List Nat × Int)

private def exListLt : List Nat → List Nat → Bool
  | [], [] => false
  | [], _ :: _ => true
  | _ :: _, [] => false
  | x :: xs, y :: ys => if x == y then exListLt xs ys else Nat.blt x y

private def exListEq : List Nat → List Nat → Bool
  | [], [] => true
  | [], _ :: _ => false
  | _ :: _, [] => false
  | x :: xs, y :: ys => (x == y) && exListEq xs ys

private def exInsertSortedNat (x : Nat) : List Nat → Option (List Nat × Int)
  | [] => some ([x], 1)
  | y :: ys =>
    if x == y then none
    else if Nat.blt x y then some (x :: y :: ys, 1)
    else
      match exInsertSortedNat x ys with
      | none => none
      | some (zs, s) => some (y :: zs, -s)

private def exMergeBasis : List Nat → List Nat → Option (List Nat × Int)
  | [], ys => some (ys, 1)
  | x :: xs, ys =>
    match exMergeBasis xs ys with
    | none => none
    | some (zs, s1) =>
      match exInsertSortedNat x zs with
      | none => none
      | some (ws, s2) => some (ws, s1 * s2)

private def exInsertTerm (k : List Nat) (c : Int) : ExtSparse → ExtSparse
  | [] => if intEq c 0 then [] else [(k, c)]
  | (k0, c0) :: rest =>
    if exListEq k k0 then
      let nc := c + c0
      if intEq nc 0 then rest else (k0, nc) :: rest
    else if exListLt k k0 then
      if intEq c 0 then (k0, c0) :: rest else (k, c) :: (k0, c0) :: rest
    else
      (k0, c0) :: exInsertTerm k c rest

private def exWedge (a b : ExtSparse) : ExtSparse :=
  a.foldl (fun acc (k1, c1) =>
    b.foldl (fun acc2 (k2, c2) =>
      match exMergeBasis k1 k2 with
      | none => acc2
      | some (k, s) => exInsertTerm k (s * c1 * c2) acc2) acc) []

private def exAdd (a b : ExtSparse) : ExtSparse :=
  b.foldl (fun acc (k, c) => exInsertTerm k c acc) a

private def exSub (a b : ExtSparse) : ExtSparse :=
  exAdd a (b.map fun (k, c) => (k, -c))

private def exFormEq : ExtSparse → ExtSparse → Bool
  | [], [] => true
  | [], _ :: _ => false
  | _ :: _, [] => false
  | (k1, c1) :: r1, (k2, c2) :: r2 =>
    exListEq k1 k2 && intEq c1 c2 && exFormEq r1 r2

private def exLookup (k : List Nat) : ExtSparse → Int
  | [] => 0
  | (k0, c0) :: rest => if exListEq k k0 then c0 else exLookup k rest

private def exDot (a b : ExtSparse) : Int :=
  a.foldl (fun acc (k, c) => acc + c * exLookup k b) 0

private def sym2WedgePairs (gens : List ExtSparse) : List ExtSparse :=
  let n := gens.length
  (rangeList 0 n).foldl (fun acc i =>
    let di := gens.drop i |>.headD []
    (rangeList i (n - i)).foldl (fun a2 j =>
      let dj := gens.drop j |>.headD []
      a2 ++ [exWedge di dj]) acc) []

private def checkEi4CoverageLadder : Bool :=
  let dualRe : ExtSparse := [([0, 2, 4, 6], 1)]
  let dualIm : ExtSparse := [([0, 2, 4, 7], 1)]
  let st1 := sym2WedgePairs (ei4NsBasis16.take 4)
  let st2 := sym2WedgePairs (ei4NsBasis16.take 10)
  let st3 := sym2WedgePairs (ei4NsBasis16.take 4 ++ ei4NsBasis16.drop 10)
  let dp02 := ei4NsBasis16.drop 5 |>.headD []
  let dp13 := ei4NsBasis16.drop 8 |>.headD []
  let dm02 := ei4NsBasis16.drop 11 |>.headD []
  let dm13 := ei4NsBasis16.drop 14 |>.headD []
  let reFromMin := exSub (exWedge dm02 dm13) (exWedge dp02 dp13)
  let imFromMin := exAdd (exWedge dp02 dm13) (exWedge dm02 dp13)
  intEq (exDot dualRe ei4WeilReForm) 1 &&
  intEq (exDot dualIm ei4WeilImForm) (-1) &&
  intEq (exDot dualRe ei4ThetaSqForm) 0 &&
  intEq (exDot dualIm ei4ThetaSqForm) 0 &&
  st1.length == 10 &&
  st1.all (fun w => intEq (exDot dualRe w) 0 && intEq (exDot dualIm w) 0) &&
  st2.length == 55 &&
  st2.all (fun w => intEq (exDot dualIm w) 0) &&
  st3.length == 55 &&
  st3.all (fun w => intEq (exDot dualRe w) 0 && intEq (exDot dualIm w) 0) &&
  exFormEq reFromMin ei4WeilReForm &&
  exFormEq imFromMin ei4WeilImForm

set_option maxHeartbeats 8000000 in
set_option maxRecDepth 8192 in
/-- Certifies integer dual-annihilator barriers across the 6-stage `E_i^4` coverage ladder:
neither `rho = 1` (`Theta^2`), `rho = 4` (`omega_a`), `rho = 10` (`diag + 50% D^+`), nor
`rho = 10` (`diag + 50% D^-`) spans both Weil classes, whereas adding minimal cross-sector
pairs `(D^+_{02}, D^+_{13}, D^-_{02}, D^-_{13})` realizes both `w_Re` and `w_Im`. -/
theorem ei4_diagonal_and_5050_offdiag_coverage_ladder_cert :
    checkEi4CoverageLadder = true :=
  rfl

#print axioms koszul_mf_sextic_band1_quadric_cubic_z_cert
#print axioms koszul_mf_r8_deformed_and_m5_aoki_cert
#print axioms spin8_schur_5050_block_bias_cert
#print axioms ei4_diagonal_and_5050_offdiag_coverage_ladder_cert
