# ARCHITECTURE DECISIONS — RH-PROJECT v3.0.0

Architecture is technical authority inside `PROJECT_INTENT.md`. The mathematical constitution remains a stricter project-specific extension where non-conflicting.

## Architecture snapshot

| Area | Observed current state | Evidence | Confidence |
|---|---|---|---|
| Runtime/stack | Local Windows scientific-computing workspace; Python 3.12.10, NumPy 2.2.6, SciPy 1.17.0, mpmath 1.3.0, SymPy 1.14.0 | `PROJECT_PROFILE.md`, `ENVIRONMENT_LOCK.md`, repository files | High |
| Data/storage | Git repository with Markdown, YAML, JSON, CSV, protected fixtures, evidence ledgers, and clean-room artifacts | `git ls-files`, `RH_RESEARCH_PATHWAY_REGISTRY.md`, `EVIDENCE_LEDGER.md` | High |
| Auth/identity | No application authentication surface; authority is typed project governance and candidate-bound provenance | v3 packet, `GOVERNANCE_STATE.yaml` | High |
| External integrations | Authenticated public `connes-cvs == 0.3.1`; primary-source mathematical references | `governance/project-governance.yaml`, source-lock records | High |
| Deployment | No external deployment or publication candidate evaluated | `CURRENT_SCIENTIFIC_STATE.md`, v3 release state | High |
| Test/CI | Deterministic Python consistency checks and research-specific verifiers; no remote CI configured | `scripts/`, test commands, `git remote -v` | High |
| Scientific control plane | Mathematical Research Constitution v1.0, problem identity register, proof dependency ledger, regression register, theorem triad | `governance/MATHEMATICAL_RESEARCH_CONSTITUTION_v1.0.md` and linked ledgers | High |

## Decision states

`OBSERVED`, `DERIVED_TECHNICAL`, `DECIDED_TECHNICAL`, `OWNER_RESERVED_DECISION`, `OPEN_TECHNICAL`, and `SUPERSEDED` are used as defined by the v3 packet.

## Decision log

### ADR-0001 — Adopt Universal Governance v3.0.0 as the outer runtime layer

- State: `DECIDED_TECHNICAL`
- Date: 2026-08-30
- Problem: Existing v2.9.x/v2.10.x governance used mixed generic approval and evidence semantics that need typed v3 reconciliation.
- Intent/requirement trace: `PROJECT_INTENT.md`; `RH-GOV-V3-MIGRATION-001`.
- Options considered: retain v2 active; replace it destructively; preserve v2 and add a bounded v3 supersession layer.
- Technical evidence: complete packet manifest verification; existing governed state and migration history; current repository checkpoint.
- Risk tier: T3; action class B.
- Affected contracts/capabilities: governance state, authority classification, evidence projections, roadmap eligibility.
- Decision: v3 is the active outer runtime governance layer; v2 files and semantics remain historical and are not rewritten.
- Why: preserves provenance while enabling typed authority, fail-closed evidence, and autonomous dependency-satisfied technical work.
- Invariants: `NO_RH_PROOF = TRUE`; release remains `UNKNOWN`; protected scientific evidence is not modified.
- Consequences/trade-offs: v2 and v3 terminology coexist in historical records; projections are additive and may expose limitations.
- Verification required: v3 schema checks, packet manifest, conformance gates, distinct review.
- Rollback/migration path: revert the bounded migration commit and retain the v2 snapshot; no history rewrite.
- Owner-reserved boundary affected? `NO`
- Supersedes: active operational use of v2 generic authority semantics only; does not supersede historical records.

### ADR-0002 — Preserve the mathematical constitution as a project-specific extension

- State: `DECIDED_TECHNICAL`
- Date: 2026-08-30
- Problem: Universal governance must not weaken the existing mathematical truth controls.
- Intent/requirement trace: `governance/MATHEMATICAL_RESEARCH_CONSTITUTION_v1.0.md` and `PROJECT_INTENT.md`.
- Technical evidence: constitution’s 13-stage claim lifecycle, evidence rules, proof-error register, and `NO_RH_PROOF` ceiling.
- Risk tier: T3; action class B.
- Decision: bind the constitution under `RESEARCH-SCIENTIFIC`; retain its stricter non-conflicting controls and preserve its scientific lifecycle orthogonally to release state.
- Why: v3 governs project execution and authority, while the constitution governs mathematical truth and claim maturity.
- Invariants: finite evidence is not continuum proof; historical failures remain; claim lifecycle is not replaced by release lifecycle.
- Consequences/trade-offs: every mathematical claim carries both scientific maturity and v3 evidence/release dimensions.
- Verification required: scientific consistency tests and claim/proof regression checks.
- Rollback/migration path: remove only the v3 binding references; preserve the constitution unchanged.
- Owner-reserved boundary affected? `NO`
- Supersedes: none.

### ADR-0003 — Treat RH-CCM-A1A2-WINDOW-OPENNESS-001 as the next technical objective

- State: `DERIVED_TECHNICAL`
- Date: 2026-08-30
- Problem: The accepted fixed-window and conditional convergence checkpoints leave the general CCM-A1/A2 continuation/window question open.
- Intent/requirement trace: `PROJECT_INTENT.md`; `ROADMAP.md`; `CURRENT_SCIENTIFIC_STATE.md`.
- Technical evidence: Chuk L=0.8 transfer, n=5 threshold preflight, CCM-A3 conditional proof, and the theorem dependency ledger.
- Risk tier: T3; action class B.
- Decision: mark the bounded window-openness analysis `READY` after migration, subject to its own task envelope and independent challenge.
- Why: dependencies and candidate identity are known, the work is research-only, and no reserved external action is required.
- Invariants: no general CCM-A1/A2 claim is promoted; threshold crossing and form-variation bounds remain explicit unknowns.
- Consequences/trade-offs: technical work continues autonomously while unresolved analytic gaps remain visible.
- Verification required: candidate-bound deterministic evidence, negative/boundary analysis, and distinct review.
- Rollback/migration path: revert only the objective’s artifacts; preserve prior checkpoints and negative evidence.
- Owner-reserved boundary affected? `NO`
- Supersedes: ceremonial owner-approval dependency for routine technical sequencing only.
