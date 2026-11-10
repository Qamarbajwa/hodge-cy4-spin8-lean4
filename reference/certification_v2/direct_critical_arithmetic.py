"""Writer candidate: shared-image twelve-mode arithmetic form, same P650.

No operator or critical positivity claim. All products use common image
linear combinations before forming bilinear products, never old matrix boxes.
"""
from pathlib import Path
from fractions import Fraction as F
import json,gzip,hashlib,time
from flint import arb,arb_mat,ctx
from research.certification_v2.certified_legendre_rule import certify_rule
from research.certification_v2.archimedean.arb_adapter import ball,encoded_bounds
from research.certification_v2.spatial_overlap import log_enclosure,prime_powers
from research.certification_v2.exact_interval_ldl import Interval
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/certification_v2/direct_critical_form'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def basis_matrix(nodes,norms):
    """True nodes lie in the mapped support; clip only this proved domain."""
    columns=[]
    for node in nodes:
        lo,hi=map(F,encoded_bounds(node));lo=max(lo,F(-1));hi=min(hi,F(1))
        if lo>hi:raise ValueError('proved support intersection empty')
        midpoint=ball((lo+hi)/2);radius=(hi-lo)/2
        columns.append([(midpoint.legendre_p(k)+ball(Interval(-F(k*(k+1),2)*radius,F(k*(k+1),2)*radius)))*norms[k] for k in range(650)])
    return arb_mat([[column[k] for column in columns] for k in range(650)])
def weighted(A,weights):
    return arb_mat([[A[i,j]*weights[j] for j in range(A.ncols())] for i in range(A.nrows())])
def symmetric_boxes(A,parity):
    answer=[]
    for i in range(A.nrows()):
        row=[]
        for j in range(A.ncols()):
            if parity[i]!=parity[j]:row.append(['0','0']);continue
            a=Interval.parse(encoded_bounds(A[i,j]));b=Interval.parse(encoded_bounds(A[j,i]))
            lo=max(a.lo,b.lo);hi=min(a.hi,b.hi)
            if lo>hi:raise ValueError('transposition enclosures disjoint')
            row.append(Interval(lo,hi).encoded())
        answer.append(row)
    return answer
def run(bits=384,bracket_bits=192):
    OUT.mkdir(exist_ok=True);target=OUT/'ARITHMETIC_RECEIPT.json'
    if target.exists():raise ValueError('preserve previous writer receipt')
    started=time.monotonic();dependencies={}
    acceptance=ROOT/'research/certification_v2/structured_schur_repair/BULK_SPLIT_ACCEPTANCE.json'
    accepted=load(acceptance)
    for p,h in accepted['files_sha256'].items():
        if digest(ROOT/p)!=h:raise ValueError('accepted input changed: '+p)
        dependencies[p]=h
    dependencies[acceptance.relative_to(ROOT).as_posix()]=digest(acceptance)
    basispath=ROOT/'research/certification_v2/structured_schur_repair/FULL_DYADIC_SPLIT_BASIS.json.gz'
    columns=json.loads(gzip.decompress(basispath.read_bytes()))[:12]
    criticalpath=ROOT/'research/certification_v2/structured_schur_repair/CRITICAL_SUBSPACE.json'
    if columns!=load(criticalpath)['CRITICAL_BASIS']:raise ValueError('critical basis mismatch')
    parity=[]
    for column in columns:
        support={i%2 for i,x in enumerate(column) if F(x)}
        if len(support)!=1:raise ValueError('pure parity basis required')
        parity.append(next(iter(support)))
    for p in [Path(__file__),ROOT/'research/certification_v2/certified_legendre_rule.py',ROOT/'research/certification_v2/archimedean/arb_adapter.py',ROOT/'research/certification_v2/spatial_overlap.py']:
        dependencies[p.relative_to(ROOT).as_posix()]=digest(p)
    def progress(phase,**kwargs):
        record={'phase':phase,'seconds':time.monotonic()-started,**kwargs,'NO_RH_PROOF':True}
        (OUT/'ARITHMETIC_PROGRESS.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record),flush=True)
    if not log_enclosure(7,1024).hi<2<log_enclosure(8,1024).lo:raise ValueError('complete active-set gate')
    with ctx.workprec(bits):
        rule=certify_rule(650,bits=bits,bracket_bits=bracket_bits,newton_steps=12)
        if rule['status']!='CERTIFIED_GAUSS_LEGENDRE_RULE_BOXES':raise ValueError('rule not certified')
        rulepath=OUT/'ARITHMETIC_GL650_RULE.json';rulepath.write_text(json.dumps(rule,indent=2)+'\n')
        dependencies[rulepath.relative_to(ROOT).as_posix()]=digest(rulepath)
        Z=arb_mat([[ball(F(columns[j][i])) for j in range(12)] for i in range(650)]);ZT=Z.transpose()
        norms=[arb(2*k+1).sqrt()/arb(2).sqrt() for k in range(650)]
        C=arb_mat(650,12);images=[];endpoints=[Interval(-1,-1),Interval(1,1)]
        for n,p in prime_powers(7):
            rbox=log_enclosure(n,1024);r=ball(rbox);half=1-r/2;center=r/2
            coefficient=-ball(log_enclosure(p,1024))/arb(n).sqrt()
            images.extend([(rbox,coefficient),(-rbox,coefficient)])
            endpoints.extend([rbox-1,Interval(1,1)-rbox])
            Xnodes=[center+half*ball(item['node']) for item in rule['nodes_weights']]
            Ynodes=[x-r for x in Xnodes]
            X=basis_matrix(Xnodes,norms);Y=basis_matrix(Ynodes,norms)
            weights=[half*ball(item['weight']) for item in rule['nodes_weights']]
            ZX=ZT*X;ZY=ZT*Y
            C+=(X*weighted(ZY,weights).transpose()+Y*weighted(ZX,weights).transpose())*coefficient
            progress('COMPLETE_P650_PROJECTION',prime_power=n)
        for i in range(650):
            for j in range(12):
                if i%2!=parity[j]:C[i,j]=arb(0)
        compression=ZT*C;full=arb_mat(12,12);endpoints.sort(key=lambda x:x.lo)
        if not all(a.hi<b.lo for a,b in zip(endpoints,endpoints[1:])):raise ValueError('support order unresolved')
        partitions=[]
        for index,(lo,hi) in enumerate(zip(endpoints,endpoints[1:])):
            center=(lo+hi)/2;half=(hi-lo)/2
            if half.lo<=0:raise ValueError('nonpositive cell')
            active=[]
            for a,(shift,coefficient) in enumerate(images):
                v=center-shift
                if -1<v.lo<=v.hi<1:active.append(a)
                elif not (v.hi<-1 or v.lo>1):raise ValueError('active image unresolved')
            nodes=[ball(center)+ball(half)*ball(item['node']) for item in rule['nodes_weights']]
            values=arb_mat(12,650)
            for a in active:
                shift,coefficient=images[a]
                shifted=[x-ball(shift) for x in nodes]
                values+=(ZT*basis_matrix(shifted,norms))*coefficient
            weights=[ball(half)*ball(item['weight']) for item in rule['nodes_weights']]
            full+=weighted(values,weights)*values.transpose()
            partitions.append({'lo':lo.encoded(),'hi':hi.encoded(),'active_images':active})
            progress('FULL_SHARED_IMAGE_PRODUCTS',cell=index+1,cells=11,active_images=len(active))
        projection_square=C.transpose()*C;gram=full-projection_square
        encoded={'Z_V_Z':symmetric_boxes(compression,parity),'Z_V2_Z':symmetric_boxes(full,parity),'PVZ_squared':symmetric_boxes(projection_square,parity),'Q650VZ_gram':symmetric_boxes(gram,parity)}
        cpath=OUT/'ARITHMETIC_PVZ.json.gz'
        cent=[[encoded_bounds(C[i,j]) for j in range(12)] for i in range(650)]
        cpath.write_bytes(gzip.compress((json.dumps(cent,separators=(',',':'))+'\n').encode(),mtime=0))
        dependencies[cpath.relative_to(ROOT).as_posix()]=digest(cpath)
        exact_metric=[[str(sum(F(columns[i][k])*F(columns[j][k]) for k in range(650))) for j in range(12)] for i in range(12)]
    widths={name:str(max(F(b)-F(a) for row in entries for a,b in row)) for name,entries in encoded.items()}
    record={'writer_id':'/root/gov_reviewer','status':'FROZEN_WRITER_CANDIDATE_NOT_REVIEWED','task':'RH-V2-P650-DIRECT-CRITICAL-FORM-L1-T400-001','bits':bits,'bracket_bits':bracket_bits,'L':'1','projection_dimension':650,'critical_dimension':12,'critical_parity':parity,'complete_active_prime_powers':[2,3,4,5,7],'signed_images':10,'projection_rows':650,'GL_degree':650,'GL_exactness_degree':1299,'maximum_product_degree':1298,'algebraic_quadrature_remainder':'0','entries':encoded,'maximum_widths':widths,'exact_critical_metric':exact_metric,'partitions':partitions,'files_sha256':dependencies,'seconds':time.monotonic()-started,'formula':'Gcritical=<VZ,VZ>-(P650VZ)*(P650VZ); all ten images, all cross terms, all650 projection rows','NO_RH_PROOF':True,'critical_positive_margin':None,'full_canonical_coupling_certified':False,'FULL_POINT_L1':'NOT_ISSUED'}
    target.write_text(json.dumps(record,indent=2)+'\n');progress('DONE',maximum_widths=widths)
if __name__=='__main__':run()
