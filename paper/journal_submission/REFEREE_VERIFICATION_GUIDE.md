# Referee 60-Second Verification Guide

**Manuscript:** *Computational Apolarity Experiments, Deformed Calabi--Yau Obstruction Cancellation, $\mathrm{Spin}(8)$ Triality Combinatorics, and Decidable Lean 4 Finite Checks for Hodge Bridges*  
**Author:** Qamar Munawer (Brandenburg University of Technology Cottbus-Senftenberg)  
**Toolchain:** Python $\ge 3.12$ (stdlib only for standalone checks), Lean `4.35.0` / Lake `5.0.0` (**zero Mathlib imports**)

All exact integer, rational, and modular $\mathbb{F}_p$ computations are deterministic, 100% free of floating-point approximations, and independently checkable in under 60 seconds from the repository root (`d:\Comfy UI\hodge conjecture` or extracted Zenodo archive).

---

## 1. Zero-Dependency Pure-Python Check (~1 second)

Run the standalone verification snippet embedded in `paper/ZENODO_MANUSCRIPT_FOUR_PILLARS_HODGE.md` (Appendix A.3) directly with standard Python:

```bash
python -c "import pathlib, re; t = pathlib.Path('paper/ZENODO_MANUSCRIPT_FOUR_PILLARS_HODGE.md').read_text(encoding='utf-8'); code = re.search(r'### Appendix A\.3.*?\x60\x60\x60python\n(.*?)\n\x60\x60\x60', t, re.S).group(1); exec(compile(code, 'appendix_a3.py', 'exec'), {})"
```

**Expected output:**
```text
VERIFIED: 1001+630+120+0=1751, rk=[155,336], ker>=1325
```

This independently confirms the Shioda--Aoki--Ran 4-band partition ($1{,}001 + 630 + 120 + 0 = 1{,}751$), Gorenstein moduli rank extremes $[155, 336]$, and the rank--nullity kernel dimension bound $\ge 1{,}325$.

---

## 2. Fast Offline Zenodo & CRT Audit (~15-25 seconds)

Run the fast verification suite and benchmark the float-free 3-prime CRT solver directly:

```bash
python verify_zenodo_deposit.py --fast
python toolkit/modular_crt_linear_solver.py
```

**What `verify_zenodo_deposit.py --fast` checks:**
1. **Zero-Float Guard:** Scans all `19` core Python experimental modules via `integrity.scan_forbidden` (`total_float_violations == 0`).
2. **Exact Invariant Replay:** Re-runs algebraic, representation-theoretic, and sextic fourfold computational experiments over $\mathbb{Z}$, $\mathbb{Q}$ (`fractions.Fraction`), and $61/62$-bit primes (`MODULAR_PRIMES_61BIT` / `MODULAR_PRIMES_62BIT`).
3. **CRT Rank Benchmark:** `modular_crt_linear_solver.py` certifies the dense $1{,}751 \times 426$ non-Fermat sextic system over $\mathbb{Q}$ via Wang's rational reconstruction in under $2\,\mathrm{s}$ (`under_2s=True`).
4. **Single-Pass Lean 4.35.0 Finite Check Audit:** Verifies all `41` decidable finite combinatorial and degree-counting checks (`by rfl`, zero Mathlib imports, NOT formalized Hodge theory/schemes/cohomology) and inspects `#print axioms` receipts (`all_axioms_empty: true`).
5. **SHA-256 Manifest & Honesty Gate:** Verifies all files in `ARTIFACT_HASH_MANIFEST.sha256` (`0` mismatches), confirms `GLOBAL_HODGE_CONJECTURE = OPEN`, and prints `all_checks_passed: true`.

---

## 3. Direct Lean 4.35.0 Kernel & `#print axioms` Inspection (~3 seconds)

Inspect and type-check the finite combinatorial checks directly using Lake without wrappers:

```bash
cd examples/math_gov/LeanDemoProject && lake env lean HodgeVerification.lean
```

**Expected behavior:**
- Exits cleanly with code `0` and zero `sorry` / warning axioms (`zero Mathlib imports`).
- Every `#print axioms <check>` statement emits `[... does not depend on any axioms]` (`axioms: []`), verifying index sets, weight-tuple counts, and polynomial degree arithmetic (`by rfl`).

---

## 4. Optional Full Test Suite (`pytest`)

To run the unit and governance integration test suite across the entire repository:

```bash
pytest -q
```
