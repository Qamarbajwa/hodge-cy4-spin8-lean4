"""Independent exact Legendre translation compression, with rational enclosures.

Includes only -Lambda(n)/sqrt(n) times the two zero-extended spatial shifts.
Does not include the Archimedean form, complement Schur correction, or RH claim.
"""
from fractions import Fraction as F
from math import comb, isqrt

from research.certification_v2.exact_interval_ldl import Interval, rational


def add(a, b):
    c = [F(0)] * max(len(a), len(b))
    for k, x in enumerate(a):
        c[k] += x
    for k, x in enumerate(b):
        c[k] += x
    return trim(c)


def trim(a):
    while len(a) > 1 and a[-1] == 0:
        a.pop()
    return a


def mul(a, b):
    c = [F(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            c[i + j] += x * y
    return trim(c)


def scale(a, c):
    return trim([x * c for x in a])


def legendre(degree):
    if not isinstance(degree, int) or isinstance(degree, bool) or degree < 0:
        raise ValueError("nonnegative integer degree required")
    a, b = [F(1)], [F(0), F(1)]
    if degree == 0:
        return a
    for k in range(1, degree):
        a, b = b, scale(add(scale([F(0)] + b, 2 * k + 1), scale(a, -k)), F(1, k + 1))
    return b


def overlap_polynomial(i, j):
    """Coefficients in r of int_{r-1}^1 P_i(t) P_j(t-r) dt / 2.

    Valid for 0 <= r <= 2. For r >= 2, zero extension gives zero.
    Integral endpoints and binomial expansions use only exact rationals.
    """
    pi, pj = legendre(i), legendre(j)
    result = [F(0)]
    for a, ca in enumerate(pi):
        for b, cb in enumerate(pj):
            for k in range(b + 1):
                degree_t = a + k
                degree_r = b - k
                c = ca * cb * comb(b, k) * (-1)**degree_r / (2 * (degree_t + 1))
                # r^(b-k) * [1 - (r-1)^(a+k+1)]
                endpoint = [-F(comb(degree_t + 1, h) * (-1)**(degree_t + 1 - h))
                            for h in range(degree_t + 2)]
                endpoint[0] += 1
                result = add(result, [F(0)] * degree_r + scale(endpoint, c))
    return result


def evaluate(poly, x):
    x = Interval.parse(x)
    value = Interval(0, 0)
    for c in reversed(poly):
        value = value * x + c
    return value


def bernstein_range(poly, domain):
    """Exact convex-hull enclosure after conversion to Bernstein basis on [a,b]."""
    domain = Interval.parse(domain)
    if domain.lo == domain.hi:
        return evaluate(poly, domain)
    degree = len(poly) - 1
    a, width = domain.lo, domain.hi - domain.lo
    monomials = [sum((poly[j] * comb(j, k) * a**(j-k) * width**k
                      for j in range(k, degree+1)), F(0)) for k in range(degree+1)]
    bernstein = [sum((monomials[k] * F(comb(i, k), comb(degree, k))
                      for k in range(i+1)), F(0)) for i in range(degree+1)]
    return Interval(min(bernstein), max(bernstein))


def overlap(i, j, ratio):
    ratio = Interval.parse(ratio)
    if ratio.lo < 0:
        raise ValueError("nonnegative shift ratio required")
    if ratio.lo >= 2:
        return Interval(0, 0)
    value = bernstein_range(overlap_polynomial(i, j), Interval(ratio.lo, min(ratio.hi, F(2))))
    if ratio.hi >= 2:
        value = Interval(min(value.lo, F(0)), max(value.hi, F(0)))
    return value


def sqrt_enclosure(value, digits=60):
    value = rational(value)
    if value < 0 or not isinstance(digits, int) or digits < 1:
        raise ValueError("nonnegative value and positive integer precision required")
    denominator = 10**digits
    floor = isqrt(value.numerator * denominator**2 // value.denominator)
    lower = F(floor, denominator)
    upper = lower if lower**2 == value else F(floor + 1, denominator)
    return Interval(lower, upper)


def log_enclosure(value, terms=90):
    """Positive rational log enclosure using convergent atanh series and tail."""
    value = rational(value)
    if value <= 0 or not isinstance(terms, int) or terms < 1:
        raise ValueError("positive argument and positive integer term count required")
    if value < 1:
        return -log_enclosure(1 / value, terms)
    exponent = 0
    while value >= 2:
        value /= 2
        exponent += 1

    def series(x):
        z = (x - 1) / (x + 1)
        partial = sum((2 * z**(2*k + 1) / (2*k + 1) for k in range(terms)), F(0))
        tail = 2 * z**(2*terms + 1) / ((2*terms + 1) * (1 - z*z))
        return Interval(partial, partial + tail)

    return series(value) + series(F(2)) * exponent


def prime_powers(limit):
    if not isinstance(limit, int) or isinstance(limit, bool) or limit < 2:
        raise ValueError("integer limit >= 2 required")
    answer = []
    for p in range(2, limit + 1):
        if all(p % d for d in range(2, isqrt(p) + 1)):
            n = p
            while n <= limit:
                answer.append((n, p))
                n *= p
    return sorted(answer)


def spatial_matrix(degrees, length, terms, digits=60, log_terms=90):
    """Uniform rational enclosure on any supplied positive length interval.

    Terms are distinct (prime power n, base prime p) pairs; invalid/duplicated
    terms fail closed. Completeness of a cutoff is external to this component.
    Polynomial Bernstein range evaluation encloses r=log(n)/L throughout the cell,
    even if its support-activation boundary r=2 crosses the cell.
    """
    length = Interval.parse(length)
    if length.lo <= 0:
        raise ValueError("positive length interval required")
    degrees = list(degrees)
    if not degrees or len(set(degrees)) != len(degrees):
        raise ValueError("nonempty distinct degrees required")
    for degree in degrees:
        legendre(degree)
    terms = list(terms)
    if any(not isinstance(n, int) or not isinstance(p, int) or n < 2 or p < 2
           for n, p in terms):
        raise ValueError("integer prime powers required")
    if len(set(n for n, _ in terms)) != len(terms):
        raise ValueError("duplicate prime power")
    for n, p in terms:
        remainder = n
        while remainder % p == 0:
            remainder //= p
        if remainder != 1 or any(p % d == 0 for d in range(2, isqrt(p) + 1)):
            raise ValueError("invalid prime power/base pair")
    matrix = [[Interval(0, 0) for _ in degrees] for _ in degrees]
    for n, p in sorted(terms):
        ratio = log_enclosure(n, log_terms) / length
        coefficient = -log_enclosure(p, log_terms) / sqrt_enclosure(n, digits)
        for a, i in enumerate(degrees):
            for b in range(a, len(degrees)):
                j = degrees[b]
                normalized = sqrt_enclosure((2*i + 1)*(2*j + 1), digits)
                # Both directions: overlap(i,j,r) + overlap(j,i,r).
                contribution = coefficient * normalized * (overlap(i, j, ratio) + overlap(j, i, ratio))
                matrix[a][b] = matrix[a][b] + contribution
                matrix[b][a] = matrix[a][b]
    return matrix
