"""Candidate sufficient positivity check by an enclosed exact congruence.

The caller must certify the input matrix's identity and entry enclosures.
A floating point preconditioner is merely a proposal: its exact dyadic
entries are used in the verified calculation below.
"""
from fractions import Fraction as F
from flint import arb, arb_mat, ctx
from research.certification_v2.archimedean.arb_adapter import ball, encoded_bounds
from research.certification_v2.exact_interval_ldl import Interval

def verify(matrix, preconditioner, bits=192):
    n=len(matrix)
    if not n or any(len(row)!=n for row in matrix):
        raise ValueError('square matrix required')
    if len(preconditioner)!=n or any(len(row)!=n for row in preconditioner):
        raise ValueError('square preconditioner of matching dimension required')
    boxes=[[Interval.parse(x) for x in row] for row in matrix]
    if any(boxes[i][j]!=boxes[j][i] for i in range(n) for j in range(n)):
        raise ValueError('exactly symmetric entry boxes required')
    # Parse numbers as exact rationals; never accept an approximate inverse
    # as an already-proved inverse or an already-proved nonsingular matrix.
    exact=[[F(x) for x in row] for row in preconditioner]
    frobenius_squared=sum((x*x for row in exact for x in row),F(0))
    if not frobenius_squared:
        return {'status':'INCONCLUSIVE','reason':'ZERO_PRECONDITIONER'}
    with ctx.workprec(bits):
        A=arb_mat([[ball(x) for x in row] for row in boxes])
        R=arb_mat([[ball(x) for x in row] for row in exact])
        B=R.transpose()*A*R
        margins=[]
        for i in range(n):
            diagonal=Interval.parse(encoded_bounds(B[i,i])).lo
            radius=F(0)
            for j in range(n):
                if i!=j:
                    x=Interval.parse(encoded_bounds(B[i,j]))
                    radius+=max(abs(x.lo),abs(x.hi))
            margins.append(diagonal-radius)
    gamma=min(margins)
    result={'status':'POSITIVE_DEFINITE_CONDITIONAL_INPUT' if gamma>0 else 'INCONCLUSIVE',
            'dimension':n,'congruence_margin_lower':str(gamma),
            'preconditioner_norm_squared_upper':str(frobenius_squared),
            'matrix_lower_bound':str(gamma/frobenius_squared) if gamma>0 else None,
            'full_operator_status':'BLOCKED','NO_RH_PROOF':True}
    return result
