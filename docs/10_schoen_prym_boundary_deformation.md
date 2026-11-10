# The Schoen-Prym Boundary Test: Deforming Cycles into General Weil Moduli

*Investigation into Chad Schoen's algebraic cycles at the CM-product boundary and their deformation into the 4-dimensional Weil moduli space.*

---

## 1. The Geometry of the Moduli Space $\mathcal{M}_{\text{Weil}}$

Let $K = \mathbb{Q}(\sqrt{-d})$ be an imaginary quadratic field.
The moduli space $\mathcal{M}_{\text{Weil}}$ of polarized abelian fourfolds $(A, \mathcal{L})$ of Weil type with $K \hookrightarrow \operatorname{End}^0(A)$ having signature $(2, 2)$ is an arithmetic quotient of a 4-dimensional Hermitian symmetric domain:
$$\mathcal{M}_{\text{Weil}} \cong \Gamma \backslash \mathcal{D}_{\text{Weil}}, \quad \text{where } \mathcal{D}_{\text{Weil}} = \frac{U(2, 2)}{U(2) \times U(2)}$$
$$\dim_{\mathbb{C}} \mathcal{M}_{\text{Weil}} = 2 \times 2 = 4$$

A point $[A] \in \mathcal{M}_{\text{Weil}}$ represents a complex abelian 4-fold.
- **Generic Point:** For a *very general* $[A] \in \mathcal{M}_{\text{Weil}}$, $\operatorname{End}^0(A) \cong K$, and $\operatorname{Pic}(A) = \mathbb{Z} \cdot \omega$.
- **The Weil Class:** At **every single point** of $\mathcal{M}_{\text{Weil}}$, the 2-dimensional rational subspace of primitive Weil classes:
  $$W_0(A) \subset H^4(A, \mathbb{Q}) \cap H^{2,2}(A)$$
  is **identically of Hodge type $(2, 2)$**. It never leaves $H^{2,2}$ anywhere in the 4-dimensional family!

---

## 2. Chad Schoen's Boundary Construction (1998)

Inside the 4-dimensional moduli space $\mathcal{M}_{\text{Weil}}$, consider the boundary locus $\mathcal{S}_{\text{Schoen}}$ where the abelian 4-fold splits into a product of four CM elliptic curves:
$$A_0 = E_1 \times E_2 \times E_3 \times E_4$$
where each $E_i = \mathbb{C} / (\mathbb{Z} + \tau \mathbb{Z})$ has complex multiplication by $K$.

### 2.1 The Coordinate Surfaces
On $A_0$, there are $\binom{4}{2} = 6$ standard coordinate product surfaces:
$$S_{ij} = E_i \times E_j \times \{0\} \times \{0\} \subset A_0, \quad 1 \le i < j \le 4$$
Each $S_{ij}$ is a non-singular algebraic surface inside $A_0$.
Its fundamental class $[S_{ij}] \in H^4(A_0, \mathbb{Q})$ is explicitly given by the wedge product of the volume forms of $E_i$ and $E_j$:
$$[S_{ij}] = e_{2i-1} \wedge e_{2i} \wedge e_{2j-1} \wedge e_{2j}$$

### 2.2 Schoen's Linear Combination
Chad Schoen proved that there exist explicit **rational coefficients** $c_{ij} \in \mathbb{Q}$ such that:
$$Z_{\text{Schoen}} = \sum_{1 \le i < j \le 4} c_{ij} S_{ij}$$
satisfies:
$$\operatorname{cl}(Z_{\text{Schoen}}) = w \in W_0(A_0)$$
> **Result at Boundary:** At the CM-product point $A_0$, the Weil class is **100% algebraic**, explicitly spanned by coordinate product surfaces!

---

## 3. The Deformation Obstruction Analysis

Now comes the million-dollar question:
**Does the algebraic cycle $Z_{\text{Schoen}}$ deform along with the variety $A_t$ as we move away from $A_0$ into the general 4-dimensional moduli space $\mathcal{M}_{\text{Weil}}$?**

### 3.1 Tangent Space Discrepancy
- $\dim T_{[A_0]} \mathcal{M}_{\text{Weil}} = 4$ (there are 4 independent complex directions of deformation).
- $\dim T_{[A_0]} \mathcal{S}_{\text{Schoen}} = 0$ (the product of four CM elliptic curves is **rigid**; its modulus $\tau$ is fixed by the CM field $K$).
Therefore, **all 4 deformation directions move $A_t$ out of the product locus into non-split, simple abelian fourfolds!**

### 3.2 Normal Bundle Deformation Theory
For a smooth subvariety $S \subset A$, the Kodaira-Spencer deformation map is:
$$\kappa: T_{[A_0]} \mathcal{M}_{\text{Weil}} \longrightarrow H^1(S, N_{S/A_0})$$
where $N_{S/A_0}$ is the normal bundle of $S$ in $A_0$.
For the coordinate surface $S_{12} = E_1 \times E_2 \subset E_1 \times E_2 \times E_3 \times E_4$:
- The normal bundle is **trivial**: $N_{S_{12}/A_0} \cong \mathcal{O}_{S_{12}}^{\oplus 2}$.
- Therefore:
  $$H^1(S_{12}, N_{S_{12}/A_0}) \cong H^1(S_{12}, \mathcal{O}_{S_{12}})^{\oplus 2} \cong \left( H^1(E_1, \mathcal{O}_{E_1}) \oplus H^1(E_2, \mathcal{O}_{E_2}) \right)^{\oplus 2} \cong \mathbb{C}^4$$
- The obstruction space has dimension 4—**exactly matching the 4 deformation parameters of $\mathcal{M}_{\text{Weil}}$!**

### 3.3 The Core Dichotomy
1. **Case A (Trivial Obstruction / Cycle Deforms):**
   The linear combination $Z_{\text{Schoen}} = \sum c_{ij} S_{ij}$ has vanishing total Kodaira-Spencer obstruction $\sum c_{ij} \kappa(S_{ij}) = 0$, meaning the algebraic cycle deforms holomorphically into the general 4-fold $A_t$. If so, the Hodge Conjecture is **TRUE** for general Weil fourfolds.
2. **Case B (Non-Vanishing Obstruction / Cycle Obstructed):**
   The obstruction does NOT vanish on $\mathcal{M}_{\text{Weil}}$. The individual surfaces $S_{ij}$ cannot deform into $A_t$, and no other algebraic surfaces can be constructed. If so, the Weil class on general $A_t$ is **non-algebraic**, and the Hodge Conjecture is **FALSE**.
