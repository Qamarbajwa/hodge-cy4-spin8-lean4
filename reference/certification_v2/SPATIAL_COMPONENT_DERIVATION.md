# Exact spatial shift compression and continuum enclosure

This derives and executes one real component of the historical operator, without
assuming its positivity or certifying the full form. `NO_RH_PROOF = TRUE`.

## Definition and independent construction

Let phi_i(x)=sqrt((2i+1)/(2L)) P_i(x/L), extended by zero outside [-L,L].
Let a=log(n), c_n=-log(p)/sqrt(n), where n=p^k. The two-shift contribution is

    M_n(i,j)=c_n sqrt((2i+1)(2j+1)) [q_ij(r)+q_ji(r)], r=a/L,
    q_ij(r)=1/2 integral_(r-1)^1 P_i(t)P_j(t-r) dt  (0 <= r <= 2),
    q_ij(r)=0 (r >= 2).

The L factors cancel exactly in the normalized coordinates. The implementation
builds P_i with its exact three-term rational recurrence, expands P_j(t-r)
binomially, and integrates each power of t at the exact polynomial endpoints.
Consequently q_ij is a rational polynomial of degree at most i+j+1; no quadrature,
floating normalization or Bessel recurrence enters this independent builder.

For positive rational L intervals, rational logarithm enclosures give a uniform
r interval. The atanh series uses z=(x-1)/(x+1): the first K terms are a lower
bound and the remaining terms are bounded by

    2 z^(2K+1) / ((2K+1)(1-z^2)).

Range reduction x=2^m y, 1 <= y < 2, gives log(x)=m log(2)+log(y).
Square roots use integer isqrt on scaled exact rational numerators and an
explicit next-grid-point upper bound. For polynomial range enclosure on [a,b],
substitute r=a+(b-a)t, then convert the rational monomial coefficients c_k to
Bernstein coefficients b_i=sum_(k<=i) c_k binom(i,k)/binom(d,k). The Bernstein
basis is nonnegative and sums to one on [0,1], so the minimum/maximum control
coefficients rigorously enclose the polynomial. A cell crossing r=2 is clipped
to its active portion and the resulting enclosure is hulled with zero.

These statements prove a uniform component enclosure for every L in the input
cell, assuming precisely the listed valid prime-power terms. They do not rely
on endpoint monotonicity. Term-list completeness and any operator domain/form
identification remain separate obligations.

## Exact activation identities

At r=0, q_ij=delta_ij/(2i+1), by Legendre orthogonality. Reflection t -> r-t
gives q_ji=(-1)^(i+j)q_ij. At r=2 every q_ij is exactly zero, so each prime-power
shift activates continuously at L_n=log(n)/2. Its left r derivative is

    q'_ij(2-)=-(-1)^j/2.

This follows directly from Leibniz's rule: the boundary integrand is
P_i(1)P_j(-1), and the integral term has zero length at activation. The tests
execute the same identity from exact polynomial derivatives for 64 pairs.

For one parity sector let v_i=sqrt(2i+1). Combining the two directions and
dr/dL=-4/log(n) at L_n gives the exact right L derivative of the new term:

    dM_n/dL (L_n+) = -4/(k sqrt(n)) vv^T  (even sector),
    dM_n/dL (L_n+) = +4/(k sqrt(n)) vv^T  (odd sector).

Below L_n the term is zero and its derivative is zero. Thus activation is
continuous but generally not differentiable. The spatial component has opposite
sign activation effects in the two sectors. This is a concrete obstruction to
inferring same-sign component monotonicity from inclusion alone; it does not
establish the sign of the derivative of the complete operator.

## Executed comparison and probes

`python scripts/probe_spatial_overlap_v2.py` checks 96 entries: four even modes
and four odd modes at L=0.8, 0.85 and 0.97, with n=2,3,4,5. The comparison
executes the historical Gauss/dyadic spatial entry formula at 85 digits using
its Legendre evaluator and 224-bit rounded factors. Exact Python integer dot
products replace its accelerator; the complete historical builder is not run.
Every reference value lies in the independently proved component enclosure.
The largest reference/midpoint difference is about 1.76e-35. This numerical
comparison is a consistency probe, not the proof of enclosure.

Executed adversarial probes give identical rational intervals after reversing
term order, reject a duplicated n=5 term, and detect omission of n=5 through
disjoint constant-mode intervals. Nine sampled lengths lie in their uniform
continuum boxes. The exact Bernstein bounds narrow under cell refinement:
maximum even-sector entry widths are approximately 1.0943 for [0.8,0.9],
0.28341 for [0.84,0.86], and 0.028785 for [0.849,0.851]. The continuum theorem
comes from the rational construction, not these samples.

Eleven spatial tests execute orthogonality, threshold zeros/derivatives, parity,
Bernstein conversion, log refinement, square-root inequalities, term validation,
ordering/omission and continuum containment. Eight finite LDL tests also pass.
The generated `spatial_probe_receipt.json` binds the historical comparison source
by SHA256. No full operator certificate is emitted: Archimedean entries,
complement floor, coupling Gram and reference spectral upper bound remain missing.
