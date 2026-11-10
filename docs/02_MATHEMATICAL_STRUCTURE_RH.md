# 02 — The Mathematical Structure Used in the RH Project

> **Honest status:** the project did **not** prove the Riemann Hypothesis (`NO_RH_PROOF = TRUE`).
> What it built is a *rigorous machine for investigating* RH-relevant spectral mechanisms
> (Connes–Consani–Moscovici "CCM" and Connes–van Suijlekom "CvS") **without overclaiming**.
> That machine is what this kit extracts.

## 1. The mathematical chain (the "spine")

```
RH  <=>  positivity of the Weil quadratic form on a test-function window  [-L/2, L/2],  L = log(lambda)
          Q_lambda[f] = Arch[f] + Prime[f] + Pole[f]  >= 0
```

| Piece | Definition used in the project | Role |
|---|---|---|
| Hilbert space | `H = L^2([-1,1])` (even sector `L^2_even`) | where the form lives |
| Archimedean term | kernel of `Re psi(1/4 + it/2)` (digamma) | smooth, indefinite part |
| Prime term | `sum_{p,m} (log p / p^{m/2}) |∫ f(x) e^{i m log p · sqrt(2πc) x} dx|^2 >= 0` | arithmetic part |
| Pole term | `-1/2 |∫ f|^2` (rank-one) | negative perturbation |
| Operator | KLMN / Friedrichs: densely defined closed semibounded form → self-adjoint `Q_c` | gives a genuine spectral problem |
| Ground eigen-equation | `A_c u = λ(c) u`, `A_c = K_Arch + P_Prime − ½Π_0` | the object whose lowest eigenvalue is tracked |
| Prolate/Slepian structure | `μ u(t)=∫ sin(√(2πc)(t−s))/(π(t−s)) u(s) ds`; analyticity strip `δ(c)=sqrt(π/(2c))` | explains why ground state is analytic ⇒ Fourier/Galerkin converges |
| Parity | `[A_λ, J]=0` ⇒ split into even/odd sectors (CCM-SYM) | reduces dimension, isolates ground state |

## 2. Finite → infinite bridge (Galerkin / Rayleigh–Ritz)

1. **Galerkin finite section** `Q_{c,N,T}` — `(2N+1)×(2N+1)` matrix in Fourier basis `e^{ikt}`, `k=-N..N`, prime sum truncated at height `T`.
2. **Even projection** (basis `e0`, `(|k>+|−k>)/√2`) → `(N+1)×(N+1)`.
3. **Competing trial subspaces of equal dimension `n+2`:**
   * **A1** — ordinary Fourier extension: leading principal block.
   * **B** — `V_n^even + span{v⊥}` where `v⊥ ∝ (−1)^k √2 / k²` (the *t²* boundary-correction profile), orthogonalised to `V_n`.
   * controls: **H** (frozen polynomial) and **RAND** (seeded random vector, seed 560803).
4. **Rayleigh–Ritz ground energy** `λ = min eig(V^T Q V)` for each subspace.
5. **Decision statistic** `R_B = λ_B / λ_A1`  (`>1` ⇒ plain Fourier extension is better).
6. Result: `R_B ∈ [10.76, 268.3]` (median 36.5) on all 20 primary cells → the *t²* augmentation was **retired**.

**Why precision matters:** ground energies are ≈ `10^-59`. `float64` destroys them (this killed RH-T056R8). Everything is `mpmath` with `dps ∈ {80,120,160}`, solver `mp.eigsy`.

## 3. Theorem-level structure (what is proved vs open)

| ID | Statement | Status |
|---|---|---|
| CCM-SYM | parity commutation | proved in primary source |
| CCM-A3 | finite-section ground eigenvalue converges (fixed λ>1) | **independently verified, conditional** (compact form embedding + energy convergence + simple limit eigenvalue) |
| Chuk transfer | fixed-window transfer to λ=e^0.8 | pass with limitations |
| CCM-A1/A2 | ground state simple & even | local window `δ>0` exists; quantitative δ, global range **OPEN** |
| CCM-A3N | normalisation bridge `δ_N(ξ)=1 → continuum` | **OPEN** |
| All-L obstruction | unconditional coercivity ∀L ⇔ RH | proved equivalence ⇒ no statistical/mollifier shortcut |
| Finite positivity ⇒ continuum positivity | — | **FALSE** (counter-example: ground state −1/10 with Galerkin values 1/N>0) |

Reading the table is the lesson: *every* line carries (correctness, novelty, significance) separately.

## 4. Load-bearing identities worth reusing
* `Q_even[j,k] = ½(Q[M+j,M+k]+Q[M+j,M−k]+Q[M−j,M+k]+Q[M−j,M−k])`, `Q_even[0,k]=(Q[M,M+k]+Q[M,M−k])/√2`.
* `Q_B[i,n+1] = Σ_{k>n} Q_even[i,k] v⊥[k]`, `Q_B[n+1,n+1] = v⊥ᵀ Q_even v⊥`.
* Variational principle: any restricted energy ≥ true ground energy (used as a calibration gate).
* Finite Galerkin positivity **never** implies continuum positivity without a quantitative lower bound exceeding truncation error.

## 5. Failure ledger that shaped the method (RH-T056 series)

| Protocol | What went wrong | Control now in kit |
|---|---|---|
| T056 | eigenvalues generated from `N^-p` formulas | `check_power_law_fabrication` |
| T056R | duplicated cells, synthetic errors | `find_duplicate_rows` |
| T056R2/R5 | wrong operator (sinc instead of Weil form) | "public oracle only, re-implementation FORBIDDEN" |
| T056R3/R4 | forced monotonicity, hard-coded fixtures | Gate A fixture computed, never hardcoded |
| T056R6 | report said success, CSV said `NO` | `report_vs_csv` |
| T056R8 | float64 corrupted 1e-16 resolution | `scan_forbidden`, precision ladder |
| T056R8R3 | — accepted (E3 + E4 clean-room) | prereg + blind seal + independent re-run |
