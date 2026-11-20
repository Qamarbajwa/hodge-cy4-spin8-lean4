/-
Copyright (c) 2026 Qamar Munawer. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Qamar Munawer
-/
import WiebeSchejaStorch

/-!
# Experiment 11 (Wall 3): Mumford H^4(A) Uniqueness & A^3 19-Dim Hodge (3,3) Collapse

Certifies with zero axioms:
1. `H^4(A) = /\^4(Z^8)` (`70`-dim) Mumford invariant uniqueness under `sl_2(R) (+) so(4)`:
   - All `9` Lie generators annihilate `Theta^2` in `/\^4(Z^8)`.
   - Dropping `Theta^2` coordinate `(0,1,4,5)`, the `69 x 69` action system `B_69` admits exact
     integer inverse `B_{69,inv} B_69 = B_69 B_{69,inv} = 12 I_69`, proving `dim H^4(A)^G = 1`.
2. Exact `21,952`-entry (`28^3`) small-diagonal-to-divisor identity on `A x A x A`:
   - `T_cup_up` and cyclic divisor cube `D_cyc = D_12 ^ D_23 ^ D_13` are totally `S_3`-symmetric
     and satisfy `8 T_cup_up = v_ttt + 2 (v_1dd + v_2dd + v_3dd) + 8 D_cyc` entrywise.
3. Exact `64`-sector probe, Casimir polynomial generation, and `5 -> {11, 12} -> 15 -> 19`
   closure diamond:
   - `24 Q_0 = T_th`, `32 Q_sd = T_ch^2 - 8 T_ch`, `32 Q_asd = T_ch^2 + 8 T_ch`,
     `16 Q_ric = 16 T_dd + 2 T_th - T_ch^2` reduce the entire `14D` non-divisor `(3,3)` obstruction
     on `A^3` onto the single chiral generator `T_ch` acting on `D_cyc`.
   - Slicing `D_cyc` along the `4` irrep probes hits all `19` allowed `(a, b, c)` triples (`45`
     strictly zero), and pairwise orthogonal `{0,1}` bases verify `5 -> 8 -> {11, 12} -> 15 -> 19`
     with all `7` parity-odd classes orthogonal to `12`-dim `A_even^3` and the `4` triple-leg odd
     classes orthogonal to the `15`-dim join `Stage 1 + Stage 2`.
4. Exhaustive Hodge `(3,3)` derivation vanishing (`9` Lie gens + `D^(2)(J_Mum3)`), factored boost
   `729 * 729 = 81^3 = 531,441` scaling under `/\^2(G_Mum9)`, and `12 + 7` parity on `A^3`.
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
private abbrev SpTen := List (Nat × Int)

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
  spDotGo (a.length + b.length + 1) a b

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

private def spEye (n : Nat) : SpMat :=
  (rangeList 0 n).map fun i => [(i, 1)]

private def spMatMul (a b : SpMat) : SpMat :=
  a.map fun rowA =>
    rowA.foldl (fun acc (k, aik) =>
      let rowB := (b.drop k).headD []
      if rowB.isEmpty then acc else spAdd acc (spScale aik rowB)) []

private def spMatMulVec (a : SpMat) (v : SpVec) : SpVec :=
  (rangeList 0 a.length).foldl (fun acc i =>
    let val := spDot ((a.drop i).headD []) v
    if intEq val 0 then acc else acc ++ [(i, val)]) []

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
-- Radix-Trie Accumulator for Flat Coordinate-Sparse 3-Tensors (depth = 15)
-- ---------------------------------------------------------------------------

private inductive IntTrie where
  | empty : IntTrie
  | val : Int → IntTrie
  | branch : IntTrie → IntTrie → IntTrie

private def intTrieAddGo (depth key : Nat) (dv : Int) : IntTrie → IntTrie
  | t =>
    match depth with
    | 0 =>
      match t with
      | .empty => .val dv
      | .val v => .val (v + dv)
      | .branch _ _ => .val dv
    | d' + 1 =>
      match t with
      | .empty =>
        if key % 2 == 0 then .branch (intTrieAddGo d' (key / 2) dv .empty) .empty
        else .branch .empty (intTrieAddGo d' (key / 2) dv .empty)
      | .val v => .val (v + dv)
      | .branch z o =>
        if key % 2 == 0 then .branch (intTrieAddGo d' (key / 2) dv z) o
        else .branch z (intTrieAddGo d' (key / 2) dv o)

private def intTrieAdd (depth key : Nat) (dv : Int) (t : IntTrie) : IntTrie :=
  if intEq dv 0 then t else intTrieAddGo depth key dv t

private def intTrieToGo (pfx bit : Nat) (acc : SpTen) : IntTrie → SpTen
  | .empty => acc
  | .val v => if intEq v 0 then acc else (pfx, v) :: acc
  | .branch z o =>
    let acc1 := intTrieToGo (pfx + bit) (bit * 2) acc o
    intTrieToGo pfx (bit * 2) acc1 z

private def intTrieToSpTen (t : IntTrie) : SpTen :=
  intTrieToGo 0 1 [] t

private def tenCode (i j k : Nat) : Nat :=
  i * 1024 + j * 32 + k

private def spTenAdd (a b : SpTen) : SpTen :=
  let t1 := a.foldl (fun tr (c, v) => intTrieAdd 15 c v tr) .empty
  let t2 := b.foldl (fun tr (c, v) => intTrieAdd 15 c v tr) t1
  intTrieToSpTen t2

private def spTenScale (s : Int) (t : SpTen) : SpTen :=
  if intEq s 0 then [] else t.map fun (c, v) => (c, s * v)

private def spTenEq (a b : SpTen) : Bool :=
  spVecEq a b

private def spTenIsZero (t : SpTen) : Bool :=
  t.isEmpty

-- ---------------------------------------------------------------------------
-- Shared Mumford Representation, Exterior Spaces & Casimirs
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

private def allGens9 : List (List (List Int)) :=
  gensSl2 ++ gensSu2P ++ gensSu2M

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

-- ---------------------------------------------------------------------------
-- Theorem 1: H^4(A) = /\^4(Z^8) (70-dim) Mumford Invariant Uniqueness
-- ---------------------------------------------------------------------------

private def sort4Nat (x0 x1 x2 x3 : Nat) : Nat × Nat × Nat × Nat × Int :=
  let swap (p : Nat × Nat) (s : Int) : Nat × Nat × Int :=
    if p.1 <= p.2 then (p.1, p.2, s) else (p.2, p.1, -s)
  let (a0, a1, s1) := swap (x0, x1) 1
  let (a2, a3, s2) := swap (x2, x3) s1
  let (b0, b2, s3) := swap (a0, a2) s2
  let (b1, b3, s4) := swap (a1, a3) s3
  let (c1, c2, s5) := swap (b1, b2) s4
  (b0, c1, c2, b3, s5)

private def tups4List : List (Nat × Nat × Nat × Nat) :=
  (rangeList 0 8).foldl (fun acc0 a =>
    (rangeList (a + 1) (8 - a - 1)).foldl (fun acc1 b =>
      (rangeList (b + 1) (8 - b - 1)).foldl (fun acc2 c =>
        (rangeList (c + 1) (8 - c - 1)).foldl (fun acc3 d =>
          acc3 ++ [(a, b, c, d)]) acc2) acc1) acc0) []

private inductive IdxTrie where
  | empty : IdxTrie
  | val : Nat → IdxTrie
  | branch : IdxTrie → IdxTrie → IdxTrie

private def idxTrieInsert (depth key v : Nat) : IdxTrie → IdxTrie
  | t =>
    match depth with
    | 0 => .val v
    | d' + 1 =>
      match t with
      | .empty =>
        if key % 2 == 0 then .branch (idxTrieInsert d' (key / 2) v .empty) .empty
        else .branch .empty (idxTrieInsert d' (key / 2) v .empty)
      | .val _ => .val v
      | .branch z o =>
        if key % 2 == 0 then .branch (idxTrieInsert d' (key / 2) v z) o
        else .branch z (idxTrieInsert d' (key / 2) v o)

private def idxTrieFind (depth key : Nat) : IdxTrie → Nat
  | .empty => 0
  | .val v => v
  | .branch z o =>
    match depth with
    | 0 => 0
    | d' + 1 =>
      if key % 2 == 0 then idxTrieFind d' (key / 2) z
      else idxTrieFind d' (key / 2) o

private def tuple48Code (a b c d : Nat) : Nat :=
  a * 512 + b * 64 + c * 8 + d

private def tup4Trie : IdxTrie :=
  (rangeList 0 tups4List.length).foldl (fun tr idx =>
    let (a, b, c, d) := (tups4List.drop idx).headD (0, 0, 0, 0)
    idxTrieInsert 12 (tuple48Code a b c d) idx tr) .empty

private def tup4Idx (a b c d : Nat) : Nat :=
  idxTrieFind 12 (tuple48Code a b c d) tup4Trie

private def ext4Sp (mat8 : List (List Int)) : SpMat :=
  let tr := tup4Trie
  let cols := tups4List.map fun (t0, t1, t2, t3) =>
    let stepPos (acc : SpVec) (pos : Nat) : SpVec :=
      let (i, o0, o1, o2, posSgn) :=
        if pos == 0 then (t0, t1, t2, t3, (1 : Int))
        else if pos == 1 then (t1, t0, t2, t3, -1)
        else if pos == 2 then (t2, t0, t1, t3, 1)
        else (t3, t0, t1, t2, -1)
      (rangeList 0 8).foldl (fun acc2 j =>
        let v := intMatCell mat8 j i
        if intEq v 0 || j == o0 || j == o1 || j == o2 then acc2
        else
          let (y0, y1, y2, y3, sgn) := sort4Nat j o0 o1 o2
          let idx := idxTrieFind 12 (tuple48Code y0 y1 y2 y3) tr
          spInsert idx (v * posSgn * sgn) acc2) acc
    stepPos (stepPos (stepPos (stepPos [] 0) 1) 2) 3
  spMatTranspose 70 cols

private def theta2Vec70 : SpVec :=
  let th := [(0, 4), (1, 5), (2, 6), (3, 7)]
  th.foldl (fun acc (a, b) =>
    th.foldl (fun acc2 (p, q) =>
      if a == p || a == q || b == p || b == q then acc2
      else
        let (x0, x1, x2, x3, sgn) := sort4Nat a b p q
        spInsert (tup4Idx x0 x1 x2 x3) sgn acc2) acc) []

private def b69Labels : List (Nat × Nat) :=
  [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (0, 15),
   (0, 16), (0, 17), (0, 18), (0, 31), (0, 32), (0, 33), (0, 34), (0, 35), (0, 36), (0, 37),
   (0, 38), (0, 51), (0, 52), (0, 53), (0, 54), (0, 61), (0, 62), (0, 63), (0, 64), (0, 65),
   (0, 66), (0, 67), (0, 68), (0, 69), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6),
   (1, 7), (1, 8), (1, 15), (1, 16), (1, 17), (1, 18), (1, 35), (1, 36), (1, 37), (1, 38),
   (3, 10), (3, 11), (3, 20), (3, 21), (3, 22), (3, 23), (3, 24), (3, 27), (3, 29), (3, 30),
   (4, 11), (4, 21), (4, 27), (4, 30), (6, 10), (6, 11), (6, 20), (6, 21), (7, 11)]

private def b69Inv : SpMat :=
  [[(0, 3)], [(1, 6)], [(2, 6)], [(3, 6)], [(4, 6)], [(5, 6)], [(6, 6)], [(7, 6)], [(8, 6)],
   [(51, 6), (65, -6)], [(50, -6), (64, 6)], [(50, -6), (64, -6)], [(51, -6), (65, -6)],
   [(37, 4), (53, -2), (60, -4), (67, -2), (68, -4)],
   [(9, 6)], [(10, 6)], [(11, 6)], [(12, 6)],
   [(34, 12), (51, 6), (65, -6)], [(53, 6), (60, 6), (67, -6), (68, -6)],
   [(42, -6), (52, -3), (66, 3)], [(36, -6), (52, -3), (66, -3)],
   [(37, -4), (53, -4), (60, -2), (67, -4), (68, -2)],
   [(34, -12), (51, -6), (61, -12), (65, 6)], [(38, 12), (50, -6), (64, 6)],
   [(42, 6), (52, -3), (66, 3)], [(60, 6), (68, -6)],
   [(37, -2), (40, -6), (43, 6), (46, 6), (53, -2), (60, 2), (67, -2), (68, 2)],
   [(41, -6), (52, -3), (57, -6), (66, 3)],
   [(38, -6), (45, -6), (50, 6), (62, -6), (64, -6)],
   [(13, -6)], [(14, -6)], [(15, -6)], [(16, -6)], [(17, 6)], [(18, 6)], [(19, 6)], [(20, 6)],
   [(35, 12), (50, -6), (64, -6)], [(36, 6), (52, -3), (66, -3)],
   [(37, 4), (53, -2), (60, 2), (67, -2), (68, 2)],
   [(37, 6), (40, 6), (43, -6), (46, -6), (53, 12), (54, -12), (60, 6), (68, -6)],
   [(36, -6), (41, 6), (42, -6), (52, -3), (55, -12), (57, 6), (66, -3)],
   [(38, 6), (45, 6), (50, -6), (56, -12), (62, 6), (64, 6)],
   [(39, 12), (51, -6), (65, -6)],
   [(37, 2), (40, 6), (43, 6), (46, 6), (53, -4), (60, -2), (67, -4), (68, -2)],
   [(41, 6), (52, -3), (57, -6), (66, 3)],
   [(36, -6), (41, 6), (42, -6), (47, 12), (52, -3), (55, -12), (57, 6), (66, -3)],
   [(37, -6), (40, -6), (43, 6), (46, 6), (53, -6), (58, -12), (60, 6), (67, -6), (68, -6)],
   [(34, -12), (51, -6), (59, -12), (61, -12), (65, 6)],
   [(21, -6)], [(22, -6)], [(23, -6)], [(24, -6)],
   [(37, -2), (40, 6), (43, 6), (46, -6), (53, -2), (60, -4), (67, -2), (68, -4)],
   [(34, -12), (44, 12), (51, -6), (61, -12), (65, 6)],
   [(38, -6), (45, 6), (50, 6), (62, -6), (64, -6)],
   [(38, 6), (45, 6), (48, 12), (50, -6), (56, -12), (62, 6), (64, 6)],
   [(34, -12), (49, 12), (51, -6), (59, -12), (61, -12), (65, 6)],
   [(37, -6), (40, -6), (43, 6), (46, 6), (60, 12), (63, -12)],
   [(25, -6)], [(26, -6)], [(27, -6)], [(28, -6)], [(29, -6)], [(30, -6)], [(31, -6)],
   [(32, -6)], [(33, -3)]]

private def dropCol9 (row : SpVec) : SpVec :=
  row.foldr (fun (c, v) acc =>
    if c == 9 then acc
    else if Nat.blt c 9 then (c, v) :: acc
    else (c - 1, v) :: acc) []

private def checkH4InvariantUniqueness : Bool :=
  let ex4s := allGens9.map ext4Sp
  let killsTh2 := ex4s.all fun g4 => (spMatMulVec g4 theta2Vec70).isEmpty
  let b69 := b69Labels.map fun (gi, r) =>
    dropCol9 (((ex4s.drop gi).headD [] |>.drop r).headD [])
  let i69s12 := spMatScale 12 (spEye 69)
  let invOk :=
    (b69.length == 69) && (b69Inv.length == 69) &&
    spMatEq (spMatMul b69Inv b69) i69s12 &&
    spMatEq (spMatMul b69 b69Inv) i69s12
  killsTh2 && invOk

set_option maxHeartbeats 16000000 in
set_option maxRecDepth 8192 in
/-- Certifies Mumford's `1969` `H^4(A) = /\^4(Z^8)` (`70`-dim) invariant uniqueness: all `9` Lie
generators annihilate `Theta^2`, and the `69 x 69` residual action matrix `B_69` admits exact
integer inverse `B_{69,inv} B_69 = B_69 B_{69,inv} = 12 I_69`, forcing `dim H^4(A)^G = 1`. -/
theorem mumford_h4_70dim_invariant_uniqueness_cert :
    checkH4InvariantUniqueness = true :=
  rfl

-- ---------------------------------------------------------------------------
-- Fast Flat 3-Tensor Builders & Theorem 2: Exact 21,952-Entry Identity
-- ---------------------------------------------------------------------------

private def pairsOf : List Nat → List (Nat × Nat)
  | [] => []
  | x :: xs => (xs.map fun y => (x, y)) ++ pairsOf xs

private def invSign8 (l : List Nat) : Int :=
  let rec goInv : List Nat → Nat
    | [] => 0
    | x :: xs =>
      let c := xs.foldl (fun acc y => if Nat.blt y x then acc + 1 else acc) 0
      c + goInv xs
  if goInv l % 2 == 0 then 1 else -1

private def buildTCupTen : SpTen :=
  let all8 := rangeList 0 8
  let th := [(0, 4), (1, 5), (2, 6), (3, 7)]
  let tr := th.foldl (fun tr0 (r, s) =>
    let rem6 := all8.filter fun u => !(u == r) && !(u == s)
    (pairsOf rem6).foldl (fun tr1 (a, b) =>
      let i := pairIdx28 a b
      let rem4 := rem6.filter fun u => !(u == a) && !(u == b)
      (pairsOf rem4).foldl (fun tr2 (p, q) =>
        let j := pairIdx28 p q
        let rem2 := rem4.filter fun u => !(u == p) && !(u == q)
        match rem2 with
        | [] => tr2
        | x :: rest =>
          match rest with
          | [] => tr2
          | y :: tail =>
            match tail with
            | [] =>
              let k := pairIdx28 x y
              intTrieAdd 15 (tenCode i j k) (invSign8 [a, b, p, q, x, y, r, s]) tr2
            | _ :: _ => tr2) tr1) tr0) .empty
  intTrieToSpTen tr

private def nzEReal : List (Nat × Nat × Int) :=
  (rangeList 0 8).foldl (fun acc i =>
    (rangeList 0 8).foldl (fun acc2 j =>
      let v := intMatCell matEReal i j
      if intEq v 0 then acc2 else acc2 ++ [(i, j, v)]) acc) []

private def buildDCycTen : SpTen :=
  let ordPair (u v : Nat) : Nat × Int :=
    if Nat.blt u v then (pairIdx28 u v, 1) else (pairIdx28 v u, -1)
  let tr := nzEReal.foldl (fun tr1 (i, j, c1) =>
    nzEReal.foldl (fun tr2 (k, l, c2) =>
      if j == k then tr2
      else
        nzEReal.foldl (fun tr3 (m, n, c3) =>
          if i == m || l == n then tr3
          else
            let (p1, s1) := ordPair i m
            let (p2, s2) := ordPair j k
            let (p3, s3) := ordPair l n
            intTrieAdd 15 (tenCode p1 p2 p3) ((-1) * s1 * s2 * s3 * c1 * c2 * c3) tr3) tr2) tr1)
    .empty
  intTrieToSpTen tr

private def extractDiag1Map (m : SpMat) : List (Nat × Int) × Bool :=
  let ok := m.all fun row => row.length == 1
  let mp := m.map fun row => row.headD (0, 0)
  (mp, ok)

private def spTenApplyPerm3 (mp : List (Nat × Int)) (t : SpTen) : SpTen :=
  let tr := t.foldl (fun acc (code, v) =>
    let i := code / 1024
    let j := (code / 32) % 32
    let k := code % 32
    let (i', si) := (mp.drop i).headD (0, 0)
    let (j', sj) := (mp.drop j).headD (0, 0)
    let (k', sk) := (mp.drop k).headD (0, 0)
    intTrieAdd 15 (tenCode i' j' k') (si * sj * sk * v) acc) .empty
  intTrieToSpTen tr

private def spTenSwap12 (t : SpTen) : SpTen :=
  let tr := t.foldl (fun acc (c, v) =>
    intTrieAdd 15 (tenCode ((c / 32) % 32) (c / 1024) (c % 32)) v acc) .empty
  intTrieToSpTen tr

private def spTenSwap23 (t : SpTen) : SpTen :=
  let tr := t.foldl (fun acc (c, v) =>
    intTrieAdd 15 (tenCode (c / 1024) (c % 32) ((c / 32) % 32)) v acc) .empty
  intTrieToSpTen tr

private def thVec28 : SpVec :=
  (rangeList 0 8).foldl (fun acc i =>
    (rangeList (i + 1) (8 - i - 1)).foldl (fun acc2 j =>
      let v := intMatCell matEReal i j - intMatCell matEReal j i
      if intEq v 0 then acc2 else spInsert (pairIdx28 i j) v acc2) acc) []

-- ---------------------------------------------------------------------------
-- Normalized Tensor & Operator Literals (Verified Equal to Constructors)
-- ---------------------------------------------------------------------------

private def spMatListEq (a b : List SpMat) : Bool :=
  (a.length == b.length) && (List.zipWith spMatEq a b).all id

private def spTenToSlices28 (t : SpTen) : List SpMat :=
  t.foldl (fun acc (c, v) =>
    let i := c / 1024
    let j := (c / 32) % 32
    let k := c % 32
    let sl := (acc.drop i).headD []
    let row := (sl.drop j).headD []
    let nSl := sl.take j ++ [spInsert k v row] ++ sl.drop (j + 1)
    acc.take i ++ [nSl] ++ acc.drop (i + 1)) (List.replicate 28 (List.replicate 28 []))

private def dCycLit : SpTen :=
  [(20224, 1), (27200, -1), (22848, 1), (19264, -1), (10944, 1), (3776, 1), (26048, -1),
  (15136, -1), (22624, 1), (25184, 1), (16096, 1), (24032, 1), (16912, 2), (18064, 1), (5584,
  1), (23600, 1), (21040, 1), (7984, 1), (14512, 1), (28080, 1), (15728, 1), (14192, 1),
  (25840, 1), (1776, 1), (11760, 1), (4872, 1), (24712, 1), (26952, 1), (11080, 1), (22344, 1),
  (22728, -1), (6856, -1), (26152, 1), (18216, 1), (27304, 1), (16232, 1), (28136, 1), (19480,
  1), (4376, 1), (8344, 1), (1688, 1), (21592, 1), (3160, 1), (20536, 1), (13496, 1), (2744,
  1), (5560, 1), (2168, 1), (632, 1), (24836, 1), (8964, 1), (18820, 1), (12868, 1), (9540, 1),
  (11716, 1), (10532, 1), (3364, 1), (9316, 1), (14692, 1), (23780, 1), (7908, 1), (17940, 1),
  (1812, 1), (15764, 1), (8020, 1), (14548, 1), (6612, 1), (24628, 1), (16948, 1), (22068, 1),
  (18100, 1), (26868, 1), (12788, 1), (18572, 1), (16012, 1), (22604, 1), (4684, 1), (19788,
  1), (2764, 1), (14124, -1), (20140, 1), (26028, -1), (10860, 1), (22124, 1), (20972, 1),
  (22274, 1), (3842, 1), (22914, 1), (10050, 1), (12994, 1), (28098, 1), (24098, 1), (26914,
  1), (25250, 1), (24674, 1), (15202, 1), (18146, 1), (26642, -1), (12434, 1), (4498, 1), (850,
  -1), (21714, 1), (3282, 1), (27698, -1), (5682, 1), (17586, 1), (6834, 1), (6258, 1), (1906,
  -1), (22538, 1), (26890, 1), (9354, 1), (19850, 1), (10570, 2), (9034, 1), (714, 1), (4394,
  1), (7978, 1), (12906, 1), (15722, 1), (25834, 1), (11754, 1), (18458, -1), (10522, 1),
  (21786, 1), (7834, 1), (9306, 1), (602, -1), (8538, 1), (2362, 1), (8890, 1), (11706, 1),
  (13690, 1), (20730, 1), (22790, -1), (14982, 1), (22086, 1), (3654, 1), (8902, -1), (20934,
  1), (19750, 1), (19110, 1), (23974, -1), (18534, 1), (9830, 1), (14054, -1), (10262, 1),
  (3094, 1), (6422, -1), (2454, 1), (12374, 1), (342, 1), (8406, -1), (11318, 1), (7350, -1),
  (118, 1), (1398, 1), (5366, -1), (25614, -1), (5646, 1), (11406, 1), (6798, 1), (27726, 1),
  (20686, 1), (814, -1), (16558, 1), (3246, 1), (5230, 1), (4462, 1), (2926, 1), (24065, 1),
  (21249, 1), (25217, 1), (28225, -1), (11969, 1), (25889, 1), (10017, 1), (23649, 1), (22881,
  1), (19297, -1), (17121, 1), (3809, 1), (21009, 1), (25873, 1), (17041, 1), (22161, 1),
  (23633, 1), (5713, 1), (9009, 1), (18609, 1), (21169, 1), (11889, 1), (19825, 1), (2801, 1),
  (10377, 1), (3209, 1), (26697, 1), (4425, 1), (2889, 1), (19657, 1), (25641, 1), (1833, 1),
  (15529, 1), (4201, 1), (6761, 1), (5609, 1), (14361, -1), (7705, 1), (17689, 1), (13721, -1),
  (7513, 1), (473, -1), (9273, 1), (8761, 1), (1337, 1), (12729, -1), (16633, 1), (10489, 1),
  (14853, 1), (14085, 1), (17989, 1), (7877, -1), (16837, 1), (3525, 1), (18981, 1), (15653,
  1), (24997, 1), (14437, 1), (22757, -1), (9701, 1), (26901, 1), (2837, 1), (18069, 1),
  (19861, 1), (24661, 1), (6741, 1), (9045, 1), (18645, 1), (21045, 1), (22197, 2), (28085, 1),
  (12917, 1), (14197, 1), (28173, 1), (5901, 1), (25997, -1), (12109, 1), (23757, -1), (13101,
  -1), (24749, 1), (28333, 1), (26989, 1), (17261, 1), (22381, 1), (6893, -1), (22531, 1),
  (2819, 1), (9347, 1), (24643, 1), (6723, 1), (18627, 1), (707, 1), (5571, 1), (23587, 1),
  (4387, 1), (14499, 1), (3171, 2), (1763, 1), (24595, 1), (787, 1), (10643, 1), (21907, 1),
  (12627, 1), (9427, 1), (11827, 1), (6451, 1), (12979, 1), (17779, 1), (8051, -1), (27891,
  -1), (15883, 1), (14475, 1), (15691, 1), (14155, 1), (1739, 1), (4555, 1), (22571, 1),
  (20011, 1), (27051, 1), (18027, 1), (16875, 1), (10731, 1), (13851, 1), (15643, 1), (14427,
  1), (1627, -1), (2523, 1), (18491, -1), (14011, 1), (16827, 1), (21947, 1), (7803, -1),
  (19707, -1), (8699, 1), (26119, 1), (23687, 1), (27271, 1), (25927, 1), (21319, 1), (5831,
  -1), (17191, 1), (11047, 1), (22695, -1), (28263, -1), (20327, -1), (4839, 1), (15383, 1),
  (1559, 1), (7319, 1), (17495, 1), (13527, -1), (16439, 1), (3127, 1), (2615, 1), (6583, -1),
  (1143, 1), (4343, 1), (503, 1), (23567, 1), (11791, 1), (27919, 1), (12943, 1), (20879, 1),
  (11599, 1), (5423, 1), (9391, 1), (16751, 1), (10607, 1), (9071, 1), (751, 1)]

private def tCupLit : SpTen :=
  [(23040, -1), (20224, 1), (27200, -1), (19264, -1), (17088, -1), (22208, -1), (26048, -1),
  (15136, -1), (23200, -1), (25184, 1), (16096, 1), (24032, 1), (22544, -1), (26896, -1),
  (2832, -1), (9360, -1), (19856, -1), (24656, -1), (6736, -1), (21840, 1), (3408, 1), (9040,
  -1), (18640, -1), (720, -1), (4400, -1), (10928, 1), (3760, 1), (10352, 1), (21616, 1),
  (12912, -1), (27144, -1), (4872, 1), (24712, 1), (17224, -1), (3912, -1), (22728, -1), (6856,
  -1), (26152, 1), (18216, 1), (26728, -1), (16232, 1), (28136, 1), (19480, 1), (2584, -1),
  (4376, 1), (8344, 1), (1688, 1), (16472, -1), (10328, -1), (2392, -1), (20536, 1), (13496,
  1), (5560, 1), (632, 1), (9732, -1), (24836, 1), (8964, 1), (18820, 1), (12868, 1), (11716,
  1), (16676, -1), (21796, -1), (9892, -1), (14692, 1), (23780, 1), (7908, 1), (1812, 1),
  (15764, 1), (17748, -1), (8020, 1), (14548, 1), (6612, 1), (24628, 1), (10804, -1), (3636,
  -1), (17524, -1), (26868, 1), (12788, 1), (19980, -1), (18572, 1), (16012, 1), (22604, 1),
  (4684, 1), (2764, 1), (14124, -1), (26028, -1), (19564, -1), (17004, -1), (3692, -1), (20972,
  1), (25090, -1), (17154, -1), (11010, -1), (22914, 1), (24898, -1), (10050, 1), (12994, 1),
  (28098, 1), (24098, 1), (26914, 1), (15202, 1), (18146, 1), (26642, -1), (6674, -1), (12434,
  1), (4498, 1), (6482, -1), (850, -1), (16594, -1), (10450, -1), (27698, -1), (5682, 1),
  (17586, 1), (1906, -1), (22026, 1), (3594, 1), (2826, -1), (18058, -1), (24650, -1), (6730,
  -1), (18634, -1), (5578, -1), (23594, -1), (21034, -1), (14506, -1), (17066, 1), (3754, 1),
  (28074, -1), (16490, 1), (21610, 1), (14186, -1), (1770, -1), (18458, -1), (8730, -1),
  (16666, -1), (3354, -1), (7834, 1), (9306, 1), (602, -1), (2362, 1), (11706, 1), (8314, -1),
  (13690, 1), (20730, 1), (18950, -1), (22790, -1), (14982, 1), (16966, -1), (10822, -1),
  (18758, -1), (8902, -1), (20934, 1), (19750, 1), (23974, -1), (9830, 1), (14054, -1), (16406,
  -1), (21526, -1), (534, -1), (6422, -1), (2454, 1), (12374, 1), (8406, -1), (11318, 1),
  (7350, -1), (694, -1), (1398, 1), (5366, -1), (25614, -1), (11406, 1), (6798, 1), (27726, 1),
  (5454, -1), (20686, 1), (814, -1), (10414, -1), (21678, -1), (5806, -1), (4462, 1), (2926,
  1), (21249, 1), (25217, 1), (28225, -1), (23873, -1), (11969, 1), (25889, 1), (10017, 1),
  (24225, -1), (22881, 1), (19297, -1), (10977, -1), (22241, -1), (25873, 1), (10897, -1),
  (3729, -1), (23633, 1), (5713, 1), (20817, -1), (9009, 1), (18609, 1), (20593, -1), (11889,
  1), (19825, 1), (2801, 1), (4617, -1), (16521, -1), (21641, -1), (26697, 1), (2889, 1),
  (19657, 1), (25641, 1), (1833, 1), (15529, 1), (4777, -1), (6761, 1), (5609, 1), (14361, -1),
  (17689, 1), (13721, -1), (473, -1), (9273, 1), (8761, 1), (1337, 1), (7865, -1), (12729, -1),
  (7289, -1), (21753, -1), (3321, -1), (14085, 1), (17989, 1), (14661, -1), (7877, -1), (10693,
  -1), (21957, -1), (18981, 1), (15653, 1), (15013, -1), (24997, 1), (22757, -1), (9701, 1),
  (22549, -1), (10773, 1), (3605, 1), (9365, -1), (16725, 1), (3413, 1), (725, -1), (5589, -1),
  (23605, -1), (4405, -1), (7989, -1), (14517, -1), (16501, 1), (10357, 1), (15733, -1),
  (25845, -1), (1781, -1), (11765, -1), (5901, 1), (25997, -1), (27981, -1), (12109, 1),
  (23757, -1), (13101, -1), (24749, 1), (27757, -1), (26989, 1), (11117, -1), (3949, -1),
  (6893, -1), (10755, 1), (22019, 1), (26883, -1), (18051, -1), (19843, -1), (16707, 1),
  (21827, 1), (9027, -1), (21027, -1), (7971, -1), (17059, 1), (10915, 1), (28067, -1), (12899,
  -1), (15715, -1), (14179, -1), (25827, -1), (11747, -1), (24595, 1), (12819, -1), (787, 1),
  (16787, -1), (3475, -1), (9427, 1), (11827, 1), (6451, 1), (12403, -1), (17779, 1), (8051,
  -1), (27891, -1), (14475, 1), (14155, 1), (1739, 1), (4555, 1), (22571, 1), (20011, 1),
  (16043, -1), (27051, 1), (15467, -1), (18027, 1), (21995, -1), (3563, -1), (15643, 1),
  (14427, 1), (1627, -1), (13659, -1), (2523, 1), (18491, -1), (10683, -1), (3515, -1), (13435,
  -1), (7803, -1), (19707, -1), (8699, 1), (23687, 1), (27271, 1), (21319, 1), (5831, -1),
  (22311, -1), (3879, -1), (22695, -1), (26279, -1), (25703, -1), (28263, -1), (20327, -1),
  (4839, 1), (15383, 1), (7319, 1), (17495, 1), (1367, -1), (13527, -1), (10295, -1), (21559,
  -1), (2615, 1), (1719, -1), (6583, -1), (4343, 1), (503, 1), (23567, 1), (27919, 1), (12943,
  1), (20879, 1), (5423, 1), (9391, 1), (11951, -1), (11375, -1), (21871, -1), (3439, -1),
  (9071, 1), (751, 1)]

private def e2MapLit : List (Nat × Int) :=
  [(22, 1), (23, 1), (24, 1), (3, 1), (9, 1), (14, 1), (18, 1), (25, 1), (26, 1), (4, 1), (10,
  1), (15, 1), (19, 1), (27, 1), (5, 1), (11, 1), (16, 1), (20, 1), (6, 1), (12, 1), (17, 1),
  (21, 1), (0, 1), (1, 1), (2, 1), (7, 1), (8, 1), (13, 1)]

private def tCupUpLit : SpTen :=
  [(23040, -1), (20224, 1), (27200, -1), (19264, -1), (17088, -1), (22208, -1), (26048, -1),
  (15136, -1), (23200, -1), (25184, 1), (16096, 1), (24032, 1), (22544, -1), (26896, -1),
  (2832, -1), (9360, -1), (19856, -1), (24656, -1), (6736, -1), (21840, 1), (3408, 1), (9040,
  -1), (18640, -1), (720, -1), (4400, -1), (10928, 1), (3760, 1), (10352, 1), (21616, 1),
  (12912, -1), (27144, -1), (4872, 1), (24712, 1), (17224, -1), (3912, -1), (22728, -1), (6856,
  -1), (26152, 1), (18216, 1), (26728, -1), (16232, 1), (28136, 1), (19480, 1), (2584, -1),
  (4376, 1), (8344, 1), (1688, 1), (16472, -1), (10328, -1), (2392, -1), (20536, 1), (13496,
  1), (5560, 1), (632, 1), (9732, -1), (24836, 1), (8964, 1), (18820, 1), (12868, 1), (11716,
  1), (16676, -1), (21796, -1), (9892, -1), (14692, 1), (23780, 1), (7908, 1), (1812, 1),
  (15764, 1), (17748, -1), (8020, 1), (14548, 1), (6612, 1), (24628, 1), (10804, -1), (3636,
  -1), (17524, -1), (26868, 1), (12788, 1), (19980, -1), (18572, 1), (16012, 1), (22604, 1),
  (4684, 1), (2764, 1), (14124, -1), (26028, -1), (19564, -1), (17004, -1), (3692, -1), (20972,
  1), (25090, -1), (17154, -1), (11010, -1), (22914, 1), (24898, -1), (10050, 1), (12994, 1),
  (28098, 1), (24098, 1), (26914, 1), (15202, 1), (18146, 1), (26642, -1), (6674, -1), (12434,
  1), (4498, 1), (6482, -1), (850, -1), (16594, -1), (10450, -1), (27698, -1), (5682, 1),
  (17586, 1), (1906, -1), (22026, 1), (3594, 1), (2826, -1), (18058, -1), (24650, -1), (6730,
  -1), (18634, -1), (5578, -1), (23594, -1), (21034, -1), (14506, -1), (17066, 1), (3754, 1),
  (28074, -1), (16490, 1), (21610, 1), (14186, -1), (1770, -1), (18458, -1), (8730, -1),
  (16666, -1), (3354, -1), (7834, 1), (9306, 1), (602, -1), (2362, 1), (11706, 1), (8314, -1),
  (13690, 1), (20730, 1), (18950, -1), (22790, -1), (14982, 1), (16966, -1), (10822, -1),
  (18758, -1), (8902, -1), (20934, 1), (19750, 1), (23974, -1), (9830, 1), (14054, -1), (16406,
  -1), (21526, -1), (534, -1), (6422, -1), (2454, 1), (12374, 1), (8406, -1), (11318, 1),
  (7350, -1), (694, -1), (1398, 1), (5366, -1), (25614, -1), (11406, 1), (6798, 1), (27726, 1),
  (5454, -1), (20686, 1), (814, -1), (10414, -1), (21678, -1), (5806, -1), (4462, 1), (2926,
  1), (21249, 1), (25217, 1), (28225, -1), (23873, -1), (11969, 1), (25889, 1), (10017, 1),
  (24225, -1), (22881, 1), (19297, -1), (10977, -1), (22241, -1), (25873, 1), (10897, -1),
  (3729, -1), (23633, 1), (5713, 1), (20817, -1), (9009, 1), (18609, 1), (20593, -1), (11889,
  1), (19825, 1), (2801, 1), (4617, -1), (16521, -1), (21641, -1), (26697, 1), (2889, 1),
  (19657, 1), (25641, 1), (1833, 1), (15529, 1), (4777, -1), (6761, 1), (5609, 1), (14361, -1),
  (17689, 1), (13721, -1), (473, -1), (9273, 1), (8761, 1), (1337, 1), (7865, -1), (12729, -1),
  (7289, -1), (21753, -1), (3321, -1), (14085, 1), (17989, 1), (14661, -1), (7877, -1), (10693,
  -1), (21957, -1), (18981, 1), (15653, 1), (15013, -1), (24997, 1), (22757, -1), (9701, 1),
  (22549, -1), (10773, 1), (3605, 1), (9365, -1), (16725, 1), (3413, 1), (725, -1), (5589, -1),
  (23605, -1), (4405, -1), (7989, -1), (14517, -1), (16501, 1), (10357, 1), (15733, -1),
  (25845, -1), (1781, -1), (11765, -1), (5901, 1), (25997, -1), (27981, -1), (12109, 1),
  (23757, -1), (13101, -1), (24749, 1), (27757, -1), (26989, 1), (11117, -1), (3949, -1),
  (6893, -1), (10755, 1), (22019, 1), (26883, -1), (18051, -1), (19843, -1), (16707, 1),
  (21827, 1), (9027, -1), (21027, -1), (7971, -1), (17059, 1), (10915, 1), (28067, -1), (12899,
  -1), (15715, -1), (14179, -1), (25827, -1), (11747, -1), (24595, 1), (12819, -1), (787, 1),
  (16787, -1), (3475, -1), (9427, 1), (11827, 1), (6451, 1), (12403, -1), (17779, 1), (8051,
  -1), (27891, -1), (14475, 1), (14155, 1), (1739, 1), (4555, 1), (22571, 1), (20011, 1),
  (16043, -1), (27051, 1), (15467, -1), (18027, 1), (21995, -1), (3563, -1), (15643, 1),
  (14427, 1), (1627, -1), (13659, -1), (2523, 1), (18491, -1), (10683, -1), (3515, -1), (13435,
  -1), (7803, -1), (19707, -1), (8699, 1), (23687, 1), (27271, 1), (21319, 1), (5831, -1),
  (22311, -1), (3879, -1), (22695, -1), (26279, -1), (25703, -1), (28263, -1), (20327, -1),
  (4839, 1), (15383, 1), (7319, 1), (17495, 1), (1367, -1), (13527, -1), (10295, -1), (21559,
  -1), (2615, 1), (1719, -1), (6583, -1), (4343, 1), (503, 1), (23567, 1), (27919, 1), (12943,
  1), (20879, 1), (5423, 1), (9391, 1), (11951, -1), (11375, -1), (21871, -1), (3439, -1),
  (9071, 1), (751, 1)]

private def dCycSlLit : List SpMat :=
  [[[], [], [], [(22, 1)], [], [], [], [], [], [], [(22, 1)], [], [], [], [(25, -1)], [(23,
  1)], [], [], [(26, -1)], [(24, 1)], [], [], [(3, 1), (10, 1)], [(15, 1)], [(19, 1)], [(14,
  -1)], [(18, -1)], []], [[], [], [], [(23, 1)], [], [], [], [], [], [(25, 1)], [], [(22, 1)],
  [], [], [], [], [(23, 1)], [], [(27, -1)], [], [(24, 1)], [], [(11, 1)], [(3, 1), (16, 1)],
  [(20, 1)], [(9, 1)], [], [(18, -1)]], [[], [], [], [(24, 1)], [], [], [], [], [], [(26, 1)],
  [], [], [(22, 1)], [], [(27, 1)], [], [], [(23, 1)], [], [], [], [(24, 1)], [(12, 1)], [(17,
  1)], [(3, 1), (21, 1)], [], [(9, 1)], [(14, 1)]], [[(22, 1)], [(23, 1)], [(24, 1)], [(3, 2)],
  [(9, 1)], [(14, 1)], [(18, 1)], [], [], [(4, 1)], [], [], [], [], [(5, 1)], [], [], [], [(6,
  1)], [], [], [], [(0, 1)], [(1, 1)], [(2, 1)], [], [], []], [[], [], [], [(9, 1)], [], [],
  [], [(23, 1)], [(24, 1)], [(3, 1), (10, 1)], [(9, 1)], [(14, 1)], [(18, 1)], [], [(11, 1)],
  [], [], [], [(12, 1)], [], [], [], [], [(7, 1)], [(8, 1)], [], [], []], [[], [], [], [(14,
  1)], [], [], [], [(22, -1)], [], [(15, 1)], [], [], [], [(24, 1)], [(3, 1), (16, 1)], [(9,
  1)], [(14, 1)], [(18, 1)], [(17, 1)], [], [], [], [(7, -1)], [], [(13, 1)], [], [], []], [[],
  [], [], [(18, 1)], [], [], [], [], [(22, -1)], [(19, 1)], [], [], [], [(23, -1)], [(20, 1)],
  [], [], [], [(3, 1), (21, 1)], [(9, 1)], [(14, 1)], [(18, 1)], [(8, -1)], [(13, -1)], [], [],
  [], []], [[], [], [], [], [(23, 1)], [(22, -1)], [], [], [], [], [(25, 1)], [], [], [], [],
  [], [(25, 1)], [], [], [(27, -1)], [(26, 1)], [], [(5, -1)], [(4, 1)], [], [(10, 1), (16,
  1)], [(20, 1)], [(19, -1)]], [[], [], [], [], [(24, 1)], [], [(22, -1)], [], [], [], [(26,
  1)], [], [], [], [], [(27, 1)], [], [(25, 1)], [], [], [], [(26, 1)], [(6, -1)], [], [(4,
  1)], [(17, 1)], [(10, 1), (21, 1)], [(15, 1)]], [[], [(25, 1)], [(26, 1)], [(4, 1)], [(3, 1),
  (10, 1)], [(15, 1)], [(19, 1)], [], [], [], [(4, 1)], [], [], [], [], [(5, 1)], [], [], [],
  [(6, 1)], [], [], [], [], [], [(1, 1)], [(2, 1)], []], [[(22, 1)], [], [], [], [(9, 1)], [],
  [], [(25, 1)], [(26, 1)], [(4, 1)], [(10, 2)], [(15, 1)], [(19, 1)], [], [], [(11, 1)], [],
  [], [], [(12, 1)], [], [], [(0, 1)], [], [], [(7, 1)], [(8, 1)], []], [[], [(22, 1)], [], [],
  [(14, 1)], [], [], [], [], [], [(15, 1)], [], [], [(26, 1)], [(4, 1)], [(10, 1), (16, 1)],
  [(15, 1)], [(19, 1)], [], [(17, 1)], [], [], [(1, 1)], [], [], [], [(13, 1)], []], [[], [],
  [(22, 1)], [], [(18, 1)], [], [], [], [], [], [(19, 1)], [], [], [(25, -1)], [], [(20, 1)],
  [], [], [(4, 1)], [(10, 1), (21, 1)], [(15, 1)], [(19, 1)], [(2, 1)], [], [], [(13, -1)], [],
  []], [[], [], [], [], [], [(24, 1)], [(23, -1)], [], [], [], [], [(26, 1)], [(25, -1)], [],
  [], [], [(27, 1)], [], [], [], [], [(27, 1)], [], [(6, -1)], [(5, 1)], [(12, -1)], [(11, 1)],
  [(16, 1), (21, 1)]], [[(25, -1)], [], [(27, 1)], [(5, 1)], [(11, 1)], [(3, 1), (16, 1)],
  [(20, 1)], [], [], [], [], [(4, 1)], [], [], [], [], [(5, 1)], [], [], [], [(6, 1)], [], [],
  [], [], [(0, -1)], [], [(2, 1)]], [[(23, 1)], [], [], [], [], [(9, 1)], [], [], [(27, 1)],
  [(5, 1)], [(11, 1)], [(10, 1), (16, 1)], [(20, 1)], [], [], [], [(11, 1)], [], [], [], [(12,
  1)], [], [], [(0, 1)], [], [], [], [(8, 1)]], [[], [(23, 1)], [], [], [], [(14, 1)], [],
  [(25, 1)], [], [], [], [(15, 1)], [], [(27, 1)], [(5, 1)], [(11, 1)], [(16, 2)], [(20, 1)],
  [], [], [(17, 1)], [], [], [(1, 1)], [], [(7, 1)], [], [(13, 1)]], [[], [], [(23, 1)], [],
  [], [(18, 1)], [], [], [(25, 1)], [], [], [(19, 1)], [], [], [], [], [(20, 1)], [], [(5, 1)],
  [(11, 1)], [(16, 1), (21, 1)], [(20, 1)], [], [(2, 1)], [], [(8, 1)], [], []], [[(26, -1)],
  [(27, -1)], [], [(6, 1)], [(12, 1)], [(17, 1)], [(3, 1), (21, 1)], [], [], [], [], [], [(4,
  1)], [], [], [], [], [(5, 1)], [], [], [], [(6, 1)], [], [], [], [], [(0, -1)], [(1, -1)]],
  [[(24, 1)], [], [], [], [], [], [(9, 1)], [(27, -1)], [], [(6, 1)], [(12, 1)], [(17, 1)],
  [(10, 1), (21, 1)], [], [], [], [], [(11, 1)], [], [], [], [(12, 1)], [], [], [(0, 1)], [],
  [], [(7, -1)]], [[], [(24, 1)], [], [], [], [], [(14, 1)], [(26, 1)], [], [], [], [], [(15,
  1)], [], [(6, 1)], [(12, 1)], [(17, 1)], [(16, 1), (21, 1)], [], [], [], [(17, 1)], [], [],
  [(1, 1)], [], [(7, 1)], []], [[], [], [(24, 1)], [], [], [], [(18, 1)], [], [(26, 1)], [],
  [], [], [(19, 1)], [(27, 1)], [], [], [], [(20, 1)], [(6, 1)], [(12, 1)], [(17, 1)], [(21,
  2)], [], [], [(2, 1)], [], [(8, 1)], [(13, 1)]], [[(3, 1), (10, 1)], [(11, 1)], [(12, 1)],
  [(0, 1)], [], [(7, -1)], [(8, -1)], [(5, -1)], [(6, -1)], [], [(0, 1)], [(1, 1)], [(2, 1)],
  [], [], [], [], [], [], [], [], [], [], [], [], [], [], []], [[(15, 1)], [(3, 1), (16, 1)],
  [(17, 1)], [(1, 1)], [(7, 1)], [], [(13, -1)], [(4, 1)], [], [], [], [], [], [(6, -1)], [],
  [(0, 1)], [(1, 1)], [(2, 1)], [], [], [], [], [], [], [], [], [], []], [[(19, 1)], [(20, 1)],
  [(3, 1), (21, 1)], [(2, 1)], [(8, 1)], [(13, 1)], [], [], [(4, 1)], [], [], [], [], [(5, 1)],
  [], [], [], [], [], [(0, 1)], [(1, 1)], [(2, 1)], [], [], [], [], [], []], [[(14, -1)], [(9,
  1)], [], [], [], [], [], [(10, 1), (16, 1)], [(17, 1)], [(1, 1)], [(7, 1)], [], [(13, -1)],
  [(12, -1)], [(0, -1)], [], [(7, 1)], [(8, 1)], [], [], [], [], [], [], [], [], [], []],
  [[(18, -1)], [], [(9, 1)], [], [], [], [], [(20, 1)], [(10, 1), (21, 1)], [(2, 1)], [(8, 1)],
  [(13, 1)], [], [(11, 1)], [], [], [], [], [(0, -1)], [], [(7, 1)], [(8, 1)], [], [], [], [],
  [], []], [[], [(18, -1)], [(14, 1)], [], [], [], [], [(19, -1)], [(15, 1)], [], [], [], [],
  [(16, 1), (21, 1)], [(2, 1)], [(8, 1)], [(13, 1)], [], [(1, -1)], [(7, -1)], [], [(13, 1)],
  [], [], [], [], [], []]]

private def q0Lit : SpMat :=
  [[], [], [], [(3, 1), (10, 1), (16, 1), (21, 1)], [], [], [], [], [], [], [(3, 1), (10, 1),
  (16, 1), (21, 1)], [], [], [], [], [], [(3, 1), (10, 1), (16, 1), (21, 1)], [], [], [], [],
  [(3, 1), (10, 1), (16, 1), (21, 1)], [], [], [], [], [], []]

private def qSdLit : SpMat :=
  [[(0, 2), (13, 2)], [(1, 2), (8, -2)], [(2, 2), (7, 2)], [], [(4, 1), (9, -1), (17, 1), (20,
  -1)], [(5, 1), (12, -1), (14, -1), (19, 1)], [(6, 1), (11, 1), (15, -1), (18, -1)], [(2, 2),
  (7, 2)], [(1, -2), (8, 2)], [(4, -1), (9, 1), (17, -1), (20, 1)], [], [(6, 1), (11, 1), (15,
  -1), (18, -1)], [(5, -1), (12, 1), (14, 1), (19, -1)], [(0, 2), (13, 2)], [(5, -1), (12, 1),
  (14, 1), (19, -1)], [(6, -1), (11, -1), (15, 1), (18, 1)], [], [(4, 1), (9, -1), (17, 1),
  (20, -1)], [(6, -1), (11, -1), (15, 1), (18, 1)], [(5, 1), (12, -1), (14, -1), (19, 1)], [(4,
  -1), (9, 1), (17, -1), (20, 1)], [], [(22, 2), (27, 2)], [(23, 2), (26, -2)], [(24, 2), (25,
  2)], [(24, 2), (25, 2)], [(23, -2), (26, 2)], [(22, 2), (27, 2)]]

private def qAsdLit : SpMat :=
  [[(0, 2), (13, -2)], [(1, 2), (8, 2)], [(2, 2), (7, -2)], [], [(4, 1), (9, -1), (17, -1),
  (20, 1)], [(5, 1), (12, 1), (14, -1), (19, -1)], [(6, 1), (11, -1), (15, 1), (18, -1)], [(2,
  -2), (7, 2)], [(1, 2), (8, 2)], [(4, -1), (9, 1), (17, 1), (20, -1)], [], [(6, -1), (11, 1),
  (15, -1), (18, 1)], [(5, 1), (12, 1), (14, -1), (19, -1)], [(0, -2), (13, 2)], [(5, -1), (12,
  -1), (14, 1), (19, 1)], [(6, 1), (11, -1), (15, 1), (18, -1)], [], [(4, -1), (9, 1), (17, 1),
  (20, -1)], [(6, -1), (11, 1), (15, -1), (18, 1)], [(5, -1), (12, -1), (14, 1), (19, 1)], [(4,
  1), (9, -1), (17, -1), (20, 1)], [], [(22, 2), (27, -2)], [(23, 2), (26, 2)], [(24, 2), (25,
  -2)], [(24, -2), (25, 2)], [(23, 2), (26, 2)], [(22, -2), (27, 2)]]

private def qRicLit : SpMat :=
  [[], [], [], [(3, 3), (10, -1), (16, -1), (21, -1)], [(4, 2), (9, 2)], [(5, 2), (14, 2)],
  [(6, 2), (18, 2)], [], [], [(4, 2), (9, 2)], [(3, -1), (10, 3), (16, -1), (21, -1)], [(11,
  2), (15, 2)], [(12, 2), (19, 2)], [], [(5, 2), (14, 2)], [(11, 2), (15, 2)], [(3, -1), (10,
  -1), (16, 3), (21, -1)], [(17, 2), (20, 2)], [(6, 2), (18, 2)], [(12, 2), (19, 2)], [(17, 2),
  (20, 2)], [(3, -1), (10, -1), (16, -1), (21, 3)], [], [], [], [], [], []]

private def d10Lit : List SpMat :=
  [[[(0, 2)], [(1, 2)], [(2, 2)], [], [], [], [], [(7, 2)], [(8, 2)], [], [], [], [], [(13,
  2)], [], [], [], [], [], [], [], [], [(22, -2)], [(23, -2)], [(24, -2)], [(25, -2)], [(26,
  -2)], [(27, -2)]], [[(4, 1), (9, -1)], [(5, 1), (14, -1)], [(6, 1), (18, -1)], [], [(22, 1)],
  [(23, 1)], [(24, 1)], [(11, 1), (15, -1)], [(12, 1), (19, -1)], [(22, -1)], [], [(25, 1)],
  [(26, 1)], [(17, 1), (20, -1)], [(23, -1)], [(25, -1)], [], [(27, 1)], [(24, -1)], [(26,
  -1)], [(27, -1)], [], [], [], [], [], [], []], [[], [], [], [], [(0, 1)], [(1, 1)], [(2, 1)],
  [], [], [(0, -1)], [], [(7, 1)], [(8, 1)], [], [(1, -1)], [(7, -1)], [], [(13, 1)], [(2,
  -1)], [(8, -1)], [(13, -1)], [], [(4, 1), (9, -1)], [(5, 1), (14, -1)], [(6, 1), (18, -1)],
  [(11, 1), (15, -1)], [(12, 1), (19, -1)], [(17, 1), (20, -1)]], [[], [(2, -1), (7, -1)], [(1,
  1), (8, -1)], [(4, -1), (9, -1)], [(3, 1), (10, -1)], [(6, -1), (11, -1)], [(5, 1), (12,
  -1)], [(1, 1), (8, -1)], [(2, 1), (7, 1)], [(3, 1), (10, -1)], [(4, 1), (9, 1)], [(5, 1),
  (12, -1)], [(6, 1), (11, 1)], [], [(15, -1), (18, -1)], [(14, 1), (19, -1)], [(17, -1), (20,
  -1)], [(16, 1), (21, -1)], [(14, 1), (19, -1)], [(15, 1), (18, 1)], [(16, 1), (21, -1)],
  [(17, 1), (20, 1)], [], [(24, -1), (25, -1)], [(23, 1), (26, -1)], [(23, 1), (26, -1)], [(24,
  1), (25, 1)], []], [[(2, 1), (7, 1)], [], [(0, -1), (13, -1)], [(5, -1), (14, -1)], [(6, 1),
  (15, -1)], [(3, 1), (16, -1)], [(4, -1), (17, -1)], [(0, -1), (13, -1)], [], [(11, -1), (18,
  1)], [(12, 1), (19, 1)], [(9, 1), (20, 1)], [(10, -1), (21, 1)], [(2, 1), (7, 1)], [(3, 1),
  (16, -1)], [(4, 1), (17, 1)], [(5, 1), (14, 1)], [(6, 1), (15, -1)], [(9, -1), (20, -1)],
  [(10, -1), (21, 1)], [(11, -1), (18, 1)], [(12, -1), (19, -1)], [(24, 1), (25, 1)], [], [(22,
  -1), (27, -1)], [(22, -1), (27, -1)], [], [(24, 1), (25, 1)]], [[(1, -1), (8, 1)], [(0, 1),
  (13, 1)], [], [(6, -1), (18, -1)], [(5, -1), (19, -1)], [(4, 1), (20, -1)], [(3, 1), (21,
  -1)], [], [(0, -1), (13, -1)], [(12, -1), (14, -1)], [(11, -1), (15, -1)], [(10, 1), (16,
  -1)], [(9, 1), (17, -1)], [(1, -1), (8, 1)], [(9, 1), (17, -1)], [(10, 1), (16, -1)], [(11,
  1), (15, 1)], [(12, 1), (14, 1)], [(3, 1), (21, -1)], [(4, 1), (20, -1)], [(5, 1), (19, 1)],
  [(6, 1), (18, 1)], [(23, -1), (26, 1)], [(22, 1), (27, 1)], [], [], [(22, -1), (27, -1)],
  [(23, -1), (26, 1)]], [[], [(2, 1), (7, -1)], [(1, -1), (8, -1)], [(4, -1), (9, -1)], [(3,
  1), (10, -1)], [(6, 1), (11, -1)], [(5, -1), (12, -1)], [(1, 1), (8, 1)], [(2, 1), (7, -1)],
  [(3, 1), (10, -1)], [(4, 1), (9, 1)], [(5, 1), (12, 1)], [(6, 1), (11, -1)], [], [(15, -1),
  (18, 1)], [(14, 1), (19, 1)], [(17, 1), (20, 1)], [(16, -1), (21, 1)], [(14, -1), (19, -1)],
  [(15, -1), (18, 1)], [(16, -1), (21, 1)], [(17, -1), (20, -1)], [], [(24, 1), (25, -1)],
  [(23, -1), (26, -1)], [(23, 1), (26, 1)], [(24, 1), (25, -1)], []], [[(2, -1), (7, 1)], [],
  [(0, 1), (13, -1)], [(5, -1), (14, -1)], [(6, -1), (15, -1)], [(3, 1), (16, -1)], [(4, 1),
  (17, -1)], [(0, -1), (13, 1)], [], [(11, -1), (18, -1)], [(12, -1), (19, -1)], [(9, 1), (20,
  -1)], [(10, 1), (21, -1)], [(2, 1), (7, -1)], [(3, 1), (16, -1)], [(4, 1), (17, -1)], [(5,
  1), (14, 1)], [(6, 1), (15, 1)], [(9, 1), (20, -1)], [(10, 1), (21, -1)], [(11, 1), (18, 1)],
  [(12, 1), (19, 1)], [(24, -1), (25, 1)], [], [(22, 1), (27, -1)], [(22, -1), (27, 1)], [],
  [(24, 1), (25, -1)]], [[(1, 1), (8, 1)], [(0, -1), (13, 1)], [], [(6, -1), (18, -1)], [(5,
  1), (19, -1)], [(4, -1), (20, -1)], [(3, 1), (21, -1)], [], [(0, -1), (13, 1)], [(12, -1),
  (14, 1)], [(11, 1), (15, 1)], [(10, -1), (16, 1)], [(9, 1), (17, 1)], [(1, -1), (8, -1)],
  [(9, -1), (17, -1)], [(10, -1), (16, 1)], [(11, -1), (15, -1)], [(12, -1), (14, 1)], [(3, 1),
  (21, -1)], [(4, 1), (20, 1)], [(5, 1), (19, -1)], [(6, 1), (18, 1)], [(23, 1), (26, 1)],
  [(22, -1), (27, 1)], [], [], [(22, -1), (27, 1)], [(23, -1), (26, -1)]], [[(0, 8), (4, 5),
  (9, -5)], [(1, 8), (5, 5), (14, -5)], [(2, 8), (6, 5), (18, -5)], [], [(0, -5), (22, 5)],
  [(1, -5), (23, 5)], [(2, -5), (24, 5)], [(7, 8), (11, 5), (15, -5)], [(8, 8), (12, 5), (19,
  -5)], [(0, 5), (22, -5)], [], [(7, -5), (25, 5)], [(8, -5), (26, 5)], [(13, 8), (17, 5), (20,
  -5)], [(1, 5), (23, -5)], [(7, 5), (25, -5)], [], [(13, -5), (27, 5)], [(2, 5), (24, -5)],
  [(8, 5), (26, -5)], [(13, 5), (27, -5)], [], [(4, -5), (9, 5), (22, -8)], [(5, -5), (14, 5),
  (23, -8)], [(6, -5), (18, 5), (24, -8)], [(11, -5), (15, 5), (25, -8)], [(12, -5), (19, 5),
  (26, -8)], [(17, -5), (20, 5), (27, -8)]]]

private def j3TLit : SpMat :=
  [[(0, 8), (4, -5), (9, 5)], [(1, 8), (5, -5), (14, 5)], [(2, 8), (6, -5), (18, 5)], [], [(0,
  5), (22, -5)], [(1, 5), (23, -5)], [(2, 5), (24, -5)], [(7, 8), (11, -5), (15, 5)], [(8, 8),
  (12, -5), (19, 5)], [(0, -5), (22, 5)], [], [(7, 5), (25, -5)], [(8, 5), (26, -5)], [(13, 8),
  (17, -5), (20, 5)], [(1, -5), (23, 5)], [(7, -5), (25, 5)], [], [(13, 5), (27, -5)], [(2,
  -5), (24, 5)], [(8, -5), (26, 5)], [(13, -5), (27, 5)], [], [(4, 5), (9, -5), (22, -8)], [(5,
  5), (14, -5), (23, -8)], [(6, 5), (18, -5), (24, -8)], [(11, 5), (15, -5), (25, -8)], [(12,
  5), (19, -5), (26, -8)], [(17, 5), (20, -5), (27, -8)]]

private def wSl2Lit : SpMat :=
  [[(0, 25), (4, 20), (9, -20), (22, 16)], [(1, 25), (5, 20), (14, -20), (23, 16)], [(2, 25),
  (6, 20), (18, -20), (24, 16)], [(3, 9)], [(0, 20), (4, 25), (9, -16), (22, 20)], [(1, 20),
  (5, 25), (14, -16), (23, 20)], [(2, 20), (6, 25), (18, -16), (24, 20)], [(7, 25), (11, 20),
  (15, -20), (25, 16)], [(8, 25), (12, 20), (19, -20), (26, 16)], [(0, -20), (4, -16), (9, 25),
  (22, -20)], [(10, 9)], [(7, 20), (11, 25), (15, -16), (25, 20)], [(8, 20), (12, 25), (19,
  -16), (26, 20)], [(13, 25), (17, 20), (20, -20), (27, 16)], [(1, -20), (5, -16), (14, 25),
  (23, -20)], [(7, -20), (11, -16), (15, 25), (25, -20)], [(16, 9)], [(13, 20), (17, 25), (20,
  -16), (27, 20)], [(2, -20), (6, -16), (18, 25), (24, -20)], [(8, -20), (12, -16), (19, 25),
  (26, -20)], [(13, -20), (17, -16), (20, 25), (27, -20)], [(21, 9)], [(0, 16), (4, 20), (9,
  -20), (22, 25)], [(1, 16), (5, 20), (14, -20), (23, 25)], [(2, 16), (6, 20), (18, -20), (24,
  25)], [(7, 16), (11, 20), (15, -20), (25, 25)], [(8, 16), (12, 20), (19, -20), (26, 25)],
  [(13, 16), (17, 20), (20, -20), (27, 25)]]

private def wQ4Lit : SpMat :=
  [[(0, 5), (1, 4), (2, -2), (7, 2), (8, 4), (13, 4)], [(0, 4), (1, 5), (2, 2), (7, -2), (8,
  -4), (13, -4)], [(0, 2), (1, -2), (2, 1), (7, 8), (8, -2), (13, -2)], [(3, 1), (4, -2), (5,
  -2), (9, -2), (10, 4), (11, 4), (14, -2), (15, 4), (16, 4)], [(3, 2), (4, 1), (6, -2), (9,
  -4), (10, -2), (12, 4), (14, -4), (15, -2), (17, 4)], [(3, 2), (5, 1), (6, 2), (9, -4), (11,
  -2), (12, -4), (14, -4), (16, -2), (17, -4)], [(4, 2), (5, -2), (6, 1), (10, -4), (11, 4),
  (12, -2), (15, -4), (16, 4), (17, -2)], [(0, -2), (1, 2), (2, 8), (7, 1), (8, 2), (13, 2)],
  [(0, 4), (1, -4), (2, 2), (7, -2), (8, 5), (13, -4)], [(3, 2), (4, -4), (5, -4), (9, 1), (10,
  -2), (11, -2), (18, -2), (19, 4), (20, 4)], [(3, 4), (4, 2), (6, -4), (9, 2), (10, 1), (12,
  -2), (18, -4), (19, -2), (21, 4)], [(3, 4), (5, 2), (6, 4), (9, 2), (11, 1), (12, 2), (18,
  -4), (20, -2), (21, -4)], [(4, 4), (5, -4), (6, 2), (10, 2), (11, -2), (12, 1), (19, -4),
  (20, 4), (21, -2)], [(0, 4), (1, -4), (2, 2), (7, -2), (8, -4), (13, 5)], [(3, 2), (4, -4),
  (5, -4), (14, 1), (15, -2), (16, -2), (18, 2), (19, -4), (20, -4)], [(3, 4), (4, 2), (6, -4),
  (14, 2), (15, 1), (17, -2), (18, 4), (19, 2), (21, -4)], [(3, 4), (5, 2), (6, 4), (14, 2),
  (16, 1), (17, 2), (18, 4), (20, 2), (21, 4)], [(4, 4), (5, -4), (6, 2), (15, 2), (16, -2),
  (17, 1), (19, 4), (20, -4), (21, 2)], [(9, 2), (10, -4), (11, -4), (14, -2), (15, 4), (16,
  4), (18, 1), (19, -2), (20, -2)], [(9, 4), (10, 2), (12, -4), (14, -4), (15, -2), (17, 4),
  (18, 2), (19, 1), (21, -2)], [(9, 4), (11, 2), (12, 4), (14, -4), (16, -2), (17, -4), (18,
  2), (20, 1), (21, 2)], [(10, 4), (11, -4), (12, 2), (15, -4), (16, 4), (17, -2), (19, 2),
  (20, -2), (21, 1)], [(22, 5), (23, 4), (24, -2), (25, 2), (26, 4), (27, 4)], [(22, 4), (23,
  5), (24, 2), (25, -2), (26, -4), (27, -4)], [(22, 2), (23, -2), (24, 1), (25, 8), (26, -2),
  (27, -2)], [(22, -2), (23, 2), (24, 8), (25, 1), (26, 2), (27, 2)], [(22, 4), (23, -4), (24,
  2), (25, -2), (26, 5), (27, -4)], [(22, 4), (23, -4), (24, 2), (25, -2), (26, -4), (27, 5)]]

private def wQ4TLit : SpMat :=
  [[(0, 5), (1, 4), (2, 2), (7, -2), (8, 4), (13, 4)], [(0, 4), (1, 5), (2, -2), (7, 2), (8,
  -4), (13, -4)], [(0, -2), (1, 2), (2, 1), (7, 8), (8, 2), (13, 2)], [(3, 1), (4, 2), (5, 2),
  (9, 2), (10, 4), (11, 4), (14, 2), (15, 4), (16, 4)], [(3, -2), (4, 1), (6, 2), (9, -4), (10,
  2), (12, 4), (14, -4), (15, 2), (17, 4)], [(3, -2), (5, 1), (6, -2), (9, -4), (11, 2), (12,
  -4), (14, -4), (16, 2), (17, -4)], [(4, -2), (5, 2), (6, 1), (10, -4), (11, 4), (12, 2), (15,
  -4), (16, 4), (17, 2)], [(0, 2), (1, -2), (2, 8), (7, 1), (8, -2), (13, -2)], [(0, 4), (1,
  -4), (2, -2), (7, 2), (8, 5), (13, -4)], [(3, -2), (4, -4), (5, -4), (9, 1), (10, 2), (11,
  2), (18, 2), (19, 4), (20, 4)], [(3, 4), (4, -2), (6, -4), (9, -2), (10, 1), (12, 2), (18,
  -4), (19, 2), (21, 4)], [(3, 4), (5, -2), (6, 4), (9, -2), (11, 1), (12, -2), (18, -4), (20,
  2), (21, -4)], [(4, 4), (5, -4), (6, -2), (10, -2), (11, 2), (12, 1), (19, -4), (20, 4), (21,
  2)], [(0, 4), (1, -4), (2, -2), (7, 2), (8, -4), (13, 5)], [(3, -2), (4, -4), (5, -4), (14,
  1), (15, 2), (16, 2), (18, -2), (19, -4), (20, -4)], [(3, 4), (4, -2), (6, -4), (14, -2),
  (15, 1), (17, 2), (18, 4), (19, -2), (21, -4)], [(3, 4), (5, -2), (6, 4), (14, -2), (16, 1),
  (17, -2), (18, 4), (20, -2), (21, 4)], [(4, 4), (5, -4), (6, -2), (15, -2), (16, 2), (17, 1),
  (19, 4), (20, -4), (21, -2)], [(9, -2), (10, -4), (11, -4), (14, 2), (15, 4), (16, 4), (18,
  1), (19, 2), (20, 2)], [(9, 4), (10, -2), (12, -4), (14, -4), (15, 2), (17, 4), (18, -2),
  (19, 1), (21, 2)], [(9, 4), (11, -2), (12, 4), (14, -4), (16, 2), (17, -4), (18, -2), (20,
  1), (21, -2)], [(10, 4), (11, -4), (12, -2), (15, -4), (16, 4), (17, 2), (19, -2), (20, 2),
  (21, 1)], [(22, 5), (23, 4), (24, 2), (25, -2), (26, 4), (27, 4)], [(22, 4), (23, 5), (24,
  -2), (25, 2), (26, -4), (27, -4)], [(22, -2), (23, 2), (24, 1), (25, 8), (26, 2), (27, 2)],
  [(22, 2), (23, -2), (24, 8), (25, 1), (26, -2), (27, -2)], [(22, 4), (23, -4), (24, -2), (25,
  2), (26, 5), (27, -4)], [(22, 4), (23, -4), (24, -2), (25, 2), (26, -4), (27, 5)]]
-- ---------------------------------------------------------------------------
-- Theorem 2: Exact 21,952-Entry Small-Diagonal-to-Divisor Identity on A^3
-- ---------------------------------------------------------------------------

private def checkA3DivisorIdentity : Bool :=
  let (e2Map, e2MapOk) := extractDiag1Map matE2_28
  let litsOk :=
    e2MapOk && spVecEq e2Map e2MapLit &&
    spTenEq dCycLit buildDCycTen &&
    spTenEq tCupLit buildTCupTen &&
    spTenEq tCupUpLit (spTenApplyPerm3 e2MapLit tCupLit)
  let s3Ok :=
    spTenEq tCupUpLit (spTenSwap12 tCupUpLit) && spTenEq tCupUpLit (spTenSwap23 tCupUpLit) &&
    spTenEq dCycLit (spTenSwap12 dCycLit) && spTenEq dCycLit (spTenSwap23 dCycLit)
  let th := thVec28
  let trTtt := th.foldl (fun tr0 (i, vi) =>
    th.foldl (fun tr1 (j, vj) =>
      th.foldl (fun tr2 (k, vk) =>
        intTrieAdd 15 (tenCode i j k) (vi * vj * vk) tr2) tr1) tr0) .empty
  let vTtt := intTrieToSpTen trTtt
  let e2Entries : List (Nat × Nat × Int) :=
    (rangeList 0 28).foldl (fun acc j =>
      let (k, s) := (e2MapLit.drop j).headD (0, 0)
      acc ++ [(j, k, (-2) * s)]) []
  let tr1Dd := th.foldl (fun tr0 (i, vi) =>
    e2Entries.foldl (fun tr1 (j, k, ev) =>
      intTrieAdd 15 (tenCode i j k) (vi * ev) tr1) tr0) .empty
  let v1Dd := intTrieToSpTen tr1Dd
  let v2Dd := spTenSwap12 v1Dd
  let v3Dd := spTenSwap23 v2Dd
  let sumDd := spTenAdd v1Dd (spTenAdd v2Dd v3Dd)
  let rhs := spTenAdd vTtt (spTenAdd (spTenScale 2 sumDd) (spTenScale 8 dCycLit))
  let idOk := spTenEq (spTenScale 8 tCupUpLit) rhs
  litsOk && s3Ok && idOk

set_option maxHeartbeats 16000000 in
set_option maxRecDepth 8192 in
/-- Certifies total `S_3` symmetry of `T_cup_up` and `D_cyc = D_12 ^ D_23 ^ D_13` alongside the
exact `21,952`-entry (`28^3`) small-diagonal-to-divisor identity
`8 T_cup_up = v_ttt + 2 (v_1dd + v_2dd + v_3dd) + 8 D_cyc`. -/
theorem mumford_a3_small_diagonal_divisor_identity_cert :
    checkA3DivisorIdentity = true :=
  rfl

-- ---------------------------------------------------------------------------
-- Theorem 3: Casimir Polynomials, 64-Sector Probe & Closure Diamond
-- ---------------------------------------------------------------------------

private def spColOf (m : SpMat) (col : Nat) : SpVec :=
  (rangeList 0 m.length).foldl (fun acc r =>
    let v := spVecLookup col ((m.drop r).headD [])
    if intEq v 0 then acc else acc ++ [(r, v)]) []

private def sliceFrom28 (v : SpVec) (sl : List SpMat) : SpMat :=
  v.foldl (fun acc (i, c) =>
    spMatAdd acc (spMatScale c ((sl.drop i).headD []))) (List.replicate 28 [])

private def intVecEq : List Int → List Int → Bool
  | [], [] => true
  | [], _ :: _ => false
  | _ :: _, [] => false
  | x :: xs, y :: ys => intEq x y && intVecEq xs ys

private def intVecDot (u v : List Int) : Int :=
  (List.zipWith (· * ·) u v).foldl (· + ·) 0

private def isOrthBasis19 (bs : List (List Int)) : Bool :=
  (rangeList 0 bs.length).all fun i =>
    (rangeList (i + 1) (bs.length - i - 1)).all fun j =>
      intEq (intVecDot ((bs.drop i).headD []) ((bs.drop j).headD [])) 0

private def inSpanOrthBasis (bs : List (List Int)) (u : List Int) : Bool :=
  let recon := bs.foldl (fun acc b =>
    let d := intVecDot b b
    let c := intVecDot u b
    if intEq d 0 || !(intEq (c % d) 0) then acc
    else List.zipWith (fun a bi => a + (c / d) * bi) acc b) (List.replicate 19 0)
  intVecEq recon u

private def checkProbeAnd19DimClosure : Bool :=
  let (q0, qSd, qAsd, qRic) := casimirProjs4
  let litsOk :=
    spMatEq q0 q0Lit && spMatEq qSd qSdLit &&
    spMatEq qAsd qAsdLit && spMatEq qRic qRicLit &&
    spMatListEq dCycSlLit (spTenToSlices28 dCycLit)
  let i28 := spEye 28
  let tTh := spMatScale 24 q0Lit
  let tDd := spMatSub (spMatScale 4 i28) (spMatScale 4 q0Lit)
  let tCh := spMatScale (-2) (spMatSub qSdLit qAsdLit)
  let tChSq := spMatMul tCh tCh
  let polyOk :=
    spMatEq (spMatScale 24 q0Lit) tTh &&
    spMatEq (spMatScale 32 qSdLit) (spMatSub tChSq (spMatScale 8 tCh)) &&
    spMatEq (spMatScale 32 qAsdLit) (spMatAdd tChSq (spMatScale 8 tCh)) &&
    spMatEq (spMatScale 16 qRicLit)
      (spMatSub (spMatAdd (spMatScale 16 tDd) (spMatScale 2 tTh)) tChSq)
  let qs := [q0Lit, qSdLit, qAsdLit, qRicLit]
  let probes := [spColOf q0Lit 3, spColOf qSdLit 0, spColOf qAsdLit 0, spColOf qRicLit 4]
  let mats := probes.map fun v =>
    let mv := sliceFrom28 v dCycSlLit
    qs.map fun qb => qs.map fun qc => spMatFrob2 (spMatMul qb (spMatMul mv qc))
  let expFrob : List (List (List Int)) :=
    [[[1024, 0, 0, 0], [0, 9216, 0, 0], [0, 0, 9216, 0], [0, 0, 0, 9216]],
     [[0, 2048, 0, 0], [2048, 8192, 0, 0], [0, 0, 0, 6144], [0, 0, 6144, 0]],
     [[0, 0, 2048, 0], [0, 0, 0, 6144], [2048, 0, 8192, 0], [0, 6144, 0, 0]],
     [[0, 0, 0, 2048], [0, 0, 6144, 0], [0, 6144, 0, 0], [2048, 0, 0, 8192]]]
  let probeOk := (List.zipWith (fun m1 m2 =>
    (List.zipWith (fun r1 r2 => intVecEq r1 r2) m1 m2).all id) mats expFrob).all id
  let eUnit (k : Nat) : List Int := (rangeList 0 19).map fun j => if j == k then 1 else 0
  let indList (idxs : List Nat) : List Int :=
    (rangeList 0 19).map fun j => if idxs.contains j then 1 else 0
  let st0 : List (List Int) :=
    [eUnit 0, indList [1, 2, 3], indList [4, 5, 6], indList [7, 8, 9],
     indList [10, 11, 12, 13, 14, 15, 16, 17, 18]]
  let st12Inter : List (List Int) :=
    [eUnit 0, indList [1, 2], eUnit 3, indList [4, 5], eUnit 6, indList [7, 8], eUnit 9,
     indList [10, 11, 12, 13, 14, 15, 16, 17, 18]]
  let st1 : List (List Int) :=
    (rangeList 0 10).map eUnit ++ [indList [10, 11, 12, 13, 14, 15, 16, 17, 18]]
  let st2 : List (List Int) :=
    [eUnit 0, indList [1, 2], eUnit 3, indList [4, 5], eUnit 6, indList [7, 8], eUnit 9,
     indList [10, 11], eUnit 12, indList [13, 15], indList [14, 16], indList [17, 18]]
  let st12Join : List (List Int) :=
    (rangeList 0 10).map eUnit ++
    [indList [10, 11], eUnit 12, indList [13, 15], indList [14, 16], indList [17, 18]]
  let st3 : List (List Int) := (rangeList 0 19).map eUnit
  let oddPairs : List (Nat × Nat) :=
    [(1, 2), (4, 5), (7, 8), (10, 11), (13, 15), (14, 16), (17, 18)]
  let odd7 := oddPairs.map fun (a, b) => List.zipWith (· - ·) (eUnit a) (eUnit b)
  let odd4Triple := (oddPairs.drop 3).map fun (a, b) => List.zipWith (· - ·) (eUnit a) (eUnit b)
  let bases := [st0, st12Inter, st1, st2, st12Join, st3]
  let lensOk :=
    (st0.length == 5) && (st12Inter.length == 8) && (st1.length == 11) &&
    (st2.length == 12) && (st12Join.length == 15) && (st3.length == 19)
  let orthOk :=
    bases.all isOrthBasis19 && lensOk &&
    st0.all (inSpanOrthBasis st12Inter) &&
    st12Inter.all (inSpanOrthBasis st1) && st12Inter.all (inSpanOrthBasis st2) &&
    st1.all (inSpanOrthBasis st12Join) && st2.all (inSpanOrthBasis st12Join) &&
    st12Join.all (inSpanOrthBasis st3) &&
    odd7.all (fun ov => st2.all fun ev => intEq (intVecDot ov ev) 0) &&
    odd4Triple.all (fun ov => st12Join.all fun jv => intEq (intVecDot ov jv) 0)
  litsOk && polyOk && probeOk && orthOk

set_option maxHeartbeats 16000000 in
set_option maxRecDepth 8192 in
/-- Certifies Casimir reconstruction inside `Q[T_th, T_dd, T_ch]`, the `4`-probe matrix slice
decomposition (`19` nonzero sectors + `45` strict zeros), and the exact closure diamond
`5 -> 8 -> {11, 12} -> 15 -> 19` (`odd7 _|_ A_even^3` and `odd4_triple _|_ join`). -/
theorem mumford_a3_64_sector_probe_and_19_dim_closure_cert :
    checkProbeAnd19DimClosure = true :=
  rfl

-- ---------------------------------------------------------------------------
-- Theorem 4: Hodge (3,3) Derivation Vanishing, Factored Boost 81^3 & Parity
-- ---------------------------------------------------------------------------

private def refl4 : List (List Int) :=
  kronMat (intEye 2) [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, -1]]

private def jMum3Mat : List (List Int) :=
  kronMat [[4, 5], [-5, -4]] (intEye 4)

private def gSl2_3Mat : List (List Int) :=
  kronMat [[5, 4], [4, 5]] (intEye 4)

private def q4_3Mat : List (List Int) :=
  kronMat (intEye 2) [[1, -2, -2, 0], [2, 1, 0, -2], [2, 0, 1, 2], [0, 2, -2, 1]]

private def gMum9Mat : List (List Int) :=
  kronMat [[5, 4], [4, 5]]
    [[1, -2, -2, 0], [2, 1, 0, -2], [2, 0, 1, 2], [0, 2, -2, 1]]

private def checkDerivAll28 (d dT : SpMat) (sl : List SpMat) : Bool :=
  (rangeList 0 28).all fun i =>
    let leg1 := ((d.drop i).headD []).foldl (fun acc (a, dia) =>
      spMatAdd acc (spMatScale dia ((sl.drop a).headD []))) (List.replicate 28 [])
    let si := (sl.drop i).headD []
    let tot := spMatAdd leg1 (spMatAdd (spMatMul d si) (spMatMul si dT))
    tot.all List.isEmpty

private def checkBoostAll28 (w wT : SpMat) (sc : Int) (sl : List SpMat) : Bool :=
  (rangeList 0 28).all fun i =>
    let comb := ((w.drop i).headD []).foldl (fun acc (a, wia) =>
      spMatAdd acc (spMatScale wia ((sl.drop a).headD []))) (List.replicate 28 [])
    let lhs := spMatMul w (spMatMul comb wT)
    let rhs := spMatScale sc ((sl.drop i).headD [])
    spMatEq lhs rhs

private def checkHodge33ModuliAndParity : Bool :=
  let genExt10 := (allGens9 ++ [jMum3Mat]).map ext2Sp
  let wSl2 := wedge2GroupSp gSl2_3Mat
  let wQ4 := wedge2GroupSp q4_3Mat
  let wG9 := wedge2GroupSp gMum9Mat
  let d10Ok :=
    spMatListEq d10Lit genExt10 &&
    spMatEq j3TLit (spMatTranspose 28 ((d10Lit.drop 9).headD [])) &&
    spMatEq wSl2Lit wSl2 &&
    spMatEq wQ4Lit wQ4 &&
    spMatEq wQ4TLit (spMatTranspose 28 wQ4Lit) &&
    spMatEq wSl2Lit (spMatTranspose 28 wSl2Lit) &&
    spMatEq wG9 (spMatMul wSl2Lit wQ4Lit) &&
    spMatListEq dCycSlLit (spTenToSlices28 dCycLit)
  let d0 := d10Lit.headD []
  let d1 := (d10Lit.drop 1).headD []
  let d2 := (d10Lit.drop 2).headD []
  let d3 := (d10Lit.drop 3).headD []
  let d4 := (d10Lit.drop 4).headD []
  let d5 := (d10Lit.drop 5).headD []
  let d6 := (d10Lit.drop 6).headD []
  let d7 := (d10Lit.drop 7).headD []
  let d8 := (d10Lit.drop 8).headD []
  let dTs : List SpMat :=
    [d0, d2, d1, spMatScale (-1) d3, spMatScale (-1) d4, spMatScale (-1) d5,
     spMatScale (-1) d6, spMatScale (-1) d7, spMatScale (-1) d8, j3TLit]
  let tMatchOk := (List.zipWith (fun d dT => spMatEq dT (spMatTranspose 28 d)) d10Lit dTs).all id
  let derivsOk := (List.zipWith (fun d dT => checkDerivAll28 d dT dCycSlLit) d10Lit dTs).all id
  let boostOk :=
    checkBoostAll28 wSl2Lit wSl2Lit 729 dCycSlLit &&
    checkBoostAll28 wQ4Lit wQ4TLit 729 dCycSlLit
  let pFlip := wedge2GroupSp refl4
  let (flipMap, flipDiagOk) := extractDiag1Map pFlip
  let flipFixes := spTenEq (spTenApplyPerm3 flipMap dCycLit) dCycLit
  let irrepList := [0, 1, 2, 3]
  let sw (a : Nat) : Nat := if a == 1 then 2 else if a == 2 then 1 else a
  let isAllowed (a b c : Nat) : Bool :=
    (a == 0 && b == 0 && c == 0) ||
    (a == 0 && b == c && !(b == 0)) || (b == 0 && a == c && !(a == 0)) ||
    (c == 0 && a == b && !(a == 0)) ||
    (a == b && b == c && !(a == 0)) ||
    (!(a == 0) && !(b == 0) && !(c == 0) && !(a == b) && !(a == c) && !(b == c))
  let counts := irrepList.foldl (fun (f, s) a =>
    irrepList.foldl (fun (f2, s2) b =>
      irrepList.foldl (fun (f3, s3) c =>
        if isAllowed a b c then
          if sw a == a && sw b == b && sw c == c then (f3 + 1, s3) else (f3, s3 + 1)
        else (f3, s3)) (f2, s2)) (f, s)) (0, 0)
  let parityCountOk := (counts.1 == 5) && (counts.2 == 14) && (counts.1 + counts.2 / 2 == 12)
  d10Ok && tMatchOk && derivsOk && boostOk && flipDiagOk && flipFixes && parityCountOk

set_option maxHeartbeats 16000000 in
set_option maxRecDepth 8192 in
/-- Certifies exhaustively across all `21,952` entries of `D_cyc`: all `9` generators of
`sl_2(R) (+) so(4)` and `D^(2)(J_Mum3)` annihilate `D_cyc` (Hodge `(3,3)` condition), factored
boost `/\^2(G_Mum9) = W_sl2 W_q4` yields `729 * 729 = 81^3 = 531,441`, `P_flip^3 D_cyc = D_cyc`,
and `19 = 12_+ + 7_-`. -/
theorem mumford_a3_hodge33_moduli_and_parity_12_7_cert :
    checkHodge33ModuliAndParity = true :=
  rfl

#print axioms mumford_h4_70dim_invariant_uniqueness_cert
#print axioms mumford_a3_small_diagonal_divisor_identity_cert
#print axioms mumford_a3_64_sector_probe_and_19_dim_closure_cert
#print axioms mumford_a3_hodge33_moduli_and_parity_12_7_cert
