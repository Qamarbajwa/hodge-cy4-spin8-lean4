# Hodge Conjecture Computational Experiment Toolkit & Combinatorial Lean 4 Checks (Edition 1.0.0)
**Project:** Computational Apolarity Experiments, $W(D_4)$ Spinor Combinatorics, and Decidable Lean 4.35.0 Finite Checks for Hodge Conjecture Testbeds  
**Author:** Qamar Munawer (Brandenburg University of Technology Cottbus-Senftenberg)  
**Governance:** MATH-GOV v0.7.0  
**Date:** 2026-11-15  
**Standing Epistemic Invariant:** `GLOBAL_HODGE_CONJECTURE = OPEN`  
**Active Bridge Frontiers:** `S-BRIDGE-DEFORM-CY4 = OPEN` | `S-BRIDGE-SPINOR-MOTIVE = OPEN`  

---

## 1. Absolute Scientific Honesty & Modest Scope Principle
The Clay Millennium Hodge Conjecture remains strictly **OPEN**. Neither this repository nor the accompanying documents claim, imply, or approach a global proof of the Hodge Conjecture.

### What This Repository Actually Is
1. **Exact Rational & Modular ($\mathbb{F}_p$) Computational Experiment Toolkit on Sextic Fourfolds & Spinor Weights:** The Python toolkit in `toolkit/` implements exact integer, `fractions.Fraction`, and 61/62-bit modular (`pow(a, p - 2, p)`) computational experiments on the Fermat sextic Calabi–Yau fourfold $X^4_6 \subset \mathbb{P}^5$ ($R^{12}(F_0)$ of dimension $1,751 = 1001 + 630 + 120 + 0$), first- and higher-order infinitesimal deformation/Macaulay apolarity linear algebra, Peskine–Szpiro liaison degree examples, and finite weight-tuple combinatorics for $\bigwedge^4 S^+_8$.
2. **Decidable Finite Combinatorial Checks in Core Lean 4.35.0 (`HodgeVerification.lean`):** `HodgeVerification.lean` has **zero Mathlib imports** and consists strictly of **43 decidable finite combinatorial and degree-counting checks (`by rfl`)** verifying index sets, weight counts, and polynomial-ring dimensions (`axioms: []`). It does **NOT** formalize schemes, sheaves, algebraic cycles, cohomology, or Hodge theory.
3. **Proper Attribution of Classical Mathematical Results:** All foundational theorems referenced or experimentally instantiated in this toolkit belong to their original authors:
   - **Griffiths (1969):** Jacobian ring residue representation $H^{4-q,q}_{\mathrm{prim}}(X) \cong R^{(q+1)d - (n+2)}(F)$ of smooth hypersurface cohomology;
   - **Shioda (1979), Aoki, & Ran:** Inductive Fermat cycle decomposition and the $1001 + 630 + 120 + 0 = 1751$ Fermat sextic fourfold spectrum;
   - **Macaulay (1916):** Inverse systems and Artinian Gorenstein apolarity duality;
   - **Peskine & Szpiro (1974):** Liaison theory for projective subschemes;
   - **Deligne (1982) & André (1996):** Absolute Hodge cycles and motivated cycles in Kuga–Satake / Spin(8) theory;
   - **Wang (1981) & Chinese Remainder Theorem:** Exact modular rational reconstruction over finite fields $\mathbb{F}_p$.

---

## 2. Quick-Start Offline Verification Commands
To verify the computational test suite and finite Lean 4 checks offline:

```bash
# 1. Automated audit (zero-float static check, exact rational/F_p replay, 43 Lean checks, DAG & manifest):
python verify_zenodo_deposit.py --fast

# 2. Run the pytest suite:
pytest -q

# 3. Run the 43 decidable finite combinatorial checks in Lean 4.35.0 (zero Mathlib required):
cd examples/math_gov/LeanDemoProject && lake env lean HodgeVerification.lean
```

---

## 3. Release Directory & Manuscript Structure
- `ZENODO_RELEASE_v1.0.0/` (11 files): Public Zenodo deposit archive (PDFs, audit report, source zips, figure, metadata, and `SHA256SUMS.txt`).
- `paper/main.tex` & `01_Monograph_Hodge_Conjecture_CY4_Spinor_Qamar_Munawer_v1.0.0.pdf`: Expository monograph documenting the computational experiments and open bridges.
- `paper/blueprint.tex` & `02_LeanBlueprint_Hodge_Formal_Verification_Qamar_Munawer_v1.0.0.pdf`: Index of the 43 decidable finite Lean 4 checks.
- `06_Hodge_Diamond_and_WD4_Coset_Transport_Visual.png`: Architecture summary figure.

---

## 4. AI Assistance Disclosure
Large language model (LLM) coding and writing assistants were used during the development of this repository to draft Python experimental scripts, structure Lean 4 decidable finite checks, assist with LaTeX formatting and exposition, and maintain repository test harnesses. All mathematical statements, attributions, and exact numerical/Lean kernel outputs were reviewed and verified deterministically via exact rational/modular arithmetic and `lake env lean` under strict authorial supervision.

---

## 5. Citation and License
```bibtex
@software{Munawer_Hodge_Experiments_2026,
  author    = {Munawer, Qamar},
  title     = {Computational Apolarity Experiments, W(D4) Spinor Combinatorics, and Decidable Lean 4.35.0 Finite Checks for Hodge Conjecture Testbeds},
  year      = {2026},
  publisher = {Zenodo},
  version   = {1.0.0},
  note      = {Standing Invariant: GLOBAL_HODGE_CONJECTURE = OPEN}
}
```
License: Creative Commons Attribution 4.0 International (CC-BY-4.0).
