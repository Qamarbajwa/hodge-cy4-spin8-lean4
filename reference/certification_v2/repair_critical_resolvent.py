"""Preserve the old resolvent; enclose the complete normalized residual."""
from pathlib import Path
from fractions import Fraction as F
import json,gzip,hashlib
from flint import arb_mat,ctx
from research.certification_v2.exact_interval_ldl import Interval
from research.certification_v2.compact_interval_ldl import certify_compact
from research.certification_v2.archimedean.arb_adapter import ball,encoded_bounds
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'research/certification_v2/direct_critical_form'
OUT=BASE/'critical_resolvent_repair'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run():
    OUT.mkdir(exist_ok=True)
    if (OUT/'WRITER_RECEIPT.json').exists():raise ValueError('preserve frozen candidate')
    paths=[BASE/'CRITICAL_COMPOSITION_WRITER.json',BASE/'streaming_k_action/PRECONDITIONER_R6_12_BY_12.json',BASE/'streaming_k_action/XR_638_BY_12.json.gz',ROOT/'research/certification_v2/structured_schur_repair/BULK_SPLIT_RECEIPT.json']
    comp,prec=map(read,paths[:2]);xr=json.loads(gzip.decompress(paths[2].read_bytes()))
    b=F(read(paths[3])['bulk_gershgorin_lower_bound']);kap=F(comp['bulk_solve_penalty'])
    assert F(15,100)<b<F(16,100)
    results=[];exports={}
    with ctx.workprec(768):
        for sector in range(2):
            R=[[F(x) for x in row] for row in prec[['R_even_exact','R_odd_exact'][sector]]]
            assert all(R[i][i]==1 and all(R[i][j]==0 for j in range(i)) for i in range(6))
            pre=[[Interval.parse(comp['boxes'][sector*6+i][sector*6+j])+(kap if i==j else 0) for j in range(6)] for i in range(6)]
            A=[[sum((pre[m][n]*(R[m][i]*R[n][j]) for m in range(6) for n in range(6)),Interval(0,0)) for j in range(6)] for i in range(6)]
            G=[[sum((Interval.parse(row[sector*6+i])*Interval.parse(row[sector*6+j]) for row in xr),Interval(0,0))/b for j in range(6)] for i in range(6)]
            M=[[A[i][j]-G[i][j] for j in range(6)] for i in range(6)]
            # Symmetric families use the same upper-triangle enclosure both ways.
            M=[[M[min(i,j)][max(i,j)] for j in range(6)] for i in range(6)]
            exported=[[x.encoded() for x in row] for row in M];exports[str(sector)]=exported
            primary=[[exported[i][j] for j in range(3)] for i in range(3)]
            exact=certify_compact(primary)
            d=[A[i][i].lo for i in range(3)];assert min(d)>0
            # M = D^(1/2)(I-H)D^(1/2), H includes G and ALL A-D terms.
            H=arb_mat([[ball(Interval(d[i] if i==j else 0,d[i] if i==j else 0)-M[i][j])/((ball(d[i])*ball(d[j])).sqrt()) for j in range(3)] for i in range(3)])
            norm=max(sum(max(abs(F(lo)),abs(F(hi))) for lo,hi in [encoded_bounds(H[i,j]) for j in range(3)]) for i in range(3))
            lower=(1-norm)*min(d)
            shifted=certify_compact(primary,shift=str(lower)) if lower>0 else None
            results.append({'parity':sector,'primary_exact_ldl':exact,'correct_full_residual_norm_upper':str(norm),'coordinate_lower_bound':str(lower),'positive':norm<1,'independent_shifted_ldl':shifted,'full_sector_ldl':certify_compact(exported)})
    matrixpath=OUT/'COMPLETE_SCHUR_BOXES.json';matrixpath.write_text(json.dumps(exports,indent=2)+'\n')
    result={'writer_id':'/root','status':'FROZEN_WRITER_CANDIDATE','bulk_floor':str(b),'results':results,'scope':'THREE_PRECONDITIONED_COORDINATES_PER_PARITY_ONLY; NOT_FULL650_OR_POINT','discrepancies':['Old mpmath norms have no directed rounding','Old diagonal-only resolvent identity omits Atrans offdiagonal','Old derivation confuses coupling upper2.6179 with bulk floor0.15135'],'files_sha256':{p.relative_to(ROOT).as_posix():sha(p) for p in paths+[Path(__file__),matrixpath]},'NO_RH_PROOF':True,'FULL_POINT_L1':'NOT_ISSUED','PUBLICATION_STATUS':'HOLD'}
    (OUT/'WRITER_RECEIPT.json').write_text(json.dumps(result,indent=2)+'\n')
    print([(r['parity'],float(F(r['correct_full_residual_norm_upper'])),float(F(r['coordinate_lower_bound'])),r['primary_exact_ldl']['status'],r['independent_shifted_ldl']['status']) for r in results])
if __name__=='__main__':run()
