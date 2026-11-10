# RH-CCM-A3-DIRECT-PROOF-001 — Independent proof audit

**Reviewer mandate:** FUNCTIONAL_ANALYSIS_PROOF_AUDIT  
**Reviewer:** independent subagent `01a04f83-2fd5-7990-9547-912de8e5b4e7` (Plato)  
**Independence:** HIGH — distinct context; no repository edits by reviewer  
**Verdict:** `PROOF_PASS_WITH_LIMITATIONS`

## Independent reconstruction

For each fixed \(\lambda>1\), the frozen assumptions suffice for:

1. strong \(H\)-convergence of normalized Ritz minimizers modulo phase, and
   strong convergence to \(\xi_\lambda\) after eventual phase alignment;
2. eventual simplicity of \(\mu_N\);
3. eventual evenness of the finite ground vectors.

The reviewer independently used the following chain. Compact resolvent gives
compact embedding of the form domain
\(\operatorname{Dom}(q)=\operatorname{Dom}((A+c)^{1/2})\) into \(H\). Bounded
Ritz energies give bounded shifted form norm. Every subsequence therefore has
a strongly \(H\)-convergent subsubsequence. Strong convergence preserves the
unit norm, and closed-form lower semicontinuity gives energy at most \(\mu\);
the variational definition gives equality, so every cluster point is a phase
of the simple ground vector. Phase alignment removes the phase, yielding full
sequence convergence.

If infinitely many finite ground spaces had dimension at least two, two
orthonormal minimizers could be extracted along one common subsequence. Their
strong limits would be orthogonal unit ground states, contradicting the
one-dimensional continuum ground eigenspace. Nestedness is not needed after
\(\mu_N\downarrow\mu\) is assumed.

Form invariance and \(JV_N=V_N\) make the finite form operator commute with
\(J\). A simple finite ground vector is therefore even or odd. The odd sector
\(\ker(J+I)\) is closed; an infinite odd subsequence would have an odd
continuum ground limit, contradicting the assumed even continuum ground
state.

## Limitations confirmed by the audit

* Without phase alignment, only convergence modulo a unimodular scalar is
  valid.
* Strong \(L^2\) convergence gives no endpoint, trace, or pointwise
  convergence, so it does not prove
  \(\delta_N(\xi_{\lambda,N})\to\xi_\lambda(\lambda)\).
* A zero-frequency scalar normalization can avoid boundary normalization for
  zero-set purposes only when the limiting scalar is nonzero and a separate
  locally uniform Mellin-limit argument is supplied.
* Every conclusion is pointwise in the fixed parameter \(\lambda\); no
  uniform-in-\(\lambda\) threshold or limit is established.

## Claim decision

The audit is sufficient for the conditional claim status
`INDEPENDENTLY_VERIFIED`. The limitations above are part of the claim and do
not promote CCM-A1, CCM-A2, CCM-A3N, CCM-B*, or any RH statement.

