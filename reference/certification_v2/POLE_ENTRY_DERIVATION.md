# Canonical pole entry enclosures

Status: internally checked entry component, independent review pending.
This constructs no Archimedean entry or complete operator certificate.

With normalized Legendre basis phi_k=sqrt((2k+1)/(2L)) P_k(x/L), Rodrigues'
formula and k integrations by parts give

    integral_-1^1 P_k(u) exp(zu) du
      = z^k/(2^k k!) integral_-1^1 (1-u^2)^k exp(zu) du = 2 i_k(z).

Boundary terms vanish because (1-u^2)^k has zeros of multiplicity k.
Expanding exp(zu), integrating even powers with the beta integral, and cancelling
factorials yields

    i_k(z)=sum_(j>=0) z^(k+2j)/(2^j j! (2k+2j+1)!!).

For z>=0 all coefficients are positive. After m retained terms, the first
omitted term is u_m and each later ratio is at most

    r=z^2/((2m+2)(2k+2m+3)).

If r<1, the exact remainder lies between0 and u_m/(1-r). Positive monomials
also prove monotonicity in z; enclosing a positive L cell by its endpoints
therefore encloses every pole vector coefficient throughout that cell.
Integer square-root rational grids enclose sqrt(2(2k+1)L). Thus

    v_k=sqrt(2(2k+1)L) i_k(L/2)

has justified exact rational bounds. The canonical Hermitian pole form is
2 c* c-2 s* s. Even-even entries are +2 v_i v_j, odd-odd are -2 v_i v_j,
and opposite-parity entries vanish. This matches the convention in the operator
identity foundation; it is not an identity with the historical L9 builder,
which omitted these blocks. No floating Bessel evaluation or quadrature is used.

The output uses exact rational arithmetic, includes the geometric series tail
and square-root error, and encloses a whole supplied L interval. Its connection
to the complete canonical form still depends on independent identity review.
