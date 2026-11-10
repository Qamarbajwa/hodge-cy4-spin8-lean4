"""Rational general-degree weighted Arch complement pilot at L1; no Schur claim."""
from fractions import Fraction as F
from functools import lru_cache
from math import factorial
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from research.certification_v2.archimedean.real_adapter import symbol,pi_enclosure
from research.certification_v2.exact_interval_ldl import Interval,rational
from research.certification_v2.pole_compact_tail import parity_tail_squared

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"research/certification_v2/general_weighted_complement"


def sha(path):
    return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def taylor_constant(degree):
    if type(degree) is not int or degree<1:
        raise ValueError("positive integer projection degree required")
    return F(2,factorial(degree)**2*(2*degree+1))


def residual_integral(degree,a,b):
    a,b=rational(a),rational(b)
    if a<0 or b<a:
        raise ValueError("ordered nonnegative panel required")
    constant=taylor_constant(degree)
    lower=(b-a)*min(F(2),constant*a**(2*degree))
    upper=min(2*(b-a),constant*(b**(2*degree+1)-a**(2*degree+1))/(2*degree+1))
    return Interval(lower,upper)


@lru_cache(maxsize=4096)
def hpoint(t,series_terms):
    return symbol(t,series_terms=series_terms,gamma_terms=256)


def arch_bound(degree,s,beta,panels=64,series_terms=1024):
    taylor_constant(degree)
    s,beta=rational(s),rational(beta)
    if s<=0 or s>400 or type(panels) is not int or panels<1 or type(series_terms) is not int or series_terms<1:
        raise ValueError("positive panel/series count and0<s<=400 required")
    hs=hpoint(s,series_terms)
    width=s/panels
    integral=Interval(0,0)
    for p in range(panels):
        a,b=p*width,(p+1)*width
        ha,hb=hpoint(a,series_terms),hpoint(b,series_terms)
        weight=Interval(max(F(0),hs.lo-hb.hi),max(F(0),hs.hi-ha.lo))
        integral=integral+weight*residual_integral(degree,a,b)
    pi=pi_enclosure()
    bound=hs-integral/pi
    return {"degree_cutoff":degree,"s":str(s),"panels":panels,
            "symbol_series_terms":series_terms,"h_s":hs.encoded(),
            "taylor_squared_constant":str(taylor_constant(degree)),
            "majorant_integral":integral.encoded(),"pi_box":pi.encoded(),
            "majorant_functional_box":bound.encoded(),
            "arch_floor":str(bound.lo),"arch_floor_float_diagnostic_only":float(bound.lo),
            "hybrid_same_beta_gate":hs.hi<=beta,
            "hybrid_arch_floor":str(bound.lo) if hs.hi<=beta else None}


def accepted_inputs():
    bindings={
        "research/certification_v2/ARCH_AND_COMPACT_ACCEPTANCE.json":[
            "research/certification_v2/archimedean/real_adapter.py",
            "research/certification_v2/archimedean/PILOT_RECEIPT.json"],
        "research/certification_v2/pole_compact_tail/IMPLEMENTATION_ACCEPTANCE.json":[
            "research/certification_v2/pole_compact_tail.py"],
        "research/certification_v2/IMPLEMENTATION_ACCEPTANCE.json":[
            "research/certification_v2/exact_interval_ldl.py",
            "research/certification_v2/spatial_overlap.py"],
        "research/certification_v2/CHAIN_REPAIR_ACCEPTANCE.json":[
            "research/certification_v2/pole_entries.py"],
    }
    hashes={}
    for manifest,files in bindings.items():
        data=json.loads((ROOT/manifest).read_text())
        if data["terminal_status"]!="DONE" or not data["verdict"].startswith("ACCEPTED_"):
            raise ValueError("accepted component missing")
        hashes[manifest]=sha(manifest)
        for path in files:
            hashes[path]=sha(path)
            if hashes[path]!=data["files_sha256"][path]:
                raise ValueError("accepted source hash mismatch")
    return hashes


def authenticate_global_spatial():
    """13/4 belongs to the GLOBAL V norm, hence survives enlarging P."""
    acceptance="research/certification_v2/full_form_l1/acceptance/TECHNICAL_ACCEPTANCE.json"
    frozen="research/certification_v2/full_form_l1/FREEZE_MANIFEST.json"
    data=json.loads((ROOT/acceptance).read_text())
    freeze=json.loads((ROOT/frozen).read_text())
    hashes={acceptance:sha(acceptance),frozen:sha(frozen)}
    ok=(data.get("all_pass") is True and
        data.get("verdict")=="PASS_SCOPED_DECOMPOSITION_AND_CONSERVATIVE_ESTIMATES_ONLY" and
        data.get("freeze_manifest_sha256")==hashes[frozen])
    branch="codex/rh-full-form-l1"
    branch_checks={}
    for path,expected in freeze["files_sha256"].items():
        hashes[path]=sha(path)
        shown=subprocess.run(["git","show",branch+":"+path],cwd=ROOT,capture_output=True)
        branch_hash=hashlib.sha256(shown.stdout).hexdigest() if shown.returncode==0 else None
        branch_checks[path]={"live_matches":hashes[path]==expected,
                             "branch_matches":branch_hash==expected,"branch_sha256":branch_hash}
        ok=ok and hashes[path]==expected and branch_hash==expected
    return {"authenticated":bool(ok),"bound":"13/4",
            "scope":"GLOBAL_ARITHMETIC_SPATIAL_OPERATOR_NORM_AT_L1",
            "branch":branch,"input_sha256":hashes,"branch_checks":branch_checks,
            "not_a_projected_eigenvalue_claim":True}


def main():
    sys.set_int_max_str_digits(50000)
    hashes=accepted_inputs()
    for path in ("research/certification_v2/general_weighted_complement.py",
                 "research/certification_v2/general_weighted_complement/DERIVATION.md",
                 "tests/test_general_weighted_complement_v2.py"):
        hashes[path]=sha(path)
    spatial=authenticate_global_spatial()
    beta=F(json.loads((ROOT/"research/certification_v2/archimedean/PILOT_RECEIPT.json").read_text())["scalar_symbol_tail_floor"]["beta"])
    rows=[]
    for degree,s in ((4,4),(128,40),(256,80),(650,200)):
        for panels in (64,128):
            row=arch_bound(degree,s,beta,panels,series_terms=1024)
            odd=2*parity_tail_squared(1,degree,1)["tail_squared_upper"]
            lower=F(row["arch_floor"])-F(13,4)-odd
            row["odd_pole_penalty_upper"]=str(odd)
            row["dependency_conditioned_full_complement_floor"]=str(lower)
            row["dependency_conditioned_floor_float_diagnostic_only"]=float(lower)
            row["global_spatial_input_authenticated"]=spatial["authenticated"]
            row["authenticated_hybrid_complement_floor"]=(str(lower) if spatial["authenticated"] and row["hybrid_same_beta_gate"] else None)
            row["positive_complement_component_bound"]=(lower>0 and spatial["authenticated"] and row["hybrid_same_beta_gate"])
            rows.append(row)
            print("degree",degree,"s",s,"panels",panels,"arch",row["arch_floor_float_diagnostic_only"],
                  "complement",float(lower),"spatial_authenticated",spatial["authenticated"],flush=True)
    receipt={"status":"WRITER_ONLY_AWAITING_INDEPENDENT_REVIEW_AND_ACCEPTANCE",
             "scope":"GENERAL_DEGREE_L1_ARCH_AND_AUTHENTICATED_DEPENDENT_COMPLEMENT_COMPONENTS",
             "input_sha256":hashes,"global_spatial_authentication":spatial,"beta":str(beta),"rows":rows,
             "serialization_digit_ceiling":50000,
             "negative_evidence":"Small-degree insufficient floors preserved; no negative Rayleigh witness",
             "NO_RH_PROOF":True,"restored_intervals":0,"full_operator_status":"BLOCKED",
             "finite_650_block_status":"NOT_CONSTRUCTED","cross_coupling_status":"MISSING",
             "Schur_margin_status":"NOT_ESTABLISHED","continuum_status":"NOT_ATTEMPTED"}
    OUT.mkdir(exist_ok=True)
    (OUT/"PILOT_RECEIPT.json").write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")


if __name__=="__main__":
    main()
