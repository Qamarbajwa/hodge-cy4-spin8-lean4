# BIBLIOGRAPHIC DEPENDENCY IMPACT REPORT
## Provenance Quarantine, Historic Evidence Preservation, Candidate Reference Comparison, and Downstream Invalidation Register

- **Report ID:** `BIB-IMPACT-2026-001`
- **Quarantined Identifier:** `arXiv:2307.03961`
- **Date:** November 10, 2026
- **Status:** `ACTIVE_BIBLIOGRAPHY_QUARANTINE_NO_SILENT_SUBSTITUTION`
- **Governing Standard:** `MATH-GOV v0.6` Protocol B (Zero Silent Substitution)

---

## 1. Historic Citation Record Preservation

The erroneous citation `arXiv:2307.03961` appears in three historic repository files:

1. **`reference/governance/PROJECT_DIRECTION.md` (Line 15):**
   > *"The project investigates the spectral realization of the zeros of the Riemann zeta function via the Connes–Consani–Moscovici (CCM) semilocal Weil quadratic form $QW_\lambda$ and the perturbed scaling operator $D_{\log}^{(\lambda, N)}$ on finite and infinite intervals (`arXiv:2511.22755v1`, `arXiv:2307.03961`, `arXiv:2607.02828v3`)."*
2. **`reference/governance/PROBLEM_IDENTITY_REGISTER.yaml` (Line 224):**
   > *"source: 'Connes–Consani–Moscovici, arXiv:2511.22755 (2025), Sections 7 & 8; arXiv:2307.03961'"*
3. **`reference/governance/PROOF_DEPENDENCY_LEDGER.yaml` (Line 46):**
   > *"source: 'Connes–Consani–Moscovici, arXiv:2511.22755 (2025) & arXiv:2307.03961'"*

**Historic Preservation Rule:** In accordance with Protocol B, these erroneous text strings are **not** silently overwritten or deleted from the historical records. They are preserved verbatim as historical evidence of bibliographic drift.

---

## 2. Comparative Analysis of Quarantined vs. Candidate References

| Field | Quarantined Reference (`2307.03961`) | Candidate Reference A (`2106.01715`) | Candidate Reference B (`2310.18423`) |
| :--- | :--- | :--- | :--- |
| **Title** | *Geometric polarized log Hodge structures for semistable families* | *Spectral Triples and Zeta-Cycles* | *Zeta zeros and prolate wave operators* |
| **Authors** | Taro Fujisawa, Chikara Nakayama | Alain Connes, Caterina Consani | Alain Connes, Caterina Consani, Henri Moscovici |
| **Date** | July 7, 2023 | June 3, 2021 | October 27, 2023 |
| **Primary Category** | `math.AG` (Algebraic Geometry) | `math.NT` (Number Theory) | `math.NT` (Number Theory) |
| **Journal Reference** | arXiv:2307.03961 [math.AG] | arXiv:2106.01715 [math.NT] | Compositio Mathematica, 2024 |
| **Subject Matter** | Projective semistable morphisms of fs log analytic spaces; polarized log Hodge structures. | Non-commutative geometry; spectral triples; archimedean factors; zeta-cycles. | Prolate spheroidal wave functions; scaling Hamiltonian $D_{\log}$; semilocal Weil form $QW_\lambda$; finite-interval approximations. |
| **Alignment with Cited Context** | **0% (Mismatch):** No connection to CCM scaling, prolate operators, or Riemann zeros. | **Partial (50%):** Foundational Connes–Consani paper, but lacks Moscovici co-authorship and prolate operator analysis. | **Exact Match (100%):** Connes–Consani–Moscovici 2023 paper directly establishing prolate operator commutation and finite-interval extensions. |

---

## 3. Downstream Claim Invalidation Register

Because `arXiv:2307.03961` was load-bearing for the provenance of the CCM scaling operator, the following mathematical claims, nodes, and narrative sections are formally marked **`STALE_PENDING_REVIEW`** and invalidated for further derivation:

| Artifact / Node ID | Repository Location | Quarantined Role | Invalidation Status | Impact & Remedy |
| :--- | :--- | :--- | :---: | :--- |
| **`CCM-SYM`** | `reference/governance/PROBLEM_IDENTITY_REGISTER.yaml` | Cited for semilocal scaling operator symmetry | `STALE_PENDING_REVIEW` | All downstream parity proofs cannot advance without authenticated source lock. |
| **`CCM-FIN-SE`** | `reference/governance/PROBLEM_IDENTITY_REGISTER.yaml` | Cited for finite-interval self-adjoint extension | `STALE_PENDING_REVIEW` | Self-adjoint extension proofs invalidated until source is owner-reconciled. |
| **`LEM-CCM-PROLATE-001`** | `reference/governance/PROOF_DEPENDENCY_LEDGER.yaml` | Cited for prolate operator commutation with $QW_\lambda$ | `STALE_PENDING_REVIEW` | Commutation lemma frozen; cannot be cited in theorem closures. |
| **Section 1.1 Narrative** | `reference/governance/PROJECT_DIRECTION.md` | Background narrative of spectral realization | `STALE_PENDING_REVIEW` | Research scope text flagged as containing erroneous citation. |

---

## 4. Owner Review and Proposed Amendment Procedure

1. **No Autonomous Substitution:** The supervisor and implementation agents are strictly forbidden from executing a find-and-replace to substitute `2310.18423` or `2106.01715` into the protected reference files.
2. **Owner Review Submission:** This report is submitted to the repository owner and authorized acceptor.
3. **Resolution Path:**
   - Owner inspects Candidate Reference B (`arXiv:2310.18423`) against Candidate Reference A (`arXiv:2106.01715`).
   - If owner confirms `arXiv:2310.18423` as the intended foundational paper, owner issues an authorized amendment transaction in `governance/PROJECT_DIRECTION.md` and clears the quarantine.
   - Until owner amendment is signed and recorded, the status of all four artifacts remains **`STALE_PENDING_REVIEW`**.
