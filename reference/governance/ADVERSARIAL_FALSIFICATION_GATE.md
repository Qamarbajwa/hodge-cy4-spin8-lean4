# ADVERSARIAL FALSIFICATION GATE PROTOCOL
**Governing Standard:** `MATHEMATICAL_RESEARCH_CONSTITUTION_v1.0 §7`  

---

## 1. Requirement

Before attempting any lengthy, resource-intensive formal proof, the proposed conjecture or lemma must be subjected to an adversarial falsification sweep.

---

## 2. Standard Counterexample Vectors

1. **Boundary & Degenerate Regimes:** Evaluate proposition at $\lambda \to 1^+$, $N=1$, $\mu \to 0$.
2. **Pathological Non-Local Perturbations:** Construct synthetic non-local kernels violating strict positivity to test if symmetry forces parity ordering.
3. **Finite-Dimensional Low-Rank Analogues:** Test whether low-rank analogues ($2 \times 2$ or $3 \times 3$ matrices) satisfy the property or exhibit counterexamples.
4. **Fourier Oscillatory Exploding Modes:** Check whether high-frequency wave-packets on $[-L/2, L/2]$ violate proposed uniform bounds under scaling $\lambda \to \infty$.

---

## 3. Decision Rule

- If a **mathematically valid counterexample** is discovered:
  - The theorem status is immediately classified as `FALSIFIED_OR_COUNTEREXAMPLE`.
  - The counterexample is logged into the `PROOF_BUG_REGRESSION_REGISTER.yaml`.
  - The target problem scope must be narrowed or retired under governed review before further work.
- If no counterexample is found after exhaustive stress testing:
  - Status is updated to `SURVIVED_ADVERSARIAL_FALSIFICATION` and proof attempts are authorized.
