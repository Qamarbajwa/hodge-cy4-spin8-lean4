# ACCEPTANCE GATE POLICY (v2.9)
**Governing Standard:** `MASTER_AUTONOMOUS_PROJECT_GOVERNANCE_DEVELOPMENT_EVOLUTION_v2.9.md`  

---

## 1. Evidence Floors by Risk Tier
- **Tier 1 (Trivial):** Requires `E2` (Direct Tool Observation).
- **Tier 2 (Standard Dev):** Requires `E3` (Reproducible Machine Evidence / Tests).
- **Tier 3 (Material Research):** Requires `E3 + E4` (Reproducible Machine Evidence + Independent Verification).
- **Tier 4 (Control Plane / Governance):** Requires `E3 + E4 + E5` (Independent Verification + Project Owner Authorization).
- **Tier 5 (Consequential Release):** Requires `E5 + Multi-Party Authority`.

---

## 2. Gate Acceptance Checklist for Numerical Experiments
1. Preregistration artifact created and SHA-256 hashed prior to execution.
2. Preregistration commit sealed in Git history before primary eigensolves start.
3. Package provenance locked to authentic public release.
4. Independent authentication fixture passes ($< 10^{-15}$ relative error).
5. Predecessor reproduction gate passes.
6. 100% of primary cells accounted for in raw CSVs and JSON receipts.
7. Independent verifier script passes with zero discrepancies.
8. Working tree clean.
