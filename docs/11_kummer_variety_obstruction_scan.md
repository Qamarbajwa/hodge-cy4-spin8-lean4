# The Kummer Variety Obstruction Scan: Exceptional Divisors and the Weil Class

*Investigation into the desingularized Kummer fourfold $\widetilde{\operatorname{Km}}(A)$ and whether its 256 exceptional algebraic surfaces can generate the Weil class.*

---

## 1. The Kummer Fourfold Architecture

Let $A = \mathbb{C}^4 / \Lambda$ be an abelian fourfold of Weil type ($K = \mathbb{Q}(\sqrt{-d})$).
Consider the inversion involution:
$$\iota: A \to A, \quad x \mapsto -x$$

### 1.1 The Singularities of the Quotient
The quotient variety:
$$\operatorname{Km}_0(A) = A / \{\pm 1\}$$
is the singular Kummer fourfold. Its singular locus consists of the fixed points of $\iota$:
$$\operatorname{Fix}(\iota) = A[2] = \frac{1}{2}\Lambda / \Lambda \cong (\mathbb{Z}/2\mathbb{Z})^8$$
There are exactly:
$$|A[2]| = 2^8 = 256 \text{ isolated singular points}$$
Each singular point $p \in A[2]$ is an ordinary quotient singularity of type $\mathbb{C}^4 / \{\pm 1\}$.

### 1.2 The Smooth Desingularization $X = \widetilde{\operatorname{Km}}(A)$
Blowing up the 256 singular points resolves all singularities:
$$\sigma: X = \widetilde{\operatorname{Km}}(A) \longrightarrow \operatorname{Km}_0(A)$$
The exceptional divisor consists of 256 disjoint projective spaces:
$$E = \bigcup_{p \in A[2]} E_p, \quad \text{where each } E_p \cong \mathbb{P}^3$$

---

## 2. Cohomology of $X = \widetilde{\operatorname{Km}}(A)$

Under the blow-up formula and the double cover correspondence:
$$H^4(X, \mathbb{Q}) \cong H^4(A, \mathbb{Q})^\iota \oplus \bigoplus_{p \in A[2]} H^4(E_p, \mathbb{Q}) \oplus \bigoplus_{p \in A[2]} H^2(E_p, \mathbb{Q})$$

### 2.1 The Exceptional Algebraic Surfaces
Inside each exceptional divisor $E_p \cong \mathbb{P}^3$, the hyperplane section:
$$h_p \in H^2(E_p, \mathbb{Q})$$
corresponds to a complex 2-dimensional algebraic subvariety (an algebraic surface $\mathbb{P}^2 \subset \mathbb{P}^3$) of codimension 2 inside the 4-fold $X$:
$$[h_p] \in H^4(X, \mathbb{Q}) \cap H^{2,2}(X)$$
These yield **256 explicit, indisputably algebraic surfaces** on the Kummer fourfold $X$.

### 2.2 The Involution Action on $H^4(A, \mathbb{Q})$
Because $\iota^*(x) = -x$ on $H^1(A, \mathbb{Q})$, its action on the 4th exterior power is:
$$\iota^*(\alpha_1 \wedge \alpha_2 \wedge \alpha_3 \wedge \alpha_4) = (-\alpha_1) \wedge (-\alpha_2) \wedge (-\alpha_3) \wedge (-\alpha_4) = (-1)^4 \alpha = +\alpha$$
> **Key Fact:** The involution acts as the **identity** on $H^4(A, \mathbb{Q})$!
> Every 4-form on $A$ is $\iota$-invariant:
> $$H^4(A, \mathbb{Q})^\iota = H^4(A, \mathbb{Q})$$
> In particular, the primitive Weil classes $W_0(A)$ are strictly $\iota$-invariant and pull back directly to genuine rational $(2,2)$ Hodge classes on the smooth Kummer fourfold $X$:
> $$\pi^* W_0(A) \subset H^4(X, \mathbb{Q}) \cap H^{2,2}(X)$$

---

## 3. The Kummer Contraction Theorem (The Zero-Escape Hatch)

Let $\pi: \widetilde{A} \to A$ be the blow-up of $A$ at the 256 2-torsion points, and $q: \widetilde{A} \to X$ the unramified double cover away from $E$.
The correspondence between cycles on $X$ and cycles on $A$ is given by the pushforward:
$$\Gamma: H^4(X, \mathbb{Q}) \longrightarrow H^4(A, \mathbb{Q}), \quad \Gamma(\alpha) = \pi_* (q^* \alpha)$$

### 3.1 The Contraction of Exceptional Classes
For every exceptional surface $h_p \subset E_p \cong \mathbb{P}^3$:
$$\Gamma([h_p]) = \pi_* (q^* [h_p]) = 2 \pi_* ([\widetilde{E}_p \cap H])$$
Because $\pi$ collapses the entire exceptional divisor $\widetilde{E}_p$ to the 0-dimensional point $p \in A$:
$$\dim(\pi(\widetilde{E}_p)) = 0 < 2 = \dim(h_p)$$
By fundamental intersection theory:
$$\pi_* ([\widetilde{E}_p \cap H]) \equiv 0 \in H^4(A, \mathbb{Q})$$

$$\Gamma\left( \bigoplus_{p \in A[2]} \mathbb{Q} \cdot [h_p] \right) = \{0\}$$

### 3.2 Orthogonality of the Exceptional Classes to the Weil Class
Under the Poincaré pairing on the smooth Kummer fourfold $X$:
$$\int_X \pi^* w \wedge [h_p] = \int_A w \wedge \Gamma([h_p]) = \int_A w \wedge 0 = 0$$

> [!CRITICAL]
> **Conclusion of the Kummer Scan:**
> 1. The 256 exceptional algebraic surfaces on the Kummer fourfold $X$ are **100% orthogonal** to the Weil class.
> 2. They collapse to 0 on $A$ and **cannot provide any algebraic cycle** representing $W_0(A)$.
> 3. Therefore, resolving the Hodge Conjecture on the Kummer fourfold $X = \widetilde{\operatorname{Km}}(A)$ is **strictly equivalent** to resolving it on the abelian fourfold $A$.
> 4. The Kummer variety offers **no auxiliary algebraic cycles** for the Weil class.
