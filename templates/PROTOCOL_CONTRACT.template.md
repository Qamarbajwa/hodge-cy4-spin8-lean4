# <PROTOCOL-ID> — Clean-Room Mathematical Contract
The clean-room writer sees ONLY this file (not the primary code).
## Oracle  — `<package==version>`; re-implementation FORBIDDEN.
## Precision — pure arbitrary precision; forbid float/numpy.float64/scipy eigensolvers.
## Subspace definitions — give every index range, formula, normalisation and symmetrisation EXPLICITLY.
## Gate A (reference fixture) — params, precision ladder, reference value, tolerance.
## Gate B (predecessor calibration) — params, expected qualitative result. Do not hardcode numbers as inputs.
## Grid — list of cells. ## Decision metric — formula and thresholds.
## Output — BLIND_RESULTS.json + SHA-256 seal BEFORE comparison with primary results.
