"""Exact prime-power enumeration and rational natural-log enclosures."""
from fractions import Fraction

def prime_power(n):
    if type(n) is not int or n < 2:
        return None
    p = next((d for d in range(2, n+1) if n % d == 0), None)
    k, remaining = 0, n
    while remaining % p == 0:
        remaining //= p
        k += 1
    return (p,k) if remaining == 1 else None

def log_box(n, terms=256):
    """For integer n>=1, enclose log(n) by positive atanh series.

    z=(n-1)/(n+1). Remainder <=2*z^(2m+1)/((2m+1)*(1-z^2)).
    Exact fractions; no rounded transcendental inputs.
    """
    if type(n) is not int or n < 1 or type(terms) is not int or terms < 1:
        raise ValueError('positive integer n and term count required')
    z = Fraction(n-1,n+1)
    total = sum((2*z**(2*j+1)/ (2*j+1) for j in range(terms)), Fraction(0))
    remainder = 2*z**(2*terms+1)/((2*terms+1)*(1-z*z))
    return total,total+remainder

def inventory(first=2,last=43):
    result=[]
    for n in range(first,last+1):
        pk=prime_power(n)
        if pk:
            low,high=log_box(n)
            result.append({'n':n,'prime':pk[0],'exponent':pk[1],
                           'threshold_L':[''+str(low/2),str(high/2)],
                           'lambda_n_exact':'log('+str(pk[0])+')',
                           'method':'EXACT_ATANH_SERIES_WITH_GEOMETRIC_REMAINDER'})
    return result
