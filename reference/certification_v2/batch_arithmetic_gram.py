"""Writer-only full arithmetic coupling Gram via clipped-image partition.

All cross terms are retained by squaring the sum of complete shifted images.
The compressed PVP square is subtracted only after full-image integration.
"""
from fractions import Fraction as F
from pathlib import Path
import gzip,hashlib,json,time
from flint import arb,arb_mat,ctx
from research.certification_v2.certified_gl_spatial import frozen_rule,ball,domain_legendre
from research.certification_v2.spatial_overlap import prime_powers,log_enclosure
from research.certification_v2.archimedean.arb_adapter import encoded_bounds
from research.certification_v2.exact_interval_ldl import Interval

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/certification_v2/batch_arithmetic_gram'

def build(dimension):
    if type(dimension) is not int or not 1<=dimension<=650:
        raise ValueError('dimension in 1..650 required')
    if not log_enclosure(7,512).hi<2<log_enclosure(8,512).lo:
        raise ValueError('complete active list required')
    rule=frozen_rule()
    with ctx.workprec(192):
        images=[];endpoints=[Interval(-1,-1),Interval(1,1)]
        for n,p in prime_powers(7):
            shift=log_enclosure(n,512)
            coefficient=-ball(log_enclosure(p,512))/arb(n).sqrt()
            images.extend([(shift,coefficient),(-shift,coefficient)])
            endpoints.extend([shift-1,Interval(1,1)-shift])
        endpoints.sort(key=lambda x:x.lo)
        if not all(x.hi<y.lo for x,y in zip(endpoints,endpoints[1:])):
            raise ValueError('support endpoints not strictly ordered')
        gram=arb_mat(dimension,dimension)
        norms=[arb(2*k+1).sqrt()/arb(2).sqrt() for k in range(dimension)]
        partitions=[]
        for lo,hi in zip(endpoints,endpoints[1:]):
            center=(lo+hi)/2;half=(hi-lo)/2
            if half.lo<=0:
                raise ValueError('positive cell width not proved')
            active=[]
            for index,(shift,coefficient) in enumerate(images):
                at_center=center-shift
                if -1<at_center.lo<=at_center.hi<1:
                    active.append(index)
                elif at_center.hi<-1 or at_center.lo>1:
                    pass
                else:
                    raise ValueError('cell active set unresolved')
            # Exhaustive endpoint partition proves this active set holds
            # throughout each true open cell; boundary values have measure0.
            left=[[] for _ in range(dimension)];right=[[] for _ in range(dimension)]
            for item in rule['nodes_weights']:
                x=ball(center)+ball(half)*ball(item['node'])
                weight=ball(item['weight'])*ball(half)
                values=[arb(0) for _ in range(dimension)]
                for index in active:
                    shift,coefficient=images[index]
                    y=x-ball(shift)
                    for k in range(dimension):
                        values[k]+=coefficient*norms[k]*domain_legendre(k,y)
                for k,value in enumerate(values):
                    left[k].append(value*weight);right[k].append(value)
            gram+=arb_mat(left)*arb_mat(right).transpose()
            partitions.append({'lo':lo.encoded(),'hi':hi.encoded(),'active_image_indices':active})
        for i in range(dimension):
            for j in range(dimension):
                if (i+j)%2:gram[i,j]=arb(0)
        return gram,partitions

def run(dimension=8):
    OUT.mkdir(exist_ok=True)
    target=OUT/f'd{dimension}_RECEIPT.json'
    if target.exists():raise ValueError('preserve earlier experiments')
    compressed_path=ROOT/f'research/certification_v2/batch_gl_spatial/d{dimension}_ARITHMETIC_MATRIX.json.gz'
    compressed=json.loads(gzip.decompress(compressed_path.read_bytes()))
    source=Path(__file__)
    hashes={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in [source,compressed_path]}
    started=time.monotonic()
    with ctx.workprec(192):
        full,partitions=build(dimension)
        A=arb_mat([[ball(x) for x in row] for row in compressed])
        coupling=full-A*A
        entries=[]
        for i in range(dimension):
            row=[]
            for j in range(dimension):
                if (i+j)%2:row.append(['0','0']);continue
                a=Interval.parse(encoded_bounds(coupling[i,j]));b=Interval.parse(encoded_bounds(coupling[j,i]))
                row.append(Interval(max(a.lo,b.lo),min(a.hi,b.hi)).encoded())
            entries.append(row)
    receipt={'status':'WRITER_ONLY_UNREVIEWED_FULL_ARITHMETIC_COUPLING_GRAM',
             'dimension':dimension,'L':'1','formula':'PV^2P-(PVP)^2',
             'entries':entries,'partitions':partitions,'input_sha256':hashes,
             'seconds':time.monotonic()-started,'NO_RH_PROOF':True,
             'full_canonical_coupling_certified':False,'restored_intervals':0}
    target.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({'status':receipt['status'],'seconds':receipt['seconds']}),flush=True)

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--dimension',type=int,default=8)
    run(parser.parse_args().dimension)
