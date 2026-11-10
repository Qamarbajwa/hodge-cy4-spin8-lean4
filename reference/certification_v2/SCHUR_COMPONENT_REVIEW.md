# Independent conditional Schur review

**PASS conditional component only. DONE.** Reviewer `/root/gov_reviewer`.

q>=<x,(A-K*K/beta)x>+beta||y+Kx/beta||^2. Norm inequality ||x||^2+||y||^2<=(1+2||K||^2/beta^2)||x||^2+2||z||^2 yields stated min lower bound. Trace diagonal upper sums bound ||K||^2 only under true full Gram enclosure assumption.

Common form domain stable under orthogonal projections; bounded L2 coupling K represents all cross terms; positive complement floor. Form-relative coupling is a separate theorem when bounded K fails.

Independently checked 80 exact rational 4x4 full blocks against the claimed bound with leading principal determinant minors. Four tests pass. Omitting true size2 coupling returns conditional finite PASS for indefinite [[1,2],[2,1]], yet operator remains BLOCKED; including G=4 correctly inconclusive.

Exact rational disjoint surviving supports for shifts separated by 1/10^9 establish norm difference >=sqrt2. Norm1 persists for r<2 while S2=0. Valid counterexample to generic compressed-shift full-space norm continuity.

No actual true A, full K*K enclosure, complement floor or common-domain theorem authenticated.

Impossible/non-PSD supplied Gram boxes may yield conditional finite results; they certify no actual Gram unless input provenance establishes it.

Noncontinuity applies to individual compressed translations; does not exclude cancellation in complete Weil form or weaker relative-form continuity.

Report does not promote prime residual Gram to full residual Gram; squared and mixed omitted component couplings remain obligations.

No actual operator/frontier certificate. `operator_status=BLOCKED`; `NO_RH_PROOF=TRUE`.

Frozen SHA256:

- `research/certification_v2/schur_component.py`: `fc4561d85f58feb82911c193f8a47cb95a707ac4f17c9603fc6e7ca21dbec980`
- `research/certification_v2/SCHUR_AND_CONTINUUM_OBLIGATIONS.md`: `9d508bb12a47829c848efc2f01a86e53a99706ed1555ee0c373022b02212130c`
- `tests/test_schur_component_v2.py`: `30f382e1af329cc2b9de19551248efd8507d0cdcf2fe939b5dad576ed9898a05`
