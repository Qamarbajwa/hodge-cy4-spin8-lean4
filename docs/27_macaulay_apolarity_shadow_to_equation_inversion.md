# 27. Macaulay Apolarity Inverse Engine (Shadow-to-Equation Reconstruction)

**Project:** `HODGE-MILLENNIUM-001` (`MATH-GOV v0.7`, Branch `candidate/math-gov-v0.6`)  
**Scope:** Inverting cohomology shadows $\lambda \in R^{12}(F_0)$ on the Fermat sextic Calabi–Yau fourfold $X^4_6 \subset \mathbb{P}^5$ back into explicit polynomial ideals $I_Z$ via `toolkit/macaulay_apolarity_inverse_engine.py`, Theorems 23 & 24 in `lean_blueprint/HodgeVerification.lean`, and governance closure in `toolkit/hodge_proof_closure_reviewer.py`.  
**Millennium Honesty Boundary:** `GLOBAL_HODGE_CONJECTURE = OPEN`, `release_authorized = false`, `theorem_progress = "UNKNOWN"`.

---

## 1. Executive Summary

Using Macaulay's Gorenstein apolarity correspondence for the Fermat sextic Jacobian ring $R(F_0) = \mathbb{Q}[x_0, \dots, x_5]/(x_0^5, \dots, x_5^5)$, any degree-12 primitive cohomology shadow $\lambda \in R^{12}(F_0) \cong H^{2,2}_{\mathrm{prim}}(X^4_6)$ induces a graded multiplication tower
$$M^{(m)}_\lambda : R^m(F_0) \longrightarrow R^{12+m}(F_0), \qquad m \in \{1, 2, 3, 4, 5, 6\}.$$
Its exact rational nullspaces $\operatorname{Ann}_{R^m}(\lambda) = \ker(M^{(m)}_\lambda)$ recover the defining equations of the underlying algebraic cycles:
- A single 2-plane $\lambda_\Pi = x_0^4 x_1^4 x_2^4$ yields $\dim \operatorname{Ann}_{R^1}(\lambda_\Pi) = 3$, recovering the exact linear ideal $(x_0, x_1, x_2)$ with zero false positives.
- A signed difference of disjoint 2-planes $\lambda_{\mathrm{signed}} = x_0^4 x_1^4 x_2^4 - x_3^4 x_4^4 x_5^4$ cancels degree-1 annihilators ($\dim \operatorname{Ann}_{R^1} = 0$), while degree-2 apolarity recovers all $3 \times 3 = 9$ cross-product quadrics $x_i x_j$ ($i \in \{0,1,2\}, j \in \{3,4,5\}$) spanning $I_+ \cdot I_-$.
- Optimizing the Apolar Sparse Decomposition score recovers $(\lambda_+, \lambda_-)$ cleanly across signed classes and audits all `18/18` partitions (`1,751` modes) across Band 1 (`10/10` 2-plane classes), Band 2 (`6/6` Shioda $3+3$ joins), and Band 3 (`2/2` Lefschetz $2+4$ joins).

---

## 2. Module 1: The Graded Macaulay Multiplication Tower (`MacaulayApolarityTower`)

| Degree $m$ | Domain $\dim R^m(F_0)$ | Codomain $\dim R^{12+m}(F_0)$ | $\lambda_\Pi$ ($\operatorname{rk} / \dim \operatorname{Ann}$) | $\lambda_{\mathrm{signed}}$ ($\operatorname{rk} / \dim \operatorname{Ann}$) |
| :---: | :---: | :---: | :---: | :---: |
| $1$ | $6$ | $1,686$ | $3 \;/\; 3$ | $6 \;/\; 0$ |
| $2$ | $21$ | $1,506$ | $6 \;/\; 15$ | $12 \;/\; 9$ |
| $3$ | $56$ | $1,246$ | $10 \;/\; 46$ | $20 \;/\; 36$ |
| $4$ | $126$ | $951$ | $15 \;/\; 111$ | $30 \;/\; 96$ |
| $5$ | $246$ | $666$ | $18 \;/\; 228$ | $36 \;/\; 210$ |
| $6$ | $426$ | $426$ | $19 \;/\; 407$ | $38 \;/\; 388$ |

All computations use sparse exact rational Gaussian elimination over $\mathbb{Q}$, cross-checked against full dense `Fraction` multiplication matrices (`scan_forbidden == []`).

---

## 3. Module 2: Signed Difference Decomposer & 18-Partition Audit (`SignedShadowDecomposer`)

Given $\lambda \in R^{12}(F_0)$, the decomposer solves $\lambda = \lambda_+ - \lambda_-$ with positive components $\lambda_+, \lambda_-$ maximizing
$$\operatorname{Score}(\lambda_+, \lambda_-) = \dim \operatorname{Ann}_{R^1}(\lambda_+) + \dim \operatorname{Ann}_{R^1}(\lambda_-) + \dim \operatorname{Ann}_{R^2}(\lambda_+) + \dim \operatorname{Ann}_{R^2}(\lambda_-).$$
- **Disjoint 2-Planes ($\lambda_{\mathrm{signed}}$):** Recovers $\lambda_+ = x_0^4 x_1^4 x_2^4$ and $\lambda_- = x_3^4 x_4^4 x_5^4$ with optimal score $3 + 3 + 15 + 15 = 36$, extracts primary linear ideals $I_+ = (x_0, x_1, x_2)$ and $I_- = (x_3, x_4, x_5)$, and verifies $I_+ \cdot I_- == \operatorname{Ann}_{R^2}(\lambda_{\mathrm{signed}})$ of exact dimension `9`.
- **Exhaustive 18-Partition Check:**
  - `18/18` partitions (`17` maximally separated orbit difference pairs + balanced center `(2,2,2,2,2,2)` via Band-1 2-plane carrier lift) reconstruct exactly.
  - **Band 1 (`10/10` partitions, `1,001` modes):** Each pairs into three disjoint linear binomials $(x_{i_r} - x_{j_r})$ annihilated in $R^1(F_0)$ (`dim Ann_{R^1} = 3`).
  - **Band 2 (`6/6` partitions, `630` modes):** Each admits a `3+3` Shioda cone/join split `(9, 3)` whose apolar carrier $Q_S(x_S) \cdot x_{S^c}^{b}$ achieves `dim Ann_{R^1} >= 2` (recovering the defining $\mathbb{P}^3$ hull equations).
  - **Band 3 (`2/2` partitions, `120` modes):** Factors cleanly into `(2,2)` $\times$ $R^8(\mathbb{P}^3) \cong H^{1,1}_{\mathrm{prim}}(X^2_6)$.

---

## 4. Module 3: Effective Degree Bound Estimator (`EffectiveDegreeEstimator`)

From the graded rank vector $\mathbf{r}(\lambda) = (r_1, \dots, r_6)$, the symmetric Gorenstein Hilbert vector $H_{A_\lambda}(0\dots 12) = (1, r_1, \dots, r_6, \dots, r_1, 1)$ satisfies **Macaulay's Growth Theorem** $r_{m+1} \le r_m^{\langle m \rangle}$ at every degree $m = 1, \dots, 5$:
- **Single 2-Plane $\lambda_\Pi$:** Pre-Jacobian Hilbert function $(3, 6, 10, 15) = \binom{t+2}{2}$ achieves equality $r_{m+1} = r_m^{\langle m \rangle}$ for $m=1,2,3$ (Gotzmann persistence), yielding Gotzmann number **$G = 1$** and minimal generator cutoff $d_{\mathrm{gen}} = 1$.
- **Signed Disjoint Pair $\lambda_{\mathrm{signed}}$:** Pre-Jacobian Hilbert function $(6, 12, 20, 30) = 2\binom{t+2}{2}$ yields Gotzmann decomposition $[2, 2, 1, 0, 0]$ with Gotzmann number **$G = 5$** and minimal generator cutoff $d_{\mathrm{gen}} = 2$.
- **Bridge A Honesty Boundary:** While Fermat apolar ideals are regularity-bounded ($\operatorname{reg}(A_\lambda) \le 12$ at socle degree 12, and $G=1, 5$ in sub-Jacobian degrees), **no effective upper bound on $\operatorname{Hilb}_D(X_t)$ is known for non-Fermat fibers $X_t$** (`general_fiber_hilbert_bound_known = False`), leaving Bridge A (`S-BRIDGE-DEFORM-CY4`) strictly **`ADVERSARIALLY_BLOCKED_OPEN_BRIDGE`**.

---

## 5. Lean 4.35.0 Kernel Proofs (`24/24`, `axioms: []`)

Two new zero-axiom theorems in `lean_blueprint/HodgeVerification.lean` and `examples/math_gov/LeanDemoProject/HodgeVerification.lean`:
- **Theorem 23 (`macaulay_annihilator_dim_bound`):** Evaluates $M^{(1)}_{P_\Pi}$ across `r1_monomials` modulo $(x_0^5,\dots,x_5^5)$ and proves $\dim R^1(F) = 6$, $\operatorname{rk}(M^{(1)}_{P_\Pi}) = 3$, and $\dim \operatorname{Ann}_{R^1}(P_\Pi) = 6 - 3 = 3$ (`by rfl`, `axioms: []`).
- **Theorem 24 (`signed_difference_ideal_intersection`):** Evaluates all `21` degree-2 monomials and `3 x 3 = 9` cross-product quadrics of $I_+ = (x_0, x_1, x_2)$ and $I_- = (x_3, x_4, x_5)$, proving $\dim \operatorname{Ann}_{R^1}(\lambda_{\mathrm{signed}}) = 0$ and $\dim \operatorname{Ann}_{R^2}(\lambda_{\mathrm{signed}}) = 9$ (`by rfl`, `axioms: []`).
