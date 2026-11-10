# RH-CCM-A3-DIRECT-PROOF-001

## Fixed-λ Ritz ground-state convergence

**Task class:** `T3 MATHEMATICAL_PROOF_ATTEMPT`  
**Scope:** one fixed λ > 1; no claim is uniform as λ → ∞.  
**Invariant:** `NO_RH_PROOF = TRUE`  
**Forbidden in this task:** CCM-A1, CCM-A2, RH-T057.

## Source and notation corrections

The logarithmic coordinate map in CCM Proposition 3.2 is recorded here in its
source direction. Put \(L=2\log\lambda\). Then

\[
 \kappa_\lambda:L^2([0,L],dx)\longrightarrow
 L^2([\lambda^{-1},\lambda],d^*u),\qquad
 (\kappa_\lambda f)(u)=f(\log(\lambda u)).
\]

This is distinct from the arithmetic map
\[
 (E f)(u)=u^{1/2}\sum_{n\geq1}f(nu).
\]
If a centered coordinate is used, it is denoted separately (for example
\(\tau=\log u\)); it is not the project symbol \(\kappa_\lambda\).

Reed--Simon XIII.64 is not used as the theorem proving Ritz eigenvector
convergence. It is retained only historically as a compact-resolvent/discrete-
spectrum reference where applicable; the CCM-A3 argument below is proved
directly from the frozen assumptions. No Chatelin theorem number is needed.

CCM Theorem 5.10 is described with the exact wording **all zeros lie on the
real line**. Its finite vector is \(\xi_{\lambda,N}\), not the continuum vector
\(\xi_\lambda\).

## Frozen assumptions

Fix \(\lambda>1\), and let
\[
 H=L^2([\lambda^{-1},\lambda],d^*u),\quad q=QW_\lambda,\quad
 A=A_\lambda,\quad V_N=E_N.
\]

For the associated closed sesquilinear form, also write \(a[\cdot,\cdot]\), so
\(q[v]=a[v,v]\). The only inputs are:

1. \(q\) is closed and lower semibounded.
2. \(\bigcup_N V_N\) is a form core.
3. \(\mu_N=\min\{q[v]:v\in V_N,\|v\|=1\}\) decreases to
   \(\mu=\inf\{q[v]:v\in\operatorname{Dom}(q),\|v\|=1\}\).
4. \(A\) has compact resolvent.
5. \(\mu\) is a simple eigenvalue.
6. Its normalized eigenvector \(\xi_\lambda\) is even under \(J\).
7. \(J\) is a unitary involution, \(JV_N=V_N\), and \(q[Jv]=q[v]\).

The word “simple” in item 5 means
\(\ker(A-\mu I)=\mathbb C\xi_\lambda\). The proof does not establish the
continuum simple-even hypothesis; it is conditional on it.

## Level 1: mechanism

**Energy convergence plus compactness forces every normalized Ritz ground-state
subsequence into the unique continuum ground eigenspace.**

## Level 2: proof architecture

Shift \(q\) by \(\beta>-\inf\sigma(A)\), so
\(q_\beta=q+\beta\|\cdot\|^2\) is a positive closed form. The convergent Ritz
energies make every normalized minimizer bounded in the form norm. Compact
resolvent makes the embedding of the form domain into \(H\) compact, so a
subsequence converges strongly in \(H\). Strong convergence preserves the unit
norm; lower semicontinuity places the limit at energy \(\mu\), hence in the
ground eigenspace. Simplicity reduces every cluster point to a phase of
\(\xi_\lambda\), and phase alignment removes that phase. The same compactness
argument applied simultaneously to two orthogonal minimizers rules out
infinitely many finite multiplicities at least two. Finally, form invariance
makes each simple finite ground vector a \(J\)-eigenvector; an infinite odd
subsequence would converge to an odd continuum ground state, contradicting the
even hypothesis.

The load-bearing ingredient is
\[
\boxed{\text{compact form-domain embedding }\operatorname{Dom}(q)\hookrightarrow H
       \text{ plus simplicity of the limit eigenvalue}.}
\]

The compact embedding is not a hidden hypothesis: for a lower-bounded
self-adjoint operator with compact resolvent it follows from the spectral
theorem, as shown explicitly below. The form domain is used throughout; no
identification with \(H^1\) is made.

## Level 3: complete proof

### Lemma 1: compact form-domain embedding

Choose \(c>-\inf\sigma(A)\). The form norm
\[
 \|v\|_{q_c}^2=q[v]+c\|v\|^2
\]
is equivalent to the usual norm on \(\operatorname{Dom}(q)\), and
\(\operatorname{Dom}(q)=\operatorname{Dom}((A+c)^{1/2})\). Since \(A\) has compact
resolvent, its spectral projections below any finite level have finite rank and
its eigenvalues \(\alpha_k+c\) tend to \(+\infty\). For a \(q_c\)-bounded
sequence \(w_j\), let \(P_K\) project onto the span of eigenvectors with
\(\alpha_k+c\le K\). Then
\[
 \|(I-P_K)w_j\|^2
 \le K^{-1}\|(A+c)^{1/2}w_j\|^2
 \le K^{-1}C
\]
uniformly in \(j\). The finite-dimensional sequences \(P_Kw_j\) have strongly
convergent subsequences. A diagonal choice followed by the displayed tail
bound gives a strongly \(H\)-convergent subsequence of \(w_j\). Thus
\[
 \operatorname{Dom}(q)\hookrightarrow H
\]
is compact. This is the only compactness input used below.

### Lemma 2: strong convergence of normalized Ritz minimizers

For each \(N\), choose a normalized minimizer
\(\xi_{\lambda,N}\in V_N\), so
\[
 \|\xi_{\lambda,N}\|=1,\qquad q[\xi_{\lambda,N}]=\mu_N.
\]
Choose \(\beta>-\inf\sigma(A)\). Because \(\mu_N\to\mu\),
\[
 q_\beta[\xi_{\lambda,N}]=\mu_N+\beta
\]
is bounded. Hence the sequence is bounded in the form norm. Lemma 1 gives,
from every subsequence, a further subsequence (still indexed by \(N_j\)) and
some \(v\in H\) such that
\[
 \xi_{\lambda,N_j}\to v\quad\text{strongly in }H.
\]
The strong convergence gives norm preservation:
\[
 \|v\|=\lim_j\|\xi_{\lambda,N_j}\|=1.
\]
The closed semibounded form is lower semicontinuous after the positive shift.
Therefore \(v\in\operatorname{Dom}(q)\) and
\[
 q_\beta[v]\le\liminf_j q_\beta[\xi_{\lambda,N_j}]
                   =\mu+\beta.
\]
Subtracting \(\beta\|v\|^2=\beta\) gives \(q[v]\le\mu\). By the definition of
\(\mu\), every unit vector in the form domain has energy at least \(\mu\), so
\[
 q[v]=\mu.
\]
The variational characterization of the bottom of a closed form therefore
puts \(v\) in \(\ker(A-\mu I)\). Simplicity yields
\[
 v=e^{i\theta}\xi_\lambda
\]
for some \(\theta\).

Now phase-align each minimizer whenever its inner product with \(\xi_\lambda\)
is nonzero: in the complex case multiply by the unique unit scalar making
\(\langle\xi_{\lambda,N},\xi_\lambda\rangle\) nonnegative real; in the real
case choose its sign. The preceding cluster-point argument shows that every
strong cluster point of the aligned sequence is \(+\xi_\lambda\), because a
cluster point \(e^{i\theta}\xi_\lambda\) has aligned inner product
\(e^{i\theta}\) with \(\xi_\lambda\), which is nonnegative real only when the
phase is \(1\). The inner product is eventually nonzero because any such
subsequence has absolute inner product tending to \(1\). If the full aligned
sequence did not converge to \(\xi_\lambda\), a subsequence would stay a fixed
positive distance away and compactness would produce a further cluster point,
contradicting the preceding uniqueness. Consequently
\[
 e^{i\theta_N}\xi_{\lambda,N}\longrightarrow\xi_\lambda
 \quad\text{strongly in }H.
\]

### Lemma 3: eventual simplicity

Suppose, for contradiction, that \(\mu_N\) has multiplicity at least two for
infinitely many \(N\). Restrict to those \(N\), and choose orthonormal ground
minimizers \(u_N,v_N\in V_N\). Both have form energy \(\mu_N\), hence both are
bounded in the shifted form norm. Applying Lemma 1 to the pair and taking a
common subsequence gives
\[
 u_{N_j}\to u,\qquad v_{N_j}\to v\quad\text{strongly in }H.
\]
Strong convergence preserves both norms and inner products, so
\[
 \|u\|=\|v\|=1,\qquad\langle u,v\rangle
 =\lim_j\langle u_{N_j},v_{N_j}\rangle=0.
\]
The lower-semicontinuity argument of Lemma 2 gives \(q[u]\le\mu\) and
\(q[v]\le\mu\). Unit norm and the definition of \(\mu\) force
\(q[u]=q[v]=\mu\), so both \(u\) and \(v\) belong to
\(\ker(A-\mu I)\). They are nonzero and orthogonal, contradicting
\(\dim\ker(A-\mu I)=1\). Therefore there is \(N_0(\lambda)\) such that
\[
 \mu_N\text{ is simple for every }N\ge N_0(\lambda).
\]

No nestedness of the individual \(V_N\) is used in this contradiction; only
the stated energy convergence and the uniform form bound are used. Nestedness
is relevant to the source proof of monotonicity, not to this extraction
argument.

### Lemma 4: eventual even parity

The hypotheses \(JV_N=V_N\), unitarity of \(J\), and \(q[Jv]=q[v]\) imply by
polarization that \(a[Jx,Jy]=a[x,y]\) on \(V_N\). Thus the finite self-adjoint
Ritz operator associated with \(a|_{V_N}\) commutes with \(J|_{V_N}\). Once
\(N\ge N_0(\lambda)\), its one-dimensional ground eigenspace is invariant
under \(J\). Hence
\[
 J\xi_{\lambda,N}=\varepsilon_N\xi_{\lambda,N},\qquad
 \varepsilon_N\in\{+1,-1\}.
\]

Assume infinitely many of these simple ground vectors are odd. Along that
subsequence, Lemma 1 and Lemma 2 give a strongly convergent subsubsequence
whose limit is a nonzero continuum ground state. The odd subspace
\[
 H_-=\ker(J+I)
\]
is closed because \(J\) is bounded: if \(w_j\to w\) strongly and
\(Jw_j=-w_j\), then \(Jw=-w\). The limit is therefore odd. But the continuum
ground eigenspace is \(\mathbb C\xi_\lambda\), and \(J\xi_\lambda=\xi_\lambda\);
every vector in that one-dimensional eigenspace is even. This is a
contradiction. Thus there is \(N_1(\lambda)\) such that
\[
 J\xi_{\lambda,N}=\xi_{\lambda,N}\quad\text{for all }N\ge N_1(\lambda).
\]

With \(N_*=\max(N_0,N_1)\), the fixed-\(\lambda\) conclusion is
\[
 \boxed{\text{simple finite ground state + even parity + strong }H\text{-convergence
 eventually in }N.}
\]

This is the conditional `CCM-FIN-SE` conclusion modulo the separate finite
normalization \(\delta_N(\xi_{\lambda,N})=1\). It is not a proof of CCM-A1 or
CCM-A2.

## CCM-A3N separation and zero-set analysis

The proof establishes no boundary-value convergence. In particular,
\[
 \delta_N(\xi_{\lambda,N})\to\xi_\lambda(\lambda)
\]
does **not** follow from strong convergence in \(L^2\).

Two statuses must remain separate:

* `A3N_NEEDED_FOR_ZERO_SETS`: **not necessarily**, after a scalar-only
  normalization. On the fixed interval, the zero-frequency Mellin functional
  \(f\mapsto\widehat f(0)=\int f\,d^*u\) is a bounded linear functional on
  \(H\). Thus strong \(H\)-convergence implies
  \(\widehat{\xi_{\lambda,N}}(0)\to\widehat{\xi_\lambda}(0)\). If the limiting
  scalar is nonzero, then it is eventually nonzero and the normalized
  transforms \(\widehat{\xi_{\lambda,N}}(z)/\widehat{\xi_{\lambda,N}}(0)\)
  have the same zero sets as the unnormalized transforms. This trivial scalar
  observation can avoid a boundary evaluation normalization when the only
  target is a zero set. It does not by itself prove the required
  \(\lambda\to\infty\) locally uniform Mellin convergence.
* `A3N_NEEDED_FOR_NORMALIZED_FUNCTION_CONVERGENCE`: **yes, for the source's
  boundary-normalized or exact determinant normalization unless another
  nonzero scalar normalization and its convergence are supplied**. The present
  \(L^2\) theorem supplies neither point evaluation nor the source constant.

Therefore CCM-A3N remains an open normalization bridge, while a scalar
zero-set route is available conditionally on a nonvanishing bounded functional
and the separate locally uniform Mellin-limit theorem.

## Adversarial proof audit

* **Compactness misuse:** none. Compactness is derived from compact resolvent
  for the form-domain embedding, not from finite-dimensionality or from an
  unbounded-operator embedding assertion.
* **Form vs operator domain:** the minimizers and lower semicontinuity use
  \(\operatorname{Dom}(q)\). Membership in the eigenspace follows only after
  attaining the form minimum, via the representation theorem.
* **Norm preservation:** explicitly supplied by strong \(H\)-convergence before
  using the variational definition of \(\mu\).
* **Phase ambiguity:** all cluster points are phases of the simple eigenvector;
  eventual nonzero overlap and phase alignment force the phase to be \(1\).
* **Multiplicity:** two orthonormal finite minimizers have a common strongly
  convergent subsequence; inner products are continuous under strong
  convergence, so orthogonality survives.
* **Parity closure:** \(\ker(J+I)\) is closed since \(J\) is bounded.
* **Non-nested \(V_N\):** no nestedness is used after the energy convergence
  assumption has been granted. The source assumptions already provide the
  needed \(\mu_N\to\mu\).
* **Uniformity:** every threshold is \(N_0(\lambda)\), \(N_1(\lambda)\), or
  \(N_*(\lambda)\) for the fixed chosen \(\lambda\). No uniform-in-\lambda
  statement is made.

## Understanding gate and claim status

The Level 1 and Level 2 explanations are given above, and the Level 3 proof
is complete under the frozen assumptions. The independent audit is recorded in
`RH-CCM-A3-DIRECT-PROOF-001_INDEPENDENT_REVIEW.md`. Its verdict is
`PROOF_PASS_WITH_LIMITATIONS`, so the conditional claim status is:

`INDEPENDENTLY_VERIFIED`

The limitations are exactly: convergence is conditional on the frozen
simple-even continuum hypothesis; without phase alignment it is only modulo
phase; no boundary normalization follows; and all thresholds are
lambda-dependent.

**Provenance:**

`yaml
protocol: RH-CCM-A3-DIRECT-PROOF-001
writer_role: orchestrator
reviewer_role: independent functional-analysis reviewer
reviewer_independence: HIGH (distinct context)
formal_theorem_prover: false
claim_status: INDEPENDENTLY_VERIFIED
review_verdict: PROOF_PASS_WITH_LIMITATIONS
`
