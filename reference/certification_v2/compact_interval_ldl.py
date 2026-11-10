"""Exact interval LDL with outward dyadic reporting of large pivot fractions.

Only reporting is rounded. Every recurrence uses exact rational intervals.
"""
from fractions import Fraction as F
import hashlib,json
from research.certification_v2.exact_interval_ldl import Interval,rational

def dyadic_report(value,bits=512):
    unit=1<<bits
    lo=(value.lo.numerator*unit)//value.lo.denominator
    hi=-((-value.hi.numerator*unit)//value.hi.denominator)
    result=Interval(F(lo,unit),F(hi,unit))
    if not result.lo<=value.lo<=value.hi<=result.hi:raise AssertionError('outward report failure')
    return result.encoded()

def certify_compact(matrix,shift='0',report_bits=512):
    if type(report_bits) is not int or report_bits<64:raise ValueError('valid reporting precision required')
    n=len(matrix);shift=rational(shift)
    if not n or any(len(row)!=n for row in matrix):raise ValueError('square nonempty matrix')
    a=[[Interval.parse(x) for x in row] for row in matrix]
    if any(a[i][j]!=a[j][i] for i in range(n) for j in range(n)):raise ValueError('symmetric boxes required')
    digest=hashlib.sha256(json.dumps({'matrix':[[x.encoded() for x in row] for row in a],'shift':str(shift)},sort_keys=True).encode()).hexdigest()
    l=[[Interval(0,0) for _ in range(n)] for _ in range(n)];p=[];reports=[]
    for j in range(n):
        d=a[j][j]-shift
        for k in range(j):d=d-l[j][k].square()*p[k]
        p.append(d);reports.append(dyadic_report(d,report_bits))
        if d.lo<=0 or F(reports[-1][0])<=0:
            return {'status':'INCONCLUSIVE','failed_pivot':j,'pivots_outward_dyadic':reports,'input_sha256':digest,'report_bits':report_bits,'recurrence':'EXACT_RATIONAL_NO_ROUNDING','NO_RH_PROOF':True}
        l[j][j]=Interval(1,1)
        for i in range(j+1,n):
            numerator=a[i][j]
            for k in range(j):numerator=numerator-l[i][k]*l[j][k]*p[k]
            l[i][j]=numerator/d
    return {'status':'FINITE_BOX_POSITIVE_DEFINITE','dimension':n,'coordinate_eigenvalue_lower_bound':str(shift),'pivots_outward_dyadic':reports,'input_sha256':digest,'report_bits':report_bits,'recurrence':'EXACT_RATIONAL_NO_ROUNDING','proof_scope':'SUPPLIED_FINITE_ENTRY_BOXES_ONLY','NO_RH_PROOF':True}
