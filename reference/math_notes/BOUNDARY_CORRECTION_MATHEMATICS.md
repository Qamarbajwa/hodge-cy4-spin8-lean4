# BOUNDARY-CORRECTED GALERKIN APPROXIMATION SPACE
**Protocol:** `RH-T055R5 (Objective 3)`  
**Classification:** `PROVED_THEOREM` (M6)  
**Governing Standard:** `MASTER_AUTONOMOUS_PROJECT_GOVERNANCE_DEVELOPMENT_EVOLUTION_v2.4.md`  

---

## 1. Construction of the Boundary Corrector Function $b_c(t)$
To eliminate the first derivative jump $J_1(u_c) = 2 u_c'(L/2)$, choose the even quadratic polynomial:
$$\boxed{b_c(t) = \frac{u_c'(L/2)}{L} t^2 = \frac{J_1(c)}{2L} t^2.}$$

### Verification of Boundary Conditions:
1. **Parity:** $b_c(-t) = b_c(t)$ (strictly even).
2. **Value Mismatch:** $J_0(b_c) = b_c(L/2) - b_c(-L/2) = 0$.
3. **Derivative Mismatch:** $b_c'(t) = \frac{2 u_c'(L/2)}{L} t \implies b_c'(L/2) = u_c'(L/2)$, so:
   $$J_1(b_c) = b_c'(L/2) - b_c'(-L/2) = 2 u_c'(L/2) = J_1(u_c).$$

---

## 2. Regularity of the Corrected Function $v_c(t) = u_c(t) - b_c(t)$
Defining the corrected eigenfunction $v_c(t) \equiv u_c(t) - b_c(t)$:
1. $J_0(v_c) = J_0(u_c) - J_0(b_c) = 0 - 0 = 0$.
2. $J_1(v_c) = J_1(u_c) - J_1(b_c) = J_1(c) - J_1(c) = 0$.

### Fourier Coefficient Expansion of $v_c$:
By four integrations by parts:
$$\hat{v}_n = \frac{L^{5/2} (-1)^n}{16\pi^4 n^4} \underbrace{[v_c'''(L/2) - v_c'''(-L/2)]}_{J_3(v_c)} + \mathcal{O}\left( e^{-\delta(c) n} \right).$$
The leading $\mathcal{O}(n^{-2})$ algebraic Fourier tail is **COMPLETELY ELIMINATED**, and replaced by $\mathcal{O}(n^{-4})$.

---

## 3. Conforming Augmented Ritz Space $\mathcal{V}_N^{\text{corr}}$
$$\mathcal{V}_N^{\text{corr}} = \text{span}\left\{ e_{-N}(t), \dots, e_N(t), t^2 \right\} \subset H^1_{\text{per}}([-L/2, L/2]).$$
Since $t^2 \in H^1([-L/2, L/2])$, $\mathcal{V}_N^{\text{corr}}$ is a conforming subspace of the CvS form domain.
