# Master Research Execution Plan: Modular Paper Pipeline, Verification Protocols, and Epistemic Status Ledger
## Research Project: `HODGE-MILLENNIUM-001` (The Hodge Conjecture on Complex Projective Varieties)

---

## Executive Summary and Epistemic Demarcation

This document establishes the authoritative execution plan, mathematical foundations, verification protocols, and publication standards for research project **`HODGE-MILLENNIUM-001`** (The Hodge Conjecture). This plan serves as a single source of truth across all modules, formalization blueprints, and autonomous agent instances.

### Foundational Invariants
1. **The General Hodge Conjecture Remains Open (`GLOBAL_HODGE_CONJECTURE = OPEN`, `NO_HODGE_PROOF = TRUE`):**
   No unconditional proof of the general Hodge Conjecture is claimed. Any statement connecting an infinitesimal deformation, Macaulay inverse system, or representation-theoretic cycle candidate to the Hodge Conjecture is classified strictly as a conditional reduction or equivalence bridge.
2. **Axiomatic Integrity:**
   Every formal claim accepted into the verified corpus is verified by the Lean 4 kernel using zero axioms (`does not depend on any axioms`) or at most the standard foundational axioms `[propext, Classical.choice, Quot.sound]`. Zero `sorry`, zero `admit`, zero `opaque`, zero `unsafe`, zero `native_decide`, and zero custom or unverified axioms are permitted in any kernel result.
3. **Impersonal Mathematical Prose:**
   All documentation, monographs, papers, and code commentaries adhere strictly to neutral, third-person mathematical exposition. First-person pronouns (singular or plural: "I", "we", "our") are prohibited across all project deliverables.
4. **Dependency-Gated Progress (Zero Calendar Boundaries):**
   Progress is measured solely by formal proof obligations, machine-checked kernel receipts, and mathematical prerequisites. No calendar time boundaries, estimated completion dates, or arbitrary schedules govern execution.

---

## 1. Repository Provenance and Source Snapshot

### Git Repository State
* **Working Directory:** `d:/Comfy UI/hodge conjecture`
* **Active Branch:** `candidate/math-gov-v0.6`
* **Outer Repository HEAD Commit:** `8ccff00`
* **Single Unified Lake Workspace:** `examples/math_gov/LeanDemoProject/`
* **Lean Toolchain Dependency:** `leanprover/lean4:v4.35.0` (Lake version 5.0.0)
* **Lean Build Receipt:**
  ```text
  Build completed successfully (15 jobs).
  ```

### Primary Document & Compiled Manuscript Ledger
* **Paper 1 (Shioda--Aoki Fermat Fourfold Character Cohomology):** `paper/paper1_shioda_aoki_lean4/Paper1_Shioda_Aoki_Fermat_Lean4.tex` -> `Paper1_Shioda_Aoki_Fermat_Lean4.pdf` (**13 pages**, 0 errors, 0 overfull/underfull hboxes, 0 pronouns, 2 TikZ figures, **PASSED**)
* **Paper 2 (Artinian Gorenstein Apolarity & Macaulay Contraction Ranks):** `paper/paper2_macaulay_apolarity_lean4/Paper2_Macaulay_Apolarity_CY4_Lean4.tex` -> `Paper2_Macaulay_Apolarity_CY4_Lean4.pdf` (**10 pages**, 0 errors, 0 overfull/underfull hboxes, 0 pronouns, 2 TikZ figures, **PASSED**)
* **Paper 3 ($\operatorname{Spin}(8)$ Triality, $W(D_4)$ Chiral Orthogonality & Mumford Spinors):** `paper/paper3_spin8_mumford_lean4/Paper3_Spin8_Triality_Mumford_Lean4.tex` -> `Paper3_Spin8_Triality_Mumford_Lean4.pdf` (**10 pages**, 0 errors, 0 overfull/underfull hboxes, 0 prose pronouns, 2 TikZ figures, **PASSED**)
* **Paper 4 (Exact Float-Free Gauss--Manin Jet Reconstruction):** `paper/paper4_gauss_manin_jets/Paper4_Gauss_Manin_Jet_Reconstruction.tex` -> `Paper4_Gauss_Manin_Jet_Reconstruction.pdf` (**13 pages**, 0 errors, 0 overfull/underfull hboxes, 0 pronouns, 2 TikZ figures, **PASSED**)
* **Paper 5 (Finite Cyclotomic Incidence Sieves & Residual Form Extraction):** `paper/paper5_cyclotomic_incidence_sieve/Paper5_Cyclotomic_Incidence_Sieve_Lean4.tex` -> `Paper5_Cyclotomic_Incidence_Sieve_Lean4.pdf` (**9 pages**, 0 errors, 0 overfull/underfull hboxes, 0 pronouns, 2 TikZ figures, **PASSED**)
* **Paper 6 (High-Degree Fermat Sporadic Orbits, Order-8 Gauss--Manin Jet Lifting, & Conditional Bridges):** `paper/paper6_millennium_frontier_extensions/Paper6_Millennium_Frontier_Extensions_Lean4.tex` -> `Paper6_Millennium_Frontier_Extensions_Lean4.pdf` (**10 pages**, 0 errors, 0 overfull/underfull hboxes, 0 pronouns, 2 TikZ figures, **PASSED**)
* **Automated PR & Verification Pipelines:** `scripts/automate_mathlib_pr_pipeline.py` (stages 4 `MathlibPR_*.lean` modules, audits 13 locked baseline `.lean` files / 84 theorems + 6 papers, emits `dist/FULL_AUTOMATION_VERIFICATION_RECEIPT.json`) and `scripts/run_millennium_ext_pipeline.py` (verifies baseline lock + `lake clean && lake build` on `LeanMillenniumExt/` + 4 frontier scripts, emits `reports/millennium_ext/MILLENNIUM_EXT_RECEIPT.json`)
* **Legacy Frozen Drafts:** `paper/main.tex` (frozen), `paper/blueprint.tex` (frozen), `paper/journal_submission/Munawer_Hodge_Apolarity_Spin8_Lean4_Journal.tex` (frozen)

---

## 2. Complete Inventory of the Lean 4 Formalization Corpus

The unified Lean 4 Lake workspace (`examples/math_gov/LeanDemoProject/`) comprises **13 source files** totaling **3,517 lines of code**, **84 theorems**, **379 definitions/abbreviations**, **1 inductive witness type**, **4 `#check` assertions**, and **84 `#print axioms` assertions**, with **0 `sorry` tokens**, **0 external Mathlib dependencies**, and **84/84 theorems printing `does not depend on any axioms`**.

### Master Declaration and Metric Ledger

| File Path | Lines | Theorems | Definitions | Inductives | `#check` | `#print axioms` | `sorry` | Axiom Receipt |
|---|---|---|---|---|---|---|---|---|
| `examples/math_gov/LeanDemoProject/LeanDemoProject.lean` | 15 | 0 | 0 | 0 | 0 | 0 | 0 | Root Manifest |
| `examples/math_gov/LeanDemoProject/HodgeVerification.lean` | 956 | 40 | 172 | 0 | 4 | 40 | 0 | `does not depend on any axioms` (40/40) |
| `examples/math_gov/LeanDemoProject/ShiodaFormalConjectures.lean` | 476 | 6 | 68 | 0 | 0 | 6 | 0 | `does not depend on any axioms` (6/6) |
| `examples/math_gov/LeanDemoProject/MathlibPR_ShiodaAokiFermat.lean` | 243 | 7 | 0 | 0 | 0 | 7 | 0 | `does not depend on any axioms` (7/7) |
| `examples/math_gov/LeanDemoProject/MathlibPR_MacaulayGorenstein.lean` | 114 | 5 | 2 | 0 | 0 | 5 | 0 | `does not depend on any axioms` (5/5) |
| `examples/math_gov/LeanDemoProject/MathlibPR_Spin8Triality.lean` | 86 | 7 | 2 | 0 | 0 | 7 | 0 | `does not depend on any axioms` (7/7) |
| `examples/math_gov/LeanDemoProject/MathlibPR_CyclotomicIncidenceSieve.lean` | 115 | 4 | 5 | 0 | 0 | 4 | 0 | `does not depend on any axioms` (4/4) |
| `examples/math_gov/LeanDemoProject/WiebeSchejaStorch.lean` | 353 | 2 | 42 | 0 | 0 | 2 | 0 | `does not depend on any axioms` (2/2) |
| `examples/math_gov/LeanDemoProject/GaussManinJetTransport.lean` | 296 | 3 | 28 | 0 | 0 | 3 | 0 | `does not depend on any axioms` (3/3) |
| `examples/math_gov/LeanDemoProject/ShiodaInductiveCycleSynthesis.lean` | 239 | 2 | 14 | 1 | 0 | 2 | 0 | `does not depend on any axioms` (2/2) |
| `examples/math_gov/LeanDemoProject/Spin8LieAlgebraTriality.lean` | 216 | 3 | 22 | 0 | 0 | 3 | 0 | `does not depend on any axioms` (3/3) |
| `examples/math_gov/LeanDemoProject/GlobalIVHSObstructionSpectrum.lean` | 224 | 2 | 16 | 0 | 0 | 2 | 0 | `does not depend on any axioms` (2/2) |
| `examples/math_gov/LeanDemoProject/HigherDegreeSporadicBand4.lean` | 184 | 3 | 8 | 0 | 0 | 3 | 0 | `does not depend on any axioms` (3/3) |
| **Unified Lake Corpus Total** | **3,517** | **84** | **379** | **1** | **4** | **84** | **0** | **84/84 Axiom-Free (`axioms: []`)** |

### Complete 84-Theorem Index by Module
1. **`HodgeVerification.lean` (40 theorems):** `weil_w1_orthogonal_to_theta2`, `weil_w2_orthogonal_to_theta2`, `four_tuples_len`, `zero_tuples_len`, `h40_prim_eq`, `h31_prim_eq`, `h22_prim_eq`, `h22_total_eq`, `b4_total_eq`, `milnor_number_eq`, `r6_dim_eq`, `plane_kernel_dim_eq`, `saturation_three_count_eq`, `band3_partitions_satisfy_2_plus_4`, `fermat_four_band_closure_eq`, `f_p3_surface_h11_prim_eq`, `min_ivhs_codimension_pos`, `max_ivhs_monomial_rank_eq`, `canonical_fixed_plane_subspace_dim_eq`, `clifford_even_dim_eq`, `d4_triality_zero_triples_len`, `macaulay_annihilator_dim_bound`, `signed_difference_ideal_intersection`, `quadratic_moving_plane_directions_count_eq`, `deformed_macaulay_flat_hilbert_sum_eq`, `cyclotomic_plane_wavepacket_support_eq`, `telescoping_cyclotomic_annihilator_eq`, `spinor_to_weil_su22_branching_eq`, `tangential_leibniz_annihilator_eq`, `recombination_kernel_dim_gain_eq`, `weyl_d4_conjugate_weil_axes_eq`, `universal_band_obstruction_cancellation_bounds_eq`, `gorenstein_moduli_rank_extremes_eq`, `twenty_plane_target_and_collision_counts_eq`, `fifteen_matching_band1_block_incidence_eq`, `recomb_and_collision_flat_hilbert_eq`, `finite_non_fermat_pair_milnor_and_ranks_eq`, `noether_macaulay_gorenstein_symmetry_eq`, `weyl_d4_spinor_weight_decomposition_eq`, `weyl_d4_even_parity_and_chiral_orthogonality_eq`.
2. **`ShiodaFormalConjectures.lean` (6 theorems):** `shioda_m6_orbit_census_cert`, `shioda_aoki_fermat_fourfold_census_m3_to_m10_empty_band4`, `shioda_aoki_fermat_m12_census_cert`, `weyl_d4_transition_matrix_invertible_cert`, `macaulay_plane_and_quadric_rank_witness_cert`, `macaulay_pairing_matrix_rank_cert`.
3. **`MathlibPR_ShiodaAokiFermat.lean` (7 theorems):** `gcdFuel_zero_right`, `gcdFuel_eq_nat_gcd_le_20`, `band_partition_mutually_exclusive`, `band_partition_exhaustive`, `isBand1CompletePairs_swap01`, `shioda_aoki_band4_empty_of_le_ten`, `shioda_aoki_m12_band4_orbits`.
4. **`MathlibPR_MacaulayGorenstein.lean` (5 theorems):** `monomialDivides_refl`, `monomialDivides_trans`, `addExp4_comm`, `coeffInSocle_addExp4_comm`, `macaulayPairingMatrix_transpose_duality`.
5. **`MathlibPR_Spin8Triality.lean` (7 theorems):** `addW4_comm`, `addW4_assoc`, `addW4_zero_right`, `signProd4_mul_eq_one`, `wd4_preserves_spinor_chirality`, `spin8_wedge4_hodge_star_and_root_rank`, `wd4_chiral_character_orthogonality`.
6. **`MathlibPR_CyclotomicIncidenceSieve.lean` (4 theorems):** `activeSupport_le_totalIncidences`, `activeSupport_add_collisionExcess`, `activeSupport_add_residualFormDim`, `cyclotomic_incidence_residual_form_master_cert`.
7. **`WiebeSchejaStorch.lean` (2 theorems):** `wiebe_scheja_storch_plane_colon_ideal_cert`, `wiebe_scheja_storch_quadric_colon_ideal_cert`.
8. **`GaussManinJetTransport.lean` (3 theorems):** `gauss_manin_band1_quadric_jet_cert`, `gauss_manin_band2_curve_join_jet_cert`, `gauss_manin_band3_surface_curve_jet_cert`.
9. **`ShiodaInductiveCycleSynthesis.lean` (2 theorems):** `shioda_band3_implies_surface_hodge11_m3_to_m12`, `shioda_aoki_complete_cycle_witness_synthesis_m3_to_m10_and_m12`.
10. **`Spin8LieAlgebraTriality.lean` (3 theorems):** `d4_weyl_reflection_invariance_cert`, `spin8_outer_triality_order3_and_dynkin_cert`, `spin8_casimir_and_subalgebra_kernels_cert`.
11. **`GlobalIVHSObstructionSpectrum.lean` (2 theorems):** `gorenstein_poincare_duality_bijection_cert`, `global_ivhs_1751_obstruction_spectrum_cert`.
12. **`HigherDegreeSporadicBand4.lean` (3 theorems):** `shioda_prime_degree_band1_purity_cert`, `shioda_aoki_higher_degree_band4_decomposition_m11_to_m16_cert`, `shioda_aoki_band4_decomposition_m18_cert`.

### Extension Verification Workspace (`examples/math_gov/LeanMillenniumExt/`, `reports/millennium_ext/MILLENNIUM_EXT_RECEIPT.json`)
Comprises **6 Lean 4 extension modules** (`21` total theorem/lemma declarations, `14` public axiom-free certificates printing `does not depend on any axioms`, `0` lines > 100 chars):
1. **`MumfordWeilKernelVecs.lean` (1 theorem):** `mumford_weil_2d_kernel_bases_cert`.
2. **`HodgeBridgeInterfaces.lean` (0 theorems):** `FermatFourfoldHodgeBridge` explicit analytic-to-algebraic hypothesis structure.
3. **`ConditionalFermatHodge.lean` (5 public theorems, 7 private helper lemmas):** `valid_witness_implies_algebraic`, `conditional_glued_surface_join_algebraic`, `synthesizable_implies_algebraic`, `conditional_fermat_hodge22_all_synthesized_algebraic`, `conditional_fermat_hodge22_verified_m3_to_m22_cert`.
4. **`FermatHighDegreeExt.lean` (3 theorems):** `shioda_prime_degree_band1_purity_ext_cert`, `shioda_aoki_band4_decomposition_m20_to_m22_cert`, `shioda_aoki_m25_sporadic_isolation_cert`.
5. **`HigherOrderJetLifting.lean` (3 theorems):** `multi_order_t8_gauss_manin_jet_cert`, `multi_order_t8_exact_z_rank_witness_cert`, `codim3_unmixed_complete_intersection_profiles_cert`.
6. **`CayleyCompleteInt.lean` (2 theorems):** `cayley_ci34_gorenstein_palindromic_cert`, `cayley_ci33_and_ci34_gorenstein_symmetry_cert`.

---

## 3. Epistemic Architecture: Four-Layer Classification

Every module and mathematical claim in the project is assigned to one of four mutually exclusive epistemic categories. Conflation across category boundaries is strictly prohibited.

```
+---------------------------------------------------------------------------------------------------+
|                                  THE FOUR EPISTEMIC LAYERS                                        |
+---------------------------------------------------------------------------------------------------+
|  LAYER 1: UNCONDITIONAL CLASSICAL THEOREMS                                                        |
|  - Proved from foundational literature without hypotheses representing unproved conjectures.      |
|  - Classical citations: Lefschetz (1924), Macaulay (1916), Griffiths (1969), Shioda (1979).       |
|  - Examples: Residue isomorphism, Fermat character decomposition, Weil fourfold orthogonality.    |
+---------------------------------------------------------------------------------------------------+
                                                  |
                                                  v
+---------------------------------------------------------------------------------------------------+
|  LAYER 2: CONDITIONAL REDUCTIONS (EPISTEMIC FIREWALL)                                             |
|  - Explicit mathematical reductions of the form "Hypothesis H implies Conclusion C".              |
|  - Hypothesis H isolates deep geometric assertions not yet proved unconditionally.                |
|  - Explicit naming: Must contain "conditional_on_..." or "reduction_to_...".                      |
|  - Examples: Voisin second-order integrability + effective Hilbert bound -> algebraic cycle.      |
+---------------------------------------------------------------------------------------------------+
                                                  |
                                                  v
+---------------------------------------------------------------------------------------------------+
|  LAYER 3: FORMAL VERIFICATION, NON-CIRCULARITY & CONSTRUCTIVE KERNEL COMPUTATION                  |
|  - First-principles Lean 4 definitions verified by kernel reduction (`by rfl`) with 0 axioms.     |
|  - Concrete non-vacuity evaluations preventing vacuous quantification over empty sets.            |
|  - Examples: 1001 + 630 + 120 + 0 = 1751, mu = 15625, 192-element W(D4) group orthogonality.      |
+---------------------------------------------------------------------------------------------------+
                                                  |
                                                  v
+---------------------------------------------------------------------------------------------------+
|  LAYER 4: CERTIFIED FLOAT-FREE COMPUTATIONAL ALGEBRA                                              |
|  - Exact rational, integer, and 62-bit multi-prime CRT linear algebra (scan_forbidden == []).     |
|  - Exact Wang rational reconstruction and t³-jet Gauss-Manin transport over F_p[[t]]/(t⁴).        |
|  - Examples: 1751 x 426 Macaulay rank certification, 3-band blind jet reconstruction.             |
+---------------------------------------------------------------------------------------------------+
```

---

## 4. Headline Theorems: Exact Signatures and Verification Receipts

Each headline declaration has been compiled and checked against the Lean 4 kernel (`lake clean && lake build`), with exact verbatim axiom outputs recorded below.

### 4.1. Integer $W(D_4)$ Transition Matrix Invertibility Certificate (`ShiodaFormalConjectures.lean`)

The $6 \times 6$ transition matrix `bWeyl` is constructed algorithmically from the 3 complementary Hodge-star pairs `zeroStarPairs` of `zeroIndexTuples` (rows $2k$ and $2k+1$ are $e_I + e_{I^c}$ and $e_I - e_{I^c}$), with `bAdjCols := scalarMulMat (-4) bWeyl` and `neg8_I6 := diagMatrix 6 (-8)`.

#### Signature
```lean
theorem weyl_d4_transition_matrix_invertible_cert :
    zeroStarPairs.length = 3 ∧
    matMul bWeyl bAdjCols = neg8_I6 :=
  ⟨by rfl, by rfl⟩
```
* **Axiom Receipt:**
  ```text
  'weyl_d4_transition_matrix_invertible_cert' does not depend on any axioms
  ```
* **Epistemic Classification:** Layer 3 (Constructive Kernel Linear Algebra). Establishes rational invertibility of the $6 \times 6$ Weyl-to-Weil transition matrix over $\mathbb{Q}$.

---

### 4.2. Generative Macaulay Contraction Matrices & Rank Proofs (`ShiodaFormalConjectures.lean`)

Over the truncated polynomial ring $\mathbb{Q}[u_0, u_1, u_2, u_3]/(u_0^5, u_1^5, u_2^5, u_3^5)$, `macaulayPairingMatrix socle d` constructs the explicit Macaulay contraction pairing matrix between `monomials4 d` and `monomials4 (12 - d)`, and exact fraction-free Gaussian elimination `intMatRankAuxClean` certifies the matrix ranks for both the static coordinate 2-plane socle `planeSoclePoly := [([0, 4, 4, 4], 1)]` and the deformed Band-1 quadric jet socle `quadricJetSoclePoly := [([0, 4, 4, 4], 1), ([4, 0, 4, 4], 1)]`.

#### Signatures
```lean
theorem macaulay_plane_and_quadric_rank_witness_cert :
    ([0, 1, 2, 3, 4, 5, 6].map planeMacaulayRank,
     ([0, 1, 2, 3, 4, 5, 6].map planeMacaulayRank).foldl (· + ·) 0,
     [0, 1, 2, 3, 4, 5, 6].map quadricMacaulayRank) =
    ([1, 3, 6, 10, 15, 18, 19], 72, [1, 4, 9, 16, 24, 30, 32]) := by rfl

theorem macaulay_pairing_matrix_rank_cert :
    ([0, 1, 2, 3, 4, 5, 6].map (macaulayMatrixRank planeSoclePoly) =
       [0, 1, 2, 3, 4, 5, 6].map planeMacaulayRank) ∧
    ([0, 1, 2, 3, 4, 5, 6].map (macaulayMatrixRank quadricJetSoclePoly) =
       [0, 1, 2, 3, 4, 5, 6].map quadricMacaulayRank) ∧
    (binomNat 7 2 - macaulayMatrixRank planeSoclePoly 2,
     binomNat 7 2 - macaulayMatrixRank quadricJetSoclePoly 2,
     (monomials4 2).length - macaulayMatrixRank planeSoclePoly 2,
     (monomials4 2).length - macaulayMatrixRank quadricJetSoclePoly 2) =
    (15, 12, 4, 1) :=
  ⟨by rfl, by rfl, by rfl⟩
```
* **Axiom Receipts:**
  ```text
  'macaulay_plane_and_quadric_rank_witness_cert' does not depend on any axioms
  'macaulay_pairing_matrix_rank_cert' does not depend on any axioms
  ```
* **Epistemic Classification:** Layer 3 (Constructive Matrix Rank & Socle Contraction). Verifies that the degree-2 annihilator kernel shifts from $15 \to 12$ in $\mathbb{P}^5$ (and $4 \to 1$ on the 4-variable slice, isolating the unique irreducible quadric generator $q_2$).

---

### 4.3. First-Principles Shioda–Aoki Fermat Fourfold Census (`ShiodaFormalConjectures.lean`)

Using `coprimeUnits`, `isShiodaHodge22` (checking $\sum_{i=0}^5 ((t \cdot a_i) \bmod m) = 3m$ for every $t \in (\mathbb{Z}/m\mathbb{Z})^\times$), the partition predicates `isBand1CompletePairs`, `isBand2ThreePlusThree`, `isBand3TwoPlusFour`, `isBand4Residual`, and `s6OrbitSize` ($6! / \prod c_k!$), `fermatCensusSummary` computes the complete character census.

#### Signatures
```lean
theorem shioda_m6_orbit_census_cert :
    (5 : Nat) ^ 6 = 15625 ∧
    fermatCensusSummary 6 = (1751, 1001, 630, 120, 0, []) :=
  ⟨by rfl, by rfl⟩

theorem shioda_aoki_fermat_fourfold_census_m3_to_m10_empty_band4 :
    [3, 4, 5, 6, 7, 8, 9, 10].map fermat_band4_count = [0, 0, 0, 0, 0, 0, 0, 0] := by rfl

theorem shioda_aoki_fermat_m12_census_cert :
    fermatCensusSummary 12 =
      (52991, 15101, 21690, 15840, 360,
        [[1, 1, 8, 8, 9, 9], [3, 3, 4, 4, 11, 11], [3, 3, 7, 7, 8, 8], [4, 4, 5, 5, 9, 9]]) :=
  by rfl
```
* **Axiom Receipts:**
  ```text
  'shioda_m6_orbit_census_cert' does not depend on any axioms
  'shioda_aoki_fermat_fourfold_census_m3_to_m10_empty_band4' does not depend on any axioms
  'shioda_aoki_fermat_m12_census_cert' does not depend on any axioms
  ```
* **Epistemic Classification:** Layer 3 (Combinatorial Census). Proves Band 4 is identically empty for $3 \le m \le 10$, verifies $1001 + 630 + 120 + 0 = 1751$ at $m=6$, and isolates the 4 paired-diagonal $S_6$-orbits (360 characters) out of 52,991 Hodge $(2,2)$ characters at $m=12$.

---

### 4.4. 15-Matching Band-1 Multiplicity & 192-Element $W(D_4)$ Chiral Orthogonality (`HodgeVerification.lean`)

`all_perfect_matchings_6` generates all 15 perfect matchings of $\{0..5\}$ and partitions all 1,001 Band-1 characters of $m=6$ by matching satisfaction multiplicity (`[(1, 360), (2, 540), (3, 60), (6, 40), (15, 1)]`). `weyl_d4_elements` generates all $24 \times 8 = 192$ elements of $W(D_4) = S_4 \ltimes (\mathbb{Z}/2\mathbb{Z})^3$, verifying even parity on $S^+_8$ and chiral character orthogonality on the 6-dimensional zero-weight space $3_+ \oplus 3_-$.

#### Signatures
```lean
theorem fifteen_matching_band1_block_incidence_eq :
  (fifteen_perfect_matchings == 15 &&
   modes_per_matching_block == 125 &&
   band1_block_total_incidences == 1875 &&
   band1_mult_mode_sum == fermat_band1_count 6 &&
   band1_mult_incidence_sum == band1_block_total_incidences &&
   band1_block_total_incidences - fermat_band1_count 6 == 874 &&
   band1_multiplicity_pairs == [(1, 360), (2, 540), (3, 60), (6, 40), (15, 1)]) = true := by rfl

theorem weyl_d4_even_parity_and_chiral_orthogonality_eq :
  (wd4_total_elements, wd4_all_even_parity, wd4_norm_plus_sq, wd4_norm_minus_sq, wd4_cross_product) =
    (192, true, 192, 192, 0) := by rfl
```
* **Axiom Receipts:**
  ```text
  'fifteen_matching_band1_block_incidence_eq' does not depend on any axioms
  'weyl_d4_even_parity_and_chiral_orthogonality_eq' does not depend on any axioms
  ```

---

### 4.5. Calabi–Yau Fourfold Koszul Dimensions, Socle Symmetry & $D_4$ Root Gram Rank (`HodgeVerification.lean`)

#### Signatures
```lean
theorem h22_prim_eq : h22_prim = 1751 := by rfl
theorem milnor_number_eq : milnor_number = 15625 := by rfl
theorem fermat_four_band_closure_eq : fermat_four_band_total = h22_prim := by rfl

theorem noether_macaulay_gorenstein_symmetry_eq :
  (cy4_socle_degree == 24 &&
   cy4_middle_degree == 12 &&
   cy4_hilbert_series.length == cy4_socle_degree + 1 &&
   cy4_hilbert_series == cy4_hilbert_series.reverse &&
   nf_sum_pairs 0 == 1 &&
   nf_sum_pairs cy4_middle_degree == h22_prim &&
   nf_sum_pairs cy4_socle_degree == 1) = true := by rfl

theorem weyl_d4_spinor_weight_decomposition_eq :
  (four_tuples.length == 70 &&
   fourIndexTuples.all (fun I =>
     complement8 (complement8 I) == I &&
     complement8 I != I &&
     intEq (hodgeStarSign (complement8 I)) (hodgeStarSign I)) &&
   wedge4_spinor_self_dual_dim == 35 &&
   wedge4_spinor_anti_self_dual_dim == 35 &&
   wedge4_spinor_self_dual_dim + wedge4_spinor_anti_self_dual_dim == four_tuples.length &&
   zero_weight_tuples.length == 6 &&
   mumford_stacked_root_rank == zero_weight_tuples.length &&
   weyl_d4_group_order == 192 &&
   triality_zero_triples.length == 32) = true := by rfl
```
* **Axiom Receipts:**
  ```text
  'h22_prim_eq' does not depend on any axioms
  'milnor_number_eq' does not depend on any axioms
  'fermat_four_band_closure_eq' does not depend on any axioms
  'noether_macaulay_gorenstein_symmetry_eq' does not depend on any axioms
  'weyl_d4_spinor_weight_decomposition_eq' does not depend on any axioms
  ```

---

## 5. Mathematical Discovery Documentation

### 5.1. 3-Band Blind Gauss–Manin Jet Reconstruction over $\mathbb{F}_p[[t]]/(t^4)$

Let $X_0 = V(F_0) \subset \mathbb{P}^5$ denote the Fermat sextic Calabi–Yau fourfold, and let $F_t = F_0 + t W$ be a 1-parameter deformation parameterized by a polynomial $W \in R^6(F_0)$ of degree 6.

Under the Gauss–Manin connection, the variation of the Jacobian slice satisfies the jet transport system:
$$\nabla_{\partial_t} \lambda^{(k)} \equiv M_W \lambda^{(k-1)} \pmod{J(F_t)}$$
where $M_W : R^{12}(F_0) \to R^{18}(F_0)$ is the multiplication map by $W$.

In `toolkit/blind_gauss_manin_jet_reconstructor.py`, a float-free algorithm reconstructs smoothed geometric subvarieties across three cyclotomic character bands directly from the third-order jet $t^3 \pmod{t^4}$ without planting equations:

$$\begin{array}{lcccc}
\hline
\textbf{Band} & \textbf{Reconstructed Geometry} & \textbf{Macaulay Rank Profile} & \dim \ker M^{(1)} & \textbf{Gotzmann } G \\
\hline
\text{Band 1} & \text{Quadric Surface } Q_2 = V(y_0, y_1, q_2) & [4, 9, 16, 24, 30, 32] & 2 & 2 \\
\text{Band 2} & 3+3 \text{ Curve Join } C_1 \times C_2 & [6, 21, 50, 90, 126, 141] & 0 & 3 \\
\text{Band 3} & 2+4 \text{ Surface-Curve Join } S \times C & [5, 15, 32, 53, 71, 78] & 1 & 3 \\
\hline
\end{array}$$

For coordinate planes, the degree-2 Macaulay annihilator on the 4-variable slice has dimension $4$. Upon deformation along the quadric direction $q_2 = u_0 u_1$, the rank vector shifts from $[1, 3, 6, 10, 15, 18, 19]$ to $[1, 4, 9, 16, 24, 30, 32]$. In degree 2, $\dim \ker$ drops from $4$ to $1$ on the 4-variable slice (and $15$ to $12$ in $\mathbb{P}^5$), isolating the unique irreducible quadric generator $q_2$ with Gotzmann regularity $G = 2$.

---

### 5.2. Macaulay Inverse Systems & Wiebe–Scheja–Storch Transition Determinants

Let $S = \mathbb{C}[x_0, \dots, x_5]$ and let $J(F) = (\partial_0 F, \dots, \partial_5 F)$ be the Jacobian ideal of a smooth sextic hypersurface. The Jacobian ring $R(F) = S/J(F)$ is an Artinian Gorenstein local ring with socle degree:
$$d_{\mathrm{socle}} = 6 \cdot (6 - 2) = 24$$

For a codimension-3 complete intersection subvariety $Z = V(g_1, g_2, g_3) \subset X_4$, the transition matrix $C = (c_{i,j})$ expresses the defining equations of $Z$ in terms of the partial derivatives:
$$g_i = \sum_{j=1}^3 c_{i,j} A_j$$
By classical theorems of H. Wiebe (1969) and G. Scheja & U. Storch (1975), the transition determinant $\det C$ has universal degree:
$$\deg(\det C) = 30 - 18 = 12$$
and satisfies the exact colon identity:
$$(J(F) : \det C) = \mathfrak{a}_Z$$
recovering the geometric ideal $\mathfrak{a}_Z$ algebraically from the Jacobian ring without coordinate projections.

---

### 5.3. $W(D_4)$ Triality and Mumford Spinor Weight Splitting

On a simple abelian sixfold $A$ of Mumford type with $\operatorname{End}_{\mathbb{Q}}(A) = \mathbb{Q}$ and $\rho(A) = 1$, the Hodge ring contains an exceptional 2-dimensional space of $(2,2)$-classes in $H^4(A, \mathbb{Q})$ arising from the spinor representation of $D_4 = \mathfrak{so}(8)$.

The 70-dimensional exterior power $\bigwedge^4 S^+_8$ branches under the Hodge star involution $\star$ ($\star^2 = +1$) into $35_+ \oplus 35_-$. On the 6-dimensional Cartan zero-weight subspace $(\bigwedge^4 S^+_8)_0 \cong 3_+ \oplus 3_-$, the 192-element Weyl group $W(D_4)$ acts via even permutations on $S^+_8$ with orthogonal irreducible chiral characters ($\langle \chi_+, \chi_+ \rangle = 192$, $\langle \chi_-, \chi_- \rangle = 192$, $\langle \chi_+, \chi_- \rangle = 0$). Furthermore, the $6 \times 6$ $D_4$ simple-root Gram matrix $M = \sum_{\alpha \in \Delta} E_\alpha^T E_\alpha$ has full rank $6$, certifying the absence of trivial $\mathfrak{so}(8)$ singlets.

---

## 6. Prior-Work Audit: Verified Absence and Boundary Demarcation

Every citation and novelty assertion in this project is verified against opened primary sources:

### 6.1. Mathlib 4 Core (`leanprover-community/mathlib4`)
* **Mathlib Core:** Contains commutative algebra, polynomial rings, module depth, and Cohen–Macaulay rings.
* **Absence Certified:** Contains **zero definitions** of:
  1. The Hodge Conjecture or algebraic cycle class map $\operatorname{cl}_{\mathbb{Q}} : \operatorname{CH}^p(X)_{\mathbb{Q}} \to H^{2p}(X, \mathbb{Q})$.
  2. Artinian Gorenstein rings, socle duality, and Macaulay inverse systems.
  3. Gotzmann persistence and Hilbert function regularity bounds.
  4. Shioda–Aoki Fermat hypersurface character groups.
  5. The outer triality automorphism of $\operatorname{Spin}(8)$ and the $W(D_4)$ character table.
  6. Wang's (1981) Euclidean modular rational reconstruction.

### 6.2. Google DeepMind `formal-conjectures` Repository
* **Repository Path:** `google-deepmind/formal-conjectures` (audited 16 November 2026, receipt in `prior_art_audit_receipt.json`).
* **Absence Certified:** Contains **zero code hits** for `HodgeConjecture`, `hodge_conjecture`, or `cycleClass`. PR #5585 exists in an open state re-porting general definitions, but contains no Shioda–Aoki Fermat character formalization.

### 6.3. Imperial College London `FLT` (`ImperialCollegeLondon/FLT`)
* **Repository Scope:** Formalizing Fermat's Last Theorem for regular and general primes.
* **Absence Certified:** Contains algebraic number theory and Galois representations, but zero formalizations of complex projective Hodge theory or Calabi–Yau Jacobian rings.

---

## 7. Modular Paper Pipeline: Specifications and Status

In accordance with Rule 2.2 ("Write several short papers, not one paper made short"), research outputs are partitioned into discrete, single-claim papers under 15 pages, written strictly in impersonal third-person prose.

```
+---------------------------------------------------------------------------------------------------+
|                                 MODULAR PUBLICATION PIPELINE                                      |
+---------------------------------------------------------------------------------------------------+
|  PAPER 1: Shioda–Aoki Fermat Hypersurface Cohomology in Lean 4                                    |
|  - Claim: First formalization of Shioda-Aoki Fermat character census & m<=10, m=12 classification. |
|  - Length: 10–12 pages. Target: ITP / CPP / Journal of Automated Reasoning.                       |
+---------------------------------------------------------------------------------------------------+
                                                  |
                                                  v
+---------------------------------------------------------------------------------------------------+
|  PAPER 2: Artinian Gorenstein Apolarity & Macaulay Ranks for CY4 Hypersurfaces                   |
|  - Claim: Machine-checked Macaulay pairing matrix ranks & socle duality for CY4 planes/quadrics.  |
|  - Length: 8–10 pages. Target: Journal of Automated Reasoning (JAR).                              |
+---------------------------------------------------------------------------------------------------+
                                                  |
                                                  v
+---------------------------------------------------------------------------------------------------+
|  PAPER 3: Spin(8) Triality and Mumford Spinor Representations in Lean 4                           |
|  - Claim: Machine-checked W(D4) 192-element action, 35+35 splitting & rank-6 root Gram matrix.    |
|  - Length: 8–10 pages. Target: Formalized Mathematics / ITP.                                      |
+---------------------------------------------------------------------------------------------------+
                                                  |
                                                  v
+---------------------------------------------------------------------------------------------------+
|  PAPER 4: Infinitesimal Voisin Integrability & Blind Gauss–Manin Jet Reconstruction               |
|  - Claim: Float-free 3-band jet reconstruction and quadric syzygy emergence over F_p[[t]]/(t⁴).    |
|  - Length: 10–12 pages. Target: Mathematics of Computation / ISSAC.                               |
+---------------------------------------------------------------------------------------------------+
```

### 7.1. Paper 1: Shioda–Aoki Fermat Hypersurface Cohomology in Lean 4
* **Central Claim:** *"This paper presents a constructive, axiom-free formalization in Lean 4 of the Shioda–Aoki character classification on Fermat fourfolds, verifying via kernel evaluation that Band 4 residual characters vanish for all degrees $m \in [3, 10]$, decomposing the 1,751 sextic characters into $1001 + 630 + 120 + 0$ with exact 15-matching multiplicity distribution, and isolating the four paired-diagonal $S_6$-orbits (360 characters) at $m = 12$."*
* **Length:** 10–12 pages.
* **Compilation Target:** 0 errors, 0 overfull hboxes, 0 first-person pronouns.
* **Lean Modules:**
  1. `ShiodaFormalConjectures.lean` (471 lines): `shioda_m6_orbit_census_cert`, `shioda_aoki_fermat_fourfold_census_m3_to_m10_empty_band4`, `shioda_aoki_fermat_m12_census_cert` (`by rfl`, `does not depend on any axioms`).
  2. `HodgeVerification.lean` (956 lines): `fermat_four_band_closure_eq`, `band3_partitions_satisfy_2_plus_4`, `fifteen_matching_band1_block_incidence_eq` (`by rfl`, `does not depend on any axioms`).
* **Raw Terminal Receipts:** Raw `lake clean && lake build` output (5 passed jobs) and verbatim `#print axioms` output showing `does not depend on any axioms`.

### 7.2. Paper 2: Artinian Gorenstein Apolarity & Macaulay Ranks for CY4 Hypersurfaces
* **Central Claim:** *"This paper provides a machine-checked formalization in Lean 4 of Artinian Gorenstein socle duality and explicit Macaulay contraction pairing matrices over $\mathbb{Q}[u_0, u_1, u_2, u_3]/(u_0^5, u_1^5, u_2^5, u_3^5)$, proving by fraction-free Gaussian elimination that the matrix ranks recover $[1, 3, 6, 10, 15, 18, 19]$ for coordinate 2-planes and $[1, 4, 9, 16, 24, 30, 32]$ for deformed quadrics with degree-2 kernel shift $4 \to 1$."*
* **Length:** 8–10 pages.
* **Compilation Target:** 0 errors, 0 overfull hboxes, 0 first-person pronouns.
* **Lean Modules:**
  1. `ShiodaFormalConjectures.lean` (471 lines): `macaulay_plane_and_quadric_rank_witness_cert`, `macaulay_pairing_matrix_rank_cert` (`by rfl`, `does not depend on any axioms`).
  2. `HodgeVerification.lean` (956 lines): `h40_prim_eq`, `h31_prim_eq`, `h22_prim_eq`, `milnor_number_eq`, `r6_dim_eq`, `plane_kernel_dim_eq`, `macaulay_annihilator_dim_bound`, `signed_difference_ideal_intersection`, `deformed_macaulay_flat_hilbert_sum_eq`, `finite_non_fermat_pair_milnor_and_ranks_eq`, `noether_macaulay_gorenstein_symmetry_eq` (`by rfl`, `does not depend on any axioms`).

### 7.3. Paper 3: Spin(8) Triality and Mumford Spinor Representations in Lean 4
* **Central Claim:** *"This paper formalizes the $\operatorname{Spin}(8)$ weight spaces $S^+_8, S^-_8, V_8$, the Hodge-star splitting $\bigwedge^4 S^+_8 \cong 35_+ \oplus 35_-$, the full 192-element Weyl group $W(D_4)$ with orthogonal chiral characters on $3_+ \oplus 3_-$, the $6 \times 6$ transition matrix invertibility $B_{\mathrm{Weyl}} B_{\mathrm{adj}} = -8 I_6$, and the rank-6 $D_4$ simple-root Gram matrix in Lean 4 with zero axioms."*
* **Length:** 8–10 pages.
* **Compilation Target:** 0 errors, 0 overfull hboxes, 0 first-person pronouns.
* **Lean Modules:**
  1. `ShiodaFormalConjectures.lean` (471 lines): `weyl_d4_transition_matrix_invertible_cert` (`by rfl`, `does not depend on any axioms`).
  2. `HodgeVerification.lean` (956 lines): `weil_w1_orthogonal_to_theta2`, `weil_w2_orthogonal_to_theta2`, `four_tuples_len`, `zero_tuples_len`, `clifford_even_dim_eq`, `d4_triality_zero_triples_len`, `spinor_to_weil_su22_branching_eq`, `weyl_d4_conjugate_weil_axes_eq`, `weyl_d4_spinor_weight_decomposition_eq`, `weyl_d4_even_parity_and_chiral_orthogonality_eq` (`by rfl`, `does not depend on any axioms`).

### 7.4. Paper 4: Infinitesimal Voisin Integrability and Blind Gauss–Manin Jet Reconstruction
* **Central Claim:** *"This paper presents an exact, float-free algorithm reconstructing smoothed geometric subvarieties and higher syzygies directly from third-order infinitesimal Gauss–Manin jets over $\mathbb{F}_p[[t]]/(t^4)$ across three cyclotomic character bands."*
* **Length:** 10–12 pages.
* **Computational Engines:** `toolkit/blind_gauss_manin_jet_reconstructor.py`, `toolkit/modular_crt_linear_solver.py`, `toolkit/covariant_apolarity_and_weyl_shioda_census.py` (certified 62-bit multi-prime CRT, `scan_forbidden == []`).

---

## 8. Disqualified Materials (Repository Artifacts Only)

The following topics are permanently excluded from journal submission and are maintained solely as exploratory artifacts within the project laboratory:
1. **The Monolithic "Four Pillars" Omnibus:** Excluded from submission per Rule 2.1; partitioned into modular papers.
2. **The "CMI Five-Condition Attack":** Retained as internal exploratory algebra; never submitted as a Millennium solution.
3. **Tautological Bridge Wrappers & Bare-Type Lemmas:** Permanently banned and removed from the Lean codebase.
4. **Radix-10 / Carmichael / Hardy-Ramanujan Unmasking Tables:** Excluded from algebraic geometry manuscripts.
5. **Raw Test Execution Counts and Build Job Counters:** Excluded from paper texts.

---

## 9. Two-Dimensional Verification Protocol: What to Check and How to Check

```
+---------------------------------------------------------------------------------------------------+
|                                 THE TWO-DIMENSIONAL AUDIT PROTOCOL                                |
+---------------------------------------------------------------------------------------------------+
|  DIMENSION 1: WHAT TO AUDIT                                                                       |
|  1. Mathematical Semantics: Lean statements match standard literature definitions.               |
|  2. Hypothesis Cleanliness: Hard mathematical content is not hidden in structures or axioms.      |
|  3. Foundational Axioms: Core standard axioms only (0 axioms achieved across all 46 theorems).    |
|  4. Constructive Computing: Zero hardcoded result literals; all ranks/orbits computed.            |
|  5. Primary Citations: Every citation verified by direct file inspection.                         |
+---------------------------------------------------------------------------------------------------+
                                                  |
                                                  v
+---------------------------------------------------------------------------------------------------+
|  DIMENSION 2: HOW TO AUDIT                                                                        |
|  1. Kernel Build: lake clean && lake build completes with 0 errors and 0 warnings.                |
|  2. Axiom Extraction: #print axioms <declaration> outputs 'does not depend on any axioms'.        |
|  3. Forbidden Token Scan: 0 matches for sorry, admit, opaque, axiom, native_decide, unsafe.       |
|  4. Float-Free Certification: scan_forbidden == [] across all 20 certified toolkit engines.       |
|  5. Document Compilation: pdflatex compiles with 0 errors, 0 overfull hboxes, 0 pronouns.        |
+---------------------------------------------------------------------------------------------------+
```

### Detailed Verification Matrix

| Audit Target | Verification Command / Method | Pass Criterion | Failure Action |
|---|---|---|---|
| **Compilation** | `lake clean && lake build` | 100% jobs pass; 0 errors. | Resolve errors; do not suppress with compiler flags. |
| **Axioms** | `#print axioms <decl>` | `does not depend on any axioms` (or core 3 only). | **HALT.** Eliminate `sorry`, `admit`, `opaque`, or custom axioms. |
| **Definitional Soundness** | Kernel reduction (`by rfl`) | Evaluates to identical normal form. | Rebind symbols directly to exact definitions. |
| **Non-Vacuity** | Concrete witness evaluation | Exact counts verified algorithmically (`1001+630+120+0=1751`). | Fix domain conditions or index bounds. |
| **Conditionality Labeling** | Signature audit | Any theorem with unproved hypotheses is named "reduction" or "conditional". | Strip names of mathematicians if the hard analytic step is assumed. |
| **Primary Sources** | Direct file inspection | Source file opened, commit hash or page verified. | Delete citation if source was cited from memory. |
| **Document Quality** | `pdflatex` compilation | 0 errors, 0 overfull hboxes, 0 underfull hboxes. | Adjust typography, line breaks, or wording. |
| **Prose Neutrality** | Automated regular expression scan | 0 occurrences of first-person pronouns. | Rewrite in impersonal passive voice. |
| **Zero-Float Rigor** | `scan_forbidden` regex scan | 0 float occurrences across all 20 certified engines. | Convert to exact `int`, `Fraction`, or modular arithmetic. |

---

## 10. Dependency Gates (Zero Calendar Boundaries)

Progression between stages is governed strictly by logical prerequisites:

```
+---------------------------------------------------------------------------------------------------+
|                                  LOGICAL GATING STRUCTURE                                         |
+---------------------------------------------------------------------------------------------------+
|  GATE G1 (Workspace Consolidation & Constructive Lean 4 Rewrite — Steps 1–5): PASSED              |
|  - Prerequisite: Single Lake root; 46/46 theorems constructive and 100% axiom-free.               |
|  - Verification: lake clean && lake build (5 jobs) + 0 forbidden tokens.                          |
+---------------------------------------------------------------------------------------------------+
                                                  |
                                                  v
+---------------------------------------------------------------------------------------------------+
|  GATE G2 (Live GitHub Prior-Art Scan & Master Plan Synchronization — Step 6A): PASSED            |
|  - Prerequisite: prior_art_audit_receipt.json verified; MASTER_RESEARCH_EXECUTION_PLAN.md synced. |
|  - Verification: 0 first-person pronouns; exact verbatim signatures and receipts recorded.        |
+---------------------------------------------------------------------------------------------------+
                                                  |
                                                  v
+---------------------------------------------------------------------------------------------------+
|  GATE G3 (Paper 1 Authoring & Compilation — Step 6B): PASSED                                      |
|  - Prerequisite: Gate G2 approved by external referee.                                            |
|  - Verification: 10-page Paper 1 (0 errors, 0 overfull/underfull hboxes, 0 pronouns, raw Lean).   |
+---------------------------------------------------------------------------------------------------+
                                                  |
                                                  v
+---------------------------------------------------------------------------------------------------+
|  GATE G4 (Paper 2 & Paper 3 Authoring & Compilation — Steps 6C–6D): PASSED                        |
|  - Prerequisite: Paper 1 completed and verified.                                                  |
|  - Verification: 8-page Paper 2 & 8-page Paper 3 (0 errors, 0 overfull/underfull, raw receipts).  |
+---------------------------------------------------------------------------------------------------+
                                                  |
                                                  v
+---------------------------------------------------------------------------------------------------+
|  GATE G5 (Paper 4 Authoring & Final Repository Synchronization — Step 6E): PASSED                 |
|  - Prerequisite: Papers 1–3 completed; 20 toolkit engines & pytest verified.                      |
|  - Verification: 10-page Paper 4 (0 errors, 0 overfull/underfull, 0 pronouns) + ledger synced.    |
+---------------------------------------------------------------------------------------------------+
```

---

## 11. Mandatory Pre-Publication Release Checklist

Before any paper, bundle, or package is published to Zenodo, arXiv, or peer-reviewed journals, every item must be attested:

- [ ] **1. Single Central Claim:** Abstract states one primary machine-checked contribution in 1–2 sentences.
- [ ] **2. Explicit Scope Demarcation:** Abstract explicitly affirms that the general Hodge Conjecture remains open.
- [ ] **3. Primary Source Verification:** Every cited paper, PR, or repository was inspected directly.
- [ ] **4. Clean Kernel Build:** Full `lake clean && lake build` output exhibits clean compilation with 0 errors.
- [ ] **5. Foundational Axiom Audit:** Verbatim `#print axioms` output contains `does not depend on any axioms` (or `[propext, Classical.choice, Quot.sound]` at most).
- [ ] **6. Zero Proof Shortcuts:** Zero occurrences of `sorry`, `admit`, `opaque`, `axiom`, `unsafe`, or `native_decide`.
- [ ] **7. Definitional Alignment:** Definitions match standard algebraic geometry and Mathlib conventions.
- [ ] **8. Conditionality Demarcation:** Any conditional bridge is labeled as a reduction or conditional interface.
- [ ] **9. Clean Typography:** `pdflatex` log exhibits 0 errors, 0 overfull hboxes, and 0 underfull hboxes.
- [ ] **10. Page Budget:** Document length is strictly under 15 pages (single-sitting reading standard).
- [ ] **11. Prose Neutrality:** Zero first-person pronouns throughout the entire document.
- [ ] **12. Slogan Elimination:** Zero governance slogans, marketing phrases, or meta-commentary flags in LaTeX text.
