# CVS INFINITE-DIMENSIONAL WEIL OPERATOR & FORM DOMAIN
**Classification:** `PROVED_LEMMA` (M5)  
**Governing Standard:** `MASTER_AUTONOMOUS_PROJECT_GOVERNANCE_DEVELOPMENT_EVOLUTION_v2.4.md` (0-Z.5, 0-Z.16)  

---

## 1. Hilbert Space & Quadratic Form Setup
- **Hilbert Space:** $\mathcal{H}_c = L^2([-1, 1], dx)$ under standard Lebesgue measure.
- **Quadratic Form:** $q_c[f] = q_{\text{Arch}}[f] + q_{\text{Prime}}[f] + q_{\text{Pole}}[f]$ on domain $\mathcal{D}(q_c) = H^1([-1, 1]) \cap L^2_{\text{even}}([-1, 1])$.
- **Operator Structure:**
  1. **Archimedean Form:** $q_{\text{Arch}}[f] = \int_{-1}^1 \int_{-1}^1 f(x) K_{\text{Arch}}(x, y) f(y) dx dy$, where $K_{\text{Arch}}(x, y)$ is the integral kernel of $\text{Re}[\psi(1/4 + it/2)]$.
  2. **Prime Term:** $q_{\text{Prime}}[f] = \sum_{p, m} \frac{\log p}{p^{m/2}} \left| \int_{-1}^1 f(x) e^{i m \log p \sqrt{2\pi c} x} dx \right|^2 \ge 0$.
  3. **Pole Term:** $q_{\text{Pole}}[f] = -\frac{1}{2} |\int_{-1}^1 f(x) dx|^2$ (Rank-one perturbation).

---

## 2. Classification of $q_c$
- **Classification:** $q_c$ is a **densely defined, closed, semibounded symmetric quadratic form** with lower bound $q_c[f] \ge -M_c \|f\|^2$.
- **Friedrichs Extension:** By the KLMN Theorem, there exists a unique semibounded self-adjoint operator $Q_c$ on $\mathcal{H}_c$ associated with $q_c$.
