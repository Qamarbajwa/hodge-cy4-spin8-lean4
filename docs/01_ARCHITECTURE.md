# 01 — Architecture: the layers of the framework

```
┌────────────────────────────────────────────────────────────────────┐
│ L5  GOVERNANCE (outer runtime law)  GOVERNANCE.md, PROJECT_STATE,  │
│     risk tiers T0–T3, authority classes, owner-reserved actions    │
├────────────────────────────────────────────────────────────────────┤
│ L4  MATHEMATICAL CONSTITUTION  6 Laws · 13-state claim lifecycle · │
│     Triad (Correctness/Novelty/Significance) · gates              │
├────────────────────────────────────────────────────────────────────┤
│ L3  LEDGERS (memory)  Problem Identity · Assumption · Proof-Bug    │
│     Regression · Proof Dependency · No-Go · Negative Evidence ·    │
│     Load-Bearing Lemma · Contradiction · Claim Classification      │
├────────────────────────────────────────────────────────────────────┤
│ L2  PROTOCOL LAYER  Preregistration → Contract → Gates → Grid →    │
│     Blind seal → Independent clean-room re-run → Reconciliation    │
├────────────────────────────────────────────────────────────────────┤
│ L1  COMPUTE LAYER  authenticated oracle · mpmath precision ladder ·│
│     parity projection · Rayleigh–Ritz competitors · hash manifest  │
├────────────────────────────────────────────────────────────────────┤
│ L0  MATH CORE  problem-specific (for RH: Weil form, CvS operator,  │
│     prolate analyticity, CCM-A1/A2/A3)                             │
└────────────────────────────────────────────────────────────────────┘
```

**Only L0 is problem-specific.** Layers L1–L5 transfer to any quantitative mathematical project.

## The Six Laws (L4)
1. **Truth** – no claim exceeds its verified evidence; `OPEN/UNKNOWN/FALSE` are valid permanent statuses.
2. **Identity** – statement, quantifiers, domain never drift silently (weaker proof = *Proof Defect*).
3. **Independence** – `WRITER_ID != REVIEWER_ID`; correlated LLM review ≠ independent verification.
4. **Understanding** – 3-level explanation: 1 sentence · 1 page · full proof.
5. **Memory** – failures/counterexamples permanently preserved + regression rule.
6. **Objective** – small, understood, assumption-minimal results beat big unverified ones.

## Evidence ladder (E-levels used in the reports)
`E0` idea · `E1` internal numerics · `E2` reproducible script · `E3` reproducible against public authenticated oracle with precision ladder · `E4` independent clean-room reproduction with zero material discrepancies. None of these is a proof.

## Gates before any claim is promoted
Adversarial Falsification · Load-Bearing Lemma isolation · Assumption Drift Monitor · Formalization Fidelity (if Lean/Isabelle) · Assumption Minimization · Alternative Proof search · Understanding Gate · Report-consistency gate · Contamination scan.

## Governance numbering (historical record)
v2.3 → v2.10.1 → v3.0 (typed authority, fail-closed evidence) → "Universal Governance Minimal" v4.0.6-r3 (3-file minimal form: `GOVERNANCE.md`, `PROJECT_DIRECTION.md`, `PROJECT_STATE.yaml` + `verify-package.mjs`). The v4 minimal package is included under `reference/` — **start from that for new projects**; it is the distilled final form.
