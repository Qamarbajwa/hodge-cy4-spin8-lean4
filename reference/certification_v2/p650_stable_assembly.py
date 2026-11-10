"""Writer-only P650 finite and corrected Schur matrices; no certificate."""
from fractions import Fraction as F
from pathlib import Path
import gzip,hashlib,json,sys
from flint import arb_mat,ctx
from research.certification_v2.archimedean.arb_adapter import ball,encoded_bounds
from research.certification_v2.exact_interval_ldl import Interval
from research.certification_v2.pole_entries import pole_matrix
from research.certification_v2.pole_compact_tail import pole_compact_bound
from research.certification_v2.compact_tail_bound import cutoff_tail_bound

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/certification_v2/p650_stable_assembly'

def read(path):
    value=(ROOT/path).read_bytes()
    return json.loads(gzip.decompress(value) if path.endswith('.gz') else value)

def run():
    sys.set_int_max_str_digits(50000)
    OUT.mkdir(exist_ok=True)
    if (OUT/'WRITER_RECEIPT.json').exists():raise ValueError('preserve earlier result')
    paths=['research/certification_v2/stable_shared_arch_quadrature/d650_RECEIPT.json',
           'research/certification_v2/batch_gl_spatial/d650_ARITHMETIC_MATRIX.json.gz',
           'research/certification_v2/batch_arithmetic_gram/d650_RECEIPT.json',
           'research/certification_v2/authenticated_symbol_tail/PILOT_RECEIPT.json']
    arch,v,gram,symbol=map(read,paths)
    if arch['dimension']!=650 or gram['dimension']!=650 or len(v)!=650:
        raise ValueError('matching P650 required')
    beta=F(symbol['beta']);M=F(symbol['symbol_sup_authenticated'])
    if F(arch['beta'])!=beta or arch['L']!='1' or arch['T']!='400' or gram['L']!='1':
        raise ValueError('canonical parameter mismatch')
    # c=9/10 requires the separate direct matching-complement supplement.
    # This writer matrix is not that theorem's acceptance.
    c=F(9,10);epsilon=F(1,10**8)
    arch_delta=cutoff_tail_bound(1,400,650,M)
    pole_delta=pole_compact_bound(F(1),650)
    pole32_delta=pole_compact_bound(F(1),32)
    delta=F(arch_delta['arch_compact_delta_upper'])+F(pole_delta['pole_delta_upper'])
    if not beta-F(13,4)-delta>c:
        raise ValueError('direct complement numerical hypothesis fails')
    truncation=F(pole32_delta['pole_delta_upper'])
    W32=pole_matrix(range(32),1)
    with ctx.workprec(192):
        A=arb_mat([[ball(x) for x in row] for row in arch['entries']])
        A+=arb_mat([[ball(x) for x in row] for row in v])
        G=arb_mat([[ball(x) for x in row] for row in gram['entries']])
        for i in range(650):
            A[i,i]+=ball(beta-truncation)
            for j in range(min(32,650)):
                if i<32:A[i,j]+=ball(W32[i][j])
        S=A-G*ball((1+epsilon)/c)
        correction=(1+1/epsilon)*delta*delta/c
        for i in range(650):S[i,i]-=ball(correction)
        outputs={}
        for name,matrix in [('FINITE_LOWER',A),('SCHUR_LOWER',S)]:
            entries=[]
            for i in range(650):
                row=[]
                for j in range(650):
                    if (i+j)%2:row.append(['0','0']);continue
                    a=Interval.parse(encoded_bounds(matrix[i,j]));b=Interval.parse(encoded_bounds(matrix[j,i]))
                    row.append(Interval(max(a.lo,b.lo),min(a.hi,b.hi)).encoded())
                entries.append(row)
            payload=json.dumps(entries,separators=(',',':')).encode()
            p=OUT/(name+'.json.gz');p.write_bytes(gzip.compress(payload,mtime=0))
            outputs[p.relative_to(ROOT).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
    sources=paths+[Path(__file__).relative_to(ROOT).as_posix(),
                  'research/certification_v2/p650_programme/L1_COMPOSITION_CANDIDATE.md',
                  'research/certification_v2/p650_programme/DIRECT_Q650_COMPLEMENT_CANDIDATE.md',
                  'research/certification_v2/p650_programme/DIRECT_Q650_COMPLEMENT_CALCULATIONS.json']
    receipt={'status':'WRITER_ONLY_UNACCEPTED_P650_ASSEMBLY',
             'input_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sources},
             'output_sha256':outputs,'c':str(c),'epsilon':str(epsilon),
             'compact_delta650':str(delta),'pole_truncation_delta32':str(truncation),
             'scalar_coupling_correction':str(correction),
             'arch_delta':arch_delta,'pole_delta':pole_delta,'pole32_delta':pole32_delta,
             'NO_RH_PROOF':True,'FULL_POINT_L1':'NOT_ISSUED',
             'finite_lower_bound':None,'Schur_margin':None,'restored_intervals':0}
    (OUT/'WRITER_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')

if __name__=='__main__':run()
