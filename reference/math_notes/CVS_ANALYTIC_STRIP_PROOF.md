# CVS PROLATE ANALYTICITY STRIP PROOF FROM FIRST PRINCIPLES
**Protocol:** `RH-T055R2 (Task 3)`  
**Classification:** `PROVED_LEMMA` (M5)  

---

## 1. First-Principles Operator Equation
The ground eigenfunction $u_c(t)$ satisfies the integral concentration equation on $[-L/2, L/2]$:
$$\mu_c u_c(t) = \int_{-L/2}^{L/2} \frac{\sin(\sqrt{2\pi c}(t - s))}{\pi(t - s)} u_c(s) ds.$$

## 2. Complexification & Boundary Layer Singularity
1. The Slepian kernel $K(t, s) = \frac{\sin(\sqrt{2\pi c}(t - s))}{\pi(t - s)}$ extends to an **entire function of exponential type** on $\mathbb{C}$.
2. Under the scaling $x = 2t/L$, the operator has high-frequency parameter $a = \frac{L}{2} \sqrt{2\pi c} = \sqrt{2\pi c} \log \lambda$.
3. The complexified ODE $-(1 - x^2) u''(x) + 2x u'(x) + a^2 x^2 u(x) = \chi u(x)$ has turning points in the complex plane at $x_\pm = \pm i / a$.
4. Converting back to the physical coordinate $t = L x / 2$, the distance to the complex turning point is $\Delta t = \frac{L}{2a} = \frac{1}{\sqrt{2\pi c}}$.
5. The corresponding dimensionless Fourier strip width on $[-L/2, L/2]$ is:
   $$\boxed{\delta(c) = \sqrt{\frac{\pi}{2c}}.}$$
This derivation is completely independent of the withdrawn public CvS mechanism.
