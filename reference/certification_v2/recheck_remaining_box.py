"""Exact update of the accepted corner witness after nine entry refinements."""
from pathlib import Path
from fractions import Fraction as F
import hashlib,json

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/certification_v2/structured_schur_repair'

def calculate():
    paths=[OUT/'TARGETED_CORNER_RECHECK.json',OUT/'CRITICAL_SUBSPACE.json',
           ROOT/'research/certification_v2/p650_stable_assembly/INDEPENDENT_EXACT_CORNER_CHECKS.json']
    refinement,basis,old=[json.loads(p.read_text()) for p in paths]
    z=list(map(F,basis['NEGATIVE_CORNER_DIRECTION']));norm=sum(v*v for v in z)
    if norm<=0:raise ValueError('nonzero exact witness required')
    value=F(old['exact_negative_normalized_corner_rayleigh'])
    for row in refinement['rows']:
        i,j=row['degrees'];product=z[i]*z[j]/norm
        lo,hi=map(F,row['new_schur_entry_box'])
        if lo>hi:raise ValueError('ordered box required')
        value+=product*((lo if product>=0 else hi)-F(row['frozen_corner_entry']))
    return {'normalized_rayleigh_exact':str(value),'strictly_negative':value<0,
            'recipe':'Retain frozen full corner except the nine refined symmetric entries; at each changed entry choose lo if exact z_i*z_j>=0 else hi.',
            'input_sha256':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
            'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'actual_operator_negative_witness':False,'NO_RH_PROOF':True,'FULL_POINT_L1':'NOT_ISSUED'}

if __name__=='__main__':
    result=calculate()
    original=json.loads((OUT/'REMAINING_BOX_OBSTRUCTION.json').read_text())
    if result['normalized_rayleigh_exact']!=original['normalized_rayleigh_exact']:raise ValueError('frozen result mismatch')
    path=OUT/'REMAINING_BOX_REPRODUCER_CHECK.json'
    if path.exists():raise ValueError('preserve prior check')
    path.write_text(json.dumps(result,indent=2)+'\n')
    print('Exact remaining negative corner reproduced.')
