# Independent spatial component review

**PASS for the defined spatial component only. DONE.** `/root/gov_reviewer`.

Exact Legendre recurrence/binomial integration and Bernstein convex hull valid; clipped support boundary with zero hull valid. Rational log tail and square-root grid enclosures valid. Derivative q_ij prime(2-)=-(-1)^j/2 gives -4/(k sqrt(n)) vvT even and +4/(k sqrt(n)) vvT odd for negative coefficient definition.

Independent checks: 196 high precision direct Legendre overlap integrals, 2100 exact rational polynomial points inside independently examined Bernstein hulls, and 384 component entries spanning active and inactive shifts. Fourteen repository tests pass. All 21 prime powers through 43 independently recovered. Negative ratio, nonpositive length, composite base, duplicate terms and boolean degree reject.

Defined negative prime-shift coefficient matches inspected pre-L7 component formula. Historical L9 builder uses positive sign and unresolved normalization/operator mapping; no equivalence to L9 pipeline is certified.

Probe reuses historical Legendre evaluator and reconstructs spatial entry formula rather than full historical builder; its source hash does not mean whole-builder independence or proof.

Listed-term completeness remains external; omitted terms can be accepted as a different component.

Precision controls sqrt digits/log terms accept bool as int; not a soundness defect but inconsistent exact input hygiene.

thresholds.inventory does not validate first/last; reversed bounds return empty list. Treat default audited inventory only as certified enumeration scope.

No full operator or frontier certification. `operator_status=BLOCKED`; `NO_RH_PROOF=TRUE`.

Frozen SHA-256:

- `research/certification_v2/spatial_overlap.py`: `4b2856db1c365aa2aaee81fc203532a947dc38ca7d9635bd500047a7528e5e8a`
- `research/certification_v2/SPATIAL_COMPONENT_DERIVATION.md`: `853b6d7a5dad8de7785be89c68aec16d0b012d30d5243a108053cb34126bee5a`
- `scripts/probe_spatial_overlap_v2.py`: `3734eefc021321df804a57f5d504813fb32ee6e8623799b8f5e9fa40d30af25c`
- `tests/test_spatial_overlap_v2.py`: `34752ac4a105d4407c7e0f8f354793deafbaf242c4026b0c227b40d67af96dc3`
- `research/certification_v2/thresholds.py`: `70f9f0407f703c954db8921f1ce1715fdde59b17eea6aea4ef4fe675d0aa23cf`
- `tests/test_certification_v2_thresholds.py`: `0df8186732934c8c6c2134a73ffda2041787023c4b2060b87443baf53a5f4d54`
