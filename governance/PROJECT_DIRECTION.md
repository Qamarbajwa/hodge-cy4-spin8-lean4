# PROJECT DIRECTION — HODGE CONJECTURE RESEARCH (BINDING RECORD)

**Status: BOUND_TO_ORIGINAL_INTENT.**  
This binding document ties the MATH-GOV v0.6 governance framework directly to the owner's original research question and verified baseline registers.

---

## 1. Owner-Authenticated Binding Fields
- **project_id:** `HODGE-MILLENNIUM-001`
- **problem_name:** `The Hodge Conjecture`
- **canonical_statement:** "Let X be a non-singular (smooth) complex projective algebraic variety of complex dimension n. For any integer 0 <= p <= n, every rational cohomology class of type (p,p), i.e., alpha in H^{2p}(X, Q) cap H^{p,p}(X), is a Q-linear combination of the cohomology classes of algebraic subvarieties of X of complex codimension p."
- **primary_source:** "Clay Mathematics Institute Millennium Prize Problem Statement: Pierre Deligne, 'The Hodge Conjecture' (2000)"
- **owner_original_prompt_archive_ref:** `governance/PROBLEM_IDENTITY_REGISTER.yaml`
- **owner_original_prompt_sha256:** `e829cd38fb13386aa93532397d4f0267c269a3059b7dbce3791edba08434ee05`
- **owner_approved_intent_ref:** `governance/PROJECT_INTENT.md`
- **owner_approved_intent_sha256:** `a7c6b7335cbefb9259d01c93b48f34300165824959a3f105a9cc1a389cbb45ec`
- **formal_target_source_ref:** `lean_blueprint/HodgeVerification.lean`
- **formal_target_sha256:** `b5c018dae146301be274a14312440114960aebb43411d02d104031be68d1023b`
- **foundation/logic/axiom_allowlist:** `["propext", "Classical.choice", "Quot.sound"]`
- **repo/branch:** `candidate/math-gov-v0.6`
- **read/write_grant_scopes:** `supervisor: read/dispatch; workers: branch-isolated writes; reviewer: read-only; acceptor: independent external authority`
- **Lean_toolchain_version:** `leanprover/lean4:v4.35.0 (Lake version 5.0.0)`
- **retention/privacy/security_policy:** `Local laboratory workspace, no private exfiltration, all evidence preserved on-disk`

---

## 2. Research Objectives
1. **Preserve and Understand Original Intent:** Maintain byte-for-byte exactness of the original user prompt, problem statement, and intuitive dialogue.
2. **Multi-Pillar Symbolic Exploration:** Formally explore the four mathematical pillars:
   - Positive/Negative cycle spaces and Gysin localization sequences ($A \xrightarrow{f} B \xrightarrow{g} C$ with $\operatorname{im}(f) \subseteq \ker(g)$).
   - Divisor and complete-intersection orthogonality for Weil classes ($\langle w_i, \Theta^2 \rangle = 0$).
   - Mumford spinor exceptional classes, Schur's lemma endomorphism vacuum ($\operatorname{End}_{\mathbb{Q}}(A) = \mathbb{Q}$), and $D_4 = \mathfrak{so}(8)$ Lie root operators ($\dim (\bigwedge^4 S^+_8)^{\mathfrak{so}(8)} = 0$).
   - Calabi–Yau fourfold Griffiths residue calculus, Koszul Hodge dimensions $(1, 426, 1751, 426, 1)$, and Voisin second-order moving-cycle integrability.
3. **Formal Verification in Lean 4:** Require all finite-dimensional algebraic/combinatorial identities to compile with zero `sorry`, zero `admit`, and zero fake axioms.
4. **Honest Demarcation of the Millennium Frontier:** Proved theorems are celebrated; the Clay Millennium Hodge Conjecture remains strictly OPEN.
5. **Fail-Closed Execution:** Any unverified assumption, invalid inference, or broken dependency halts high-impact promotion.

---

## 3. Scope Boundaries
- **Projectivity Mandatory:** Non-projective Kähler manifolds are rejected per Claire Voisin's 2002 counterexamples (`FLAG-HODGE-02`).
- **Rational Coefficients Mandatory:** Integral Hodge conjecture claims are rejected per Atiyah–Hirzebruch and Totaro torsion counterexamples (`FLAG-HODGE-01`).
- **Higher Codimension Separation:** Codimension $p \ge 2$ classes cannot be generated solely from vector bundle Chern classes (`FLAG-HODGE-03`).
- **Zero Hallucinated Proofs:** No autonomous agent or LLM may declare the general Millennium conjecture proved.

---

## 4. Completion Contract
An output is finished only when its task-specific acceptance obligations are met and recorded. A proof is fully accepted only when the exact independently specified theorem has a trusted formal check, no unacceptable axiom dependencies, semantic and external review, and distinct acceptance tied to a frozen source digest.
