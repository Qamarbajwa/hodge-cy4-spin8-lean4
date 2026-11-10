"""Small moment controls plus ACTUAL n650 certified root/weight cost probe."""
import hashlib
import json
from pathlib import Path
import time

from research.certification_v2.certified_legendre_rule import certify_rule,moments

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"research/certification_v2/certified_legendre_rule"


def main():
    OUT.mkdir(exist_ok=True)
    hashes={}
    for path in ("research/certification_v2/certified_legendre_rule.py",
                 "research/certification_v2/probe_certified_legendre_rule.py",
                 "research/certification_v2/p650_programme/SPATIAL_ARCHITECTURE_CANDIDATE.md",
                 "tests/test_certified_legendre_rule_v2.py",
                 "research/certification_v2/archimedean/arb_adapter.py",
                 "research/certification_v2/certified_legendre_rule/return_optional_import/test_rule_original.py.txt",
                 "research/certification_v2/certified_legendre_rule/return_optional_import/FIRST_FREEZE_PILOT_RECEIPT.json"):
        hashes[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    rows=[]
    # Deliberately inadequate Newton candidate does not imply a valid root.
    negative=certify_rule(8,bits=64,bracket_bits=80,newton_steps=1)
    for n,bits in ((1,128),(2,128),(4,128),(8,128),(650,192)):
        started=time.monotonic()
        rule=certify_rule(n,bits=bits)
        row={"n":n,"bits":bits,"wall_seconds":round(time.monotonic()-started,3),"rule":rule}
        if rule["status"]=="CERTIFIED_GAUSS_LEGENDRE_RULE_BOXES":
            indices=range(2*n) if n<=8 else (0,1,2,3,4,5,12,1298,1299)
            row["moment_controls"]=moments(rule,indices)
            if not all(item["contained"] for item in row["moment_controls"]):
                raise ValueError("certified quadrature moment containment failed")
        rows.append(row)
        receipt={"status":"WRITER_ONLY_ARCHITECTURE_AND_RULES_AWAITING_INDEPENDENT_REVIEW_AND_ACCEPTANCE",
                 "input_sha256":hashes,"negative_seed_control":negative,"rows":rows,
                 "preserved_implementation_failure":"Initial moment check used Arb generic real power on zero-containing rootbox and returned nonfinite; repaired with exact nonnegative integer multiplication powers.",
                 "preserved_integration_failure":"First frozen optional test imported python-flint unconditionally and broke system unittest discovery. Original test and first frozen receipt preserved; corrected test honestly SkipTests when optional dependency absent.",
                 "NO_RH_PROOF":True,"full_operator_status":"BLOCKED",
                 "matrix650_status":"NOT_CONSTRUCTED","spatial_entry649_status":"NOT_YET_INTEGRATED",
                 "architecture_adoption_status":"PENDING_INDEPENDENT_REVIEW"}
        (OUT/"PILOT_RECEIPT.json").write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")
        print("n",n,rule["status"],"seconds",row["wall_seconds"],flush=True)


if __name__=="__main__":
    main()
