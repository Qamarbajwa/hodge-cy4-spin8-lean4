# Hodge CY4 & Spin(8) Triality — Lean 4 Reservoir

Pure root-level Lean 4 (`leanprover/lean4:v4.35.0`, Lake 5.0.0) package containing all **20 verified Lean 4 modules** (13 baseline modules + 7 extension modules, zero `sorry`, zero external dependencies).

> **Mathematical Scope:** Twenty axiom-free Lean 4.35.0 modules establishing constructive Fermat fourfold cycle synthesis ($3 \le m \le 25$), six-variable Artinian Gorenstein Wiebe–Scheja–Storch colon ideals, $\operatorname{Spin}(8)$ outer triality and $D_4$ Weyl representations, order-8 Gauss–Manin infinitesimal jets, Cayley-bundle spectra, and explicit conditional Fermat algebraicity interfaces (`FermatFourfoldHodgeBridge`).

## Quick Verification
```bash
lake build
```

## Companion Repositories, Zenodo Record & Fork-Internal Merge
- **Six-Paper Series & Symbolic Companions:** `https://github.com/Qamarbajwa/hodge-cy4-spin8-papers`
- **Zenodo Published Record (PUBLISHED, state=done):** `10.5281/zenodo.24354741` (https://zenodo.org/records/24354741)
- **Fork-Internal Merge (`Qamarbajwa/mathlib4`):** https://github.com/Qamarbajwa/mathlib4/pull/8 (`MERGED`, commit `01a630c90aa2ca1678857f0e8f30dc33a65df984`)

## Module Inventory (20 `.lean` Files)
- `HodgeVerification.lean` (`sha256:54f6aa1af3d9...`)
- `ShiodaFormalConjectures.lean` (`sha256:334e52a0f20c...`)
- `MathlibPR_ShiodaAokiFermat.lean` (`sha256:00e049bcfdd8...`)
- `MathlibPR_MacaulayGorenstein.lean` (`sha256:55974fee713e...`)
- `MathlibPR_Spin8Triality.lean` (`sha256:c3e3f604b41c...`)
- `MathlibPR_CyclotomicIncidenceSieve.lean` (`sha256:ee0819fc6002...`)
- `WiebeSchejaStorch.lean` (`sha256:8ee0da01b797...`)
- `GaussManinJetTransport.lean` (`sha256:23aee87dacbc...`)
- `ShiodaInductiveCycleSynthesis.lean` (`sha256:d6ec4d41e4a8...`)
- `Spin8LieAlgebraTriality.lean` (`sha256:4a118e126e92...`)
- `GlobalIVHSObstructionSpectrum.lean` (`sha256:bd183d99161b...`)
- `HigherDegreeSporadicBand4.lean` (`sha256:52f273aff322...`)
- `LeanDemoProject.lean` (`sha256:3305591663c9...`)
- `MumfordWeilKernelVecs.lean` (`sha256:b14bbdd7bca6...`)
- `HodgeBridgeInterfaces.lean` (`sha256:6b2ac49d3c6d...`)
- `ConditionalFermatHodge.lean` (`sha256:00cddea86004...`)
- `FermatHighDegreeExt.lean` (`sha256:7dabe1e44897...`)
- `HigherOrderJetLifting.lean` (`sha256:e37544ce8add...`)
- `CayleyCompleteInt.lean` (`sha256:0ecd0d03b0a5...`)
- `Poly6ToMvPoly.lean` (`sha256:c71dcb3bc101...`)
