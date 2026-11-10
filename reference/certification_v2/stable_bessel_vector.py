"""Candidate validated common spherical-Bessel vector at real node boxes."""
from fractions import Fraction as F
from flint import arb,acb,ctx
from research.certification_v2.archimedean.arb_adapter import spherical_j,ball,encoded_bounds
from research.certification_v2.exact_interval_ldl import Interval

def vector(node,dimension=650,bits=1024):
    if type(dimension) is not int or not 1<=dimension<=650:
        raise ValueError('dimension in 1..650 required')
    box=Interval.parse(encoded_bounds(node))
    if box.lo<=0:raise ValueError('strictly positive real node required')
    midpoint=(box.lo+box.hi)/2;radius=(box.hi-box.lo)/2
    with ctx.workprec(bits):
        t=ball(midpoint)
        previous=spherical_j(650,acb(t)).real
        following=spherical_j(651,acb(t)).real
        values=[None]*650
        for k in range(650,0,-1):
            current=(2*k+1)*previous/t-following
            values[k-1]=current
            following,previous=previous,current
        result=[]
        uncertainty=ball(Interval(-radius/2,radius/2))
        limit=ball(F(1,2*10**25)).lower()
        for value in values[:dimension]:
            # j_k(t)=i^-k/2 integral exp(itu)P_k(u)du and |P_k|<=1
            # give |j'_k(t)|<=1/2 on the real axis, for every k.
            expanded=value+uncertainty
            if not expanded.is_finite() or not expanded.rad().upper()<limit:
                raise ValueError('insufficient verified vector precision')
            result.append(expanded)
        return result
