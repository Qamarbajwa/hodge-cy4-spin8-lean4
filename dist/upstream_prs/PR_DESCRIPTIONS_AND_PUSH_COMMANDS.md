# Fork-Internal Mathlib4 Staging Guide (`Qamarbajwa/mathlib4` Only)

> **Governance Lock:** Upstream PR creation and automated comments on external repositories are permanently disabled. Push and merge ONLY into `Qamarbajwa/mathlib4:master`.

All staged files below are 100% self-contained (zero local workspace imports), have zero `#print` commands, `<= 100` char lines, and pass standalone `lake env lean` (`rc=0`).

## Staged Target Files
- `Mathlib/AlgebraicGeometry/FermatHypersurface/ShiodaAoki.lean`
- `Mathlib/RingTheory/ArtinianGorenstein/MacaulayContraction.lean`
- `Mathlib/RepresentationTheory/Spin8Triality.lean`
- `Mathlib/Combinatorics/IncidenceSieve/CyclotomicResidualForm.lean`

## Fork-Internal Merge Commands (`Qamarbajwa/mathlib4` ONLY)
```bash
git checkout -b feat/shioda-aoki-macaulay-spin8-sieve
cp -r dist/upstream_prs/mathlib4/Mathlib/* Mathlib/
git add Mathlib/
git commit -m "feat: add Shioda-Aoki, Macaulay, Spin(8), and cyclotomic sieve modules"
git push -u origin feat/shioda-aoki-macaulay-spin8-sieve
gh pr create --repo Qamarbajwa/mathlib4 --base master --head feat/shioda-aoki-macaulay-spin8-sieve --title "feat: merge verified zero-axiom Shioda-Aoki, Macaulay, Spin(8) triality, and cyclotomic sieve modules" --body "Merges standalone-verified zero-axiom Lean 4 modules into fork master."
gh pr merge feat/shioda-aoki-macaulay-spin8-sieve --repo Qamarbajwa/mathlib4 --merge
```
