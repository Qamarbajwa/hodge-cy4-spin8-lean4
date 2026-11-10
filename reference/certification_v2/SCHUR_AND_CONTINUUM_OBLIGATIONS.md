# Conditional full-coupling Schur reduction and continuum strategy

Status: internally checked conditional lemma and executable finite arithmetic.
No actual Weil form, tail floor or cross-coupling enclosure is certified here.

Let H=X orthogonal-sum Y, with X finite dimensional. Assume a common form domain
stable under the projections, finite block A, and a bounded K:X->Y representing
ALL cross terms. Suppose

    q(x+y)=<Ax,x>+2 Re<Kx,y>+c[y],   c[y]>=beta ||y||^2, beta>0.

Then completion of the square gives

    q(x+y)>=(x,(A-K* K/beta)x)+beta ||y+Kx/beta||^2.

If enclosed finite inputs prove A-K* K/beta >= gamma I with gamma>0, write
z=y+Kx/beta and k^2>=||K||^2. Since

    ||x||^2+||y||^2 <= (1+2k^2/beta^2)||x||^2+2||z||^2,

the full lower bound is min(gamma/(1+2k^2/beta^2),beta/2)>0. A valid full
Gram enclosure supplies k^2<=trace(K* K)<=sum of diagonal upper endpoints.
Exact interval subtraction and LDL prove only the conditional finite inequality.
The function schur_bound always keeps operator_status=BLOCKED because it cannot
authenticate these analytic assumptions. A matrix with omitted cross terms can
give a false lower bound, demonstrated by the indefinite block [[1,2],[2,1]].

If the form's complement coupling is not representable by bounded K under this
L2 splitting, use a form-relative coupling theorem instead. Do not silently
replace it by a bounded-operator block matrix. Test functions must lie in the
appropriate form domain; operator-domain assumptions are stronger and separate.

The historical prime residual Gram G_prime-M_prime^2 encloses only that part of
the coupling. For K=K_prime+K_arch+K_pole, K* K contains all squared and mixed
terms. Using the prime residual alone needs a proof that remaining coupling is
zero or absorbed by an explicit error budget. Calling a truncation radius small
is insufficient until that radius is proved to cover the omitted blocks.

## Continuum obstacle and viable alternative

On L2([-1,1]) let S_r h(t)=h(t-r), with zero extension, 0<r<2. If
r'<2 and r'>r, choose a unit vector supported in [-1,-1+epsilon] with
epsilon<r'-r and epsilon<2-r'. Then S_r h and S_r' h have disjoint supports
and both retain norm1. Thus ||S_r-S_r'||>=sqrt(2) for arbitrarily small
r'-r: the compressed translations are not operator-norm continuous. At r=2
the shift is zero, whereas for every r<2 its norm is1, by a unit vector on
the nonempty surviving support. Support overlap going to zero does not imply
operator norm going to zero. This disproves a generic full-space linear norm
modulus for an individual shift, not a possible cancellation theorem for the
complete Weil form or a weaker relative-form modulus.

Preferred certificate architecture: transport to one fixed Hilbert space;
enclose the finite A_L and FULL residual Gram uniformly on a cell; prove a
uniform beta for its complement. The same conditional Schur argument then
covers every L in that closed cell without a full-operator Lipschitz assumption.
The accepted spatial Bernstein component already contributes one necessary
finite box. Remaining Archimedean and coupling boxes still need construction.
Adaptive cell subdivision tightens valid boxes; sampling cannot validate them.
