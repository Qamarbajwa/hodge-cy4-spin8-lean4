# Upstream PR Guide: Shioda's Fermat Hodge Conjecture (`google-deepmind/formal-conjectures`)

This guide prepares the formal pull request submitting `ShiodaFermatHodgeConjecture.lean` to the upstream repository [`google-deepmind/formal-conjectures`](https://github.com/google-deepmind/formal-conjectures).

---

## 1. Pull Request Title & Overview

- **PR Title:** `feat(algebraic-geometry): Formalize Shioda's Fermat Hodge Conjecture and Aoki Inductive Spanning`
- **Topic:** Algebraic Geometry / Hodge Theory (AMS Subject Classification: `14C30`, `14J70`)
- **Target File:** `FormalConjectures/AlgebraicGeometry/ShiodaFermatHodgeConjecture.lean`
- **Authors:** Qamar Munawer (Brandenburg University of Technology Cottbus–Senftenberg)

---

## 2. Prior-Art Justification

According to our exhaustive live repository audit (recorded in [`prior_art_audit_receipt.json`](../../prior_art_audit_receipt.json)):
- `leanprover-community/mathlib4`: **0** hits for `Shioda`, `fermatHypersurface`, or `hodgeCharacter`.
- `google-deepmind/formal-conjectures`: **0** hits for Shioda Fermat character theory or algebraic cycle criteria on hypersurfaces.
- `ImperialCollegeLondon/FLT`: **0** hits for higher-dimensional Fermat varieties.

This upstream submission fills a major foundational gap in formal algebraic geometry by encoding:
1. The exact character-theoretic formulation of Hodge classes on Fermat varieties via Shioda's Galois norm condition ($\sum \langle t \alpha_j / m \rangle = (n+2)/2$).
2. Aoki's inductive spanning predicates (pair-matching and triple-sum sub-Fermat joins).
3. The paired-diagonal character orbit condition isolating non-inductive algebraic classes.
4. Three classically solved theorems ($n=4, 3 \le m \le 10$; $n=4, m=6$; $n=4, m=12$) and the general open conjecture.

---

## 3. Mapping: Standalone Zero-Mathlib Kernel Proofs vs. Upstream Mathlib4 Form

| Concept | Standalone Zero-Mathlib Implementation (`ShiodaFormalConjectures.lean`) | Upstream `formal-conjectures` File (`ShiodaFermatHodgeConjecture.lean`) |
| :--- | :--- | :--- |
| **Character Representation** | `List Nat` (6-tuples) with entries in $\{1, \dots, m-1\}$ | `FermatCharacter (n m : ℕ) := { α : Fin (n+2) → ZMod m // ... }` |
| **Shioda Galois Norm** | `satisfiesGaloisNormTuple (m : Nat) : Bool` | `IsShiodaHodgeCharacter (hn : Even n) (α : FermatCharacter n m) : Prop` |
| **Band 1 (Pair Match)** | `hasPairMatchTuple (m : Nat) : Bool` | `HasPairMatch (α : FermatCharacter n m) : Prop` |
| **Band 2 (Triple Sum)** | `triples.any (fun s => s % m == 0)` | `HasTripleSum (α : FermatCharacter n m) : Prop` |
| **Inductive Band 1--3** | `hasPairMatchTuple \|\| hasTripleSum` | `IsInductiveFermatCharacter α := HasPairMatch α ∨ HasTripleSum α` |
| **Paired Diagonals** | `m12PairedReps : List (Nat × ...)` | `IsPairedDiagonalCharacter α : Prop` |
| **$n=4, 3 \le m \le 10$** | Generative kernel evaluation `by rfl` (Check 46) | `@[category research solved, AMS 14] theorem shioda_fermat_fourfold_m3_to_m10_all_inductive` |
| **$n=4, m=6$ (1,751)** | `1001 + 630 + 120 + 0 = 1751` (`by rfl`) | `@[category research solved, AMS 14] theorem shioda_fermat_n4_m6_primitive_hodge_algebraic` |
| **$n=4, m=12$ (360)** | `m12PairedReps.length * 90 = 360` (`by rfl`) | `@[category research solved, AMS 14] theorem shioda_aoki_n4_m12_paired_diagonal_algebraic` |
| **Open Frontier** | Epistemic boundary `GLOBAL_HODGE_CONJECTURE = OPEN` | `@[category research open, AMS 14] conjecture shioda_general_fermat_hodge_conjecture` |

---

## 4. Submission Checklist

- [x] File placed in standalone directory (`docs/upstream_formal_conjectures/`) outside local Lake workspace to maintain zero-Mathlib purity.
- [x] Conforms to `google-deepmind/formal-conjectures` tag syntax (`@[category research solved, AMS 14]` and `@[category research open, AMS 14]`).
- [x] Citations included to Shioda (Math. Ann. 1979) and Aoki (Comment. Math. Univ. St. Pauli 1983).
- [x] Explicitly separates proven theorems on Fermat varieties from the global open Hodge conjecture.
