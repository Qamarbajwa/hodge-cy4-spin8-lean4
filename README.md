# Math Research Framework Kit
*Extracted from the Riemann Hypothesis CCM/CvS research project, packaged for reuse on other mathematical projects.*

> **Read first:** the source project did **not** prove RH (`NO_RH_PROOF = TRUE`). What it produced is a
> disciplined, falsification-first framework for working on hard problems without fooling yourself. That framework is this kit.

## Contents
| Path | What it is |
|---|---|
| `docs/01_ARCHITECTURE.md` | The 6 layers (math core → compute → protocol → ledgers → constitution → governance) and which are reusable |
| `docs/02_MATHEMATICAL_STRUCTURE_RH.md` | The actual RH mathematics: Weil form, CvS operator, Galerkin/even projection, A1 vs B subspaces, proved/open table, failure ledger |
| `docs/03_PLAYBOOK.md` | Step-by-step procedure to apply it to a new problem + adaptation table |
| `templates/` | Fill-in ledgers, preregistration JSON, clean-room contract, task envelope, intent, understanding artifact |
| `toolkit/` | Python: `claims.py` (13-state lifecycle + triad + independence law), `hp_linalg.py` (mpmath finite sections, parity projection, Ritz competitors, precision ladder), `prereg.py` (preregistered fail-closed grid runner), `integrity.py` (seals, manifests, fabrication/duplicate/float scans, report-vs-CSV, Wilson CI) |
| `examples/toy_pipeline.py` | Whole pipeline on a toy operator with a known answer (`python -m examples.toy_pipeline`) |
| `tests/` | `python -m unittest discover tests` |
| `reference/` | Untouched originals: constitution, all ledgers, clean-room E4 package, RH math notes, certification code, scripts, and the distilled **Universal Governance v4.0.6-r3** package |

## Quick start
```bash
pip install mpmath==1.3.0            # only dependency (connes-cvs==0.3.1 only for the RH oracle)
python -m unittest discover tests
python -m examples.toy_pipeline
```
Then follow `docs/03_PLAYBOOK.md`. To replace the toy: supply your own `build_Q`, reference fixture, calibration gate and `cell_eval`.

## The 10-line summary of the method
1. Freeze the problem identity. 2. Reduce to a spine (target ⇔ operator/form statement) with a computable finite section.
3. Use only an authenticated oracle. 4. Preregister grid + decision rules + contamination disclosure.
5. Compute in arbitrary precision with reference-fixture and calibration gates (fail-closed).
6. Seal results by hash. 7. Independent clean-room re-run from contract only.
8. Run integrity scans. 9. Classify with Correctness/Novelty/Significance separately, never promote numerics to proof.
10. Record every failure permanently with a regression rule.
