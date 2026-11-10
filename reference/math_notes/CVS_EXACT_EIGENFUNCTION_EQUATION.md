# EXACT CVS EIGENFUNCTION OPERATOR EQUATION
**Protocol:** `RH-T055R3 (Task 5)`  
**Classification:** `PROVED_LEMMA` (M5)  

---

## 1. Exact Operator Representation
The infinite-dimensional CvS ground mode $u_c \in H^1_{\text{per}}([-L/2, L/2])$ satisfies the **integro-differential / pseudodifferential equation**:
$$\mathcal{A}_c u_c(t) = \lambda(c) u_c(t),$$
where:
$$\mathcal{A}_c = \mathcal{K}_{\text{Arch}} + \mathcal{P}_{\text{Prime}} - \frac{1}{2} \Pi_0.$$
- $\mathcal{K}_{\text{Arch}} f(t) = \frac{1}{2\pi} \int_{-L/2}^{L/2} \left( \int_{-\infty}^\infty \text{Re}[\psi(1/4 + iu/2)] e^{-i u(t-s)} du \right) f(s) ds$.
- $\mathcal{P}_{\text{Prime}} f(t) = \sum_{p, m} \frac{\log p}{p^{m/2}} e^{i m \log p t} \int_{-L/2}^{L/2} f(s) e^{-i m \log p s} ds$.
- $\Pi_0 f(t) = \int_{-L/2}^{L/2} f(s) ds$.
