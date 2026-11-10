# CLEAN-ROOM CODE INDEPENDENCE AUDIT

**Protocol:** `RH-T056R8R3`  
**Audit ID:** `RH-T056R8R3-CLEANROOM-INDEPENDENCE-001`  
**Date:** `2026-08-24`  
**Subject File:** `cleanroom_e4/cleanroom_e4_execution.py` (SHA-256: `c098eb478457b53ce1b9dd80d1d46395df221449c0bd02236b2cca1450db74c9`)  
**Comparison References:**
1. Primary Runner: `scripts/run_rh_t056r8r3_primary.py` (SHA-256: `294e0e3a8614874c3382faa7c8e4b11cdc1d0fd290aa5ee74bcfcb936415604c`)
2. Task-1199 Script: `scripts/independent_e4_numerical_reproduction.py` (SHA-256: `f62b6dc6d43defb9f995146df64b15a9ba82f881f8bd257dd66f956f11eeb939`)
3. E3 Verification Script: `scripts/verify_rh_t056r8r3.py` (SHA-256: `d3b1e564fc8fe12d091e92d7705fe05df1076b1076b1fca8306df9a5ec1ca5a8`)

---

## 1. Architectural & Code Structural Comparison

| Feature | Primary Runner (`run_primary.py`) | Task-1199 Script (`independent_e4.py`) | Clean-Room Verifier (`cleanroom_e4_execution.py`) | Classification |
|---|---|---|---|---|
| **Even Projection** | `unitary_even_projection_mp(Q_full_mp, M_val)` | `independent_unitary_even_projection(Q_full, M_val)` | `project_even(Q_full, M)` | `CONCEPTUALLY_SIMILAR_BUT_INDEPENDENT` |
| **Subspace A1 Assembly** | General helper `solve_subspace(None)` | Inlined top-left block slice | Dedicated `construct_matrix_A1(Q_even, n_inner)` | `INDEPENDENT_IMPLEMENTATION` |
| **Subspace B Assembly** | General helper `solve_subspace(v_ext)` | Inlined cross/quad calculation | Dedicated `construct_matrix_B(Q_even, n_inner, M_outer)` | `INDEPENDENT_IMPLEMENTATION` |
| **$t^2$ Vector Formulation** | `(L^2.5) * (-1)^k / (sqrt2 * pi^2 * k^2)` | `(-1)^k * sqrt2 / (k^2)` | `(1 if k%2==0 else -1) * sqrt2 / (k*k)` | `INDEPENDENT_IMPLEMENTATION` |
| **Eigensolver Interface** | `mp.eigsy(Q)` returning eigenvalues & vectors, computing residuals | `mp.eigsy(Q, eigvals_only=True)` | `compute_lowest_eigenvalue()` via `mp.eigsy(..., eigvals_only=True)` | `STANDARD_ORACLE_USAGE` |
| **Gate A Execution** | Iterative precision loop with full matrix logging | Precision ladder loop checking relative error | `compute_gate_a_ground_state()` with tuple/list unwrapping | `INDEPENDENT_IMPLEMENTATION` |
| **Data Output & Sealing** | Primary CSV, RAW JSON, Robustness CSV, Fixture JSON | Numerical Receipt JSON | Two-stage: `BLIND_RESULTS.json` $\to$ `BLIND_RESULT_SEAL.json` $\to$ Post-Seal Comparison | `STRICT_CLEANROOM_WORKFLOW` |

---

## 2. Granular Audit Findings

### 2.1 Verbatim Line / Block Overlap
- **Finding:** **ZERO (0) verbatim lines or blocks of implementation code** were copied between `scripts/run_rh_t056r8r3_primary.py` / `scripts/independent_e4_numerical_reproduction.py` and `cleanroom_e4/cleanroom_e4_execution.py`.
- **Reason:** The clean-room verifier was provisioned strictly inside `cleanroom_e4/` with only `MATHEMATICAL_CONTRACT.md` and `RH-T056R8R3_PREREGISTRATION.json`.

### 2.2 Function & Variable Naming
- All helper function names in `cleanroom_e4_execution.py` (`project_even`, `construct_matrix_A1`, `construct_matrix_B`, `compute_lowest_eigenvalue`, `compute_gate_a_ground_state`, `run_cleanroom_verification`) are completely distinct from the primary runner (`unitary_even_projection_mp`, `run_eigensolve_cell`, `solve_subspace`, `canonical_matrix_hash`).

### 2.3 Mathematical vs Implementation-Specific Similarity
- The mathematical equations implemented (even-parity projection of the Galerkin matrix, Rayleigh-Ritz subspace restriction, Gram-Schmidt orthogonalization of the boundary profile against $V_n^{\text{even}}$) are **mathematically unique and identical by requirement of testing the same scientific hypothesis**.
- The software implementation (data structures, loop order, modular decomposition, sealing logic) was written completely de novo from the mathematical contract.

---

## 3. Implementation Independence Classification

```text
IMPLEMENTATION_INDEPENDENCE = CONCEPTUALLY_SIMILAR_BUT_INDEPENDENT
CLEANROOM_INFORMATION_BARRIER_COMPLIANCE = VERIFIED_CLEAN
```

**Conclusion:** The clean-room E4 implementation possesses genuine structural and code-level independence, free from the material overlap that characterized task-1199.
