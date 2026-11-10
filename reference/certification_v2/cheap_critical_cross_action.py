"""Writer-only cheap directional cross audit on the original S box family."""
from pathlib import Path
from fractions import Fraction as F
import json,gzip,hashlib,time,sys
from flint import arb_mat,ctx
from research.certification_v2.archimedean.arb_adapter import ball,encoded_bounds
from research.certification_v2.exact_interval_ldl import Interval
from research.certification_v2.compact_interval_ldl import certify_compact,dyadic_report
from research.certification_v2.pole_entries import pole_matrix
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'research/certification_v2/direct_critical_form/cheap_cross_action'
def read(p):return json.loads(p.read_text())
def gz(p):return json.loads(gzip.decompress(p.read_bytes()))
def squared_upper(entries):return sum(max(abs(F(a)),abs(F(b)))**2 for a,b in entries)
def run():
 sys.set_int_max_str_digits(50000);OUT.mkdir(exist_ok=True)
 target=OUT/'WRITER_RECEIPT.json'
 if target.exists():raise ValueError('preserve previous candidate')
 started=time.monotonic();base=ROOT/'research/certification_v2/structured_schur_repair';direct=ROOT/'research/certification_v2/direct_critical_form'
 accepted=read(base/'BULK_SPLIT_ACCEPTANCE.json')
 for p,h in accepted['files_sha256'].items():
  if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('accepted input changed '+p)
 basispath=base/'FULL_DYADIC_SPLIT_BASIS.json.gz';mpath=ROOT/'research/certification_v2/p650_stable_assembly/SCHUR_LOWER.json.gz'
 columns=[[F(x) for x in c] for c in gz(basispath)];zcols=columns[:12];ycols=columns[12:]
 witnesspath=direct/'EXACT_LDL_NEGATIVE_TRIAL.json';v=list(map(F,read(witnesspath)['exact_vector']))
 norm=sum(x*x for x in v)
 if norm<=0:raise ValueError('nonzero witness required')
 u=[sum(zcols[j][i]*v[j] for j in range(12)) for i in range(650)]
 b=F(read(base/'BULK_SPLIT_RECEIPT.json')['bulk_gershgorin_lower_bound']);eta=F(read(base/'BULK_SPLIT_RECEIPT.json')['metric_residual_row_norm_upper'])
 if b<=0 or eta>=1:raise ValueError('accepted bulk premise')
 compositionpath=direct/'CRITICAL_COMPOSITION_WRITER.json';composition=read(compositionpath)
 kappa=F(composition['bulk_solve_penalty'])
 pre=[[Interval.parse(x)+(kappa if i==j else 0) for j,x in enumerate(row)] for i,row in enumerate(composition['boxes'])]
 witnessbound=read(direct/'EXACT_LDL_COMPARISON_WITNESS.json')['actual_fixed_S_lower_rayleigh_bound']
 alpha=F(witnessbound[0]);threshold=b*alpha
 with ctx.workprec(384):
  W=arb_mat([[ball(c[i]) for c in zcols+[u]] for i in range(650)])
  Y=arb_mat([[ball(c[i]) for c in ycols] for i in range(650)])
  M=arb_mat([[ball(x) for x in row] for row in gz(mpath)])
  actions=Y.transpose()*(M*W)
  X=[[encoded_bounds(actions[i,j]) for j in range(12)] for i in range(638)]
  direction=[encoded_bounds(actions[i,12]) for i in range(638)]
  q=squared_upper(direction)/norm;penalty=q/b
  # Reboxed Xv is a separate, usually weaker valid comparison.
  reboxed=[]
  for row in X:
   val=sum((Interval.parse(x)*v[j] for j,x in enumerate(row)),Interval(0,0))
   reboxed.append(val.encoded())
  q_reboxed=squared_upper(reboxed)/norm
  centers=[[(F(a)+F(b))/2 for a,b in row] for row in X]
  radii=[[(F(b)-F(a))/2 for a,b in row] for row in X]
  e2=sum(r*r for row in radii for r in row)
  x02=sum(x*x for row in centers for x in row)
  X0=arb_mat([[ball(x) for x in row] for row in centers]);P=X0.transpose()*X0
  grams=[[encoded_bounds(P[i,j]) for j in range(12)] for i in range(12)]
 # The symmetrized Gram bounds must include the true point product.
 for i in range(12):
  for j in range(i,12):
   a=Interval.parse(grams[i][j]);d=Interval.parse(grams[j][i]);e=Interval(max(a.lo,d.lo),min(a.hi,d.hi));grams[i][j]=grams[j][i]=e.encoded()
 candidates=[]
 for theta in [F(1),F(10),F(100),F(1000)]:
  matrix=[]
  for i in range(12):
   row=[]
   for j in range(12):
    pi=Interval.parse(grams[i][j])*(1+theta)/b
    if i==j:pi=pi+(1+1/theta)*e2/b
    row.append((pre[i][j]-pi).encoded())
   matrix.append(row)
  tests=[]
  for sector in [list(range(6)),list(range(6,12))]:
   block=[[matrix[i][j] for j in sector] for i in sector]
   result=certify_compact(block,report_bits=512);tests.append(result)
  candidates.append({'theta':str(theta),'scalar_error_penalty':str((1+1/theta)*e2/b),'tests':tests})
  (OUT/f'YOUNG_MATRIX_THETA_{theta.numerator}.json').write_text(json.dumps(matrix,indent=2)+'\n')
 # Cheap action-error audit: all old cutoff errors are retained, not reset.
 archpath=ROOT/'research/certification_v2/stable_shared_arch_quadrature/d650_RECEIPT.json'
 arch=read(archpath)['entries'];arch_radius=max(sum((F(hi)-F(lo))/2 for lo,hi in row) for row in arch)
 pole=pole_matrix(range(32),1);pole_radius=max(sum((x.hi-x.lo)/2 for x in row) for row in pole)
 metric_upper=1+eta
 Xpath=OUT/'X_638_BY_12.json.gz';Xpath.write_bytes(gzip.compress((json.dumps(X,separators=(',',':'))+'\n').encode(),mtime=0))
 dpath=OUT/'DIRECT_WITNESS_ACTION.json';dpath.write_text(json.dumps({'entries':direction,'critical_vector':list(map(str,v)),'euclidean_critical_norm_squared':str(norm)},indent=2)+'\n')
 inputs=[basispath,mpath,witnesspath,compositionpath,direct/'EXACT_LDL_COMPARISON_WITNESS.json',base/'BULK_SPLIT_ACCEPTANCE.json',base/'BULK_SPLIT_RECEIPT.json',archpath,Path(__file__),ROOT/'research/certification_v2/compact_interval_ldl.py',ROOT/'research/certification_v2/pole_entries.py']
 record={'writer_id':'/root/gov_reviewer','status':'FROZEN_WRITER_CANDIDATE_NOT_REVIEWED','seconds':time.monotonic()-started,'bits':384,'projection_dimension':650,'critical_dimension':12,'bulk_dimension':638,'basis_unchanged':True,'formula':'X=Y*SZ for the original frozen S family; direct witness=Y*S*(Zv), before reboxing columns','bulk_lower':str(b),'positive_prebulk_witness_lower':str(alpha),'squared_directional_cross_threshold':str(threshold),'squared_direct_witness_norm_upper_normalized':str(q),'direct_bulk_penalty_upper':str(penalty),'directional_bound_strictly_below_positive_threshold':q<threshold,'squared_reboxed_witness_norm_upper_normalized':str(q_reboxed),'midpoint_cross_frobenius_squared':str(x02),'cross_error_frobenius_squared':str(e2),'directional_Young_candidates':candidates,'audit':{'old_cutoff_midpoint_error_operator_norm_upper':str(arch_radius),'old_cutoff_cross_error_upper':str(arch_radius*metric_upper),'signed_pole32_midpoint_error_operator_norm_upper':str(pole_radius),'signed_pole32_cross_error_upper':str(pole_radius*metric_upper)},'input_sha256':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},'output_sha256':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in [Xpath,dpath]},'critical_positive_margin':None,'NO_RH_PROOF':True,'FULL_POINT_L1':'NOT_ISSUED'}
 target.write_text(json.dumps(record,indent=2)+'\n')
 print(json.dumps({'seconds':record['seconds'],'q':float(q),'threshold':float(threshold),'passed_direction':q<threshold,'midpoint2':float(x02),'error2':float(e2),'young_tests':[[x['status'] for x in r['tests']] for r in candidates],'arch_radius':float(arch_radius),'pole_radius':float(pole_radius)}),flush=True)
if __name__=='__main__':run()
