"""Highdegree649 Arch repair evidence; preserve the prior Arb nonfinite attempt."""
from decimal import Decimal,localcontext
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys

from research.certification_v2.arch_entry_majorant import entry_box

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"research/certification_v2/arch_entry_majorant"


def sha(path):
    return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def diagnostic(value):
    value=F(value)
    with localcontext() as context:
        context.prec=14
        return str(Decimal(value.numerator)/Decimal(value.denominator))


def main():
    sys.set_int_max_str_digits(50000)
    hashes={}
    for manifest in ("research/certification_v2/authenticated_symbol_tail/IMPLEMENTATION_ACCEPTANCE.json",
                     "research/certification_v2/pole_compact_tail/IMPLEMENTATION_ACCEPTANCE.json"):
        data=json.loads((ROOT/manifest).read_text())
        if data["terminal_status"]!="DONE" or not data["verdict"].startswith("ACCEPTED_"):
            raise ValueError("accepted dependency missing")
        hashes[manifest]=sha(manifest)
        for path,expected in {**data.get("input_sha256",{}),**data["files_sha256"]}.items():
            hashes[path]=sha(path)
            if hashes[path]!=expected:
                raise ValueError("accepted dependency changed: "+path)
    symbol=json.loads((ROOT/"research/certification_v2/authenticated_symbol_tail/PILOT_RECEIPT.json").read_text())
    floor=json.loads((ROOT/"research/certification_v2/archimedean/PILOT_RECEIPT.json").read_text())["scalar_symbol_tail_floor"]
    if symbol["beta"]!=floor["beta"] or floor["cutoff"]!="400":
        raise ValueError("same-beta cutoff linkage failed")
    M=F(symbol["symbol_sup_authenticated"])
    for path in ("research/certification_v2/arch_entry_majorant.py",
                 "research/certification_v2/probe_arch_entry_majorant.py",
                 "research/certification_v2/arch_entry_majorant/DERIVATION.md",
                 "tests/test_arch_entry_majorant_v2.py",
                 "research/certification_v2/degree650_entry_cost/PILOT_RECEIPT.json",
                 "research/certification_v2/degree650_entry_cost/arch_CHILD_RESULT.json"):
        hashes[path]=sha(path)
    rows=[]
    for i,j in ((0,0),(1,649),(3,649),(127,649),(255,649),(647,649),(649,649),(0,649)):
        row=entry_box(i,j,1,400,M)
        row["radius_decimal_diagnostic_only"]=diagnostic(row["radius"])
        rows.append(row)
        print(i,j,row["status"],"radius",row["radius_decimal_diagnostic_only"])
    result={"status":"WRITER_ONLY_AWAITING_INDEPENDENT_REVIEW_AND_ACCEPTANCE",
            "scope":"SAME_BETA_CANONICAL_CUTOFF_ARCH_ENTRY_ENCLOSURES_ONLY",
            "input_sha256":hashes,"beta":floor["beta"],"rows":rows,
            "serialization_digit_ceiling":50000,
            "preserved_negative_evidence":"Original actual649Arb nonfinite attempt unchanged and hash bound; lowdegree0majorant target fails honestly",
            "NO_RH_PROOF":True,"restored_intervals":0,"full_operator_status":"BLOCKED",
            "matrix650_status":"NOT_CONSTRUCTED","spatial650_status":"CERTIFIED_GL_ARCHITECTURE_STILL_REQUIRED",
            "PSD_status":"NOT_TESTED_OR_PROMOTED","coupling_status":"NOT_COMPUTED"}
    OUT.mkdir(exist_ok=True)
    (OUT/"PILOT_RECEIPT.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")


if __name__=="__main__":
    main()
