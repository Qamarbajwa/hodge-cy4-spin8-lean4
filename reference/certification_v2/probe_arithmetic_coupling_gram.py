"""Reproducible writer-only arithmetic Gram pilot at L1, degrees0..3."""
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path

from research.certification_v2.arithmetic_coupling_gram import arithmetic_gram
from research.certification_v2.exact_interval_ldl import certify
from research.certification_v2.spatial_overlap import log_enclosure,prime_powers

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"research/certification_v2/arithmetic_coupling_gram"


def sha(path):
    return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def encode(matrix):
    return [[x.encoded() for x in row] for row in matrix]


def main():
    manifest="research/certification_v2/IMPLEMENTATION_ACCEPTANCE.json"
    accepted=json.loads((ROOT/manifest).read_text())
    if accepted["terminal_status"]!="DONE" or not accepted["verdict"].startswith("ACCEPTED_"):
        raise ValueError("accepted arithmetic components missing")
    hashes={manifest:sha(manifest)}
    for path in ("research/certification_v2/spatial_overlap.py",
                 "research/certification_v2/exact_interval_ldl.py"):
        hashes[path]=sha(path)
        if hashes[path]!=accepted["files_sha256"][path]:
            raise ValueError("accepted input hash mismatch")
    for path in ("research/certification_v2/arithmetic_coupling_gram.py",
                 "research/certification_v2/probe_arithmetic_coupling_gram.py",
                 "research/certification_v2/arithmetic_coupling_gram/DERIVATION.md",
                 "tests/test_arithmetic_coupling_gram_v2.py"):
        hashes[path]=sha(path)
    logs=[log_enclosure(k,35) for k in (7,8)]
    assert logs[0].hi<2<logs[1].lo
    terms=prime_powers(7)
    full=arithmetic_gram([0,1,2,3],1,terms)
    missing=arithmetic_gram([0,1,2,3],1,terms,omit_cross_terms=True)
    assert full["PV2P"][0][0].lo>missing["PV2P"][0][0].hi
    reordered=arithmetic_gram([0,1,2,3],1,list(reversed(terms)))
    assert full==reordered
    receipt={"status":"WRITER_ONLY_AWAITING_INDEPENDENT_REVIEW_AND_ACCEPTANCE",
             "scope":"FULL_INFINITE_ARITHMETIC_QVP_GRAM_ONLY_NOT_FULL_HYBRID_COUPLING",
             "formula":"G=P V² P-(PVP)²=(QVP)*QVP","L":"1","degrees":[0,1,2,3],
             "active_prime_powers":terms,"active_set_log_boxes":[x.encoded() for x in logs],
             "input_sha256":hashes,
             "components":{key:encode(full[key]) for key in ("PV2P","PVP","PVP_squared","arithmetic_gram")},
             "signed_image_count":full["signed_image_count"],
             "ordered_pairs_per_entry":full["ordered_pairs_per_entry"],
             "Gram_box_LDL_diagnostic":certify(full["arithmetic_gram"]),
             "Gram_diagonal_float_diagnostics_only":[float((full["arithmetic_gram"][i][i].lo+full["arithmetic_gram"][i][i].hi)/2) for i in range(4)],
             "executed_negative_control":{"all_cross_terms_omitted":encode(missing["PV2P"]),
                                          "constant_mode_boxes_disjoint":True,"not_certificate":True},
             "executed_ordering_control":"IDENTICAL_EXACT_BOXES",
             "NO_RH_PROOF":True,"restored_intervals":0,"full_operator_status":"BLOCKED",
             "full_hybrid_coupling_status":"ARCH_AND_POLE_COUPLING_NOT_INCLUDED",
             "Q4_positive_complement_status":"NOT_ESTABLISHED",
             "finite650_and_coupling_status":"NOT_CONSTRUCTED","Schur_status":"BLOCKED"}
    OUT.mkdir(exist_ok=True)
    (OUT/"PILOT_RECEIPT.json").write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")
    print("Gram diagonals",receipt["Gram_diagonal_float_diagnostics_only"])
    print("Gram box LDL",receipt["Gram_box_LDL_diagnostic"]["status"])


if __name__=="__main__":
    main()
