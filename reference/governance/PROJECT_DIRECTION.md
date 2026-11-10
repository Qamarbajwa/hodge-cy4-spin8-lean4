# Project Direction — Riemann Hypothesis CCM Spectral Research

- **Status:** `ACTIVE PROJECT-LOCAL AUTHORITY (Bound for Riemann Hypothesis under R3 Promotion Acceptance at State Revision 23)`
- **Universal Provenance Baseline:** `UNIVERSAL_GOVERNANCE_MINIMAL_v4.0.4` (`Drive ID: 1hmpfaHSQ35PA4x3Vu7naVRVA5kLjOcel`, `V404_SOURCE_SHA256: NOT_PROVEN` locally due to external Drive authentication gate)
- **Project-Local Stricter Candidate:** `UNIVERSAL_GOVERNANCE_MINIMAL_v4.0.6-r3_CANDIDATE` (`SHA-256: 1200e60450d1d2f13dc607ec82101cdfcbe6690020645fb6db0ac0c7f8140ccc`)
- **Global `v4.0.6-r3` Canonical Promotion:** `NOT_CLAIMED` (`v4.0.4` remains globally canonical universal baseline)
- **Project ID:** `riemann-hypothesis-ccm`
- **Standing Invariant:** $\boxed{\mathbf{NO\_RH\_PROOF = TRUE}}$

---

## 1. Intent and Boundaries

### 1.1 Project Identity & Purpose
The project investigates the spectral realization of the zeros of the Riemann zeta function via the Connes–Consani–Moscovici (CCM) semilocal Weil quadratic form $QW_\lambda$ and the perturbed scaling operator $D_{\log}^{(\lambda, N)}$ on finite and infinite intervals (`arXiv:2511.22755v1`, `arXiv:2307.03961`, `arXiv:2607.02828v3`). The objective is to rigorously analyze and prove (or falsify) prerequisite functional-analytic theorems concerning ground-state parity, simplicity, quantitative continuation across prime-power thresholds, and prolate ground-state approximation without heuristic leaps.

### 1.2 Epistemic Ceilings & Non-Goals
- **Permanent Invariant:** `NO_RH_PROOF = TRUE` (`PROVE_RH: FORBIDDEN`).
- **Frozen Protocol:** `RH-T057 = DEFERRED / FROZEN_UNEXECUTED` (`EXECUTE_RH_T057: FORBIDDEN`).
- **Program Completion Ceiling:** `GOAL_COMPLETE = REJECTED`.
- **Open Mathematical Prerequisites:**
  - `GENERAL_CCM_A1A2 = OPEN`
  - `CCM_A3N = OPEN / PARTIAL`
  - `CCM_B_STAR = OPEN`
  - `BEYOND_L7 = OPEN`
- **Certified Bounded Result on $[0.8, L_7]$ ($L_7 = \frac{1}{2}\log 7$):**
  - `FULL_INTERVAL_STABILITY_FINAL_STATUS = CERTIFIED_FULL_INTERVAL_0_8_TO_L7` (certified via outward-rounded 10-step hybrid interval certificate in `RH-CCM-L7-TEN-STEP-HYBRID-INTERVAL-CERTIFICATION-001` and independently verified in `RH-CCM-J5-L7-INDEPENDENT-MATHEMATICAL-VERIFICATION-001`).
  - No claim of continuation beyond $L_7$ (`BEYOND_L7 = OPEN`) is permitted until the infinite-rank prime-7 shift perturbation $J_7$ is resolved.

---

## 2. Delegated Source Map

Under Section 1 of `governance/GOVERNANCE.md`, specialized mathematical, verification, and historical specifications are narrowly delegated without creating competing operational authorities:

| Delegated Source | Path | Delegated Role & Conflict Rule |
| :--- | :--- | :--- |
| **Higher Mathematical Constitution** | `governance/MATHEMATICAL_RESEARCH_CONSTITUTION_v1.0.md` | Non-negotiable domain law governing mathematical truth, problem identities, assumption drift, 13 claim states, and the evaluation triad; **strictly outranks operational governance rules wherever stronger**. |
| **RH Hard-Gate Inventory (`v4.0.6-r3`)** | `governance/RH_HARD_GATE_INVENTORY_v406r3.yaml` | Complete 19-gate RH hard-gate specification (`HG-RH-01` through `HG-RH-19`) enforced by `scripts/rh_bound_readiness_adapter.py`. |
| **RH Evidence Companion (`v4.0.6-r3`)** | `governance/RH_EVIDENCE_COMPANION_v406r3.md` | Evidence tiers `E0`–`E5`, cryptographic Git-blob provenance rules, `IND2` / `THREE_ROLE` independence requirements, and supersession discipline. |
| **Problem Identity Register** | `governance/PROBLEM_IDENTITY_REGISTER.yaml` | Frozen problem targets: `CCM-SYM`, `CCM-FIN-SE`, `CCM-A1`, `CCM-A2`, `CCM-A3`, `CCM-A3N`, `CCM-B*`. |
| **Assumption Ledger** | `governance/ASSUMPTION_LEDGER.yaml` | Tracking active mathematical assumptions and preventing unproven substitutions. |
| **Proof Dependency Ledger** | `governance/PROOF_DEPENDENCY_LEDGER.yaml` | Directed Acyclic Graph (DAG) of authenticated theorems and external dependencies. |
| **Proof Bug Regression Register** | `governance/PROOF_BUG_REGRESSION_REGISTER.yaml` | Active mathematical bug regression rules (`PROOF-ERROR-001..010` / `REG-MATH-001..014`). |
| **Theorem Evaluation Triad** | `governance/THEOREM_EVALUATION_TRIAD.yaml` | Decoupled evaluation of Correctness, Novelty, and Significance. |
| **Known-Good Mathematical State** | `KNOWN_GOOD_MATHEMATICAL_STATE.md` | Source-locked inventory of authenticated propositions and certified bounds. |
| **Negative Evidence & Quarantine** | `NEGATIVE_EVIDENCE_REGISTER.md`, `PERMANENT_NO_GO_LEDGER.md`, `INTEGRITY_QUARANTINE.md` | 17 permanent `NO-GO-001..017` entries and quarantined invalid historical protocols (immutable). |

---

## 3. Capability Contracts and Actors

1. **`CAP-MATH-PROVING` (`ACTIVE_RESTRICTED`):** Variational and functional-analytic proofs under `MATHEMATICAL_RESEARCH_CONSTITUTION_v1.0.md` and `HG-RH-01..19`.
2. **`CAP-MATH-E4-CLEANROOM` (`ACTIVE`):** Arbitrary-precision (`mpmath.mp.dps >= 45`) and outward-rounded interval-arithmetic (`mpmath.iv`) verification with zero `fp64` downcasting.
3. **`CAP-GOV-CONSISTENCY` (`ACTIVE`):** Deterministic manifest linting, `StateTransaction` concurrency checks, `verify-package.mjs`, and `rh_bound_readiness_adapter.py`.
- **Actors:** `WRITER` (`84030caf-f971-4466-bf47-c5bb688903f6`), `REVIEWER` (`IND2`, `WRITER_ID != REVIEWER_ID`), and `FINAL_ACCEPTOR` (`THREE_ROLE`, `WRITER_ID != REVIEWER_ID != FINAL_ACCEPTOR_ID`).

---

## 4. Architecture, Presentation & Post-Launch Applicability

- **Execution Topology:** Local isolated repository (`d:/Comfy UI/rheihman hypothesis`) using Python 3.12 (`mpmath 1.3.0`, `connes_cvs 0.3.1`, `pytest`) and Node.js (`verify-package.mjs`).
- **Shared Presentation / UI (`Section 7`):** `NONE_BY_DESIGN` (`N/A` — pure mathematical research codebase with no user-facing frontend, browser routes, or visual components).
- **Post-Launch Operations & Live Deployment (`Sections 12 & 14`):** Live production deployment effects are `N/A` (`PURE_RESEARCH_REPOSITORY_NO_PUBLIC_RELEASE`, `release.eligibility.status = NO-GO`, `release.deployment_authorization.status = NONE`). However, the exact-candidate binding, `hard_gates` completeness, and `validateBoundReleaseReadiness` adapter semantics of `v4.0.6-r3` are strictly enforced for every mathematical claim promotion and state transition via `scripts/rh_bound_readiness_adapter.py`.

---

## 5. Roadmap and Next Eligible Scientific Task

1. **Completed & Certified Milestones (`[0.8, L_7]`):**
   - `RH-CCM-L5-INTERVAL-QUADRATURE-AND-MPSI-REPAIR-003`: Certified full interval $[0.8, L_5]$.
   - `RH-CCM-J5-THRESHOLD-CROSSING-AND-L7-BRIDGE-001` & `RH-CCM-L7-TEN-STEP-HYBRID-INTERVAL-CERTIFICATION-001`: Proved J5 threshold crossing and certified 10-step hybrid interval bridge across $[L_5, L_7]$, independently verified in `RH-CCM-J5-L7-INDEPENDENT-MATHEMATICAL-VERIFICATION-001` and accepted in `RH-CCM-J5-L7-FINAL-ACCEPTANCE-AND-STATE-PROMOTION-001`, establishing `CERTIFIED_FULL_INTERVAL_0_8_TO_L7`.
2. **Next Eligible Scientific Task (After Governance Cutover Only):**
   - `RH-CCM-J7-THRESHOLD-CROSSING-AND-L11-BRIDGE-001` (Analyze the prime-7 jump perturbation $J_7$ across $L_7 = \frac{1}{2}\log 7$ and investigate continuation toward $L_{11} = \frac{1}{2}\log 11$).
   - **Frozen During Promotion:** Do NOT execute `RH-CCM-J7-THRESHOLD-CROSSING-AND-L11-BRIDGE-001` during `RH-GOV-V406R3-ADAPTER-ALIGNMENT-AND-STATE-PROMOTION-001`.

---

## 6. Completion & Update Rule

Changes to `governance/PROJECT_DIRECTION.md` require bounded governance review (`WRITER_ID != REVIEWER_ID != FINAL_ACCEPTOR_ID`) and must preserve all standing epistemic invariants (`NO_RH_PROOF = TRUE`) and delegated technical sources.
