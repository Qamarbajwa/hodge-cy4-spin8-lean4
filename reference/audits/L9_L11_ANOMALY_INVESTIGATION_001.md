# L9-L11 anomaly: independent spatial quadrature diagnosis

Date: 2026-10-04. Status: DIAGNOSTIC_FINDING; NO_RH_PROOF = TRUE.

The historical audit reports stored minimum 0.663105 versus recomputed minimum 0.072035, with maximum odd drift 0.6500888. These values are inherited from `RH_CERTIFICATION_PIPELINE_AUDIT_001.md`, not newly recomputed in this investigation. The full drift cause remains unresolved.

## Direct code finding

`scripts/verify_l9_l11_coercive_interval_stability_001.py` fixes spatial quadrature `gl_deg=20` at line 165 and calls its builder with `N_sec=50` at line 323. The odd basis includes Legendre degree 99. Products of the two shifted Legendre polynomials therefore reach degree 198 in the affine quadrature variable. A q-node Gauss-Legendre rule integrates degrees through 2q-1 exactly, so q=100 suffices in exact arithmetic; q=20 guarantees only degree39. See [NIST DLMF section 3.5(v)](https://dlmf.nist.gov/3.5#v). This degree argument is an elementary algebraic deduction; it is independent of the eigenvalue audit.

The builder uses rounded float64 nodes and weights, high precision polynomial evaluation and integer accumulation. Accurate accumulation does not repair inaccurate integration. Other interval builders also use degree20, so this defect is not exclusive to L9-L11. In particular N_sec35 in L11-L13 requires70 nodes for all spatial products.

## Executed isolation probe

Run `python research/audits/l9_l11_spatial_quadrature_probe.py`. Results are saved in `L9_L11_SPATIAL_QUADRATURE_PROBE_001.json`. This independent float64 implementation reproduces the historical spatial basis factors, coefficients and positive sign, excluding the archimedean block and integer/Ozaki implementation.

| Endpoint | Degree20 versus120 even norm | Degree20 versus120 odd norm | Degree100 versus120 maximum norm |
| --- | ---: | ---: | ---: |
| log3 | 1.423177811 | 1.358633545 | 9.85e-13 |
| half log11 | 1.723551359 | 1.681145245 | 1.07e-12 |

Differences are spectral matrix norms of spatial blocks, not eigenvalue differences of the complete operator. These are floating point observations, not outward-rounded bounds. The near agreement of degrees100 and120 is consistent with the algebraic degree requirement. Degree60 still differs by approximately0.38 to0.47, so a modest quadrature escalation is insufficient.

## Consequences and open attribution

The observed spatial discrepancy is larger than the historical stored positive margin, so the existing degree20 calculation cannot support a negligible spatial quadrature-error claim without additional analysis. This does not prove the true quadratic form is negative: matrix perturbation norms supply possible error budgets, not realized eigenvalue shifts.

The fixture provenance is not reconstructible from this isolation probe. Attribution requires matched full builder runs at degrees20,100,120, exact matching T/N/precision/sign conventions, and separate archimedean-quadrature convergence. A corrected implementation must use verified polynomial integration or verified Gauss nodes/weights and include rounding errors. Replacing20 by100 alone gives no rigorous certificate.

An additional unresolved identity issue is that this builder adds the prime overlap with a positive coefficient, whereas the root legacy synthesis describes an attractive negative prime contribution. The correct sign must be settled from a single explicit-formula convention, including whether the matrix represents Q, a correction to Q, or a transformed comparison form. This report preserves the historical sign in its diagnostic and does not infer a sign bug from naming alone.

No governance promotion, endpoint extension, or proof claim follows from this investigation.
