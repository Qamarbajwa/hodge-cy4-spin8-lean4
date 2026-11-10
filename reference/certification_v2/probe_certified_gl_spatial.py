"""Actual649 clipped-spatial repair pilot; candidate rule not silently adopted."""
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import time

from research.certification_v2.certified_gl_spatial import entry,RULE_PATH,SOURCE_PATH,ACCEPTANCE_PATH
from research.certification_v2.spatial_overlap import spatial_matrix,prime_powers,log_enclosure

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"research/certification_v2/certified_gl_spatial"


def main():
    OUT.mkdir(exist_ok=True)
    hashes={}
    for path in ("research/certification_v2/certified_gl_spatial.py",
                 "research/certification_v2/probe_certified_gl_spatial.py",
                 "research/certification_v2/certified_gl_spatial/DERIVATION.md",
                 "tests/test_certified_gl_spatial_v2.py",RULE_PATH,SOURCE_PATH,
                 ACCEPTANCE_PATH,
                 "research/certification_v2/certified_gl_spatial/first_candidate_pending_rule/source.py.txt",
                 "research/certification_v2/certified_gl_spatial/first_candidate_pending_rule/test.py.txt",
                 "research/certification_v2/certified_gl_spatial/first_candidate_pending_rule/PILOT_RECEIPT.json",
                 "research/certification_v2/degree650_entry_cost/PILOT_RECEIPT.json"):
        hashes[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    manifest="research/certification_v2/IMPLEMENTATION_ACCEPTANCE.json"
    data=json.loads((ROOT/manifest).read_text())
    if data["terminal_status"]!="DONE" or not data["verdict"].startswith("ACCEPTED_"):
        raise ValueError("accepted rational component disposition missing")
    hashes[manifest]=hashlib.sha256((ROOT/manifest).read_bytes()).hexdigest()
    for path in ("research/certification_v2/spatial_overlap.py","research/certification_v2/exact_interval_ldl.py"):
        actual=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
        if data["files_sha256"][path]!=actual:
            raise ValueError("accepted rational component changed")
        hashes[path]=actual
    terms=prime_powers(7)
    logs=[log_enclosure(n,512) for n in (7,8)]
    if not logs[0].hi<2<logs[1].lo:
        raise ValueError("complete active-set proof failed")
    checks=[]
    old=spatial_matrix([0,1,2,3],1,terms,digits=40,log_terms=35)
    for i,j in ((0,0),(0,2),(1,1),(1,3),(2,2),(3,3)):
        result=entry(i,j,terms)
        if "entry" not in result:
            raise ValueError("lowdegree comparison lacks valid entry")
        box=[F(x) for x in result["entry"]]
        overlap=max(box[0],old[i][j].lo)<=min(box[1],old[i][j].hi)
        if not overlap:
            raise ValueError("independent accepted polynomial comparison disjoint")
        checks.append({"degrees":[i,j],"candidate":result,"accepted_exact_box":old[i][j].encoded(),"boxes_overlap":overlap})
    rows=[]
    for i,j,selected in ((649,649,[(2,2)]),(1,649,terms),(3,649,terms),
                         (127,649,terms),(647,649,terms),(649,649,terms),(648,649,terms)):
        started=time.monotonic()
        result=entry(i,j,selected)
        row={"degrees":[i,j],"complete_active_set":selected==terms,
             "terms":selected,"result":result,"wall_seconds":round(time.monotonic()-started,3)}
        rows.append(row)
        print(i,j,"allprimes",selected==terms,result["status"],"seconds",row["wall_seconds"],flush=True)
        receipt={"status":"WRITER_ONLY_CANDIDATE_SPATIAL_REPAIR_AWAITING_DISTINCT_REVIEW",
                 "input_sha256":hashes,"lowdegree_comparisons":checks,"rows":rows,
                 "active_set_proof":"upper(log7)<2<lower(log8); n2,3,4,5,7 precisely active",
                 "preserved_negative_evidence":"Original actual649one-prime exact symbolic builder10s timeout receipt preserved/hash linked",
                 "architecture_acceptance_status":"DISTINCT_ACCEPTED_INPUT_ADAPTER_REVIEW_PENDING","NO_RH_PROOF":True,
                 "full_operator_status":"BLOCKED","matrix650_status":"NOT_CONSTRUCTED",
                 "Gram650_status":"NOT_CONSTRUCTED"}
        (OUT/"PILOT_RECEIPT.json").write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")


if __name__=="__main__":
    main()
