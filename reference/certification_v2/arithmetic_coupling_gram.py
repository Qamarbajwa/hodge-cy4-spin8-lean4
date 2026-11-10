"""Enclosed FULL arithmetic QVP Gram via complete clipped-shift images.

No claim is made for the hybrid's additional compact cross coupling.
"""
from fractions import Fraction as F
from math import comb

from research.certification_v2.exact_interval_ldl import Interval,rational
from research.certification_v2.spatial_overlap import (
    legendre,log_enclosure,sqrt_enclosure,spatial_matrix,prime_powers)


def rounded(value,bits=112):
    value=Interval.parse(value)
    denominator=2**bits
    lo=value.lo.numerator*denominator//value.lo.denominator
    hi=-((-value.hi.numerator*denominator)//value.hi.denominator)
    return Interval(F(lo,denominator),F(hi,denominator))


def maximum(intervals):
    intervals=[Interval.parse(x) for x in intervals]
    return Interval(max(x.lo for x in intervals),max(x.hi for x in intervals))


def minimum(intervals):
    intervals=[Interval.parse(x) for x in intervals]
    return Interval(min(x.lo for x in intervals),min(x.hi for x in intervals))


def intersection(length,shift1,shift2):
    length=rational(length)
    if length<=0:
        raise ValueError("positive rational length required")
    shift1,shift2=Interval.parse(shift1),Interval.parse(shift2)
    lower=maximum([-length,-shift1-length,-shift2-length])
    upper=minimum([length,-shift1+length,-shift2+length])
    difference=upper-lower
    width=Interval(max(F(0),difference.lo),max(F(0),difference.hi))
    return lower,width


def power(value,degree):
    value=Interval.parse(value)
    result=Interval(1,1)
    for _ in range(degree):
        result=result*value
    return result


def shifted_polynomial(degree,constant,slope):
    """Legendre P_degree(constant+slope*y), interval coefficient enclosure."""
    poly=legendre(degree)
    answer=[Interval(0,0) for _ in poly]
    for j,c in enumerate(poly):
        for k in range(j+1):
            answer[k]=answer[k]+power(constant,j-k)*power(slope,k)*(c*comb(j,k))
    return answer


def image_product_integral(i,j,length,shift1,shift2):
    """Unnormalized exact polynomial integral on the TRUE support intersection.

    x=a+w*y, y∈[0,1], w=max(0,b-a). Endpoint boxes include all support
    configurations, including uncertain empty/touching intersections.
    """
    length=rational(length)
    shift1,shift2=Interval.parse(shift1),Interval.parse(shift2)
    start,width=intersection(length,shift1,shift2)
    first=shifted_polynomial(i,(start+shift1)/length,width/length)
    second=shifted_polynomial(j,(start+shift2)/length,width/length)
    integral=Interval(0,0)
    for a,c in enumerate(first):
        for b,d in enumerate(second):
            integral=integral+c*d/F(a+b+1)
    return integral*width


def complete_images(terms):
    # Reuse accepted term validation before constructing complete ±shift images.
    spatial_matrix([0],1,terms,digits=40,log_terms=35)
    answer=[]
    for n,p in sorted(terms):
        shift=rounded(log_enclosure(n,35))
        coefficient=rounded(-log_enclosure(p,35)/sqrt_enclosure(n,40))
        for sign in (-1,1):
            answer.append({"n":n,"base":p,"sign":sign,
                           "shift":shift*sign,"coefficient":coefficient})
    return answer


def arithmetic_gram(degrees,length,terms,omit_cross_terms=False):
    """Enclose <Vphi_i,Vphi_j>-(PVP)^2, including every image-image pair.

    omit_cross_terms is an executed negative-control mode, never a certificate.
    Full arithmetic means ALL infinite QVP coupling for the specified V; it
    does not include Arch/pole cross coupling or validate term completeness.
    """
    length=rational(length)
    degrees=list(degrees)
    if length<=0 or not degrees or len(set(degrees))!=len(degrees):
        raise ValueError("positive rational length and distinct nonempty degrees required")
    for degree in degrees:
        legendre(degree)
    terms=list(terms)
    images=complete_images(terms)
    n=len(degrees)
    v2=[[Interval(0,0) for _ in degrees] for _ in degrees]
    for a,i in enumerate(degrees):
        for b in range(a,n):
            j=degrees[b]
            # Paired shifts make V commute with reflection; opposite parity zero.
            if (i+j)%2:
                continue
            total=Interval(0,0)
            for left,image1 in enumerate(images):
                for right,image2 in enumerate(images):
                    if omit_cross_terms and left!=right:
                        continue
                    integral=image_product_integral(i,j,length,image1["shift"],image2["shift"])
                    total=total+rounded(integral*image1["coefficient"]*image2["coefficient"])
            norm=rounded(sqrt_enclosure((2*i+1)*(2*j+1),40)/(2*length))
            v2[a][b]=v2[b][a]=rounded(total*norm)
    finite=[[rounded(x) for x in row] for row in spatial_matrix(degrees,length,terms,digits=40,log_terms=35)]
    square=[[Interval(0,0) for _ in degrees] for _ in degrees]
    gram=[[Interval(0,0) for _ in degrees] for _ in degrees]
    for i in range(n):
        for j in range(i,n):
            product=Interval(0,0)
            for k in range(n):
                product=product+(finite[i][k].square() if i==j else finite[i][k]*finite[k][j])
            square[i][j]=square[j][i]=rounded(product)
            gram[i][j]=gram[j][i]=rounded(v2[i][j]-square[i][j])
    return {"PV2P":v2,"PVP":finite,"PVP_squared":square,"arithmetic_gram":gram,
            "signed_image_count":len(images),"ordered_pairs_per_entry":len(images)**2,
            "certificate_mode":not omit_cross_terms}
