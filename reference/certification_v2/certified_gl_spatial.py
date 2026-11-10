"""Candidate exact polynomial spatial quadrature with frozen GL650 boxes.

Rule architecture is a distinct accepted input; entry adapter remains candidate.
"""
from fractions import Fraction as F
from functools import lru_cache
import hashlib
import json
from pathlib import Path

from flint import arb,fmpq,ctx
from research.certification_v2.certified_legendre_rule import legendre_box
from research.certification_v2.archimedean.arb_adapter import encoded_bounds
from research.certification_v2.exact_interval_ldl import Interval,rational
from research.certification_v2.spatial_overlap import log_enclosure,sqrt_enclosure,spatial_matrix

ROOT=Path(__file__).resolve().parents[2]
RULE_PATH="research/certification_v2/certified_legendre_rule/PILOT_RECEIPT.json"
RULE_SHA="c341385c5751260596314aadb0585f2164341352e4f3e90ca799970da397d074"
SOURCE_PATH="research/certification_v2/certified_legendre_rule.py"
SOURCE_SHA="cd1c1e94f96d64ae0ee3db35572c1be8fbd9d7c2cf9f1b602466e4b099ef4f8e"
ACCEPTANCE_PATH="research/certification_v2/certified_legendre_rule/IMPLEMENTATION_ACCEPTANCE.json"


def sha(path):
    return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


@lru_cache(maxsize=1)
def frozen_rule():
    acceptance=json.loads((ROOT/ACCEPTANCE_PATH).read_text())
    if acceptance["terminal_status"]!="DONE" or acceptance["verdict"]!="ACCEPTED_BOUNDED_CERTIFIED_GL650_RULE_BOXES_AND_ARCHITECTURE_ONLY":
        raise ValueError("distinct accepted rule/architecture missing")
    for path,expected in {**acceptance.get("input_sha256",{}),**acceptance["files_sha256"]}.items():
        if sha(path)!=expected:
            raise ValueError("accepted rule dependency changed: "+path)
    if sha(RULE_PATH)!=RULE_SHA or sha(SOURCE_PATH)!=SOURCE_SHA:
        raise ValueError("frozen candidate rule source/receipt mismatch; no adoption")
    data=json.loads((ROOT/RULE_PATH).read_text())
    dependency="research/certification_v2/archimedean/arb_adapter.py"
    if sha(dependency)!=data["input_sha256"][dependency]:
        raise ValueError("frozen rule dyadic/ball helper changed")
    rule=next(row["rule"] for row in data["rows"] if row["n"]==650)
    if rule["status"]!="CERTIFIED_GAUSS_LEGENDRE_RULE_BOXES" or len(rule["nodes_weights"])!=650:
        raise ValueError("complete frozen650rule unavailable")
    return rule


def ball(value):
    value=Interval.parse(value)
    midpoint=(value.lo+value.hi)/2
    radius=(value.hi-value.lo)/2
    return arb(fmpq(midpoint.numerator,midpoint.denominator),fmpq(radius.numerator,radius.denominator))


def domain_legendre(degree,value):
    box=Interval.parse(encoded_bounds(value))
    # True quadrature arguments belong to[-1,1] by the proved support map.
    # Intersect numerical overhang with this domain before derivative enclosure.
    lower,upper=max(F(-1),box.lo),min(F(1),box.hi)
    if lower>upper:
        raise ValueError("support argument has no proved-domain intersection")
    return legendre_box(degree,Interval(lower,upper))


def entry(i,j,terms,length=1,bits=192,target_width="1e-12"):
    length,target_width=map(rational,(length,target_width))
    if type(i) is not int or type(j) is not int or min(i,j)<0 or length<=0 or target_width<=0 or type(bits) is not int or bits<64:
        raise ValueError("valid degrees, positive rational length/target and precision required")
    rule=frozen_rule()
    if i+j>2*rule["degree"]-1:
        raise ValueError("integrand degree exceeds exact quadrature rule")
    terms=list(terms)
    spatial_matrix([0],length,terms,digits=40,log_terms=35)  # accepted exact term validation
    runs=[]
    with ctx.workprec(bits):
        value=arb(0)
        for n,p in sorted(terms):
            shift=log_enclosure(n,512)
            ratio=shift/length
            if ratio.lo>=2:
                runs.append({"n":n,"status":"INACTIVE_BY_SUPPORT"})
                continue
            if ratio.hi>=2 or ratio.lo<0:
                return {"status":"INCONCLUSIVE_ACTIVATION_BOUNDARY","n":n,"ratio":ratio.encoded(),
                        "NO_RH_PROOF":True,"full_operator_status":"BLOCKED"}
            if (i+j)%2:
                runs.append({"n":n,"status":"EXACT_OPPOSITE_PARITY_ZERO"})
                continue
            r=ball(ratio)
            # Dimensionless t in[r-1,1]; t=r/2+(1-r/2)*node.
            half=1-r/2
            midpoint=r/2
            integral=arb(0)
            for item in rule["nodes_weights"]:
                node,weight=ball(item["node"]),ball(item["weight"])
                t=midpoint+half*node
                u=domain_legendre(i,t)
                v=domain_legendre(j,t-r)
                integral+=weight*u*v
            # Same-parity reflection makes the two shift directions equal.
            # Spatial normalization cancels L: 2 * sqrtprod/2 * half integral.
            coefficient=-ball(log_enclosure(p,512))/arb(n).sqrt()
            contribution=coefficient*arb((2*i+1)*(2*j+1)).sqrt()*half*integral
            if not contribution.is_finite():
                return {"status":"INCONCLUSIVE_NONFINITE_SPATIAL_ENCLOSURE","n":n,
                        "NO_RH_PROOF":True,"full_operator_status":"BLOCKED"}
            value+=contribution
            runs.append({"n":n,"status":"FULL_POLYNOMIAL_RULE_EVALUATED","entry":encoded_bounds(contribution)})
        if not value.is_finite():
            return {"status":"INCONCLUSIVE_NONFINITE_SPATIAL_SUM","NO_RH_PROOF":True,"full_operator_status":"BLOCKED"}
        box=Interval.parse(encoded_bounds(value))
    return {"status":"CANDIDATE_SPATIAL_ENTRY_TARGET_MET" if box.hi-box.lo<=target_width else "VALID_CANDIDATE_SPATIAL_ENTRY_TARGET_NOT_MET",
            "entry":box.encoded(),"width":str(box.hi-box.lo),"degrees":[i,j],
            "length":str(length),"precision_bits":bits,"log_series_terms":512,
            "rule_degree":650,"polynomial_integrand_degree":i+j,"quadrature_truncation_remainder":"EXACTLY_ZERO_BY_POLYNOMIAL_DEGREE",
            "method":"CERTIFIED_NODE_WEIGHT_ENDPOINT_AND_NATIVE_POINT_DERIVATIVE_IMAGE_BALLS",
            "term_runs":runs,"target_width":str(target_width),
            "rule_acceptance_status":"DISTINCT_ACCEPTED_RULE_INPUT_SPATIAL_ADAPTER_PENDING_REVIEW",
            "NO_RH_PROOF":True,"full_operator_status":"BLOCKED"}
