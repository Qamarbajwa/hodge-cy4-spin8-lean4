"""Exact uniform canonical pole compact replacement norm bound; no operator claim."""
from fractions import Fraction as F
from math import factorial, isqrt

from research.certification_v2.exact_interval_ldl import rational
from research.certification_v2.pole_entries import odd_double_factorial


def sinh_upper(length,terms=32):
    length=rational(length)
    if length<0 or type(terms) is not int or terms<1:
        raise ValueError("nonnegative argument and positive term count required")
    total=sum((length**(2*j+1)/factorial(2*j+1) for j in range(terms)),F(0))
    omitted=length**(2*terms+1)/factorial(2*terms+1)
    rho=length**2/((2*terms+2)*(2*terms+3))
    if rho>=1:
        raise ValueError("more sinh series terms required")
    return total+omitted/(1-rho)


def relative_sqrt_upper(value,bits=128):
    """Integer square-root grid with scale adapting to very small exact values."""
    value=rational(value)
    if value<0 or type(bits) is not int or bits<1:
        raise ValueError("nonnegative value and positive precision required")
    if value==0:
        return F(0)
    exponent=max(bits,bits+(value.denominator.bit_length()-value.numerator.bit_length()+1)//2)
    denominator=2**exponent
    floor=isqrt(value.numerator*denominator**2//value.denominator)
    low=F(floor,denominator)
    return low if low**2==value else F(floor+1,denominator)


def parity_tail_squared(length_upper,degree_cutoff,parity,terms=16):
    """Upper bound sum of squared cosh(even)/sinh(odd) coefficients at k>=d."""
    length_upper=rational(length_upper)
    if length_upper<=0 or type(degree_cutoff) is not int or degree_cutoff<1 or parity not in (0,1) or type(terms) is not int or terms<1:
        raise ValueError("positive length/degree/terms and parity0 or1 required")
    start=degree_cutoff+(degree_cutoff%2!=parity)
    z=length_upper/2
    # i_k(z) <= z^k/(2k+1)!! /(1-r_start) for all k>=start.
    r=z*z/(2*(2*start+3))
    if r>=1:
        raise ValueError("modified-Bessel geometric coefficient majorant unavailable")
    term=(2*start+1)*z**(2*start)/odd_double_factorial(2*start+1)**2
    total=F(0)
    k=start
    for _ in range(terms):
        total+=term
        term*=z**4/((2*k+1)*(2*k+3)**2*(2*k+5))
        k+=2
    rho=z**4/((2*k+1)*(2*k+3)**2*(2*k+5))
    if rho>=1:
        raise ValueError("more parity tail terms required")
    raw_sum=total+term/(1-rho)
    return {"tail_squared_upper":2*length_upper*raw_sum/(1-r)**2,
            "first_degree":start,"explicit_terms":terms,
            "modified_bessel_series_ratio_upper":r,
            "tail_geometric_ratio_upper":rho}


def pole_compact_bound(length_upper,degree_cutoff,tail_terms=16,sinh_terms=32):
    length_upper=rational(length_upper)
    even=parity_tail_squared(length_upper,degree_cutoff,0,tail_terms)
    odd=parity_tail_squared(length_upper,degree_cutoff,1,tail_terms)
    sinh=sinh_upper(length_upper,sinh_terms)
    c_squared=length_upper+sinh
    s_squared=sinh-length_upper
    c_norm=relative_sqrt_upper(c_squared)
    s_norm=relative_sqrt_upper(s_squared)
    c_tail=relative_sqrt_upper(even["tail_squared_upper"])
    s_tail=relative_sqrt_upper(odd["tail_squared_upper"])
    delta=4*c_norm*c_tail+4*s_norm*s_tail
    return {"status":"UNIFORM_CANONICAL_POLE_COMPACT_NORM_ERROR_BOUND",
            "length_upper":str(length_upper),"degree_cutoff":degree_cutoff,
            "pole_delta_upper":str(delta),"c_full_norm_squared_upper":str(c_squared),
            "s_full_norm_squared_upper":str(s_squared),
            "c_full_norm_upper":str(c_norm),"s_full_norm_upper":str(s_norm),
            "c_tail_norm_upper":str(c_tail),"s_tail_norm_upper":str(s_tail),
            "even_tail":{k:str(v) if isinstance(v,F) else v for k,v in even.items()},
            "odd_tail":{k:str(v) if isinstance(v,F) else v for k,v in odd.items()},
            "sinh_terms":sinh_terms,"sqrt_relative_precision_bits":128,
            "projection":"orthogonal real Legendre degrees0 through d-1 on [-L,L]",
            "formula":"delta_pole<=4||c||||Qc||+4||s||||Qs||",
            "canonical_vectors":"c=cosh(x/2), s=sinh(x/2)",
            "uniform_scope":"every0<L<=length_upper, canonical metric/projection",
            "full_operator_status":"BLOCKED","NO_RH_PROOF":True}
