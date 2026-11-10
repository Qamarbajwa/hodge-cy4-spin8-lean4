"""Target three sensitive odd Gram entries from shared image primitives.

Preserves P650; GL331 degree661 covers 649+11 and GL20 covers22.
No positivity follows from this writer computation.
"""
from pathlib import Path
from fractions import Fraction as F
import hashlib,json,time
from flint import arb,arb_mat,ctx
from research.certification_v2.certified_legendre_rule import certify_rule
from research.certification_v2.certified_gl_spatial import domain_legendre
from research.certification_v2.archimedean.arb_adapter import ball,encoded_bounds
from research.certification_v2.spatial_overlap import log_enclosure,prime_powers
from research.certification_v2.exact_interval_ldl import Interval

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/certification_v2/structured_schur_repair'
DEGREES=[7,9,11]

def basis_vector(node,norms):
    bounds=Interval.parse(encoded_bounds(node));lo=max(F(-1),bounds.lo);hi=min(F(1),bounds.hi)
    if lo>hi:raise ValueError('no proved domain')
    mid=(lo+hi)/2;rad=(hi-lo)/2;x=ball(mid)
    previous=arb(1);current=x;result=[]
    for k in range(650):
        if k==0:p=previous
        elif k==1:p=current
        else:
            p=((2*k-1)*x*current-(k-1)*previous)/k
            previous,current=current,p
        e=F(k*(k+1),2)*rad
        result.append((p+ball(Interval(-e,e)))*norms[k])
    return result

def run():
    target=OUT/'TARGETED_GRAM_REFINEMENT.json'
    if target.exists():raise ValueError('preserve prior run')
    OUT.mkdir(exist_ok=True);runs=[]
    for bits in [192,384,768]:
        started=time.monotonic()
        with ctx.workprec(bits):
            rule=certify_rule(331,bits=bits,bracket_bits=bits-40,newton_steps=12)
            small=certify_rule(20,bits=bits,bracket_bits=bits-40,newton_steps=12)
            if any(r['status']!='CERTIFIED_GAUSS_LEGENDRE_RULE_BOXES' for r in [rule,small]):raise ValueError('rule not enclosed')
            (OUT/f'TARGETED_RULES_{bits}.json').write_text(json.dumps({'projection':rule,'full_image':small},indent=2)+'\n')
            norms=[arb(F(2*k+1).numerator).sqrt()/arb(2).sqrt() for k in range(650)]
            C=arb_mat(650,3);images=[];endpoints=[Interval(-1,-1),Interval(1,1)]
            for n,p in prime_powers(7):
                rbox=log_enclosure(n,1024);r=ball(rbox);half=1-r/2;center=r/2
                coefficient=-ball(log_enclosure(p,1024))/arb(n).sqrt()
                images.extend([(rbox,coefficient),(-rbox,coefficient)])
                endpoints.extend([rbox-1,Interval(1,1)-rbox])
                X=[];Y=[]
                for item in rule['nodes_weights']:
                    x=center+half*ball(item['node']);y=x-r
                    X.append(basis_vector(x,norms));Y.append(basis_vector(y,norms))
                weights=[ball(item['weight'])*half for item in rule['nodes_weights']]
                L=arb_mat([[row[k] for row in X] for k in range(650)])
                R=arb_mat([[row[k] for row in Y] for k in range(650)])
                selectedX=arb_mat([[row[k]*w for row,w in zip(X,weights)] for k in DEGREES])
                selectedY=arb_mat([[row[k]*w for row,w in zip(Y,weights)] for k in DEGREES])
                C+=(L*selectedY.transpose()+R*selectedX.transpose())*coefficient
                print(json.dumps({'bits':bits,'prime_power':n,'phase':'SHARED_PROJECTION'}),flush=True)
            for i in range(650):
                if i%2==0:
                    for j in range(3):C[i,j]=arb(0)
            endpoints.sort(key=lambda b:b.lo)
            if not all(a.hi<b.lo for a,b in zip(endpoints,endpoints[1:])):raise ValueError('support order')
            full=arb_mat(3,3)
            for lo,hi in zip(endpoints,endpoints[1:]):
                center=(lo+hi)/2;half=(hi-lo)/2;active=[]
                for shift,coefficient in images:
                    v=center-shift
                    if -1<v.lo<=v.hi<1:active.append((shift,coefficient))
                    elif not (v.hi<-1 or v.lo>1):raise ValueError('active set')
                for item in small['nodes_weights']:
                    x=ball(center)+ball(half)*ball(item['node']);weight=ball(half)*ball(item['weight'])
                    values=[sum((coef*norms[k]*domain_legendre(k,x-ball(shift)) for shift,coef in active),arb(0)) for k in DEGREES]
                    for i in range(3):
                        for j in range(3):full[i,j]+=weight*values[i]*values[j]
            gram=full-C.transpose()*C
            entries=[[encoded_bounds(gram[i,j]) for j in range(3)] for i in range(3)]
        row={'bits':bits,'seconds':time.monotonic()-started,'entries':entries,
             'maximum_width':str(max(F(b)-F(a) for row in entries for a,b in row)),
             'status':'WRITER_ONLY_SHARED_PRIMITIVE_REFINED_GRAM','projection_degrees':list(range(650)),'target_degrees':DEGREES}
        runs.append(row);(OUT/f'TARGETED_GRAM_{bits}.json').write_text(json.dumps(row,indent=2)+'\n')
        print(json.dumps({'bits':bits,'seconds':row['seconds'],'maximum_width':row['maximum_width']}),flush=True)
    path=ROOT/'research/certification_v2/batch_arithmetic_gram/d650_RECEIPT.json'
    old=json.loads(path.read_text())['entries']
    changes=[]
    for i,k in enumerate(DEGREES):
        for j,l in enumerate(DEGREES):
            original=old[k][l];new=runs[-1]['entries'][i][j]
            if max(F(original[0]),F(new[0]))>min(F(original[1]),F(new[1])):raise ValueError('incompatible frozen Gram')
            changes.append({'degrees':[k,l],'OLD_WIDTH':str(F(original[1])-F(original[0])),'NEW_WIDTH':str(F(new[1])-F(new[0])),'old_new_overlap':True,'EFFECT_ON_CRITICAL_MARGIN':'NOT_YET_CERTIFIED; ONLY_NINE_TARGETED_ENTRIES_REFINED'})
    record={'status':'WRITER_ONLY_TARGETED_PRIMITIVE_RECOMPUTATION','runs':runs,'refinement':changes,
            'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'old_gram_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'NO_RH_PROOF':True,'FULL_POINT_L1':'NOT_ISSUED','old_corner_excluded':False}
    target.write_text(json.dumps(record,indent=2)+'\n')

if __name__=='__main__':run()
