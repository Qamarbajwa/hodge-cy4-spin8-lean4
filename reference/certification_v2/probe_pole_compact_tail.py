"""Reproduce writer-only pole compact bounds; accepted input files stay unchanged."""
from decimal import Decimal,localcontext
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys

from research.certification_v2.pole_compact_tail import pole_compact_bound

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"research/certification_v2/pole_compact_tail"


def sha(path):
    return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def diagnostic(value):
    value=F(value)
    with localcontext() as context:
        context.prec=14
        return str(Decimal(value.numerator)/Decimal(value.denominator))


def main():
    sys.set_int_max_str_digits(50000)
    manifest="research/certification_v2/CHAIN_REPAIR_ACCEPTANCE.json"
    accepted=json.loads((ROOT/manifest).read_text())
    if accepted["terminal_status"]!="DONE" or not accepted["verdict"].startswith("ACCEPTED_"):
        raise ValueError("accepted pole implementation unavailable")
    hashes={manifest:sha(manifest)}
    for path in ("research/certification_v2/pole_entries.py",
                 "research/certification_v2/POLE_ENTRY_DERIVATION.md"):
        hashes[path]=sha(path)
        if hashes[path]!=accepted["files_sha256"][path]:
            raise ValueError("accepted pole source mismatch")
    for path in ("research/certification_v2/pole_compact_tail.py",
                 "research/certification_v2/probe_pole_compact_tail.py",
                 "research/certification_v2/pole_compact_tail/DERIVATION.md",
                 "tests/test_pole_compact_tail_v2.py"):
        hashes[path]=sha(path)
    rows=[]
    for degree in (4,650,700):
        row=pole_compact_bound("23/20",degree)
        row["delta_decimal_diagnostic_only"]=diagnostic(row["pole_delta_upper"])
        rows.append(row)
        print("degree",degree,"delta",row["delta_decimal_diagnostic_only"])
    receipt={"status":"WRITER_ONLY_AWAITING_INDEPENDENT_REVIEW_AND_ACCEPTANCE",
             "scope":"POLE_COMPACT_REPLACEMENT_COMPONENT_ONLY",
             "input_sha256":hashes,"rows":rows,"serialization_digit_ceiling":50000,
             "NO_RH_PROOF":True,"restored_intervals":0,"full_operator_status":"BLOCKED",
             "remaining_obligations":["Canonical projection and form domain linkage",
                                      "Full complement lower bound and arithmetic norm",
                                      "Cross-coupling estimate","Finite Schur positivity",
                                      "Reference spectral upper bound and uniform continuum certificate"]}
    OUT.mkdir(exist_ok=True)
    (OUT/"PILOT_RECEIPT.json").write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")


if __name__=="__main__":
    main()
