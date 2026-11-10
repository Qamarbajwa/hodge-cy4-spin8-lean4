"""Writer-only shared cutoff quadrature with an explicit candidate remainder.

No matrix or theorem acceptance follows from executing this experiment.
"""
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json
import time
from flint import arb, acb, arb_mat, ctx
from research.certification_v2.certified_legendre_rule import certify_rule, moments
from research.certification_v2.archimedean.arb_adapter import ball, encoded_bounds, spherical_j
from research.certification_v2.exact_interval_ldl import Interval
from research.certification_v2.stable_bessel_vector import vector

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/certification_v2/stable_shared_arch_quadrature'

def run(dimension=8):
    if type(dimension) is not int or not 1<=dimension<=650:
        raise ValueError('dimension in 1..650 required')
    OUT.mkdir(exist_ok=True)
    path=OUT/f'd{dimension}_RECEIPT.json'
    if path.exists():
        raise ValueError('preserve earlier experiment')
    beta_path=ROOT/'research/certification_v2/authenticated_symbol_tail/PILOT_RECEIPT.json'
    beta=F(json.loads(beta_path.read_text())['beta'])
    if not 0<beta<5:
        raise ValueError('candidate symbol-bound hypothesis fails')
    sources=[Path(__file__).relative_to(ROOT).as_posix(),
             'research/certification_v2/p650_programme/SHARED_ARCH_QUADRATURE_CANDIDATE.md',
             beta_path.relative_to(ROOT).as_posix(),
             'research/certification_v2/certified_legendre_rule.py',
             'research/certification_v2/archimedean/arb_adapter.py',
             'research/certification_v2/stable_bessel_vector.py']
    hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sources}
    started=time.monotonic()
    with ctx.workprec(192):
        rule=certify_rule(20,bracket_bits=100)
        if rule['status']!='CERTIFIED_GAUSS_LEGENDRE_RULE_BOXES':
            raise ValueError('rule failed')
        checks=moments(rule,range(40))
        if not all(x['contained'] for x in checks):
            raise ValueError('moment check failed')
        (OUT/'RULE20.json').write_text(json.dumps({'rule':rule,'moments':checks},indent=2)+'\n')
        result=arb_mat(dimension,dimension)
        norms=[arb(2*(2*k+1)).sqrt() for k in range(dimension)]
        for panel in range(3200):
            center=F(2*panel+1,16)
            left=[[] for _ in range(dimension)]
            right=[[] for _ in range(dimension)]
            for item in rule['nodes_weights']:
                t=ball(center)+ball(F(1,16))*ball(item['node'])
                z=acb(t)
                h=(acb(ball(F(1,4)),t/2).digamma().real-arb.pi().log()-ball(beta))
                scale=ball(item['weight'])*ball(F(1,16))*h/arb.pi()
                values=vector(t,dimension)
                for k in range(dimension):
                    v=norms[k]*values[k]
                    left[k].append(v*scale)
                    right[k].append(v)
            result+=arb_mat(left)*arb_mat(right).transpose()
            if panel%200==199:
                print(json.dumps({'panels':panel+1,'seconds':time.monotonic()-started}),flush=True)
        remainder=F(800*8112)*F(4,3)*F(4)**(-40)
        entries=[]
        for i in range(dimension):
            row=[]
            for j in range(dimension):
                if (i-j)%2:
                    row.append(['0','0']);continue
                value=result[i,j]*((-1)**((i-j)//2))
                box=Interval.parse(encoded_bounds(value))
                row.append(Interval(box.lo-remainder,box.hi+remainder).encoded())
            entries.append(row)
    receipt={'status':'WRITER_ONLY_UNREVIEWED_SHARED_ARCH_MATRIX',
             'dimension':dimension,'L':'1','T':'400','beta':str(beta),
             'components':'CUTOFF_K_T_ONLY','entries':entries,
             'analytic_remainder_per_entry':str(remainder),
             'input_sha256':hashes,'seconds':time.monotonic()-started,
             'NO_RH_PROOF':True,'full_operator_status':'BLOCKED',
             'P650_ENTRY_CERTIFIED':False,'restored_intervals':0}
    path.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({'status':receipt['status'],'seconds':receipt['seconds']}),flush=True)

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--dimension',type=int,default=8)
    run(parser.parse_args().dimension)
