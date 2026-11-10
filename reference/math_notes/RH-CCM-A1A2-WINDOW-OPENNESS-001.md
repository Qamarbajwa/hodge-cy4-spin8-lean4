# RH-CCM-A1A2-WINDOW-OPENNESS-001 — Fixed-Window Openness Analysis

## Governance and scope

- Task class: `T3 MATHEMATICAL_RESEARCH`
- Base accepted governance candidate: `git:ab20fafd1b81b4de306a236067f169b113684a4c`
- Base tree: `git-tree:2900def398b8313f8397102733d7a739e8736a1f`
- Task envelope: `RH-CCM-A1A2-WINDOW-OPENNESS-001_TASK_EXECUTION_ENVELOPE.yaml`
- Invariant: `NO_RH_PROOF = TRUE`
- `RH-T057`: `DEFERRED / FROZEN_UNEXECUTED`
- Status: `PROVED_EXISTENTIAL_NONQUANTITATIVE — QUANTITATIVE_DELTA_OPEN`

This record tests local openness of Chuk's simple-even result at ℓ₀ = 0.8. It does not claim a general CCM-A1/A2 theorem, a large-ℓ result, or an RH proof. The failed L² operator-norm route is not used.

## 1. Threshold-free interval

The active prime-power cutoff is `log n < 2ℓ`. At ℓ₀ = 0.8 the active entries are 2, 3, and 4. The next entry is 5, at

\[
 \ell_5=\frac12\log 5=0.8047189562170501\ldots.
\]

Therefore the first candidate region is

\[
 I_0=[0.8,\ell_5),
 \qquad 0<\delta<\ell_5-0.8.
\]

On `I_0` the finite prime sum is fixed. This removes the arithmetic jump from the interior of the candidate interval, but it does not by itself give uniform form continuity at the moving support boundary.

## 2. Fixed-space formulation

Let

\[
 H=L^2([-1,1]),\qquad
 (S_\ell v)(t)=\ell^{-1/2}v(t/\ell),
\]

so `S_ell` is unitary from `H` onto `L²([-ell,ell],dt)`. Define the transported forms

\[
 a_\ell[v]=q_\ell[S_\ell v].
\]

Let `Jv(x)=v(-x)`. The even and odd spaces `H_+` and `H_-` reduce `a_ell` whenever the transported form preserves inversion parity. The endpoint bounds from Chuk give

\[
 g_0\ge \min(8.206\times10^{-15}-2.523\times10^{-16},
                 2.085\times10^{-12}-2.523\times10^{-16})
      =7.9537\times10^{-15}.
\]

This is the available endpoint separation between the even ground state and the nearer of the odd ground state and second even level.

## 3. Conditional form-convergence theorem

The following is the exact variational statement needed for a positive window.

### Proposition (form/compactness/boundary-tightness continuation)

Assume that for `ell` in a right neighborhood of `ell0=0.8`:

1. `a_ell` are closed, uniformly lower-bounded forms on one common parity-invariant domain `D` contained in `H`, with a common form norm equivalent on that neighborhood.
2. The family converges in form topology at `ell0`: for every `v in D`, `a_ell[v] -> a_ell0[v]`, with a uniform form bound on bounded subsets of `D`.
3. The embedding `D -> H` is compact, and the low-energy sublevel sets of `a_ell` are uniformly boundary-tight: for every `eta>0` there is a boundary width `r>0` such that every normalized vector with `a_ell[v]` below one fixed low-energy bound has mass outside `[-1+r,1-r]` below `eta`, uniformly for `ell` near `ell0`.
4. The parity sectors reduce every `a_ell`, and the endpoint form has the simple-even gap `g_0` above.

Then the first even and odd min-max values, and the second even min-max value, converge to their `ell0` values as `ell downarrow ell0`. Consequently there is a `delta>0` such that for every `ell in [0.8,0.8+delta)`:

\[
 \lambda_1^{\rm even}(\ell)<\lambda_1^{\rm odd}(\ell),
 \qquad
 \lambda_1^{\rm even}(\ell)<\lambda_2^{\rm even}(\ell).
\]

The continuum ground state therefore remains even and simple on that interval.

### Proof skeleton

Form convergence gives the limsup inequalities by transporting endpoint trial spaces through `S_ell`. For the liminf, take normalized low-energy approximate minimizers. Uniform lower bounds keep them in a bounded subset of `D`; compact embedding gives an `H`-convergent subsequence. Boundary tightness prevents mass from escaping through the newly exposed support layer, so the limit belongs to the endpoint problem and the form liminf inequality applies. The min-max values therefore converge in each parity sector. Choose the neighborhood so that each of the three relevant values changes by less than `g_0/3`; both strict inequalities then persist.

This is a standard compact variational argument. It does not require, and does not assert, an `L² -> L²` operator-norm estimate.

## 4. CCM-specific obligations

The proposition becomes an unconditional Window Openness proof only after the following items are established for the actual transported Weil forms:

| Obligation | Required result | Current status |
|---|---|---|
| Common form domain | One parity-invariant closed domain for `a_ell`, `ell in I_0` | OPEN |
| Uniform lower/form bound | Uniform control sufficient for low-energy sublevel compactness | OPEN |
| Form convergence | `a_ell -> a_0.8` on the common domain, including archimedean and pole terms | OPEN |
| Boundary tightness | No low-energy mass escapes through the moving support boundary | OPEN |
| Threshold endpoint convention | One-sided treatment as `ell` approaches `ell_5` | OPEN; not needed in the strict interior of `I_0` |
| Quantitative modulus | Any explicit neighborhood size or an existence argument from the preceding limits | OPEN |

The existing source-locked record establishes only the fixed-scale certificate and the abstract conditional min-max lemma. It does not establish these CCM-specific hypotheses. The endpoint gap budget `g_0/3` is therefore a target tolerance, not achieved evidence.

## 5. Rejected route and failure boundary

The expression `||Q_ell - Q_0.8||_{L² -> L²}` is not a valid substitute: the relevant operator is unbounded, and changing support/dilation does not produce a bounded operator-norm perturbation. Any argument that silently replaces the form-domain problem by this norm estimate is rejected under the task envelope.

Likewise, fixed-vector pointwise continuity or continuity of the prime sum on `I_0` does not imply uniform form convergence, compact-resolvent continuity, or low-energy boundary tightness.

## 6. Initial preflight conclusion (superseded by Section 7)

The initial preflight correctly reduced Window Openness to a precise conditional theorem, but it was written before the nested-form compactness argument below was completed. Its statement that no positive `delta` had been established is retained as the historical preflight state and is superseded by Section 7.

The initial preflight established:

- a proved fixed-scale simple-even result at `ell=0.8`;
- a standard conditional form/compactness continuation lemma;
- an exact threshold-free candidate interval before `ell_5`;
- a quantitative endpoint gap budget;
- no unconditional positive `delta` had yet been recorded at that stage.

The historical preflight status was:

```text
WINDOW_OPENNESS = NOT_YET_PROVED_AT_INITIAL_PREFLIGHT
CONDITIONAL_ROUTE = FORM_CONVERGENCE + COMPACTNESS + LOW_ENERGY_BOUNDARY_TIGHTNESS
MISSING_RESULT = CCM_SPECIFIC_UNIFORM_FORM_AND_BOUNDARY_ESTIMATE
NO_RH_PROOF = TRUE
```

Section 7 supplies the bounded successor result. No claim promotion follows from the historical preflight alone.

## 7. Proof upgrade: nested-form right continuity

The source audit supplies a route that does not require a common form domain on every moving interval. CCM defines `QW_\lambda` as the restriction of the global Weil form to the support window, proves lower semicontinuity and a form core, and proves compactness of the form-domain embedding for each fixed outer window (CCM, Propositions 3.3–3.6). Its explicit formula has a finite prime sum indexed by `n <= lambda^2`.

Choose any

\[
 0.8<\ell_1<\ell_5=\tfrac12\log 5,
 \qquad \lambda_1=e^{\ell_1}.
\]

For every `ell` in `[0.8,ell_1]`, the active prime powers are exactly `{2,3,4}`. Thus, after zero extension to the fixed outer space

\[
 H_1=L^2([-\ell_1,\ell_1]),
\]

the quadratic expression is one fixed lower-bounded closed form `q` restricted to the nested subspaces

\[
 H_\ell=\{f\in H_1:\operatorname{supp}f\subseteq[-\ell,\ell]\}.
\]

The prime terms agree under zero extension because each is a bounded convolution-evaluation term; the archimedean and pole terms are already parts of the same global form. The same statement holds after restricting to the even or odd parity subspaces.

### Lemma (right continuity of nested compact-form min–max values)

Let `q` be a lower-bounded closed form on `H_1` whose form-domain embedding into `H_1` is compact. Let the restricted form domains be `D_ell^sigma = D(q) intersect H_ell^sigma`, with `ell downarrow ell0`, and let `mu_j^sigma(ell)` be any fixed finite min–max value in a parity sector. Then

\[
 \lim_{\ell\downarrow\ell_0}\mu_j^\sigma(\ell)=\mu_j^\sigma(\ell_0).
\]

#### Proof

Because the subspaces increase with `ell`, the min–max values are nonincreasing, so the right limit is at most the endpoint value. For the reverse inequality when `j=1`, choose normalized approximate minimizers `f_k` in `D_{ell_k}^sigma` with bounded form values. Lower boundedness makes them bounded in the shifted outer form norm. Compactness of the outer form-domain embedding gives a subsequence converging strongly in `H_1` to a normalized limit `f`. Since every `f_k` vanishes outside `[-ell_k,ell_k]`, the strong limit vanishes outside `[-ell0,ell0]`; this is the required low-energy boundary tightness. Lower semicontinuity gives `q[f] <= liminf q[f_k]`, and the min–max characterization at `ell0` gives the reverse inequality for the endpoint value.

For `j=2`, choose approximate minimizing orthonormal pairs `(f_k^1,f_k^2)` in `D_{ell_k}^sigma`. Compactness gives a diagonal subsequence converging strongly in `H_1` for both vectors. Strong convergence preserves orthonormality in the limit, support nesting places both limits in `D_{ell0}^sigma`, and the same lower-semicontinuity argument applies to the two-dimensional Rayleigh subspaces. The finite-index min–max argument is identical for higher `j`. Thus the two inequalities coincide. ∎

This is form convergence through the closed-form topology plus compactness and support-induced boundary tightness. It is not an operator-norm perturbation statement.

### Theorem (existential Window Openness)

Apply the lemma to the first odd value, first even value, and second even value at `ell0=0.8`. The endpoint gap satisfies `g0 >= 7.9537e-15`. By right continuity, there is an actual `delta>0`, with `delta <= ell1-0.8 < ell5-0.8`, for which each of the three values differs from its endpoint value by less than `g0/3`. Therefore

\[
 \lambda_1^{\rm even}(\ell)<\lambda_1^{\rm odd}(\ell),
 \qquad
 \lambda_1^{\rm even}(\ell)<\lambda_2^{\rm even}(\ell)
 \quad\text{for }0.8\leq\ell<0.8+\delta.
\]

Hence the continuum ground state remains even and simple on some genuine right-hand interval.

### Scope and limitations of the upgrade

This proves existence of a positive window but does not provide a numerical lower bound for `delta`. It also does not prove continuity through the threshold `ell5`, does not establish a uniform quantitative modulus, and does not alter the open general CCM-A1/A2 status. The proof uses the fixed prime set on the strict threshold-free interval and the compact outer-window form theorem; it does not claim that the sources prove a common domain globally in `ell`.

The complete theorem/lemma-level mathematical proof closure with full 2-dimensional Courant–Fischer min-max dimension and orthogonality preservation is established in [`RH-CCM-WINDOW-001-PROOF-CLOSURE-004.md`](file:///d:/Comfy%20UI/rheihman%20hypothesis/RH-CCM-WINDOW-001-PROOF-CLOSURE-004.md).

Updated status:

```text
WINDOW_OPENNESS = PROVED_EXISTENTIAL_NONQUANTITATIVE
INTERVAL = [0.8, 0.8+delta) for some delta>0 with delta < 0.5 log(5)-0.8
PROOF_CLOSURE = COMPLETED_WITH_EXPLICIT_LIMITATIONS (RH-CCM-WINDOW-001-PROOF-CLOSURE-004)
QUANTITATIVE_DELTA = OPEN
THRESHOLD_CROSSING = OPEN
NO_RH_PROOF = TRUE
```

Primary-source anchors: [CCM Proposition 3.3–3.6 & Theorem 3.5](https://arxiv.org/html/2511.22755#S3.SS1), [Chuk v1 Thm 8 / Zhu v2 Thm 6.2 and fixed-window formula](https://arxiv.org/html/2608.24827#S4), and [Zhu’s threshold-indexed symbol](https://arxiv.org/html/2608.24827#S2).

