"""Conditional form Schur bound from enclosed finite block and full coupling Gram.

This does not establish input provenance or any infinite operator certificate.
"""
from fractions import Fraction
from research.certification_v2.exact_interval_ldl import Interval, certify, rational

def schur_bound(matrix, coupling_gram, beta, gamma):
    """If C>=beta I and K* K lies in coupling_gram, certify A-G/beta>gamma I.

    Gram must enclose the FULL finite/complement coupling, not just a component.
    The input assumptions stay external, so operator_status always BLOCKED.
    """
    beta,gamma = rational(beta),rational(gamma)
    if beta <= 0 or gamma <= 0:
        raise ValueError('positive exact complement floor and finite margin required')
    n=len(matrix)
    if not n or any(len(row)!=n for row in matrix) or len(coupling_gram)!=n or any(len(row)!=n for row in coupling_gram):
        raise ValueError('matching nonempty square matrices required')
    a=[[Interval.parse(x) for x in row] for row in matrix]
    g=[[Interval.parse(x) for x in row] for row in coupling_gram]
    if any(a[i][j]!=a[j][i] or g[i][j]!=g[j][i] for i in range(n) for j in range(n)):
        raise ValueError('symmetric interval inputs required')
    if any(g[i][i].hi<0 for i in range(n)):
        raise ValueError('negative Gram diagonal upper bound')
    s=[[a[i][j]-g[i][j]/beta for j in range(n)] for i in range(n)]
    result=certify(s,gamma)
    bound=None
    if result['status']=='FINITE_BOX_POSITIVE_DEFINITE':
        k_sq=sum((g[i][i].hi for i in range(n)),Fraction(0))
        bound=str(min(gamma/(1+2*k_sq/beta**2),beta/2))
    return {'status':'CONDITIONAL_SCHUR_BOUND' if bound else 'INCONCLUSIVE',
            'full_form_lower_bound_conditional':bound,'beta':str(beta),'gamma':str(gamma),
            'schur_matrix':[[x.encoded() for x in row] for row in s],
            'finite_result':result,'operator_status':'BLOCKED',
            'assumptions':['COMMON_FORM_DOMAIN_AND_ORTHOGONAL_SPLIT',
                           'TRUE_FINITE_BLOCK_INCLUDED_IN_INPUT_BOX',
                           'TRUE_COMPLEMENT_FORM_AT_LEAST_BETA_I',
                           'INPUT_GRAM_ENCLOSES_ALL_CROSS_COUPLING_K_STAR_K'],
            'NO_RH_PROOF':True}
