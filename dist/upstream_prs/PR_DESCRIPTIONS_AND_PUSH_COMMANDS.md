# Mathlib4 Upstream PR Staging Guide

All staged files below are 100% self-contained (zero local workspace imports) and verified standalone via `lake env lean`.

## Staged Target Files
- `Mathlib/AlgebraicGeometry/FermatHypersurface/ShiodaAoki.lean`
- `Mathlib/RingTheory/ArtinianGorenstein/MacaulayContraction.lean`
- `Mathlib/RepresentationTheory/Spin8Triality.lean`
- `Mathlib/Combinatorics/IncidenceSieve/CyclotomicResidualForm.lean`

## Push & PR Commands
```bash
git checkout -b feat/shioda-aoki-macaulay-spin8-sieve
cp -r dist/upstream_prs/mathlib4/Mathlib/* Mathlib/
git add Mathlib/
git commit -m "feat: add Shioda-Aoki, Macaulay, Spin(8), and cyclotomic sieve modules"
git push -u origin feat/shioda-aoki-macaulay-spin8-sieve
gh pr create --title "feat: Shioda-Aoki, Macaulay Gorenstein, Spin(8) triality, and cyclotomic sieve" --body "Formalizes universally quantified Shioda-Aoki character bands, Macaulay transpose duality, Spin(8) weight-lattice laws, and finite cyclotomic incidence sieve conservation laws."
```
