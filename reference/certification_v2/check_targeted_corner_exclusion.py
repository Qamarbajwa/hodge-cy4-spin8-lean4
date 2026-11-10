"""Recheck the frozen corner against nine rigorously refined Schur entries.

Excluding one old corner does not prove the repaired matrix family positive.
"""
from pathlib import Path
from fractions import Fraction as F
import json,gzip,hashlib

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/certification_v2/structured_schur_repair'

def run():
    target=OUT/'TARGETED_CORNER_RECHECK.json'
    if target.exists():raise ValueError('preserve existing check')
    refined=OUT/'STABLE_TARGETED_GRAM_REFINEMENT.json'
    receipt=json.loads(refined.read_text());new=receipt['runs'][-1]['entries']
    Apath=ROOT/'research/certification_v2/p650_stable_assembly/FINITE_LOWER.json.gz'
    A=json.loads(gzip.decompress(Apath.read_bytes()))
    corner_path=OUT/'EXACT_NEGATIVE_CORNER.json.gz'
    corner=json.loads(gzip.decompress(corner_path.read_bytes()))
    writer_path=ROOT/'research/certification_v2/p650_stable_assembly/WRITER_RECEIPT.json'
    writer=json.loads(writer_path.read_text());factor=(1+F(writer['epsilon']))/F(writer['c']);correction=F(writer['scalar_coupling_correction'])
    rows=[]
    for i,k in enumerate([7,9,11]):
        for j,l in enumerate([7,9,11]):
            alo,ahi=map(F,A[k][l]);glo,ghi=map(F,new[i][j]);shift=correction if k==l else 0
            lo=alo-factor*ghi-shift;hi=ahi-factor*glo-shift;old=F(corner[k][l])
            rows.append({'degrees':[k,l],'new_schur_entry_box':[str(lo),str(hi)],'frozen_corner_entry':str(old),
                         'frozen_corner_admissible_at_this_entry':lo<=old<=hi,
                         'constraint':'S_kl=A_lower_kl-(1+epsilon)/c*Gv_kl-diagonal_correction; Gv from shared full images minus complete P650 projection'})
    record={'status':'WRITER_ONLY_EXACT_CORNER_EXCLUSION_RECHECK','rows':rows,
            'old_corner_excluded':any(not r['frozen_corner_admissible_at_this_entry'] for r in rows),
            'new_family_positive':False,'actual_operator_negative_witness':False,'NO_RH_PROOF':True,'FULL_POINT_L1':'NOT_ISSUED',
            'input_sha256':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in [refined,Apath,corner_path,writer_path]},
            'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    target.write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({'old_corner_excluded':record['old_corner_excluded'],'excluded_entries':sum(not r['frozen_corner_admissible_at_this_entry'] for r in rows)}))

if __name__=='__main__':run()
