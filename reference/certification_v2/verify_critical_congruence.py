"""Actual increasing-precision transformed boxes and exact dyadic Gram.

Rectangular critical basis is not a full invertible congruence. No bulk claim.
"""
from pathlib import Path
from fractions import Fraction as F
import gzip, hashlib, json, time
from flint import arb_mat, ctx
from research.certification_v2.archimedean.arb_adapter import ball, encoded_bounds

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/certification_v2/structured_schur_repair'

def run():
    path=OUT/'CONGRUENCE_PRECISION_TEST.json'
    if path.exists():raise ValueError('preserve existing run')
    basis_path=OUT/'CRITICAL_SUBSPACE.json'
    basis=json.loads(basis_path.read_text())['CRITICAL_BASIS']
    columns=[list(map(F,c)) for c in basis]
    gram=[[sum(a*b for a,b in zip(x,y)) for y in columns] for x in columns]
    lo=min(gram[i][i]-sum(abs(gram[i][j]) for j in range(12) if j!=i) for i in range(12))
    hi=max(gram[i][i]+sum(abs(gram[i][j]) for j in range(12) if j!=i) for i in range(12))
    assert lo>0
    matrix_path=ROOT/'research/certification_v2/p650_stable_assembly/SCHUR_LOWER.json.gz'
    matrix=json.loads(gzip.decompress(matrix_path.read_bytes()))
    runs=[]; previous=None
    for bits in [192,384,768]:
        started=time.monotonic()
        with ctx.workprec(bits):
            Z=arb_mat([[ball(columns[j][i]) for j in range(12)] for i in range(650)])
            M=arb_mat([[ball(x) for x in row] for row in matrix])
            transformed=Z.transpose()*M*Z
            boxes=[[encoded_bounds(transformed[i,j]) for j in range(12)] for i in range(12)]
        nested=None if previous is None else all(F(old[0])<=F(new[0])<=F(new[1])<=F(old[1]) for r,s in zip(previous,boxes) for old,new in zip(r,s))
        row={'bits':bits,'seconds':time.monotonic()-started,'transformed_entry_boxes':boxes,
             'maximum_width':str(max(F(x[1])-F(x[0]) for row in boxes for x in row)),
             'nested_in_previous':nested,'positivity_status':'NOT_CERTIFIED; ORIGINAL_ENTRY_BOX_DEPENDENCY_NOT_REPAIRED'}
        runs.append(row);previous=boxes
        print(json.dumps({k:row[k] for k in ['bits','seconds','maximum_width','nested_in_previous']}),flush=True)
    record={'status':'WRITER_ONLY_ACTUAL_ARBITRARY_PRECISION_RESTRICTED_CONGRUENCE',
            'exact_gram':[[str(x) for x in row] for row in gram],
            'gram_lower_bound_exact':str(lo),'gram_upper_bound_exact':str(hi),
            'critical_basis_rank':12,'rank_proof':'EXACT_RATIONAL_GRAM_GERSHGORIN_POSITIVE',
            'original_metric':'||Zy||^2=y^T G y; lo||y||^2<=||Zy||^2<=hi||y||^2',
            'full_650_change_of_basis_invertible':False,'safe_bulk_certified':False,
            'smallest_generalized_eigenvalue':None,'Schur_margin':None,'runs':runs,
            'input_sha256':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in [basis_path,matrix_path]},
            'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'NO_RH_PROOF':True,'FULL_POINT_L1':'NOT_ISSUED'}
    path.write_text(json.dumps(record,indent=2)+'\n')

if __name__=='__main__':run()
