"""Diagnostic Ritz basis plus exact frozen negative corner and sensitivities.

Floating eigenspaces propose directions only; no spectral theorem is issued.
"""
from pathlib import Path
from fractions import Fraction as F
import gzip, hashlib, json, time
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'research/certification_v2/structured_schur_repair'

def read(p):
    data=(ROOT/p).read_bytes()
    return json.loads(gzip.decompress(data) if p.endswith('.gz') else data)

def run():
    started=time.monotonic(); OUT.mkdir(exist_ok=True)
    target=OUT/'CRITICAL_SUBSPACE.json'
    if target.exists(): raise ValueError('preserve previous evidence')
    base='research/certification_v2/p650_stable_assembly/'
    matrix=read(base+'SCHUR_LOWER.json.gz')
    proposal=read(base+'SCHUR_LOWER_RAYLEIGH_PROPOSAL.json')
    z=list(map(F,proposal['exact_dyadic_trial_vector']))
    norm=sum(v*v for v in z)
    assert norm>0
    corner=[]; sensitive=[]; total=F(0)
    for i,row in enumerate(matrix):
        out=[]
        for j,pair in enumerate(row):
            lo,hi=map(F,pair); product=z[i]*z[j]
            out.append(str(lo if product>=0 else hi))
            if j>=i:
                sensitivity=abs(product)*(hi-lo)*(1 if i==j else 2)/norm
                total+=sensitivity
                sensitive.append((sensitivity,i,j))
        corner.append(out)
    payload=json.dumps(corner,separators=(',',':')).encode()
    p=OUT/'EXACT_NEGATIVE_CORNER.json.gz';p.write_bytes(gzip.compress(payload,mtime=0))
    midpoint=np.array([[(float(F(a))+float(F(b)))/2 for a,b in row] for row in matrix])
    sectors=[];basis=[]
    for parity in [0,1]:
        indices=list(range(parity,650,2))
        values,vectors=np.linalg.eigh(midpoint[np.ix_(indices,indices)])
        # Six per sector is a diagnostic starting space, never a safe-bulk claim.
        for k in range(6):
            column=['0']*650
            for i,value in zip(indices,vectors[:,k]):column[i]=str(F.from_float(float(value)))
            basis.append(column)
        sectors.append({'parity':parity,'six_smallest_midpoint_ritz_values':values[:6].tolist(),
                        'seventh_midpoint_ritz_value':float(values[6]),'spectral_status':'FLOAT_DIAGNOSTIC_ONLY'})
    masses=[sum(z[k]*z[k] for k in range(p,650,2))/norm for p in [0,1]]
    ordered=sorted(((z[i]*z[i]/norm,i) for i in range(650)),reverse=True)
    paths=[base+'SCHUR_LOWER.json.gz',base+'SCHUR_LOWER_RAYLEIGH_PROPOSAL.json',base+'IMPLEMENTATION_ACCEPTANCE.json']
    result={'task':'RH-V2-P650-CRITICAL-SUBSPACE-IDENTIFICATION-L1-T400-001',
            'status':'WRITER_ONLY_DIAGNOSTIC_RITZ_BASIS_WITH_EXACT_BOX_SENSITIVITY',
            'CRITICAL_SUBSPACE_DIMENSION':12,'dimension_scope':'PROPOSED_NOT_PROVEN_EXHAUSTIVE',
            'CRITICAL_BASIS':basis,'CRITICAL_PARITY':{'exact_witness_even_mass':str(masses[0]),'exact_witness_odd_mass':str(masses[1])},
            'NEGATIVE_CORNER_DIRECTION':proposal['exact_dyadic_trial_vector'],
            'DOMINANT_SENSITIVE_ENTRIES':[{'i':i,'j':j,'full_width_rayleigh_effect':str(v)} for v,i,j in sorted(sensitive,reverse=True)[:40]],
            'total_independent_box_rayleigh_width':str(total),
            'dominant_basis_degrees':[{'degree':i,'exact_mass':str(v)} for v,i in ordered[:30]],
            'sectors':sectors,'CONDITIONING':'EXACT_GRAM_VALIDATION_PENDING; FLOAT_RITZ_BASIS_NOT_A_VERIFIED_CONGRUENCE',
            'DOMINANT_OPERATOR_TERMS':'COMPONENT_SENSITIVITY_RECOMPUTATION_PENDING',
            'exact_corner_file':p.relative_to(ROOT).as_posix(),'exact_corner_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
            'input_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths},
            'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'seconds':time.monotonic()-started,'NO_RH_PROOF':True,'FULL_POINT_L1':'NOT_ISSUED',
            'actual_operator_negative_witness':False,'safe_bulk_certified':False}
    target.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'seconds':result['seconds'],'parity':result['CRITICAL_PARITY'],'top_degrees':result['dominant_basis_degrees'][:5],'top_sensitivities':result['DOMINANT_SENSITIVE_ENTRIES'][:3]}))

if __name__=='__main__':run()
