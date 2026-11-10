"""Exact cutoff Arch entry boxes from Fourier energy/Cauchy-Schwarz majorants."""
from fractions import Fraction as F
from research.certification_v2.exact_interval_ldl import Interval,rational
from research.certification_v2.pole_entries import odd_double_factorial
from research.certification_v2.pole_compact_tail import relative_sqrt_upper


def energy_upper(degree,length,cutoff):
    length,cutoff=map(rational,(length,cutoff))
    if type(degree) is not int or degree<0 or length<=0 or cutoff<=0:
        raise ValueError("nonnegative integer degree and positive L,T required")
    z=length*cutoff
    polynomial_majorant=2*z*z**(2*degree)/(3*odd_double_factorial(2*degree+1)**2)
    return min(F(1),polynomial_majorant)


def entry_box(i,j,length,cutoff,symbol_sup,target_width="1e-12"):
    symbol_sup,target_width=map(rational,(symbol_sup,target_width))
    if symbol_sup<0 or target_width<=0:
        raise ValueError("nonnegative authenticated symbol bound and positive target required")
    ei,ej=energy_upper(i,length,cutoff),energy_upper(j,length,cutoff)
    if (i-j)%2:
        radius=F(0)
    else:
        radius=symbol_sup*relative_sqrt_upper(ei*ej)
    box=Interval(-radius,radius)
    return {"entry":box.encoded(),"radius":str(radius),"degrees":[i,j],
            "length":str(rational(length)),"cutoff":str(rational(cutoff)),
            "energy_i_upper":str(ei),"energy_j_upper":str(ej),
            "symbol_sup":str(symbol_sup),"target_width":str(target_width),
            "status":"ARCH_ENTRY_MAJORANT_TARGET_MET" if 2*radius<=target_width else "VALID_ARCH_ENTRY_MAJORANT_TARGET_NOT_MET",
            "method":"EXACT_RODRIGUES_ENERGY_MAJORANT_AND_CAUCHY_SCHWARZ_NO_QUADRATURE",
            "assumptions":["CANONICAL_NORMALIZED_REAL_LEGENDRE_BASIS",
                           "AUTHENTICATED_SUP_OF_ABS_H_MINUS_SAME_BETA_ON_CUTOFF"],
            "NO_RH_PROOF":True,"full_operator_status":"BLOCKED"}
