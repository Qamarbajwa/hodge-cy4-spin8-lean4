"""Writer-only nested critical comparison from direct shared primitives.

No full-point certificate is issued, even if a conditional finite check passes.
"""
from pathlib import Path
from fractions import Fraction as F
import hashlib,json,time,sys
from flint import arb_mat,ctx
from research.certification_v2.archimedean.arb_adapter import ball,encoded_bounds
from research.certification_v2.exact_interval_ldl import Interval,certify
from research.certification_v2.pole_entries import pole_matrix

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/certification_v2/direct_critical_form'

def run():
    sys.set_int_max_str_digits(100000)
    target=OUT/'CRITICAL_COMPOSITION_WRITER.json'
    if target.exists():raise ValueError('preserve prior result')
    paths=[OUT/'ARCH_M32_B384.json',OUT/'ARITHMETIC_RECEIPT.json',
           ROOT/'research/certification_v2/structured_schur_repair/BULK_SPLIT_RECEIPT.json',
           ROOT/'research/certification_v2/p650_stable_assembly/WRITER_RECEIPT.json',
           ROOT/'research/certification_v2/structured_schur_repair/CRITICAL_SUBSPACE.json']
    arch,arith,bulk,original,basis=[json.loads(p.read_text()) for p in paths]
    metric=arch['exact_gram']
    if metric!=arith['exact_critical_metric']:raise ValueError('same physical critical Gram required')
    if arch['parities']!=arith['critical_parity'] or arith['projection_dimension']!=650:raise ValueError('projection mismatch')
    beta=F(arch['beta']);epsarch=F(arch['analytic_form_remainder_epsilon'])
    epsilon=F(original['epsilon']);c=F(original['c'])
    poleerror=F(original['pole_truncation_delta32']);correction=F(original['scalar_coupling_correction'])
    penalty=F(bulk['nested_schur_scalar_penalty']);started=time.monotonic()
    with ctx.workprec(384):
        G=arb_mat([[ball(F(x)) for x in row] for row in metric])
        Z32=arb_mat([[ball(F(col[k])) for col in basis['CRITICAL_BASIS']] for k in range(32)])
        W=arb_mat([[ball(x) for x in row] for row in pole_matrix(range(32),1)])
        A=arb_mat([[ball(x) for x in row] for row in arch['quadrature_entry_boxes']])
        A+=arb_mat([[ball(x) for x in row] for row in arith['entries']['Z_V_Z']])
        A+=Z32.transpose()*W*Z32
        A+=G*ball(beta-poleerror-epsarch-correction)
        A-=arb_mat([[ball(x) for x in row] for row in arith['entries']['Q650VZ_gram']])*ball((1+epsilon)/c)
        for i in range(12):A[i,i]-=ball(penalty)
        boxes=[]
        for i in range(12):
            row=[]
            for j in range(12):
                if arch['parities'][i]!=arch['parities'][j]:row.append(['0','0']);continue
                a=Interval.parse(encoded_bounds(A[i,j]));b=Interval.parse(encoded_bounds(A[j,i]))
                row.append(Interval(max(a.lo,b.lo),min(a.hi,b.hi)).encoded())
            boxes.append(row)
    # Two independent parity sectors keep exact LDL costs and meaning explicit.
    tests=[]
    for shift in ['0','1e-30']:
        for parity in [0,1]:
            indices=[i for i,p in enumerate(arch['parities']) if p==parity]
            block=[[boxes[i][j] for j in indices] for i in indices]
            result=certify(block,shift=shift)
            tests.append({'parity':parity,'coordinate_shift':shift,'result':result})
    record={'writer_id':'/root','status':'WRITER_ONLY_NESTED_CRITICAL_FORM_COMPOSITION',
            'boxes':boxes,'tests':tests,'analytic_arch_remainder_used_as_form_order':True,
            'pole_error_used_as_physical_gram_shift':True,'bulk_solve_penalty':str(penalty),
            'input_sha256':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
            'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'seconds':time.monotonic()-started,'FULL_POINT_L1':'NOT_ISSUED','NO_RH_PROOF':True,
            'acceptance_obligations':['all primitive component acceptances','distinct composition reviewer and acceptor','positive original-metric margin and full lower-hybrid comparison proof']}
    target.write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps([{'parity':t['parity'],'shift':t['coordinate_shift'],'status':t['result']['status'],'failed_pivot':t['result'].get('failed_pivot')} for t in tests]))

if __name__=='__main__':run()
