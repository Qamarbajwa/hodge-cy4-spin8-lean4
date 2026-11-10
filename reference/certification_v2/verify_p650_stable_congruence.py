"""Actual P650 conditional matrix checks; never full-proof acceptance."""
from pathlib import Path
import gzip,hashlib,json
from research.certification_v2.verified_congruence import verify

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/certification_v2/p650_stable_assembly'

def run():
    for name in ['FINITE_LOWER','SCHUR_LOWER']:
        source=OUT/(name+'.json.gz');proposal=OUT/(name+'_PRECONDITIONER_PROPOSAL.json')
        target=OUT/(name+'_CONGRUENCE_RECEIPT.json')
        if target.exists():raise ValueError('preserve earlier check')
        data=json.loads(proposal.read_text())
        if data['input_sha256']!=hashlib.sha256(source.read_bytes()).hexdigest():
            raise ValueError('proposal input changed')
        if 'exact_dyadic_preconditioner' not in data:
            result={'status':'INCONCLUSIVE_NO_PRECONDITIONER','matrix_lower_bound':None}
        else:
            matrix=json.loads(gzip.decompress(source.read_bytes()))
            result=verify(matrix,data['exact_dyadic_preconditioner'])
        result.update({'scope':'WRITER_ONLY_CONDITIONAL_P650_'+name,
                       'NO_RH_PROOF':True,'FULL_POINT_L1':'NOT_ISSUED',
                       'input_sha256':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                                       for p in [source,proposal,Path(__file__),ROOT/'research/certification_v2/verified_congruence.py']}})
        target.write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps({'name':name,'status':result['status'],'matrix_lower_bound':result['matrix_lower_bound']}),flush=True)

if __name__=='__main__':run()
