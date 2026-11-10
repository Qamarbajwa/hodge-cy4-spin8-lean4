"""Floating proposals only; scientific verification is a separate operation."""
from fractions import Fraction as F
from pathlib import Path
import gzip,hashlib,json
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/certification_v2/p650_stable_assembly'

def run():
    for name in ['FINITE_LOWER','SCHUR_LOWER']:
        source=OUT/(name+'.json.gz');output=OUT/(name+'_PRECONDITIONER_PROPOSAL.json')
        if output.exists():raise ValueError('preserve earlier proposal')
        boxes=json.loads(gzip.decompress(source.read_bytes()))
        midpoint=np.array([[float((F(x[0])+F(x[1]))/2) for x in row] for row in boxes])
        receipt={'status':'FLOAT_DIAGNOSTIC_PROPOSAL_ONLY',
                 'input_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
                 'full_operator_status':'BLOCKED','NO_RH_PROOF':True}
        try:
            factor=np.linalg.cholesky(midpoint)
            R=np.linalg.solve(factor.T,np.eye(650))
            receipt['exact_dyadic_preconditioner']=[[str(F(float(x))) for x in row] for row in R]
        except np.linalg.LinAlgError as error:
            receipt['status']='FLOAT_DIAGNOSTIC_CHOLESKY_FAILURE_NOT_RIGOROUS'
            receipt['error']=str(error)
        output.write_text(json.dumps(receipt,indent=2)+'\n')

if __name__=='__main__':run()
