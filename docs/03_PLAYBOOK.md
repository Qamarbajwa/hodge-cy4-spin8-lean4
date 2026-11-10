# 03 — Playbook: apply this to a NEW mathematical project

Work top to bottom. Each step names the template/tool to use.

## Phase 0 — Freeze identity
1. Copy `templates/PROJECT_INTENT.template.md` → state purpose, non-goals, **unacceptable outcomes** (e.g. "claiming X solved").
2. Fill `templates/PROBLEM_IDENTITY_REGISTER.template.yaml`: canonical statement, quantifiers, domain, equivalent forms, what is *not* the problem.
3. Pick the **authenticated oracle** (published package/dataset/known theorem). Forbid re-implementing it.

## Phase 1 — Reduce to a spine
Find the analogue of RH's spine: *target ⇔ positivity/boundedness/spectral statement of an operator or form*, plus a **finite section** (Galerkin / truncation / lattice) that can be computed and a **competitor-subspace** question to falsify.
Write the exact definitions as `PROVED_LEMMA`-style notes (see `reference/CVS_*` examples): space, form, domain, operator, ground equation.

## Phase 2 — Build ledgers (memory)
Create from templates: `ASSUMPTION_LEDGER`, `PROOF_BUG_REGRESSION_REGISTER`, `PROOF_DEPENDENCY_LEDGER`, `PERMANENT_NO_GO_LEDGER`, `THEOREM_TRIAD`, `NEGATIVE_EVIDENCE_REGISTER`. Seed assumption **flag patterns** for your field (RH: silent threshold, unproved positivity-improving, unproved simplicity, unproved parity ordering, unproved uniform gap).

## Phase 3 — Preregister a protocol
`templates/PREREGISTRATION.template.json` + `PROTOCOL_CONTRACT.template.md`:
* exact matrix/subspace constructions (formulas, indices),
* **Gate A** reference fixture (known value, ladder of precisions, rtol),
* **Gate B** predecessor calibration (must reproduce an earlier known result, never hard-code it),
* the grid, decision rules (Outcome A/B/C/D), robustness grids (truncation, height, outer section),
* random control with fixed seed, contamination declarations (disclose anything you already saw).

## Phase 4 — Compute (`toolkit/hp_linalg.py`, `toolkit/prereg.py`)
Pure arbitrary precision. Gate fail ⇒ **no outcome** (fail-closed). Output JSON → `integrity.seal()` **before** comparing with anyone.

## Phase 5 — Independent clean-room re-run
Different writer, spec = contract only (not the primary code). Document code-independence audit (structural comparison + SHA-256 of each script). Compare **after** seal. Pattern in `reference/cleanroom_e4/`.

## Phase 6 — Adversarial & integrity checks
`integrity.scan_forbidden`, `find_duplicate_rows`, `check_power_law_fabrication`, `report_vs_csv`, `banned_language`, `wilson_interval` for any "k of n" claim. Run the falsification sweep (boundary, symmetry-breaking, toy projections, pathological kernels, limit interchange).

## Phase 7 — Classify, don't promote
Use `toolkit/claims.py`. Record Triad. Bounded results get words like `COMPLETED_WITH_LIMITATIONS`, `CONDITIONAL`, `LOCAL_WINDOW`. Negative results go in the ledgers *immediately*.

## Phase 8 — Reconcile & seal the repo
`integrity.build_manifest(root)` → `ARTIFACT_HASH_MANIFEST.sha256`; `verify_manifest` before every release. Update `CURRENT_SCIENTIFIC_STATE.md`, `OPEN_QUESTIONS.md`, `NEXT_ACTION.md`.

## Rules of thumb learned the hard way
* Finite evidence ≠ continuum theorem. $L^2$ convergence ≠ pointwise/boundary convergence.
* Never let a report be written before the CSV it summarizes is final.
* If a result is "too clean" (exact power law, duplicate rows) assume fabrication until disproved.
* A wrong-operator result is not a weak result — it is *no* result.
* Re-derive normalisations/scales from scratch; mismatched constants silently change the theorem.
* Fixed-parameter theorem ≠ uniform-parameter theorem (watch every "for λ>λ₀").

## Adapting L0 to other problems (examples)
| Problem class | Spine analogue | Finite section | Competitor test |
|---|---|---|---|
| Other L-function / GRH | Weil form for Dirichlet L | Fourier basis + prime cutoff | augmentation of extension space |
| Spectral gap / Schrödinger | quadratic form on H¹ | Galerkin / finite elements | basis enrichment vs refinement |
| Positivity of kernels / PSD | form `∫∫fKf ≥ 0` | quadrature matrix | min-eigenvalue with interval arithmetic |
| Inequality / extremal constant | variational ratio | restricted Ritz space | upper bound ladder vs lower bound certificate |
| Number-theory conjecture w/ numerics | truncated sum / sieve | rigorous interval enclosures | counter-example search with seeds |
