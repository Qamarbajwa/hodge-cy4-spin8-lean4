# Certification pipeline v2: finite arithmetic kernel

Status: executable exact finite interval LDL checker and independent verified
spatial shift component builder; full operator certification blocked.
`NO_RH_PROOF = TRUE`. No historical scientific frontier is recertified here.

Run `python -m unittest discover -s tests -p test_certification_v2.py -v`.
Run `python scripts/verify_certification_v2.py research/certification_v2/synthetic_box.json`.
Exit 0 means only the supplied finite interval box passed. The output separately
reports the blocked operator gate. Input errors raise an exception; inconclusive
finite boxes exit 1. No default fixture or historical eigenvalue table is loaded.

## Exact theorem and limits

For every real symmetric matrix A whose entries lie in the supplied symmetric
rational intervals, the recurrence encloses the exact unpivoted LDL factors of
A - sI. Inductively positive lower bounds for every diagonal pivot ensure the
denominators cannot vanish and imply positive definiteness by congruence.
Thus lambda_min(A) > s for every A in the box. Pivot values themselves are NOT
eigenvalue bounds. All arithmetic uses Python Fraction, so no rounding-error
budget or floating eigensolver is involved. A nonpositive interval pivot is
inconclusive; interval dependency can cause failure even when the box is positive.

The theorem does not establish that any analytic operator has these entries.
Decimal strings mean exact decimals, not outward enclosures of rounded floats.
Only externally established entry enclosures can connect this theorem to a
Galerkin matrix. No approximate builder receives automatic provenance approval.

The kernel costs O(n^3) rational operations and may suffer large integer growth.
It has been tested on small synthetic matrices, not the historical 205-mode
matrices. A future verified rational congruence/preconditioner can improve
conditioning; a floating candidate transform must be frozen as exact rationals
and its invertibility verified before using congruence for a spectral claim.

## Analytic adapters still missing

Inspection of `scripts/verify_l7_ten_step_hybrid_interval_certification_001.py`
found that `build_hybrid_and_schur_matrices` combines mpmath nodes/weights,
special-function recurrences, square-root basis normalization, dyadic conversion,
prime-shift Gram terms, and Schur correction. `refine_and_certify_interval_matrix`
accepts a numerical midpoint and `eps_H_entry`; its proof depends on a valid bound
covering every earlier construction error. Naming a matrix or shift formula
"exact" does not supply that bound. The v2 adapter must enclose quadrature
nodes/weights, special-function recurrence/truncation error, transcendental
constants, conversion/accumulation error, and quadrature remainder together.
The older L5 builder likewise contains scalar mpmath digamma/Bessel evaluations
and numpy floating limb calculations. This inspection does not assert every
historical error estimate is false; it identifies what v2 has not verified.

For continuum L, one must transport forms to one fixed Hilbert space and establish
uniform enclosures over each cell, including normalization and moving shift
breakpoints. An endpoint enclosure proves only that endpoint. Sampling/refining
L or asserting domain inclusion cannot replace a verified derivative bound or
uniform interval enclosure. Prime-power activation thresholds require explicit
handling at boundaries.

For a full operator, a positive finite compression alone is insufficient:
the orthogonal complement and cross coupling must be bounded. One possible
Schur route requires a proved complement floor beta > 0 and verified coupling
bound B*C^{-1}*B^* <= beta^{-1}*B*B^*, followed by positivity of the corrected
finite block. Spectral-gap claims also require verified trial upper bounds for
the reference eigenvalue and the appropriate min-max/complement decomposition.
No such validator is implemented here. User-supplied `PASS` fields never bypass
the gate; `operator_gate` always returns the three specific missing-adapter
obstructions.

## Validation

Eight executable tests cover a known exact spectral threshold, an interval box
with independently checked positive corner determinants, singular/negative/
uncertain rejection, float/malformed/asymmetry rejection, a 200-digit denominator,
sign-crossing multiplication/squaring/division, input hash binding, and an
adversarial attempt to promote operator positivity through `PASS` metadata.
The synthetic example is an arithmetic demonstration, not RH evidence.

## Independent spatial component

`spatial_overlap.py` now supplies real component enclosures through exact rational
Legendre overlap polynomials, rigorously bounded logarithms/square roots, and
Bernstein polynomial range bounds on continuum L cells. Read
`SPATIAL_COMPONENT_DERIVATION.md` for assumptions, activation identities and
executed probes. Run `python scripts/probe_spatial_overlap_v2.py` to reproduce
the 96-entry spatial comparison receipt. Run
`python -m unittest discover -s tests -p '*v2.py' -v` for all 19 v2 tests.

This repairs the spatial compression component only. It does not verify the
Archimedean matrix, coupling Gram, complement floor or reference spectral upper
bound. The full-operator gate continues to block. The earlier missing-adapter
list describes the complete historical matrix, not the now implemented isolated
spatial component.
