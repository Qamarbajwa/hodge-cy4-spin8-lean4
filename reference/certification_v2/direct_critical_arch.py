"""Shared Fourier combinations for the exact twelve critical columns.

Numerical primitive boxes and analytic epsilon G remain distinct. Writer only.
"""
from pathlib import Path
from fractions import Fraction as F
import hashlib,json,time
from flint import arb,acb,arb_mat,ctx
from research.certification_v2.archimedean.arb_adapter import ball,encoded_bounds
from research.certification_v2.certified_legendre_rule import certify_rule,moments
from research.certification_v2.stable_bessel_vector import vector

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/certification_v2/direct_critical_form'

def run(order=32,bits=384):
    OUT.mkdir(exist_ok=True);target=OUT/f'ARCH_M{order}_B{bits}.json'
    if target.exists():raise ValueError('preserve prior result')
    if order<20 or bits<192:raise ValueError('valid quadrature and precision required')
    basispath=ROOT/'research/certification_v2/structured_schur_repair/CRITICAL_SUBSPACE.json'
    columns=[list(map(F,c)) for c in json.loads(basispath.read_text())['CRITICAL_BASIS']]
    if len(columns)!=12 or any(len(c)!=650 for c in columns):raise ValueError('same exact twelve P650 columns required')
    symbolpath=ROOT/'research/certification_v2/authenticated_symbol_tail/PILOT_RECEIPT.json'
    beta=F(json.loads(symbolpath.read_text())['beta'])
    gram=[[sum(a*b for a,b in zip(x,y)) for y in columns] for x in columns]
    epsilon=F(800*8112)*F(4,3)*F(4)**(-2*order)
    started=time.monotonic();parities=[]
    for col in columns:
        active={k%2 for k,v in enumerate(col) if v}
        if len(active)!=1:raise ValueError('exact pure parity basis required')
        parities.append(active.pop())
    with ctx.workprec(bits):
        rule=certify_rule(order,bits=bits,bracket_bits=bits-80,newton_steps=12)
        if rule['status']!='CERTIFIED_GAUSS_LEGENDRE_RULE_BOXES':raise ValueError('rule not certified')
        checks=moments(rule,[0,1,2,2*order-2,2*order-1])
        if not all(c['contained'] for c in checks):raise ValueError('quadrature controls failed')
        (OUT/f'ARCH_RULE_M{order}_B{bits}.json').write_text(json.dumps({'rule':rule,'moments':checks},indent=2)+'\n')
        coefficients=arb_mat([[ball(col[k])*arb(2*(2*k+1)).sqrt()*((-1)**((k-parities[j])//2))
                               if k%2==parities[j] else arb(0) for k in range(650)] for j,col in enumerate(columns)])
        result=arb_mat(12,12)
        for panel in range(3200):
            center=F(2*panel+1,16);nodes=[];scales=[]
            for item in rule['nodes_weights']:
                t=ball(center)+ball(F(1,16))*ball(item['node'])
                h=acb(ball(F(1,4)),t/2).digamma().real-arb.pi().log()-ball(beta)
                nodes.append(vector(t,650,bits=max(1024,bits+256)))
                scales.append(ball(item['weight'])*ball(F(1,16))*h/arb.pi())
            values=coefficients*arb_mat([[node[k] for node in nodes] for k in range(650)])
            weighted=arb_mat([[values[j,n]*scales[n] for n in range(order)] for j in range(12)])
            result+=weighted*values.transpose()
            if panel%200==199:print(json.dumps({'panels':panel+1,'seconds':time.monotonic()-started}),flush=True)
        entries=[]
        for i in range(12):
            row=[]
            for j in range(12):
                row.append(['0','0'] if parities[i]!=parities[j] else encoded_bounds(result[i,j]))
            entries.append(row)
    paths=[basispath,symbolpath,Path(__file__),ROOT/'research/certification_v2/stable_bessel_vector.py',
           ROOT/'research/certification_v2/certified_legendre_rule.py',ROOT/'research/certification_v2/archimedean/arb_adapter.py',
           ROOT/'research/certification_v2/structured_schur_repair/COMPONENT_IMPLEMENTATION_ACCEPTANCE.json']
    receipt={'writer_id':'/root','status':'WRITER_ONLY_SHARED_CRITICAL_ARCH_QUADRATURE',
             'dimension':12,'physical_P_dimension':650,'L':'1','T':'400','beta':str(beta),'order':order,'bits':bits,
             'quadrature_entry_boxes':entries,'exact_gram':[[str(x) for x in row] for row in gram],
             'analytic_form_remainder_epsilon':str(epsilon),'analytic_remainder_semantics':'-epsilon G <= R <= epsilon G; numerical quadrature boxes are additional',
             'parities':parities,'seconds':time.monotonic()-started,
             'maximum_quadrature_entry_width':str(max(F(b)-F(a) for row in entries for a,b in row)),
             'input_sha256':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
             'NO_RH_PROOF':True,'FULL_POINT_L1':'NOT_ISSUED','critical_margin':None}
    target.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({'status':receipt['status'],'seconds':receipt['seconds'],'max_width':receipt['maximum_quadrature_entry_width']}),flush=True)

if __name__=='__main__':run()
