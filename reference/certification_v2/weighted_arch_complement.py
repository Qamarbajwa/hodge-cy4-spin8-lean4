"""Rational weighted Arch complement lower bound at L1, projectiondegrees<4."""
from fractions import Fraction as F
from functools import lru_cache
import hashlib
import json
from pathlib import Path

from research.certification_v2.archimedean.real_adapter import symbol,pi_enclosure
from research.certification_v2.exact_interval_ldl import Interval,rational
from research.certification_v2.pole_compact_tail import parity_tail_squared

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"research/certification_v2/weighted_arch_complement"


def sha(path):
    return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


@lru_cache(maxsize=4096)
def point_symbol(t):
    return symbol(t,series_terms=128,gamma_terms=256)


def residual_upper(t):
    t=rational(t)
    if t<0:
        raise ValueError("nonnegative t required")
    return min(F(2),t**8/F(2592))


def residual_integral_bounds(a,b):
    """Enclose integral of U(t)=min(2,t^8/2592) over a positive panel."""
    a,b=rational(a),rational(b)
    if a<0 or b<a:
        raise ValueError("ordered nonnegative panel required")
    lower=(b-a)*residual_upper(a)
    # integral min(f,g) <= min(integral f, integral g), even across its kink.
    upper=min(2*(b-a),(b**9-a**9)/F(9*2592))
    return Interval(lower,upper)


def weighted_bound(s,beta,panels=64):
    s,beta=rational(s),rational(beta)
    if s<=0 or s>400 or type(panels) is not int or panels<1:
        raise ValueError("0<s<=400 and positive panel count required")
    hs=point_symbol(s)
    integral=Interval(0,0)
    width=s/panels
    for p in range(panels):
        a,b=p*width,(p+1)*width
        ha,hb=point_symbol(a),point_symbol(b)
        weight=Interval(max(F(0),hs.lo-hb.hi),max(F(0),hs.hi-ha.lo))
        integral=integral+weight*residual_integral_bounds(a,b)
    pi=pi_enclosure()
    penalty=integral/pi
    # J_U may overestimate the exact-R4 penalty: ONLY its lower functional bound
    # implies an Arch floor, never its upper endpoint as an Arch upper bound.
    functional=hs-penalty
    return {"s":str(s),"panels":panels,"h_s":hs.encoded(),
            "majorant_penalty_integral":integral.encoded(),
            "majorant_functional_enclosure":functional.encoded(),
            "canonical_arch_lower_bound":str(functional.lo),
            "hybrid_h_s_le_beta_proved":hs.hi<=beta,
            "hybrid_arch_lower_bound":str(functional.lo) if hs.hi<=beta else None,
            "residual_majorant":"min(2,t^8/2592)",
            "pi_box":pi.encoded(),"NO_RH_PROOF":True,"full_operator_status":"BLOCKED"}


def authenticate():
    manifests={
        "research/certification_v2/ARCH_AND_COMPACT_ACCEPTANCE.json":[
            "research/certification_v2/archimedean/real_adapter.py",
            "research/certification_v2/archimedean/PILOT_RECEIPT.json"],
        "research/certification_v2/pole_compact_tail/IMPLEMENTATION_ACCEPTANCE.json":[
            "research/certification_v2/pole_compact_tail.py"],
    }
    hashes={}
    for manifest,files in manifests.items():
        data=json.loads((ROOT/manifest).read_text())
        if data["terminal_status"]!="DONE" or not data["verdict"].startswith("ACCEPTED_"):
            raise ValueError("accepted component missing")
        hashes[manifest]=sha(manifest)
        for path in files:
            hashes[path]=sha(path)
            if hashes[path]!=data["files_sha256"][path]:
                raise ValueError("accepted hash mismatch: "+path)
    return hashes


def main():
    hashes=authenticate()
    for path in ("research/certification_v2/weighted_arch_complement.py",
                 "research/certification_v2/weighted_arch_complement/DERIVATION.md",
                 "tests/test_weighted_arch_complement_v2.py",
                 "research/certification_v2/full_form_l1/next_route/WEIGHTED_COMPLEMENT.md",
                 "research/certification_v2/full_form_l1/complement_writer/COMPLEMENT_ROUTE_DRAFT.md",
                 "research/certification_v2/full_form_l1/acceptance/TECHNICAL_ACCEPTANCE.json"):
        hashes[path]=sha(path)
    beta=F(json.loads((ROOT/"research/certification_v2/archimedean/PILOT_RECEIPT.json").read_text())["scalar_symbol_tail_floor"]["beta"])
    odd_penalty=2*parity_tail_squared(1,4,1)["tail_squared_upper"]
    rows=[]
    for s in (1,2,3,4,8,10):
        for panels in (64,128):
            row=weighted_bound(s,beta,panels)
            arch=F(row["canonical_arch_lower_bound"])
            row["diagnostic_arch_lower_float_only"]=float(arch)
            row["dependency_conditioned_even_floor"]=str(arch-F(13,4))
            row["dependency_conditioned_odd_floor"]=str(arch-F(13,4)-odd_penalty)
            row["spatial_13_over4_status"]="EXTERNAL_SCOPED_BRANCH_INPUT_HASHED_NOT_REVALIDATED_HERE"
            rows.append(row)
            print("s",s,"panels",panels,"arch floor",float(arch),"hybrid gate",row["hybrid_h_s_le_beta_proved"],flush=True)
    best=max(F(row["canonical_arch_lower_bound"]) for row in rows)
    receipt={"status":"WRITER_ONLY_AWAITING_INDEPENDENT_REVIEW_AND_ACCEPTANCE",
             "scope":"WEIGHTED_ARCH_COMPLEMENT_FLOOR_L1_DEGREES0_THROUGH3",
             "input_sha256":hashes,"beta":str(beta),"rows":rows,
             "odd_pole_penalty_upper":str(odd_penalty),
             "odd_pole_scope":"2||Q sinh(x/2)||²; entire accepted odd coefficient tail at L1,d4",
             "best_canonical_arch_lower_bound":str(best),
             "best_arch_lower_float_diagnostic_only":float(best),
             "positive_full_complement_established":False,
             "negative_evidence":["All sampled sufficient Arch lower bounds and dependency-conditioned full floors fail to establish positivity; no negative Rayleigh witness implied."],
             "NO_RH_PROOF":True,"restored_intervals":0,"full_operator_status":"BLOCKED",
             "remaining_obligations":["Independent analytic route and implementation review",
                                      "Positive full complement lower bound","Full cross coupling and Schur margin",
                                      "Uniform continuum certificate"]}
    OUT.mkdir(exist_ok=True)
    (OUT/"PILOT_RECEIPT.json").write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")


if __name__=="__main__":
    main()
