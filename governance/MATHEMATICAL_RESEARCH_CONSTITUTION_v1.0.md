# MATHEMATICAL RESEARCH CONSTITUTION (v1.0)
## Governing Authority for Problem Identity HODGE-MILLENNIUM-001

**Principal Investigator:** Qamar Munawer (Brandenburg University of Technology Cottbus-Senftenberg)  
**Problem Identity:** `HODGE-MILLENNIUM-001` (Clay Millennium Prize Problem: The Hodge Conjecture)  
**Standing Epistemic Invariant:** `GLOBAL_HODGE_CONJECTURE = OPEN`  
**Standing Formal Invariant:** `S-BRIDGE-DEFORM-CY4 = OPEN`, `S-BRIDGE-SPINOR-MOTIVE = OPEN`  
**Lean 4 Toolchain:** `leanprover/lean4:v4.35.0`, Lake version 5.0.0, Zero Custom Axioms (`axioms: []`)  
**Companion Records:** RH Monograph v2.4.0 (`10.5281/zenodo.24237604`) & v2.5.0 (`10.5281/zenodo.24242053`)

---

## ARTICLE I: THE THREE CARDINAL LAWS OF MATHEMATICAL INQUIRY

### Section 1.01: The Truth Law
No mathematical claim may exceed the verified deductive evidence supporting it.
1. Finite-dimensional coordinate calculations, isolated algebraic variety families (such as the Fermat sextic fourfold $X^4_6$ or CM abelian varieties), heuristic deformations, and numerical certificates constitute rigorous evidence for their specific subdomains, **never** a continuum proof of the universal Clay Millennium Hodge Conjecture across all arbitrary smooth projective complex varieties.
2. Every mathematical assertion must be accompanied by its exact deductive boundary, its precise hypotheses, and its verified counterexample/obstruction analysis.

### Section 1.02: The Identity Law
Problem definitions, quantifiers, domain restrictions, and foundational hypotheses must never drift silently.
1. The canonical Deligne (2000) problem identity:
   $$\operatorname{cl}_X\left(Z^p(X)_{\mathbb{Q}}\right) = \operatorname{Hdg}^{2p}(X) := H^{2p}(X, \mathbb{Q}) \cap H^{p,p}(X)$$
   for every non-singular complex projective variety $X$ and every $0 \le p \le \dim_{\mathbb{C}} X$ is immutable.
2. Proving an algebraic cycle realization for a special subvariety class or along an unobstructed formal deformation while claiming progress on the universal problem without formal reclassification is a **Proof Defect**.
3. All intermediate or conditional progress must be tracked strictly under designated sub-identifiers (`S-BRIDGE-DEFORM-CY4`, `S-BRIDGE-SPINOR-MOTIVE`).

### Section 1.03: The Understanding Law
A mathematical truth is not fully possessed until it is pedagogically and structurally understood. Every major result in this repository must provide a three-level explanation:
1. **Level 1 (Intuitive):** A single-sentence description of the core mathematical mechanism.
2. **Level 2 (Architectural):** A one-page structural proof architecture mapping premises, intermediate syzygies, and obstruction cancellations.
3. **Level 3 (Formal):** A complete, rigorous, byte-verified Lean 4 kernel proof and/or float-free rational/integer certificate.

---

## ARTICLE II: THE ORTHOGONAL EVALUATION TRIAD

Every mathematical claim, lemma, theorem, and bridge proposal is evaluated independently along three non-collapsible axes:

$$\text{Evaluation} = \langle \text{Correctness}, \text{Novelty}, \text{Significance} \rangle$$

### Section 2.01: Correctness Axis
1. `UNCHECKED`: Proposed claim with informal motivation.
2. `INTERNALLY_CHECKED`: Symbolic script or float-free arithmetic verification completed.
3. `VERIFIED`: Kernel-verified in Lean 4.35.0 with empty custom axioms (`axioms: []`).
4. `PROVED_CONDITIONAL`: Formally verified modulo explicit conditional interfaces (`ClassicalHodgeBridgeInterface`).
5. `FALSE_OR_COUNTEREXAMPLE`: Refuted by adversarial auditor or obstruction certificate.

### Section 2.02: Novelty Axis
1. `UNAUDITED`: Prior-art search incomplete.
2. `KNOWN`: Classical result in the literature (e.g., Deligne 1972, Voisin 1992, CDK 1995).
3. `KNOWN_EQUIVALENT`: Reformulation of standard Hodge-theoretic theorems.
4. `POSSIBLY_NEW`: Novel structural decomposition or algorithm without external priority.
5. `AUTHENTICATED_NOVEL`: Independently audited new mathematical construction (e.g., deformed Macaulay apolarity rank stabilization, $W(D_4)$ spinor coset transport, Turán $K_5$ plane coverage).

### Section 2.03: Significance Axis
1. `TECHNICAL_LEMMA`: Local computational or combinatorial helper.
2. `STRUCTURAL_BRIDGE`: Invariant linking disparate mathematical domains (e.g., Lie root operators to Weil divisors, Macaulay apolarity to IVHS kernels).
3. `MAJOR_THEOREM`: Definitive resolution of a major structural bottleneck on a specified variety class.
4. `FOUNDATIONAL_BREAKTHROUGH`: Unconditional resolution of a Millennium Prize Problem. (Status: `NOT_ISSUED`).

---

## ARTICLE III: THE FOUR-TIER EPISTEMIC PARTITION LEDGER

All research publications, manuscripts (`main.tex`), blueprints (`blueprint.tex`), and release bundles must explicitly categorize every assertion into the four-tier ledger:

1. **Tier 1: Unconditional Algebraic & Lie Theorems**  
   Proved purely algebraically, combinatorially, or formally in Lean 4 with strictly zero custom axioms (e.g., Fermat sextic primitive diamond $h^{2,2}_{\text{prim}} = 1751$, four-band split $1001 + 630 + 120 + 0 = 1751$, Gorenstein socle duality in degree 24, Mumford spinor 6/70 zero-weight tuples, $W(D_4)$ triality, Turán $K_5$ bound).
2. **Tier 2: Exact Float-Free $\mathbb{Z}/p\mathbb{Z}$ + CRT & Certified Arithmetic Receipts**  
   Validated by exact integer, rational (`fractions.Fraction`), and multi-prime Chinese Remainder Theorem engines with strictly zero floating-point arithmetic (`scan_forbidden == []`).
3. **Tier 3: Conditional Bridge Equivalences**  
   Formalized as typed implication structures (`ClassicalHodgeBridgeInterface`, `UniversalClayHodgeInterface`) proving that **IF** Bridge A (`effective_hilbert_degree_bound_cy4`) and Bridge B (`kuga_satake_algebraic_cycle_q`) hold, **THEN** global Hodge closure follows.
4. **Tier 4: Lean 4 Kernel Declarations**  
   Formally checked against the Lean 4.35.0 kernel (`[propext, Classical.choice, Quot.sound]`), with all `#print axioms` queries verified empty (`axioms: []`).

---

## ARTICLE IV: CODE AND FLOATING-POINT GUARDRAILS

### Section 4.01: Absolute Zero-Float Mandate
1. In algebraic geometry and Hodge theory, floating-point approximations are an epistemological defect: cohomology classes are rational, intersection numbers are integers, and IVHS ranks are exact natural numbers.
2. The static analysis scanner `toolkit.integrity.scan_forbidden` must return `[]` across all audited mathematical engines. The use of IEEE 754 `float`, `numpy.float64`, or heuristic numerical tolerance thresholds in proof engines is strictly prohibited.

### Section 4.02: Multi-Prime CRT Rank Certification
All large matrix rank determinations (such as the $1751 \times 426$ Macaulay apolarity matrices) must be executed over multiple distinct prime fields $\mathbb{Z}/p\mathbb{Z}$ ($p \in \{65537, 65539, 65543, \dots\}$) and reconstructed via the Chinese Remainder Theorem to guarantee exact determinantal non-vanishing.

---

## ARTICLE V: THREE-ROLE SEPARATION & GOVERNED PUBLICATION

1. **Three-Role Separation:**
   $$\mathrm{WRITER\_ID} \ne \mathrm{REVIEWER\_ID} \ne \mathrm{FINAL\_ACCEPTOR\_ID}$$
   No agent, model, or researcher may review, approve, or certify their own mathematical work.
2. **Release Authorization:**
   `release_authorized = false` and `theorem_progress = UNKNOWN` are permanent standing invariants of the repository until the two open bridges are unconditionally closed and authenticated by external peer review.
3. **Attribution Principle:**
   Scientific credit for all original architectural designs, mathematical theorems, Lean 4 formalizations, and monograph texts belongs solely to **Qamar Munawer** (*Brandenburg University of Technology Cottbus-Senftenberg*).
