"""Candidate batched arithmetic compression; never a full-form certificate."""
from fractions import Fraction as F
from pathlib import Path
import gzip
import hashlib
import json
import time

from flint import arb, arb_mat, ctx
from research.certification_v2.certified_gl_spatial import frozen_rule, ball, domain_legendre
from research.certification_v2.archimedean.arb_adapter import encoded_bounds
from research.certification_v2.spatial_overlap import log_enclosure, prime_powers
from research.certification_v2.exact_interval_ldl import Interval

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'research/certification_v2/batch_gl_spatial'


def build(dimension, bits=192, progress=None):
    """All degrees below dimension, exact L=1; arithmetic contribution only.

    U diag(weights) V^T encloses one clipped shift. Adding its transpose
    retains both shift directions, rather than composing truncated shifts.
    """
    if type(dimension) is not int or not 1 <= dimension <= 650:
        raise ValueError('dimension in 1..650 required')
    if type(bits) is not int or bits < 64:
        raise ValueError('valid precision required')
    rule = frozen_rule()
    terms = prime_powers(7)
    if not log_enclosure(7, 512).hi < 2 < log_enclosure(8, 512).lo:
        raise ValueError('complete active set not proved')
    with ctx.workprec(bits):
        result = arb_mat(dimension, dimension)
        for n, p in terms:
            started = time.monotonic()
            ratio = log_enclosure(n, 512)
            if not 0 < ratio.lo <= ratio.hi < 2:
                raise ValueError('unresolved activation boundary')
            r = ball(ratio)
            half = 1-r/2
            center = r/2
            left = [[] for _ in range(dimension)]
            right = [[] for _ in range(dimension)]
            norms = [arb(2*k+1).sqrt() for k in range(dimension)]
            for item in rule['nodes_weights']:
                x = center + half*ball(item['node'])
                y = x-r
                weight = ball(item['weight'])
                for k in range(dimension):
                    left[k].append(norms[k]*domain_legendre(k, x)*weight)
                    right[k].append(norms[k]*domain_legendre(k, y))
            if progress:
                progress({'n':n, 'phase':'VECTORS_ENCLOSED', 'seconds':time.monotonic()-started})
            # phi normalization contributes 1/2; the support map contributes half.
            one = (arb_mat(left)*arb_mat(right).transpose())*(half/2)
            paired = one + one.transpose()
            coefficient = -ball(log_enclosure(p, 512))/arb(n).sqrt()
            result += paired*coefficient
            if progress:
                progress({'n':n, 'phase':'PAIRED_SHIFT_ACCUMULATED', 'seconds':time.monotonic()-started})
        # Reflection commutes with the complete paired-shift arithmetic operator.
        for i in range(dimension):
            for j in range(dimension):
                if (i+j)%2:
                    result[i,j] = arb(0)
        return result


def run(dimension=8):
    OUT.mkdir(exist_ok=True)
    label = f'd{dimension}'
    receipt_path = OUT / (label+'_RECEIPT.json')
    if receipt_path.exists():
        raise ValueError('refusing to overwrite an existing experiment')
    progress = []
    def record(value):
        progress.append(value)
        (OUT/(label+'_PROGRESS.json')).write_text(json.dumps(progress,indent=2)+'\n')
        print(json.dumps(value),flush=True)
    paths = [Path(__file__).relative_to(ROOT).as_posix(),
             'research/certification_v2/certified_gl_spatial.py',
             'research/certification_v2/certified_legendre_rule/IMPLEMENTATION_ACCEPTANCE.json',
             'research/certification_v2/certified_legendre_rule/PILOT_RECEIPT.json']
    hashes = {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}
    started = time.monotonic()
    matrix = build(dimension, progress=record)
    entries = [[encoded_bounds(matrix[i,j]) for j in range(dimension)] for i in range(dimension)]
    # Enforce exact symmetric boxes by intersecting two enclosures of the same entry.
    for i in range(dimension):
        for j in range(i,dimension):
            a,b = Interval.parse(entries[i][j]),Interval.parse(entries[j][i])
            box = Interval(max(a.lo,b.lo),min(a.hi,b.hi))
            entries[i][j]=entries[j][i]=box.encoded()
    payload = json.dumps(entries,separators=(',',':')).encode()
    target = OUT/(label+'_ARITHMETIC_MATRIX.json.gz')
    target.write_bytes(gzip.compress(payload,mtime=0))
    widths = [F(x[1])-F(x[0]) for row in entries for x in row]
    receipt = {'status':'WRITER_ONLY_CANDIDATE_ARITHMETIC_MATRIX_ENCLOSED',
               'dimension':dimension,'L':'1','degrees':list(range(dimension)),
               'active_prime_powers':prime_powers(7), 'precision_bits':192,
               'polynomial_degree_max':2*dimension-2,'rule_exactness_degree':1299,
               'matrix_file':target.relative_to(ROOT).as_posix(),
               'matrix_uncompressed_sha256':hashlib.sha256(payload).hexdigest(),
               'matrix_compressed_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
               'maximum_entry_width':str(max(widths)), 'seconds':time.monotonic()-started,
               'input_sha256':hashes,'components':'ARITHMETIC_ONLY',
               'P650_ENTRY_CERTIFIED':False,'full_operator_status':'BLOCKED',
               'NO_RH_PROOF':True,'restored_intervals':0}
    receipt_path.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:receipt[k] for k in ['status','dimension','maximum_entry_width','seconds']}),flush=True)


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--dimension',type=int,default=8)
    run(parser.parse_args().dimension)
