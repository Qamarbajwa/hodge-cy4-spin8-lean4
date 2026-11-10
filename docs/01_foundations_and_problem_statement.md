# Laboratory Foundation: The Hodge Conjecture

## 1. Formal Setup

Let $X$ be a non-singular (smooth), projective, complex algebraic variety of complex dimension $n$.

### 1.1 Cohomology and Hodge Decomposition
Via the de Rham theorem and Hodge theory on compact Kähler manifolds:
$$H^k(X, \mathbb{C}) \cong H^k_{\text{dR}}(X) \cong \bigoplus_{p+q=k} H^{p,q}(X)$$
where $H^{p,q}(X)$ is represented by harmonic differential forms of type $(p,q)$, satisfying:
$$\overline{H^{p,q}(X)} = H^{q,p}(X)$$

### 1.2 Hodge Classes
The rational Hodge classes of codimension $p$ (cohomological degree $2p$) are:
$$\operatorname{Hdg}^{2p}(X) = H^{2p}(X, \mathbb{Q}) \cap H^{p,p}(X)$$
where $H^{2p}(X, \mathbb{Q}) \subset H^{2p}(X, \mathbb{C})$ via the natural comparison isomorphism:
$$H^{2p}(X, \mathbb{Q}) \otimes_{\mathbb{Q}} \mathbb{C} \cong H^{2p}(X, \mathbb{C})$$

### 1.3 Algebraic Cycles
An algebraic cycle of codimension $p$ is a formal linear combination:
$$Z = \sum_{i} c_i Z_i$$
where $Z_i \subset X$ are irreducible closed algebraic subvarieties of complex codimension $p$.
- $\mathcal{Z}^p(X)$: Group of algebraic cycles of codimension $p$ with integer coefficients.
- $\mathcal{Z}^p(X)_{\mathbb{Q}} = \mathcal{Z}^p(X) \otimes_{\mathbb{Z}} \mathbb{Q}$: Group with rational coefficients.

### 1.4 The Cycle Class Map
There exists a cycle class map:
$$\operatorname{cl}_X: \mathcal{Z}^p(X)_{\mathbb{Q}} \to H^{2p}(X, \mathbb{Q})$$
Integration of closed forms over the smooth locus of $Z_i$ proves that:
$$\operatorname{image}(\operatorname{cl}_X) \subseteq \operatorname{Hdg}^{2p}(X) = H^{2p}(X, \mathbb{Q}) \cap H^{p,p}(X)$$

## 2. Statement of the Hodge Conjecture
$$\operatorname{cl}_X\left(\mathcal{Z}^p(X)_{\mathbb{Q}}\right) = \operatorname{Hdg}^{2p}(X)$$
Equivalently: Every rational cohomology class of type $(p,p)$ on a smooth complex projective variety is a $\mathbb{Q}$-linear combination of the cohomology classes of algebraic subvarieties.
