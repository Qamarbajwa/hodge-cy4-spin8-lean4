# Independent canonical pole entry review

**PASS for canonical pole component only. DONE.** Reviewer `/root/gov_reviewer`.

Rodrigues integration by parts boundary terms vanish; beta integral expansion gives stated positive modified spherical Bessel series. Subsequent term ratios decrease, first post-omitted ratio z^2/((2m+2)(2k+2m+3)) bounds tail geometrically. Endpoint monotonicity with positive series and exact sqrt grids encloses full positive L cell. Even positive/odd negative/mixed zero pole signs agree with canonical Hermitian form.

Independently checked50 Legendre exponential integrals and256 pole entries over a positive length cell, degrees0..7. Four tests passed. High precision quadrature is corroboration; enclosure proof uses exact series, geometric remainder and rational sqrt bounds.

Direct spherical_i_point converts z using Fraction rather than rational validator, so accepts binary floats and booleans as exact rational values; pole_matrix length uses strict validator. This does not invalidate enclosure for converted input but inconsistent input hygiene should be clarified.

Component matrix alone has no metadata operator gate; caller must retain conditional-component scope and full operator BLOCKED.

No Archimedean, coupling or complement bound follows from pole entries.

No actual operator or frontier certification. `NO_RH_PROOF=TRUE`.

Frozen SHA256:

- `research/certification_v2/pole_entries.py`: `8ebf795818bcce282d6569d4b369d042e00e2d81004b17e430d9272998f3f326`
- `research/certification_v2/POLE_ENTRY_DERIVATION.md`: `b1606a1d8ab368f582e9a616a0a61b04af2fa8a617acbd98f008fe7b417c050e`
- `tests/test_pole_entries_v2.py`: `f08856947a1ec50e1815ee57e71a30794871b4bebe9a2b407b032a872ff57153`
