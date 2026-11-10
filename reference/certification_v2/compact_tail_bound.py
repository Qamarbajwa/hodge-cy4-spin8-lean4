"""Exact sufficient cutoff-tail bound; all analytic inputs remain explicit."""
from fractions import Fraction as F
from research.certification_v2.exact_interval_ldl import rational
from research.certification_v2.spatial_overlap import sqrt_enclosure

def cutoff_tail_bound(length_upper,cutoff,degree_cutoff,symbol_sup,terms=32):
    length_upper,cutoff,symbol_sup=map(rational,(length_upper,cutoff,symbol_sup))
    if length_upper<=0 or cutoff<=0 or symbol_sup<0 or type(degree_cutoff) is not int or degree_cutoff<1 or type(terms) is not int or terms<1:
        raise ValueError('positive length/cutoff, nonnegative symbol bound, positive degree/terms required')
    z=length_upper*cutoff
    df=1
    for k in range(1,2*degree_cutoff+2,2):
        df*=k
    term=z**(2*degree_cutoff)/(df*df)
    total=F(0)
    for k in range(degree_cutoff,degree_cutoff+terms):
        total+=term
        term*=z*z/(2*k+3)**2
    next_degree=degree_cutoff+terms
    rho=z*z/(2*next_degree+3)**2
    if rho>=1:
        raise ValueError('more terms required before geometric remainder applies')
    tail_sum=total+term/(1-rho)
    # pi>3 provides a deliberately conservative exact lower denominator.
    trace_upper=2*length_upper*cutoff*tail_sum/3
    sqrt_upper=sqrt_enclosure(trace_upper,60).hi
    return {'trace_upper':str(trace_upper),'arch_compact_delta_upper':str(2*symbol_sup*sqrt_upper),
            'status':'CONDITIONAL_ARCH_COMPACT_NORM_ERROR_BOUND',
            'assumptions':['CANONICAL_LEGENDRE_PROJECTION_DEGREES_0_THROUGH_D_MINUS_1',
                           'SYMBOL_SUP_BOUNDS_ABS_H_MINUS_BETA_ON_CUTOFF',
                           'L_IS_AT_MOST_LENGTH_UPPER'],
            'pole_compact_error':'NOT_INCLUDED','full_operator_status':'BLOCKED',
            'NO_RH_PROOF':True}
