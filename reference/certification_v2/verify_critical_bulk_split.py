"""Propose a full dyadic basis; validate metric and safely positive bulk.

Uses original frozen Schur boxes. Critical block sign is not certified.
"""
from fractions import Fraction as F
from pathlib import Path
import gzip,hashlib,json,time
from flint import arb_mat,ctx
from research.certification_v2.archimedean.arb_adapter import ball,encoded_bounds

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/certification_v2/structured_schur_repair'

def run():
    target=OUT/'BULK_SPLIT_RECEIPT.json'
    if target.exists():raise ValueError('preserve earlier run')
    started=time.monotonic()
    path=ROOT/'research/certification_v2/p650_stable_assembly/SCHUR_LOWER.json.gz'
    entries=json.loads(gzip.decompress(path.read_bytes()))
    basispath=OUT/'FULL_DYADIC_SPLIT_BASIS.json.gz'
    if not basispath.exists():raise ValueError('system NumPy dyadic proposal must be saved first')
    columns=[list(map(F,col)) for col in json.loads(gzip.decompress(basispath.read_bytes()))]
    assert len(columns)==650 and all(len(col)==650 for col in columns)
    with ctx.workprec(192):
        S=arb_mat([[ball(columns[j][i]) for j in range(650)] for i in range(650)])
        G=S.transpose()*S
        residual=[]
        for i in range(650):
            row=F(0)
            for j in range(650):
                a,b=map(F,encoded_bounds(G[i,j]-(1 if i==j else 0)))
                row+=max(abs(a),abs(b))
            residual.append(row)
        eta=max(residual)
        if eta>=1:raise ValueError('basis invertibility not verified')
        M=arb_mat([[ball(x) for x in row] for row in entries])
        transformed=S.transpose()*M*S
        bulk=[]
        for i in range(12,650):
            diagonal=F(encoded_bounds(transformed[i,i])[0]);radius=F(0)
            for j in range(12,650):
                if i==j:continue
                a,b=map(F,encoded_bounds(transformed[i,j]));radius+=max(abs(a),abs(b))
            bulk.append(diagonal-radius)
        beta=min(bulk)
        criticalboxes=[[encoded_bounds(transformed[i,j]) for j in range(12)] for i in range(12)]
        # A rigorous Frobenius cross bound suffices for a conditional nested Schur.
        coupling2=F(0)
        for i in range(12):
            for j in range(12,650):
                a,b=map(F,encoded_bounds(transformed[i,j]));coupling2+=max(abs(a),abs(b))**2
    record={'status':'WRITER_ONLY_VALIDATED_DYADIC_FULL_BASIS_AND_BULK',
            'S_invertible':True,'metric_residual_row_norm_upper':str(eta),
            'gram_lower_bound':str(1-eta),'gram_upper_bound':str(1+eta),
            'original_metric_identity':'x=Sy; x^T M x=y^T(S^T M S)y; ||x||^2=y^T(S^T S)y',
            'critical_dimension':12,'bulk_dimension':638,'bulk_gershgorin_lower_bound':str(beta),
            'bulk_positive':beta>0,'critical_boxes':criticalboxes,
            'critical_bulk_coupling_frobenius_squared_upper':str(coupling2),
            'nested_schur_scalar_penalty':str(coupling2/beta) if beta>0 else None,
            'critical_positive_margin':None,'FULL_POINT_L1':'NOT_ISSUED','NO_RH_PROOF':True,
            'input_sha256':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,OUT/'CRITICAL_SUBSPACE.json',basispath]},
            'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'seconds':time.monotonic()-started}
    target.write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({'seconds':record['seconds'],'metric_residual_diagnostic':float(eta),'bulk_lower_diagnostic':float(beta),'cross_squared_diagnostic':float(coupling2),'nested_penalty_diagnostic':float(coupling2/beta) if beta>0 else None}),flush=True)

if __name__=='__main__':run()
