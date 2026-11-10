"""Exact rational positive-series enclosures of canonical parity pole entries."""
from fractions import Fraction as F
from math import factorial
from research.certification_v2.exact_interval_ldl import Interval
from research.certification_v2.spatial_overlap import sqrt_enclosure

def odd_double_factorial(n):
    value=1
    for j in range(1,n+1,2):
        value*=j
    return value

def spherical_i_point(k,z,terms):
    z=F(z)
    if type(k) is not int or k<0 or z<0 or type(terms) is not int or terms<1:
        raise ValueError('nonnegative degree/argument and positive term count required')
    total=F(0)
    for j in range(terms):
        total+=z**(k+2*j)/(2**j*factorial(j)*odd_double_factorial(2*k+2*j+1))
    omitted=z**(k+2*terms)/(2**terms*factorial(terms)*odd_double_factorial(2*k+2*terms+1))
    ratio=z*z/((2*terms+2)*(2*k+2*terms+3))
    if ratio>=1:
        raise ValueError('more series terms required for geometric tail')
    return Interval(total,total+omitted/(1-ratio))

def pole_matrix(degrees,length,terms=32,digits=60):
    length=Interval.parse(length)
    degrees=list(degrees)
    if length.lo<=0 or not degrees or len(set(degrees))!=len(degrees) or any(type(k) is not int or k<0 for k in degrees):
        raise ValueError('positive length and distinct nonnegative degrees required')
    vectors=[]
    for k in degrees:
        zlo,zhi=length.lo/2,length.hi/2
        low=spherical_i_point(k,zlo,terms)
        high=spherical_i_point(k,zhi,terms)
        rootlo=sqrt_enclosure(2*(2*k+1)*length.lo,digits)
        roothi=sqrt_enclosure(2*(2*k+1)*length.hi,digits)
        vectors.append(Interval(rootlo.lo,roothi.hi)*Interval(low.lo,high.hi))
    return [[Interval(0,0) if (i+j)%2 else vectors[a]*vectors[b]*(2 if i%2==0 else -2)
             for b,j in enumerate(degrees)] for a,i in enumerate(degrees)]
