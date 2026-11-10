# RH-T056R8R3 — Clean-Room Mathematical Contract

## Protocol
Protocol ID: `RH-T056R8R3`  
Title: PUBLIC-CVS MULTI-CELL BOUNDARY-AUGMENTATION FALSIFICATION GRID

## Public Operator Oracle
Package: `connes-cvs == 0.3.1`  
Install: `pip install connes-cvs==0.3.1`  
Import: `from connes_cvs import build_galerkin_matrix, compute_ground_state`

The function `build_galerkin_matrix(c, N, T, dps)` returns a `(2N+1) x (2N+1)` mpmath matrix `Q_{c,N,T}` — the Galerkin finite-section matrix of the Connes–van Suijlekom operator.

**CUSTOM_CVS_OPERATOR_REIMPLEMENTATION IS FORBIDDEN.** The verifier must obtain all operator finite sections from the authenticated public package.

## Precision Requirements
- Pure `mpmath` arbitrary precision (initial `dps = 80`).
- Solvers: `mpmath.eigsy` or `compute_ground_state`.
- Strict Prohibition: `float`, `numpy.float64`, `scipy.linalg.eigh`, custom synthetic operators.

## Mathematical Subspace Definitions

### Even Unitary Projection
Given full Galerkin matrix `Q_full` of dimension `(2M+1) x (2M+1)` (with frequency indices `-M, ..., 0, ..., M`, center at index `M`):
The even-parity subspace has dimension `M+1` with basis:
- `e_0 = |0>` (zero frequency, row/col index `M`)
- `e_k = (|k> + |-k>) / sqrt(2)` for `k = 1, ..., M`

The projected matrix `Q_even` has entries:
```
Q_even[0, 0] = Q_full[M, M]
Q_even[0, k] = (Q_full[M, M+k] + Q_full[M, M-k]) / sqrt(2)       for k >= 1
Q_even[k, 0] = Q_even[0, k]
Q_even[j, k] = 0.5 * (Q_full[M+j, M+k] + Q_full[M+j, M-k] + Q_full[M-j, M+k] + Q_full[M-j, M-k])   for j,k >= 1
```
Symmetrize: `Q_even[i,j] = 0.5 * (Q_even[i,j] + Q_even[j,i])`.

### Subspace A1: Standard One-Step Fourier Extension
- Dimension: `n_inner + 2` (indices `0, 1, ..., n_inner + 1` in the even basis)
- Subspace matrix `Q_A1`: top-left `(n_inner + 2) x (n_inner + 2)` principal submatrix of `Q_even`.
- Ground eigenvalue: `lambda_A1 = min(eigvals(Q_A1))`.

### Subspace B: Single t^2 Boundary Augmentation
- Equal dimension to A1: `dim = n_inner + 2`.
- Augmented basis: `V_n^even + span{v_perp}`, where `V_n^even` has dimension `n_inner + 1` (indices `0, ..., n_inner`).
- The unnormalized t^2 boundary profile in the even basis has coefficients:
  `a_k = (-1)^k * sqrt(2) / k^2` for `k = 1, ..., M_outer`, and `a_0 = 0`.
- Orthogonal projection onto the orthogonal complement of `V_n^even`:
  `a_perp[k] = 0` for `k = 0, ..., n_inner`, and `a_perp[k] = a_k` for `k = n_inner + 1, ..., M_outer`.
- Normalized vector: `v_perp = a_perp / sqrt(sum(x^2 for x in a_perp))`.
- Subspace matrix `Q_B` of size `(n_inner + 2) x (n_inner + 2)`:
  - Top-left `(n_inner + 1) x (n_inner + 1)` block: `Q_even[i, j]` for `i, j in 0..n_inner`.
  - Border cross-terms: `Q_B[i, n_inner + 1] = sum_{k=n_inner + 1}^{M_outer} Q_even[i, k] * v_perp[k]` for `i in 0..n_inner`.
  - `Q_B[n_inner + 1, i] = Q_B[i, n_inner + 1]`.
  - Diagonal corner self-energy: `Q_B[n_inner + 1, n_inner + 1] = sum_{j, k = n_inner + 1}^{M_outer} v_perp[j] * Q_even[j, k] * v_perp[k]`.
- Ground eigenvalue: `lambda_B = min(eigvals(Q_B))`.

### Ratio & Decision Metric
`R_B = lambda_B / lambda_A1`
- `R_B > 1.0` -> `FOURIER_EXTENSION_LOWER`
- `R_B < 1.0` -> `T2_EXTENSION_LOWER`
- Unresolved / unstable -> `NUMERICALLY_UNRESOLVED`

## Gate A: Public Reference Fixture
- `c = 13, N = 80, T = 400`
- Precision ladder: `dps in {80, 120, 160}`
- Reference ground state eigenvalue: `2.5282661401965756026859551460395357984852932822457493202998634125895744410943922e-59`
- Tolerance: relative error `< 1e-15` across all tiers.

## Gate B: Predecessor Calibration
- `c = 13, n = 10, M = 20, T = 400, dps = 80`
- Requires `R_B > 1.0` (expected calibration `~51.25`).
- Do NOT hardcode the ratio as an input.

## Primary 20-Cell Grid ($T=400, M_{\text{outer}} = \max(20, 2n)$)
- `c in {9, 11, 13, 15, 17}`
- `n_inner in {6, 8, 10, 12}`
- All 20 cells evaluated at `dps = 80`.
