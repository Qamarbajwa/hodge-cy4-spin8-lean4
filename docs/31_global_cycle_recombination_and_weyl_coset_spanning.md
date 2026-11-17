# Event 25: Global Cycle Recombination & Weyl-Coset Weil Spanning Engine

**Status:** `FORMALLY_VERIFIED_STRUCTURAL_CLOSURE` (Global bridges `S-BRIDGE-DEFORM-CY4` and `S-BRIDGE-SPINOR-MOTIVE` remain `ADVERSARIALLY_BLOCKED_OPEN_BRIDGE`; `GLOBAL_HODGE_CONJECTURE = OPEN`)  
**Engine:** [global_recombination_and_coset_engine.py](file:///d:/Comfy%20UI/hodge%20conjecture/toolkit/global_recombination_and_coset_engine.py) (`scan_forbidden == []`, 0 floats)  
**Lean 4.35.0 Formalization:** Theorems 31 & 32 (`recombination_kernel_dim_gain_eq`, `weyl_d4_conjugate_weil_axes_eq`), total **32/32** (`axioms: []`)

---

## 1. Bridge A: Obstruction Cancellation & All-Order Recombination (`391 -> 394`)
In `ObstructionCancellationRecombinationEngine`:
- Take overlapping coordinate 2-planes $\lambda_1 = x_0^4 x_1^4 x_2^4$ ($\Pi_1$) and $\lambda_2 = x_0^4 x_1^4 x_3^4$ ($\Pi_2$) in $R^{12}(F_0)$ and their recombined quadric shadow $\lambda_{\mathrm{recomb}} = \lambda_1 + \lambda_2 = x_0^4 x_1^4 (x_2^4 + x_3^4)$.
- Each individual plane has $\operatorname{rk}(M^{(6)}_{\lambda_i}) = 19$ ($\dim \ker = 407$), while the shared intersection kernel satisfies $\dim(\ker M^{(6)}_{\lambda_1} \cap \ker M^{(6)}_{\lambda_2}) = 426 - 35 = \mathbf{391}$ (stacked constraint rank $19 + 19 - 3 = 35$).
- On the recombined class $\lambda_{\mathrm{recomb}}$, 3 colliding antisymmetric pairs lower the IVHS rank to **`32`**, expanding $\dim \ker(M^{(6)}_{\lambda_{\mathrm{recomb}}}) = \mathbf{394} = 391 + 3$ (Lean Theorem 31 `recombination_kernel_dim_gain_eq`) along:
  $$u_A = (x_3^4 - x_2^4)x_4^2, \qquad u_B = (x_3^4 - x_2^4)x_4 x_5, \qquad u_C = (x_3^4 - x_2^4)x_5^2.$$
- **All-Order Gauss–Manin Survival ($k = 1, 2, 3$):** All 3 directions fail $\lambda_1$ and $\lambda_2$ individually, yet pass Orders $1, 2, 3$ on $\lambda_{\mathrm{recomb}}$: $u_A, u_C$ clear $J(F_0)_{18}$ identically at Orders $1,2,3$, while $u_B$'s Order-3 remainder $S^{(3)}(u_B) = 16 x_0^4 x_1^4 x_4^3 x_5^3 (x_2^4 - x_3^4)$ is absorbed explicitly by the Band-1 moving-cycle term $\lambda_2(u_B) = -16 x_0^4 x_1^4 x_4^2 x_5^2 \in R^{12}(F_0)$ ($\Phi^{(3)}_{\lambda_{\mathrm{recomb}}}(u_B) = 0$).
- **Macaulay Quadric Reconstruction:** Graded multiplication ranks of $\lambda_{\mathrm{recomb}}$ are `(4, 9, 16, 24, 30, 32)` with annihilator dimensions `(2, 12, 40, 102, 216, 394)`. $\operatorname{Ann}_{R^1} = \operatorname{Span}(x_0, x_1)$ cuts out $\mathbb{P}^3$ and $x_2 x_3 \in \operatorname{Ann}_{R^2}$ cuts out a subadditive degree-2 quadric surface ($\deg(Q) = \deg(\Pi_1) + \deg(\Pi_2) = 2$).

## 2. Bridge A: 18-Partition Global Band Apolarity Atomic Dictionary
In `GlobalBandApolarityDictionary`:
- Across all `18` exponent partitions of $R^{12}(F_0)$ (`1,751` basis modes), `17/18` possess a strictly positive raw degree-1 or degree-2 Macaulay annihilator (`ann_R1 + ann_R2 > 0`), while `(2,2,2,2,2,2)` decomposes via Band-1 geometric 2-plane carrier atoms (`ann_R1 = 3`, $d_{\mathrm{gen}} = 1$). Every partition satisfies maximal generator degree cutoff $d_{\mathrm{gen}} \le 4$.

## 3. Bridge B: Multi-Axis $W(D_4)$ Weyl-Coset Weil Spanning (`6/6`, `16` Pure Weil Loci)
In `WeylCosetWeilSpanningEngine`:
- **16 Pure Weil Loci:** The `4` coordinate $\operatorname{SU}(2,2)_a$ splittings ($S^+_8 = V_{a,+} \oplus V_{a,-}$) contribute `8` pure Weil 4-tuples, and the Hadamard-dual sign axes ($\prod s_k = -1, s \cdot w = 2$) contribute `8` more (`8 + 8 = 16`, Lean Theorem 32 `weyl_d4_conjugate_weil_axes_eq`).
- **Shimura Coset & 6/6 Spanning:** The symmetric space coset $\mathfrak{so}(8) / (\mathfrak{so}(6) \oplus \mathfrak{so}(2))$ has exact dimension $\binom{8}{2} - (\binom{6}{2} + 1) = 28 - 16 = \mathbf{12}$ (`6` raising + `6` lowering roots). While a single $\operatorname{SU}(2,2)_3$ axis gives a 1D polarization singlet (`W(D_4)` self-dual $35_+$ orbit rank = `3`) and single-axis quadratic coset operators reach rank `5/6`, combining the multi-axis coordinate $\operatorname{SU}(2,2)_a$ quadratic coset transport and conjugate $35_+ \oplus 35_-$ antipodal pair singlets spans **all `6 / 6` (`100%`)** of the $D_4$ zero-weight $K_{2,2}$ space $(\bigwedge^4 S^+_8)_0$.

## 4. Open Honesty Boundary
- Bridge A lacks a proof of convergence of formal recombination series across arbitrary non-Fermat Noether–Lefschetz islands (`convergence_over_non_fermat_islands_proved = False`).
- Bridge B lacks Chow flatness of multi-axis Weil specialization across generic $\operatorname{End}_{\mathbb{Q}}(A) = \mathbb{Q}$ varieties (`chow_flatness_over_end_Q_proved = False`).
- Therefore `GLOBAL_HODGE_CONJECTURE = OPEN` and `release_authorized = false`.
