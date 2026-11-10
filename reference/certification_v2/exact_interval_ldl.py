"""Exact rational finite-matrix positivity checker; no operator proof claims.

Endpoints must be integers or rational/decimal strings, never binary floats.
The theorem is conditional on the supplied intervals enclosing the true entries.
"""
from dataclasses import dataclass
from fractions import Fraction
import hashlib
import json


def rational(value):
    if isinstance(value, bool) or not isinstance(value, (int, str, Fraction)):
        raise ValueError("exact integer or rational/decimal string required")
    return Fraction(value)


@dataclass(frozen=True)
class Interval:
    lo: Fraction
    hi: Fraction

    def __post_init__(self):
        object.__setattr__(self, "lo", rational(self.lo))
        object.__setattr__(self, "hi", rational(self.hi))
        if self.lo > self.hi:
            raise ValueError("reversed interval")

    @classmethod
    def parse(cls, value):
        if isinstance(value, cls):
            return value
        if isinstance(value, (list, tuple)) and len(value) == 2:
            return cls(*value)
        return cls(value, value)

    def __add__(self, other):
        other = self.parse(other)
        return Interval(self.lo + other.lo, self.hi + other.hi)

    def __neg__(self):
        return Interval(-self.hi, -self.lo)

    def __sub__(self, other):
        return self + -self.parse(other)

    def __mul__(self, other):
        other = self.parse(other)
        values = [a * b for a in (self.lo, self.hi) for b in (other.lo, other.hi)]
        return Interval(min(values), max(values))

    def __truediv__(self, other):
        other = self.parse(other)
        if other.lo <= 0 <= other.hi:
            raise ZeroDivisionError("interval contains zero")
        return self * Interval(1 / other.hi, 1 / other.lo)

    def square(self):
        low = 0 if self.lo <= 0 <= self.hi else min(self.lo**2, self.hi**2)
        return Interval(low, max(self.lo**2, self.hi**2))

    def encoded(self):
        return [str(self.lo), str(self.hi)]


def certify(matrix, shift="0"):
    """Prove A - shift*I positive definite for every symmetric A in the box.

    Unpivoted interval LDL encloses the exact scalar recurrence for each A.
    Positive pivot lower bounds prove positive definiteness by congruence.
    Failure means inconclusive, never that a true matrix is indefinite.
    """
    shift = rational(shift)
    n = len(matrix)
    if not n or any(len(row) != n for row in matrix):
        raise ValueError("nonempty square matrix required")
    a = [[Interval.parse(x) for x in row] for row in matrix]
    if any(a[i][j] != a[j][i] for i in range(n) for j in range(n)):
        raise ValueError("symmetric entry enclosures required")
    canonical = {"matrix": [[x.encoded() for x in row] for row in a], "shift": str(shift)}
    digest = hashlib.sha256(json.dumps(canonical, sort_keys=True).encode()).hexdigest()
    l = [[Interval(0, 0) for _ in range(n)] for _ in range(n)]
    pivots = []
    for j in range(n):
        d = a[j][j] - shift
        for k in range(j):
            d = d - l[j][k].square() * pivots[k]
        pivots.append(d)
        if d.lo <= 0:
            return {"status": "INCONCLUSIVE", "failed_pivot": j,
                    "pivots": [x.encoded() for x in pivots], "input_sha256": digest,
                    "operator_status": "BLOCKED", "NO_RH_PROOF": True}
        l[j][j] = Interval(1, 1)
        for i in range(j + 1, n):
            numerator = a[i][j]
            for k in range(j):
                numerator = numerator - l[i][k] * l[j][k] * pivots[k]
            l[i][j] = numerator / d
    return {"status": "FINITE_BOX_POSITIVE_DEFINITE", "dimension": n,
            "strict_eigenvalue_lower_bound": str(shift),
            "pivots": [x.encoded() for x in pivots], "input_sha256": digest,
            "entry_provenance_status": "UNVERIFIED_EXTERNAL_INPUT",
            "operator_status": "BLOCKED", "NO_RH_PROOF": True}


def operator_gate(finite_result, evidence=None):
    """Fail closed: metadata and positive fixtures cannot promote an operator claim.

    No validated entry/continuum/complement adapters exist in v2 yet. Even
    evidence marked 'PASS' cannot bypass this missing implementation.
    """
    return {"status": "BLOCKED", "NO_RH_PROOF": True,
            "finite_status": finite_result.get("status", "MISSING"),
            "obstructions": ["VERIFIED_ENTRY_ENCLOSURE_ADAPTER_MISSING",
                             "CONTINUUM_OPERATOR_ENCLOSURE_MISSING",
                             "COMPLEMENT_TAIL_AND_COUPLING_PROOF_MISSING"]}
