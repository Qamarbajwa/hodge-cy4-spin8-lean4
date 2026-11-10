# INTEGRITY QUARANTINE REGISTER

- **Artifact ID:** `QUARANTINE-BIB-2026-001`
- **Registration Date:** `2026-11-10T03:00:00Z`
- **Status:** `ACTIVE_BIBLIOGRAPHY_QUARANTINE`

---

## 1. Quarantined Identifier: `arXiv:2307.03961`

### 1.1 Verified Bibliography Mismatch
In `reference/governance/PROJECT_DIRECTION.md` (line 15), `reference/governance/PROBLEM_IDENTITY_REGISTER.yaml` (line 224), and `reference/governance/PROOF_DEPENDENCY_LEDGER.yaml` (line 46), the identifier `arXiv:2307.03961` is erroneously attributed to:
> *"Connes–Consani–Moscovici, arXiv:2511.22755 (2025) & arXiv:2307.03961"*

### 1.2 Observed Real Source Metadata
An exact query to the arXiv API (`http://export.arxiv.org/api/query?id_list=2307.03961`) returns:
- **Title:** "Geometric polarized log Hodge structures for semistable families"
- **Authors:** Taro Fujisawa, Chikara Nakayama
- **Primary Category:** `math.AG` (Algebraic Geometry)
- **Summary:** Proves that a projective semistable morphism of fs log analytic spaces yields polarized log Hodge structures in the canonical way.
- **Mismatch Finding:** The paper is on logarithmic Hodge structures in complex algebraic geometry, containing zero discussion of the Connes–Consani–Moscovici scaling operator, prolate wave operators, or the Riemann zeta function.

### 1.3 Intended Source Identification
An exact author query on the arXiv API (`au:Connes AND au:Consani AND au:Moscovici`) identifies the intended 2023 foundational paper:
- **Title:** "Zeta zeros and prolate wave operators"
- **Authors:** Alain Connes, Caterina Consani, Henri Moscovici
- **arXiv Identifier:** `arXiv:2310.18423` [math.NT]
- **Published Reference:** Compositio Mathematica / arXiv preprint (October 2023).

---

## 2. Inventory of Stale Dependent Artifacts

Pending formal owner review and recorded bibliographic amendment, the following claims, notes, and ledger entries are marked **`STALE_PENDING_REVIEW`**:

| Artifact / Node ID | File Location | Quarantined Citation Context | Stale Status |
| :--- | :--- | :--- | :---: |
| `CCM-SYM` | `reference/governance/PROBLEM_IDENTITY_REGISTER.yaml` | Cited for semilocal scaling operator symmetry | `STALE_PENDING_REVIEW` |
| `CCM-FIN-SE` | `reference/governance/PROBLEM_IDENTITY_REGISTER.yaml` | Cited for finite-interval self-adjoint extension | `STALE_PENDING_REVIEW` |
| `LEM-CCM-PROLATE-001`| `reference/governance/PROOF_DEPENDENCY_LEDGER.yaml` | Cited for prolate operator commutation | `STALE_PENDING_REVIEW` |
| Section 1.1 Text | `reference/governance/PROJECT_DIRECTION.md` | Background narrative of spectral realization | `STALE_PENDING_REVIEW` |

*No downstream mathematical derivation may promote claims based on `arXiv:2307.03961` without an owner-authenticated amendment substituting the verified source.*
