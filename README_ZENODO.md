# Zenodo Deposit & Verification Kit (`HODGE-MILLENNIUM-001`)

**Author & Affiliation:** Qamar Munawer (Brandenburg University of Technology Cottbus-Senftenberg)  
**Version / Edition:** `0.7.0` (Edition `1.0.0`, Date: `2026-11-15`)  
**Repository Branch:** `candidate/math-gov-v0.6`  
**Toolchain:** Python 3.12 (exact integer / `fractions.Fraction` / `pow(a, p - 2, p)` arithmetic, zero floats) & Lean `leanprover/lean4:v4.35.0` (Lake 5.0.0, **zero Mathlib imports**)  
**Scientific Honesty Status:**
- `GLOBAL_HODGE_CONJECTURE`: **OPEN** (`NO_HODGE_PROOF = TRUE`)
- `S-BRIDGE-DEFORM-CY4`: `ADVERSARIALLY_BLOCKED_OPEN_BRIDGE`
- `S-BRIDGE-SPINOR-MOTIVE`: `ADVERSARIALLY_BLOCKED_OPEN_BRIDGE`
- `release_authorized`: `false`
- `theorem_progress`: `UNKNOWN`

---

## Scope & Classical Attribution Notice
- **Exact Rational & Modular ($\mathbb{F}_p$) Experiment Toolkit:** The Python modules in `toolkit/` perform exact computational experiments on sextic Calabi–Yau fourfolds ($X^4_6 \subset \mathbb{P}^5$) and Mumford spinor weight-tuple combinatorics ($\bigwedge^4 S^+_8$).
- **Decidable Finite Checks Only (`HodgeVerification.lean`):** `HodgeVerification.lean` imports **zero Mathlib libraries** and checks **43 decidable finite combinatorial and degree-counting identities (`by rfl`)** verifying index sets and dimensions (`axioms: []`). It does **not** formalize schemes, sheaves, cohomology, or Hodge theory.
- **Classical Attributions:** Griffiths' residue theorem, Shioda–Aoki–Ran's Fermat cycle decomposition, Macaulay's inverse systems, Peskine–Szpiro liaison, Deligne's absolute Hodge / André's motivated cycle framework, and Wang's modular rational reconstruction are strictly attributed to their original authors.

---

## Deposit Contents & File Tree

```text
.
├── .zenodo.json                                   # Zenodo publication metadata (CC-BY-4.0)
├── CITATION.cff                                   # Citation File Format 1.2.0
├── README_ZENODO.md                               # Deposit guide, file tree & reproduction protocol
├── ARTIFACT_HASH_MANIFEST.sha256                  # SHA-256 integrity manifest of tracked deposit files
├── verify_zenodo_deposit.py                       # Standalone zero-float + Lean 4 + governance verifier
├── paper/
│   └── ZENODO_MANUSCRIPT_FOUR_PILLARS_HODGE.md    # Expository manuscript + Appendix A (Check Ledger)
├── lean_blueprint/
│   └── HodgeVerification.lean                     # Canonical 43 decidable finite checks (0 Mathlib, axioms: [])
├── examples/math_gov/LeanDemoProject/
│   └── HodgeVerification.lean                     # Byte-identical Lake-built target (43/43 finite checks)
├── toolkit/                                       # 19 audited zero-float Python experiment modules (see below)
├── governance/                                    # Case DAG, PROJECT_STATE.yaml, SQLite/JSONL ledger
├── policies/hodge_gates.rego                      # Fail-closed OPA release gate policy
├── docs/                                          # Technical verification notes (01..37)
└── tests/                                         # Automated pytest unit & integration tests
```

---

## Audited Stack Summary

- **19 Audited Zero-Float Python Files (`scan_forbidden == []`):**
  1. `toolkit/three_agent_space_comparison.py`
  2. `toolkit/markman_secant_engine.py`
  3. `toolkit/mumford_spinor_engine.py`
  4. `toolkit/calabi_yau_jacobian_engine.py`
  5. `toolkit/erdos_fourier_incidence_engine.py`
  6. `toolkit/hodge_proof_closure_reviewer.py`
  7. `toolkit/kuga_satake_clifford_engine.py`
  8. `toolkit/higher_order_gauss_manin_sieve.py`
  9. `toolkit/macaulay_apolarity_inverse_engine.py`
  10. `toolkit/deformed_macaulay_transport_engine.py`
  11. `toolkit/four_wall_strategic_resolution_engine.py`
  12. `toolkit/global_recombination_and_coset_engine.py`
  13. `toolkit/universal_obstruction_cancellation_engine.py`
  14. `toolkit/surjective_cokernel_integrability_engine.py`
  15. `toolkit/twenty_plane_minimal_rank_stabilization_engine.py`
  16. `toolkit/non_fermat_determinantal_stabilization_engine.py`
  17. `toolkit/modular_crt_linear_solver.py`
  18. `toolkit/cmi_five_condition_attack_engine.py`
  19. `verify_zenodo_deposit.py`

- **43 Decidable Finite Combinatorial Checks in Core Lean 4.35.0 (`axioms: []`, 0 Mathlib imports):**
  - *Index & Chain Set Checks (1):* `exact_chain_im_sub_ker`
  - *Lattice Orthogonality Checks (2):* `weil_w1_orthogonal_to_theta2`, `weil_w2_orthogonal_to_theta2`
  - *Spinor & Weight Tuple Counts (7):* `four_tuples_len`, `zero_tuples_len`, `clifford_even_dim_eq`, `d4_triality_zero_triples_len`, `spinor_to_weil_su22_branching_eq`, `weyl_d4_conjugate_weil_axes_eq`, `weyl_d4_spinor_weight_decomposition_eq`
  - *Sextic Polynomial Ring & Degree Counting (31):* `h40_prim_eq`, `h31_prim_eq`, `h22_prim_eq`, `h22_total_eq`, `b4_total_eq`, `milnor_number_eq`, `r6_dim_eq`, `plane_kernel_dim_eq`, `saturation_three_count_eq`, `band3_partitions_satisfy_2_plus_4`, `fermat_four_band_closure_eq`, `f_p3_surface_h11_prim_eq`, `min_ivhs_codimension_pos`, `max_ivhs_monomial_rank_eq`, `canonical_fixed_plane_subspace_dim_eq`, `macaulay_annihilator_dim_bound`, `signed_difference_ideal_intersection`, `quadratic_moving_plane_directions_count_eq`, `deformed_macaulay_flat_hilbert_sum_eq`, `cyclotomic_plane_wavepacket_support_eq`, `telescoping_cyclotomic_annihilator_eq`, `tangential_leibniz_annihilator_eq`, `recombination_kernel_dim_gain_eq`, `universal_band_obstruction_cancellation_bounds_eq`, `gorenstein_moduli_rank_extremes_eq`, `nine_partition_cokernel_dims_eq`, `twenty_plane_target_and_collision_counts_eq`, `fifteen_matching_band1_block_incidence_eq`, `recomb_and_collision_flat_hilbert_eq`, `finite_non_fermat_pair_milnor_and_ranks_eq`, `noether_macaulay_gorenstein_symmetry_eq`

---

## Quick-Start Reproducibility Verification

1. Run the standalone Zenodo verifier (full kernel + math replay, or `--fast` single-pass Lean mode):
   ```bash
   python verify_zenodo_deposit.py
   python verify_zenodo_deposit.py --fast
   ```
2. Run the core Lean 4.35.0 finite checks directly:
   ```bash
   cd examples/math_gov/LeanDemoProject && lake env lean HodgeVerification.lean
   ```
3. Run the complete pytest suite:
   ```bash
   pytest -q
   ```

---

## Scientific Scope Boundary

Verifying Shioda–Aoki–Ran's decomposition $1,001 + 630 + 120 + 0 = 1,751$ numerically reproduces the primitive $(2,2)$ Hodge dimension at the **Fermat sextic Calabi–Yau fourfold** $X^4_6 = \{\sum_{i=0}^5 x_i^6 = 0\} \subset \mathbb{P}^5$ via $(\mathbb{Z}/6\mathbb{Z})^6$ character splitting and Lefschetz $(1,1)$ on $X^2_6 \subset \mathbb{P}^3$ ($\dim R^8(F_{\mathbb{P}^3}) = 85$), while our non-separable 6-variable cross-coupled CY4 experiment records the preserved plane orbit `[3, 6, 10, 15, 18, 19]`. General deformed sextics $X_t \subset \mathbb{P}^5$ lack a universal effective Hilbert degree bound, and simple Mumford spinor varieties satisfy $\operatorname{End}_{\mathbb{Q}}(A) = \mathbb{Q}$; hence `GLOBAL_HODGE_CONJECTURE` remains strictly **OPEN**.
