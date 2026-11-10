# Laboratory Requirements and Verification Gates

To evaluate any proposed method, proof strategy, or conceptual framework for the Hodge Conjecture, the following strict criteria and verification gates must be applied.

---

## Gate 1: Coefficient Sensitivity Gate (The Integral Trap)
* **Question:** Does the proposed mechanism depend purely on integral topology or sheaf cohomology with $\mathbb{Z}$ coefficients?
* **Verification Criterion:** If the argument would imply the *integral* Hodge conjecture, it is **guaranteed to be flawed** due to the Atiyah-Hirzebruch counterexamples. The argument must crucially depend on tensoring with $\mathbb{Q}$ (divisibility, rational linear combinations, or $\mathbb{Q}$-motive constructions).

---

## Gate 2: Projectivity Dependency Gate (The Kähler Barrier)
* **Question:** Where does the proof invoke the projective embedding $X \subset \mathbb{P}^N$ or the existence of an ample line bundle $\mathcal{O}_X(1)$?
* **Verification Criterion:** Claire Voisin proved that the Hodge conjecture fails on general compact Kähler manifolds of dimension 4 or higher. Therefore, any valid proof *must* break if $X$ is merely Kähler and not projective. If an analytic or differential geometric argument holds for arbitrary compact Kähler manifolds, it is invalid.

---

## Gate 3: The Higher-Codimension Barrier ($p \ge 2$)
* **Question:** Why does the construction succeed for $p \ge 2$ when the exponential sheaf sequence:
  $$0 \to \mathbb{Z} \to \mathcal{O}_X \to \mathcal{O}_X^\times \to 0$$
  no longer provides an immediate link between $H^{p,p}(X)$ and geometric objects?
* **Verification Criterion:** For $p=1$, line bundles directly yield divisors. For $p=2$, vector bundles only generate classes via Chern classes $c_2(E)$, but $c_2(E)$ does not span all codimension-2 cycles (by Grothendieck / Mumford). The proposed method must explain how it constructs algebraic cycles without relying exclusively on vector bundle Chern classes.

---

## Gate 4: Functoriality and Deformation Check
* **Question:** How does the proposed cycle construction behave under continuous deformation of complex structure?
* **Verification Criterion:** By the Cattani-Deligne-Kaplan theorem, the locus in the moduli space of varieties where a given Hodge class remains of type $(p,p)$ (the Hodge locus) is an algebraic subvariety. The constructed cycles must vary compatibly with the variation of Hodge structure (VHS).

---

## Gate 5: Concrete Testbeds (Verification Benchmarks)
Any general technique must be testable and confirmable on classic benchmark cases:
1. **Fourfolds ($n=4, p=2$):** Complete intersections in $\mathbb{P}^5$, Fermat fourfolds $x_0^d + \dots + x_5^d = 0$.
2. **Abelian Fourfolds:** Products of elliptic curves $E_1 \times E_2 \times E_3 \times E_4$ and abelian varieties of Weil type.
3. **Calabi-Yau Fourfolds:** Holomorphic symplectic manifolds / hyperkähler fourfolds.
